import sys
import os
import PyPDF2
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QLabel, QScrollArea, QHBoxLayout
from PyQt5.QtGui import QPixmap

class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.pdf_files = []

    def initUI(self):
        self.setWindowTitle('PDF Merger')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.list_widget = QListWidget(self)
        self.layout.addWidget(self.list_widget)

        self.add_button = QPushButton('Agregar PDFs', self)
        self.add_button.clicked.connect(self.add_pdfs)
        self.layout.addWidget(self.add_button)

        self.remove_button = QPushButton('Eliminar PDF', self)
        self.remove_button.clicked.connect(self.remove_pdf)
        self.layout.addWidget(self.remove_button)

        self.output_label = QLabel('Nombre del archivo de salida:', self)
        self.layout.addWidget(self.output_label)

        self.output_name = QLineEdit(self)
        self.layout.addWidget(self.output_name)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.preview_widget = QWidget()
        self.preview_layout = QHBoxLayout(self.preview_widget)
        self.scroll_area.setWidget(self.preview_widget)
        self.layout.addWidget(self.scroll_area)

        self.merge_button = QPushButton('Unir PDFs', self)
        self.merge_button.clicked.connect(self.merge_pdfs)
        self.layout.addWidget(self.merge_button)

        self.setLayout(self.layout)

    def add_pdfs(self):
        options = QFileDialog.Options()
        file_names, _ = QFileDialog.getOpenFileNames(self, "Selecciona archivos PDF", "", "PDF Files (*.pdf)", options=options)

        if file_names:
            for file_name in file_names:
                item = QListWidgetItem(file_name)
                self.pdf_files.append(file_name)
                self.list_widget.addItem(item)
            self.update_preview()  # Actualizar la vista previa después de agregar archivos PDF

    def remove_pdf(self):
        selected_items = self.list_widget.selectedItems()
        for item in selected_items:
            file_name = item.text()
            self.pdf_files.remove(file_name)
            self.list_widget.takeItem(self.list_widget.row(item))
        self.update_preview()  # Actualizar la vista previa después de eliminar archivos PDF

    def render_pdf_preview(self, pdf_path):
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)  # Mostrar la primera página como vista previa
        pixmap = QPixmap()
        pixmap.loadFromData(page.get_pixmap().tobytes("png"))
        return pixmap

    def update_preview(self):
        # Borrar todas las vistas previas anteriores
        for i in reversed(range(self.preview_layout.count())):
            widget = self.preview_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        if self.pdf_files:
            for pdf_file in self.pdf_files:
                pixmap = self.render_pdf_preview(pdf_file)
                label = QLabel(self)
                label.setPixmap(pixmap)
                self.preview_layout.addWidget(label)

    def merge_pdfs(self):
        if not self.pdf_files:
            return

        output_file, _ = QFileDialog.getSaveFileName(self, "Guardar archivo PDF de salida", "", "PDF Files (*.pdf)")

        if output_file:
            if not output_file.endswith('.pdf'):
                output_file += '.pdf'

            merged_pdf = PyPDF2.PdfMerger()
            for file_name in self.pdf_files:
                merged_pdf.append(file_name)

            output_name = self.output_name.text()
            if not output_name:
                output_name = "merged.pdf"

            output_file = os.path.join(os.path.dirname(output_file), output_name)
            merged_pdf.write(output_file)
            merged_pdf.close()
            self.list_widget.clear()
            self.pdf_files = []
            self.list_widget.addItem('PDFs unidos y guardados en: ' + output_file)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec_())
