# EPUB Translator Agent

EPUB Translator Agent is an AI-powered translation tool designed for translating EPUB books while maintaining their original formatting and structure. It leverages **Ollama's API** for translation, **Jinja2** for prompt templating, and **PyQt5** for an intuitive GUI.

⚠ **Disclaimer:** The usage of this tool must comply with copyright laws. Ensure you have the necessary rights to translate and distribute EPUB content. The authors and developers of EPUB Translator Agent are not responsible for any copyright violations arising from its use.

## Features
✅ **Translate EPUB books** while preserving paragraph structure  
✅ **Customizable translation style** based on book genre  
✅ **Bilingual mode** (original + translated text)  

## Installation
### **1. Clone the Repository**
```sh
git clone https://github.com/Mikael17125/EPUB-Translator-Agent
cd EPUB-Translator-Agent
```

### **2. Install Dependencies**
Use `pip` to install the required libraries:
```sh
pip install -r requirements.txt
```

### **3. Install Ollama and Download the Model**
Ollama is required to run the translation model. Install it and download your preferred model:
```sh
# Install Ollama (if not already installed)
# Refer to Ollama's official installation guide for your OS

# Download the translation model (e.g., llama3.2)
ollama pull llama3.2
```

### **4. Download NLTK Tokenizer (First-Time Only)**
```python
import nltk
nltk.download("punkt")
```

## Usage
### **Run the GUI**
```sh
python main.py
```
In the GUI, fill in the **Model Name** field with the **Ollama model** you want to use (e.g., `llama3.2`).

## Project Structure
```
📂 EPUB-Translator-Agent/
 ├── gui.py               # PyQt5 GUI Implementation
 ├── main.py              # Launches the application
 ├── translator.py        # EPUB translation logic
 ├── prompt_template.txt  # Jinja2 translation prompt
 ├── requirements.txt     # Project dependencies
```

## Configuration
### **Customize the Translation Prompt**
Modify `prompt_template.txt` to change translation behavior:
```
You are a professional translator specializing in translating {{genre}} books.
Your task is to faithfully translate the following text into {{language}}, maintaining the original style, tone, voice, and meaning without adding, removing, or modifying any content.

Instructions:
Provide only the translated text—no explanations, comments, disclaimers, or warnings.
Do not omit or alter any part of the original text. If a section contains legal disclaimers, website references, or addresses, translate them exactly as written.
Retain formatting, including line breaks and paragraph separations.
Idiomatic expressions should be translated into their closest natural equivalent in {{language}} while preserving their intended meaning.

Text to translate:
{{text}}

Output: Provide only the translated text, without any extra information.
```

## Troubleshooting
### **Common Issues & Fixes**
1️⃣ **Missing `punkt` tokenizer** → Run `nltk.download("punkt")`  
2️⃣ **EPUB file not found** → Ensure correct input path  
3️⃣ **Translation too slow** → Reduce token limit in settings 

## Legal & Copyright Considerations
⚠ **Users must ensure they have legal rights to translate and modify EPUB files.** Some books may be protected under copyright law, and unauthorized translation/distribution may violate regulations. This software is provided for legal and ethical use only.

## Contributing
Pull requests are welcome! If you find a bug or have an idea, feel free to open an issue.