import sys
import os
import PyPDF2
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QLabel, QScrollArea, QHBoxLayout, QInputDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage

class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.pdf_files = []

    def initUI(self):
        self.setWindowTitle('PDF Merger & Editor')
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

        self.move_up_button = QPushButton('Mover Arriba', self)
        self.move_up_button.clicked.connect(self.move_up)
        self.layout.addWidget(self.move_up_button)

        self.move_down_button = QPushButton('Mover Abajo', self)
        self.move_down_button.clicked.connect(self.move_down)
        self.layout.addWidget(self.move_down_button)

        self.edit_label = QLabel('Editar PDF:', self)
        self.layout.addWidget(self.edit_label)

        self.remove_pages_button = QPushButton('Quitar Páginas', self)
        self.remove_pages_button.clicked.connect(self.remove_pages)
        self.layout.addWidget(self.remove_pages_button)

        self.add_pages_button = QPushButton('Añadir Páginas desde Otro PDF', self)
        self.add_pages_button.clicked.connect(self.add_pages)
        self.layout.addWidget(self.add_pages_button)

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
                if file_name not in self.pdf_files:
                    item = QListWidgetItem(file_name)
                    self.pdf_files.append(file_name)
                    self.list_widget.addItem(item)
            self.update_preview()  # Actualizar la vista previa después de agregar archivos PDF

    def remove_pdf(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            for item in selected_items:
                file_name = item.text()
                if file_name in self.pdf_files:
                    self.pdf_files.remove(file_name)
                self.list_widget.takeItem(self.list_widget.row(item))
            self.update_preview()  # Actualizar la vista previa después de eliminar archivos PDF

    def move_up(self):
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            current_item = self.list_widget.takeItem(current_row)
            self.pdf_files.insert(current_row - 1, self.pdf_files.pop(current_row))
            self.list_widget.insertItem(current_row - 1, current_item)
            self.list_widget.setCurrentItem(current_item)

    def move_down(self):
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1:
            current_item = self.list_widget.takeItem(current_row)
            self.pdf_files.insert(current_row + 1, self.pdf_files.pop(current_row))
            self.list_widget.insertItem(current_row + 1, current_item)
            self.list_widget.setCurrentItem(current_item)

    def render_pdf_preview(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)  # Mostrar la primera página como vista previa
            pix = page.get_pixmap()
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            return QPixmap.fromImage(image)
        except Exception as e:
            print(f"Error al cargar vista previa del PDF: {str(e)}")
            return QPixmap()

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

    def remove_pages(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return

        pdf_file = selected_items[0].text()
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(reader.pages)

            page_nums, ok = QInputDialog.getText(self, "Quitar Páginas", f"Ingresa los números de página a quitar (1-{total_pages}), separados por comas:")

            if ok and page_nums:
                pages_to_remove = sorted(set(int(num) - 1 for num in page_nums.split(',')))
                writer = PyPDF2.PdfWriter()

                for i in range(total_pages):
                    if i not in pages_to_remove:
                        writer.add_page(reader.pages[i])

                edited_pdf = pdf_file.replace('.pdf', '_edited.pdf')
                with open(edited_pdf, 'wb') as f:
                    writer.write(f)

                self.pdf_files.append(edited_pdf)
                self.list_widget.addItem(edited_pdf)
                self.update_preview()  # Actualizar la vista previa después de quitar páginas
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al quitar páginas: {str(e)}")

    def add_pages(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return

        target_pdf_file = selected_items[0].text()
        options = QFileDialog.Options()
        source_pdf_file, _ = QFileDialog.getOpenFileName(self, "Selecciona un PDF para añadir páginas", "", "PDF Files (*.pdf)", options=options)

        if source_pdf_file:
            try:
                reader_target = PyPDF2.PdfReader(target_pdf_file)
                reader_source = PyPDF2.PdfReader(source_pdf_file)
                writer = PyPDF2.PdfWriter()

                for page in reader_target.pages:
                    writer.add_page(page)

                for page in reader_source.pages:
                    writer.add_page(page)

                edited_pdf = target_pdf_file.replace('.pdf', '_with_added_pages.pdf')
                with open(edited_pdf, 'wb') as f:
                    writer.write(f)

                self.pdf_files.append(edited_pdf)
                self.list_widget.addItem(edited_pdf)
                self.update_preview()  # Actualizar la vista previa después de añadir páginas
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al añadir páginas: {str(e)}")

    def merge_pdfs(self):
        if not self.pdf_files:
            self.list_widget.addItem('No hay archivos PDF para unir.')
            return

        output_file, _ = QFileDialog.getSaveFileName(self, "Guardar archivo PDF de salida", "", "PDF Files (*.pdf)")

        if output_file:
            if not output_file.endswith('.pdf'):
                output_file += '.pdf'

            try:
                merged_pdf = PyPDF2.PdfMerger()
                for file_name in self.pdf_files:
                    with open(file_name, 'rb') as f:
                        merged_pdf.append(f)

                merged_pdf.write(output_file)
                merged_pdf.close()

                self.list_widget.clear()
                self.pdf_files = []
                self.update_preview()  # Limpiar la vista previa después de la fusión
                self.list_widget.addItem(f'PDFs unidos y guardados en: {output_file}')
            except Exception as e:
                self.list_widget.addItem(f'Error al unir PDFs: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec_())
