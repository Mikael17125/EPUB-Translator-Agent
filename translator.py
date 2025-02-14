import re
import nltk
import tiktoken
from bs4 import BeautifulSoup
from ebooklib import epub
import ebooklib
from ollama import chat
from jinja2 import Template

# Ensure NLTK tokenizer is available (only needs to be run once in your environment)
nltk.download("punkt", quiet=True)

ENCODER = tiktoken.get_encoding("cl100k_base")

def load_prompt_template(template_path: str) -> Template:
    """
    Load and return a Jinja2 Template object from a text file.
    """
    with open(template_path, "r", encoding="utf-8") as f:
        template_str = f.read()
    return Template(template_str)

def count_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string using the configured tokenizer.
    """
    return len(ENCODER.encode(text))

def clean_text(text: str) -> str:
    """
    Remove unwanted escape characters but preserve important punctuation.
    """
    text = text.replace("\n", " ").replace("\r", " ")
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def split_text_by_tokens(text: str, max_tokens: int) -> list[str]:
    """
    Split a large text by sentence boundaries to ensure we don't exceed the model's token limit.
    """
    from nltk import sent_tokenize
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_cleaned = clean_text(sentence)
        sentence_length = count_tokens(sentence_cleaned)

        if current_length + sentence_length > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [sentence_cleaned]
            current_length = sentence_length
        else:
            current_chunk.append(sentence_cleaned)
            current_length += sentence_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

import time
import logging

def translate_text(
    text: str,
    target_language: str,
    model_name: str,
    token_limit: int,
    prompt_template: Template,
    genre: str,
    title: str,
    author: str,
    max_retries: int = 3,
    delay: float = 2.0
) -> str:
    """
    Translates the given text into the specified target language using Ollama's API.
    Implements retry logic to handle API failures and ensures robust chunk processing.
    """
    text = text.strip()
    if not text:
        return ""

    # Split text to avoid exceeding the model's token limit.
    chunks = split_text_by_tokens(text, max_tokens=token_limit // 2)
    translated_chunks = []

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        # Render the template with language, chunk, genre, title, and author
        prompt_content = prompt_template.render(
            language=target_language,
            text=chunk,
            genre=genre,
            title=title,
            author=author
        )

        # Retry mechanism in case of API failures
        for attempt in range(max_retries):
            try:
                response = chat(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt_content}]
                )

                if "message" in response and "content" in response["message"]:
                    translated_text = response["message"]["content"].strip()
                    translated_chunks.append(translated_text)
                    break  # Exit retry loop on success
            except Exception as e:
                logging.error(f"Translation attempt {attempt + 1} failed: {e}")
                time.sleep(delay)  # Wait before retrying
        else:
            logging.error(f"Translation failed after {max_retries} attempts. Skipping chunk.")

    return " ".join(translated_chunks)


def count_paragraphs_in_book(input_path: str) -> int:
    """
    Returns the total number of <p> paragraphs in the EPUB for progress reporting.
    """
    book = epub.read_epub(input_path)
    total_paragraphs = 0
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(content, "html.parser")
            total_paragraphs += len(soup.find_all("p"))
    return total_paragraphs

def translate_book(
    input_path: str,
    output_path: str,
    language: str,
    model_name: str,
    token_limit: int,
    template_path: str,
    progress_callback=None,
    genre: str = "General",
    bilingual: bool = False,
    override_title: str = "",
    override_author: str = ""
) -> None:
    """
    Translates an EPUB file paragraph-by-paragraph.
    If bilingual=True, displays original + italicized translation in the same paragraph with a line break.
    Metadata (title, author) is read from the EPUB, but can be overridden by user input.
    """
    prompt_template = load_prompt_template(template_path)
    book = epub.read_epub(input_path)

    # Fetch metadata from EPUB
    title_data = book.get_metadata("DC", "title")
    author_data = book.get_metadata("DC", "creator")

    # Determine final title/author to use
    epub_title = title_data[0][0] if title_data else "Unknown Title"
    epub_author = author_data[0][0] if author_data else "Unknown Author"

    # If user overrides are non-empty, use them; otherwise use EPUB metadata
    final_title = override_title if override_title else epub_title
    final_author = override_author if override_author else epub_author

    total_paragraphs = count_paragraphs_in_book(input_path)
    current_count = 0

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(content, "html.parser")

            paragraphs = soup.find_all("p")
            for p_tag in paragraphs:
                original_text = p_tag.get_text(strip=True)
                clean_paragraph = clean_text(original_text)

                if clean_paragraph:
                    # Translate text, passing final title/author
                    translated = translate_text(
                        text=clean_paragraph,
                        target_language=language,
                        model_name=model_name,
                        token_limit=token_limit,
                        prompt_template=prompt_template,
                        genre=genre,
                        title=final_title,
                        author=final_author
                    )

                    p_tag.clear()

                    if bilingual:
                        combined_html = (
                            f"ORIGINAL: {clean_paragraph}"
                            f"<br/><br/>"
                            f"<i>TRANSLATION: {translated}</i>"
                        )
                        soup_fragment = BeautifulSoup(combined_html, "html.parser")
                        p_tag.append(soup_fragment)
                    else:
                        p_tag.append(translated)

                # Update progress
                current_count += 1
                if progress_callback:
                    progress_callback(current_count, total_paragraphs)

            item.set_content(str(soup).encode("utf-8"))

    epub.write_epub(output_path, book, {})
