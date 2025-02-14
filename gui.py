import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from translator import translate_book

# -------------------- Worker -------------------- #
class Worker(QtCore.QObject):
    """
    Runs translation in a separate thread. Emits signals for progress, completion, and errors.
    """
    progressChanged = QtCore.pyqtSignal(int, int)  # current, total
    finished = QtCore.pyqtSignal()                 # translation done
    error = QtCore.pyqtSignal(str)                 # emits error message

    def __init__(
        self, 
        input_path, 
        output_path, 
        language, 
        model_name, 
        token_limit,
        template_path, 
        genre, 
        bilingual,
        override_title,
        override_author
    ):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.language = language
        self.model_name = model_name
        self.token_limit = token_limit
        self.template_path = template_path
        self.genre = genre
        self.bilingual = bilingual
        self.override_title = override_title
        self.override_author = override_author

    @QtCore.pyqtSlot()
    def run(self):
        """
        Called when the QThread starts. Executes the translation
        and uses a progress callback to emit progressChanged signals.
        """
        def progress_callback(current, total):
            self.progressChanged.emit(current, total)

        try:
            translate_book(
                input_path=self.input_path,
                output_path=self.output_path,
                language=self.language,
                model_name=self.model_name,
                token_limit=self.token_limit,
                template_path=self.template_path,
                progress_callback=progress_callback,
                genre=self.genre,
                bilingual=self.bilingual,
                override_title=self.override_title,
                override_author=self.override_author
            )
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

# -------------------- Custom Title Bar -------------------- #
class TitleBar(QtWidgets.QWidget):
    """
    Custom title bar for a frameless window. Includes:
    - Drag support to move the window
    - Title label
    - Minimize and Close buttons
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setFixedHeight(36)

        self.titleLabel = QtWidgets.QLabel("EPUB Translator Agent")
        self.titleLabel.setStyleSheet("font-size: 12pt; font-weight: 500; color: #444444;")

        # Close & Minimize Buttons in pastel
        self.minButton = QtWidgets.QPushButton()
        self.minButton.setFixedSize(20, 20)
        # Light green pastel
        self.minButton.setStyleSheet("""
            QPushButton {
                background-color: #E1F7E7; 
                border: none; 
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #D1F0DA;
            }
        """)

        self.closeButton = QtWidgets.QPushButton()
        self.closeButton.setFixedSize(20, 20)
        # Light red pastel
        self.closeButton.setStyleSheet("""
            QPushButton {
                background-color: #FDE1E1; 
                border: none; 
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #F8CFCF;
            }
        """)

        # Layout for title bar
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(self.titleLabel, 1)
        layout.addWidget(self.minButton)
        layout.addWidget(self.closeButton)
        self.setLayout(layout)

        self._mousePos = None

        # Connect signals
        self.minButton.clicked.connect(self.on_min_clicked)
        self.closeButton.clicked.connect(self.on_close_clicked)

    def on_min_clicked(self):
        if self.parent is not None:
            self.parent.showMinimized()

    def on_close_clicked(self):
        if self.parent is not None:
            self.parent.close()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self._mousePos = event.globalPos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._mousePos is not None and event.buttons() == QtCore.Qt.LeftButton:
            diff = event.globalPos() - self._mousePos
            self.parent.move(self.parent.x() + diff.x(), self.parent.y() + diff.y())
            self._mousePos = event.globalPos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self._mousePos = None
        super().mouseReleaseEvent(event)

# -------------------- Main Window -------------------- #
class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Frameless
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)

        self.resize(600, 480)

        # Minimal pastel style
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 10pt;
                background-color: #FFFFFF; /* White background */
                color: #444444; /* Slightly darker gray for text */
            }

            QGroupBox {
                border: 1px solid #EEEEEE;
                border-radius: 4px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                font-weight: 500;
            }

            QLabel {
                font-weight: normal;
            }

            QLineEdit, QSpinBox, QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #DDDDDD;
                border-radius: 3px;
                padding: 4px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #B3D7FF; /* pastel blue border on focus */
            }

            QCheckBox {
                padding: 4px;
            }

            QPushButton {
                background-color: #E8F0FE; /* pastel blue button */
                color: #444444;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #D7E8FD;
            }

            QProgressBar {
                text-align: center;
                height: 16px;
                border: 1px solid #EEEEEE;
                border-radius: 3px;
                background-color: #FAFAFA;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background-color: #B3D7FF; /* pastel progress chunk */
            }

            #statusLabel {
                color: #777777;
                margin-left: 4px;
            }
        """)

        # Title bar
        self.titleBar = TitleBar(self)

        # Content layout below title bar
        contentLayout = QtWidgets.QVBoxLayout()
        contentLayout.setContentsMargins(10, 10, 10, 10)
        contentLayout.setSpacing(10)

        # Group box: File Selection
        fileGroupBox = QtWidgets.QGroupBox("File Selection")
        fileLayout = QtWidgets.QGridLayout()

        self.inputEdit = QtWidgets.QLineEdit()
        self.inputEdit.setPlaceholderText("Path to input EPUB...")
        self.outputEdit = QtWidgets.QLineEdit()
        self.outputEdit.setPlaceholderText("Path to output EPUB...")
        self.templateEdit = QtWidgets.QLineEdit()
        self.templateEdit.setPlaceholderText("Path to template file...")

        self.browseInputBtn = QtWidgets.QPushButton("Browse")
        self.browseOutputBtn = QtWidgets.QPushButton("Browse")
        self.browseTemplateBtn = QtWidgets.QPushButton("Browse")

        row = 0
        fileLayout.addWidget(QtWidgets.QLabel("Input EPUB:"), row, 0)
        fileLayout.addWidget(self.inputEdit, row, 1)
        fileLayout.addWidget(self.browseInputBtn, row, 2)
        row += 1

        fileLayout.addWidget(QtWidgets.QLabel("Output EPUB:"), row, 0)
        fileLayout.addWidget(self.outputEdit, row, 1)
        fileLayout.addWidget(self.browseOutputBtn, row, 2)
        row += 1

        fileLayout.addWidget(QtWidgets.QLabel("Prompt Template:"), row, 0)
        fileLayout.addWidget(self.templateEdit, row, 1)
        fileLayout.addWidget(self.browseTemplateBtn, row, 2)
        row += 1

        fileGroupBox.setLayout(fileLayout)

        # Group box: Translation Settings
        settingsGroupBox = QtWidgets.QGroupBox("Translation Settings")
        settingsLayout = QtWidgets.QFormLayout()

        self.languageEdit = QtWidgets.QLineEdit("Indonesian")
        self.languageEdit.setPlaceholderText("e.g., English, Indonesian...")

        self.modelEdit = QtWidgets.QLineEdit("llama3.2")
        self.modelEdit.setPlaceholderText("e.g., llama3.2, gpt-4, etc.")

        self.tokenSpin = QtWidgets.QSpinBox()
        self.tokenSpin.setRange(1, 999999)
        self.tokenSpin.setValue(512)

        self.genreEdit = QtWidgets.QLineEdit("General")
        self.genreEdit.setPlaceholderText("e.g., Mystery, Fantasy...")

        # Bilingual checkbox
        self.bilingualCheck = QtWidgets.QCheckBox("Bilingual Output (Original + Translation)")

        # Override Title/Author
        self.titleEdit = QtWidgets.QLineEdit("")
        self.titleEdit.setPlaceholderText("Override book title here (optional)")

        self.authorEdit = QtWidgets.QLineEdit("")
        self.authorEdit.setPlaceholderText("Override book author here (optional)")

        settingsLayout.addRow("Language:", self.languageEdit)
        settingsLayout.addRow("Model Name:", self.modelEdit)
        settingsLayout.addRow("Token Limit:", self.tokenSpin)
        settingsLayout.addRow("Book Genre:", self.genreEdit)
        settingsLayout.addRow("Override Title:", self.titleEdit)
        settingsLayout.addRow("Override Author:", self.authorEdit)
        settingsLayout.addRow(self.bilingualCheck)

        settingsGroupBox.setLayout(settingsLayout)

        # Progress and status
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setValue(0)
        self.statusLabel = QtWidgets.QLabel("")
        self.statusLabel.setObjectName("statusLabel")

        self.translateBtn = QtWidgets.QPushButton("Translate")
        self.translateBtn.setFixedWidth(120)

        # Bottom layout
        bottomLayout = QtWidgets.QHBoxLayout()
        bottomLayout.addWidget(self.translateBtn)
        bottomLayout.addSpacing(10)
        bottomLayout.addWidget(self.progressBar)

        # Add everything to contentLayout
        contentLayout.addWidget(fileGroupBox)
        contentLayout.addWidget(settingsGroupBox)
        contentLayout.addLayout(bottomLayout)
        contentLayout.addWidget(self.statusLabel)

        # Main layout with TitleBar on top
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(self.titleBar)
        mainLayout.addLayout(contentLayout)
        self.setLayout(mainLayout)

        # --- Connect signals ---
        self.browseInputBtn.clicked.connect(self.select_input_file)
        self.browseOutputBtn.clicked.connect(self.select_output_file)
        self.browseTemplateBtn.clicked.connect(self.select_template_file)
        self.translateBtn.clicked.connect(self.start_translation)

        # Thread references
        self.thread = None
        self.worker = None

    # -------------- File Browsing Methods -------------- #
    def select_input_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Select Input EPUB", 
            "", 
            "EPUB Files (*.epub)"
        )
        if path:
            self.inputEdit.setText(path)

    def select_output_file(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Output EPUB",
            "",
            "EPUB Files (*.epub)"
        )
        if path:
            self.outputEdit.setText(path)

    def select_template_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Template File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            self.templateEdit.setText(path)

    # -------------- Translation Methods -------------- #
    def start_translation(self):
        input_path = self.inputEdit.text().strip()
        output_path = self.outputEdit.text().strip()
        template_path = self.templateEdit.text().strip()
        language = self.languageEdit.text().strip()
        model_name = self.modelEdit.text().strip()
        token_limit = self.tokenSpin.value()
        genre_str = self.genreEdit.text().strip()
        bilingual_flag = self.bilingualCheck.isChecked()

        # New override fields
        override_title = self.titleEdit.text().strip()
        override_author = self.authorEdit.text().strip()

        # Validate required fields
        if not all([input_path, output_path, template_path, language, model_name, genre_str]):
            QtWidgets.QMessageBox.warning(self, "Missing Info", "Please fill in all required fields.")
            return

        self.progressBar.setValue(0)
        self.statusLabel.setText("Translating...")

        self.thread = QtCore.QThread()
        self.worker = Worker(
            input_path,
            output_path,
            language,
            model_name,
            token_limit,
            template_path,
            genre_str,
            bilingual_flag,
            override_title,
            override_author
        )
        self.worker.moveToThread(self.thread)

        # Connect worker signals
        self.worker.progressChanged.connect(self.on_progress_changed)
        self.worker.finished.connect(self.on_translation_done)
        self.worker.error.connect(self.on_translation_error)

        # When the thread starts, call the worker's run() method
        self.thread.started.connect(self.worker.run)

        # When finished or error, terminate the thread
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        # Cleanup
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    @QtCore.pyqtSlot(int, int)
    def on_progress_changed(self, current, total):
        self.progressBar.setMaximum(total)
        self.progressBar.setValue(current)
        self.statusLabel.setText(f"Translating paragraph {current} of {total}")

    @QtCore.pyqtSlot()
    def on_translation_done(self):
        self.statusLabel.setText("Translation complete!")
        QtWidgets.QMessageBox.information(self, "Success", "Translation completed successfully!")

    @QtCore.pyqtSlot(str)
    def on_translation_error(self, msg):
        self.statusLabel.setText("Error during translation.")
        QtWidgets.QMessageBox.critical(self, "Error", f"Translation failed:\n{msg}")