import csv
import os
import random
import string
import sys
import typing
from copy import deepcopy

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qdarkgraystyle import load_stylesheet

import ui_batch
import ui_export
import ui_words
import ui_wordsearch
from wordsearch.wordsearch import WordSearch
from utilities.utilities import clean_words, fill, remove_asterisks, predict_width_height


class WordSearchModel(QAbstractTableModel):
    def __init__(self, data, upper=True):
        super().__init__()
        self._data = data
        self.upper = upper

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data[0])

    def case(self, text: str):
        text = str(text)
        if self.upper:
            return text.upper()
        return text.lower()

    def data(self, index: QModelIndex, role: int) -> bool:
        if role == Qt.DisplayRole:
            return self.case(self._data[index.row()][index.column()])

        if role == Qt.TextAlignmentRole:
            value = self.case(self._data[index.row()][index.column()])
            return Qt.AlignVCenter + Qt.AlignHCenter


class BatchWords(QDialog, ui_batch.Ui_Dialog):
    def __init__(self, parent, *args, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.buttonBox.accepted.connect(self.set_words)
        self.buttonBox.rejected.connect(self.reject)

    def guess_sep(self, string):
        pass

    def get_words(self):
        words_text = self.wordscreen.toPlainText()
        if "," in words_text:
            words = words_text.split(",")
        else:
            words = words_text.split()
        if "" in words and isinstance(words, list):
            words.remove("")
        words = [word.strip() for word in words]
        words = clean_words(words)
        return words

    def set_words(self):
        words = self.get_words()
        original_words = self.parent.get_words(self.parent.words_list)
        if original_words is not None:
            words = clean_words(words + original_words)
        self.parent.words_list.addItems(words)
        self.close()


class ImportWords(QDialog, ui_words.Ui_words):
    def __init__(self, parent, *args, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.import_btn.clicked.connect(self.import_words)
        self.clear_btn.clicked.connect(self.words_list.clear)
        self.buttonBox.accepted.connect(self.load_words)

    def load_words(self):
        words = [self.words_list.item(i, 0) for i in range(
            50) if self.words_list.item(i, 0) is not None]
        words = [item.text() for item in words]
        self.parent.words_list.addItems(words)

    def import_words(self):
        file, kind = QFileDialog.getOpenFileName(
            self, "Select File", None, "CSV (*.csv);;")
        if file:
            with open(file, errors="ignore") as f:
                reader = csv.reader(f)
                words = list(reader)
            if len(words) >= 1:
                if len(words) > 50:
                    QMessageBox.warning(
                        self, "Import words", "Words imported must be less than 50")
                    return
                if len(words[0]) > 1:
                    QMessageBox.warning(
                        self, "Import words", "Csv file must have one column, please adjust")
                    return
                else:
                    words = clean_words(
                        [item for sublist in words for item in sublist])
                    for word in range(len(words)):
                        self.words_list.setItem(
                            word, 0, QTableWidgetItem(str(words[word])))
            del words, reader


class Export(QDialog, ui_export.Ui_Dialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.export_list.itemClicked.connect(lambda x: self.export_ui_widget.setCurrentIndex(
            self.export_list.indexFromItem(x).row()))
        self.save_btn_txt.clicked.connect(
            lambda kind: self.get_file_name("txt"))
        self.save_btn_csv.clicked.connect(
            lambda kind: self.get_file_name("csv"))
        self.save_btn_xl.clicked.connect(lambda kind: self.get_file_name("xl"))
        self.save_btn_pdf.clicked.connect(
            lambda kind: self.get_file_name("pdf"))
        self.save_btn_json.clicked.connect(
            lambda kind: self.get_file_name("json"))
        self.save_btn_word.clicked.connect(
            lambda kind: self.get_file_name("word"))
        self.save_btn_html.clicked.connect(
            lambda kind: self.get_file_name("html"))
        self.export_btn_csv.clicked.connect(self.save_csv)
        self.export_btn_txt.clicked.connect(self.save_text)
        self.export_btn_json.clicked.connect(self.save_json)
        self.export_btn_xl.clicked.connect(self.save_excel)
        self.export_btn_pdf.clicked.connect(self.save_pdf)

    def verify_file(self, line: QLineEdit, kind: str):
        if line.text() != "":
            if line.text().lower().endswith(kind):
                return True
            else:
                QMessageBox.warning(
                    self, "Export wordsearch", f"The file your trying to save needs to be of type {kind}")
                return False
        else:
            QMessageBox.warning(self, "Export wordsearch",
                                f"please enter a filename")
            return False

    def get_file_name(self, kind):
        filters = {"csv": " CSV (*.csv)", "xl": "XLSX (*.xlsx);;XLSM (*.xlsm)", "pdf": "PDF (*.pdf)",
                   "json": "JSON (*.json)", "word": "DOCX (*.docx)", "html": "HTML (*.html)", "txt": "TXT (*.txt)"}
        file, tipo = QFileDialog.getSaveFileName(
            self, "Select a file", None, f"{filters[kind]}")
        if file:
            if file.lower().endswith("csv"):
                self.filename_csv.setText(file)
            elif file.lower().endswith("xlsx") or file.lower().endswith("xlsm"):
                self.filenamexl.setText(file)
            elif file.lower().endswith("txt"):
                self.filename_txt.setText(file)
            elif file.lower().endswith("json"):
                self.filename_json.setText(file)
            elif file.lower().endswith("docx"):
                self.filename_word.setText(file)
            elif file.lower().endswith("pdf"):
                self.filenamepdf.setText(file)

    def save_text(self):
        try:
            if self.verify_file(self.filename_txt, "txt"):
                file = self.filename_txt.text()
                self.parent.wordsearch.export_text(file)
                QMessageBox.about(self, "Export wordsearch",
                                  f"file successfully saved as {file}")
                if self.open_file_txt.isChecked():
                    os.startfile(file)
        except Exception as e:
            msg = QMessageBox.warning(self, "Save Wordsearch", str(e))

    def save_csv(self):
        try:
            if self.verify_file(self.filename_csv, "csv"):
                file = self.filename_csv.text()
                self.parent.wordsearch.export_csv(
                    file, self.delimiter.currentText(), self.encoding.currentText())
                QMessageBox.about(self, "Export wordsearch",
                                  f"file successfully saved as {file}")
                if self.open_file_csv.isChecked():
                    os.startfile(file)
        except Exception as e:
            msg = QMessageBox.warning(self, "Save Wordsearch", str(e))

    def save_json(self):
        try:
            if self.verify_file(self.filename_json, "json"):
                file = self.filename_json.text()
                self.parent.wordsearch.export_json(file)
                QMessageBox.about(self, "Export wordsearch",
                                  f"file successfully saved as {file}")
                if self.open_file_json.isChecked():
                    os.startfile(file)
        except Exception as e:
            msg = QMessageBox.warning(self, "Save Wordsearch", str(e))

    def save_excel(self):
        try:
            if self.verify_file(self.filenamexl, "xlsx"):
                file = self.filenamexl.text()
                self.parent.wordsearch.export_excel(
                    file, self.sheet_name.text(), self.show_answers_xl.isChecked())
                QMessageBox.about(self, "Export wordsearch",
                                  f"file successfully saved as {file}")
                if self.open_file_xl.isChecked():
                    os.startfile(file)
        except Exception as e:
            msg = QMessageBox.warning(self, "Save Wordsearch", str(e))

    def save_pdf(self):
        try:
            if self.verify_file(self.filenamepdf, "pdf"):
                file = self.filenamepdf.text()
                self.parent.wordsearch.export_pdf(
                    file, self.pdf_title.text(), self.show_answers_pdf.isChecked())
                QMessageBox.about(self, "Export wordsearch",
                                  f"file successfully saved as {file}")
                if self.open_file_pdf.isChecked():
                    os.startfile(file)
        except Exception as e:
            msg = QMessageBox.warning(self, "Save Wordsearch", str(e))

    def save_word(self):
        try:
            if self.verify_file(self.filenamepdf, "docx"):
                file = self.filenamepdf.text()
                self.parent.wordsearch.export_pdf(
                    file, self.pdf_title.text(), self.show_answers_word.isChecked())
                QMessageBox.about(self, "Export wordsearch",
                                  f"file successfully saved as {file}")
                if self.open_file_pdf.isChecked():
                    os.startfile(file)
        except Exception as e:
            msg = QMessageBox.warning(self, "Save Wordsearch", str(e))


class Window(QMainWindow, ui_wordsearch.Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.action_Export.triggered.connect(self.export)
        self.title_font_btn.clicked.connect(self.set_title_font)
        self.letters_font_btn.clicked.connect(self.set_letters_font)
        self.title_text_color_btn.clicked.connect(self.set_title_color)
        self.gridcolor_btn.clicked.connect(self.set_grid_color)
        self.letters_color_btn.clicked.connect(self.set_letters_color)
        self.load_btn.clicked.connect(self.import_words)
        self.add_btn.clicked.connect(self.add_word)
        self.edit_btn.clicked.connect(self.edit_word)
        self.remove_btn.clicked.connect(self.remove_word)
        self.clear_btn.clicked.connect(self.words_list.clear)
        self.generate_btn.clicked.connect(self.generate)
        self.add_words_batch_btn.clicked.connect(self.add_words_batch)
        self.export_words_btn.clicked.connect(self.export_words)
        self.rows.valueChanged.connect(
            lambda x: self.number_rows.setText(str(x)))
        self.columns.valueChanged.connect(
            lambda x: self.number_columns.setText(str(x)))
        self.rows.editingFinished.connect(
            lambda: self.columns.setValue(self.rows.value()))
        self.words_list.doubleClicked.connect(self.edit_word)
        self.uppercase.clicked.connect(lambda x: self.switch_case(True))
        self.lowercase.clicked.connect(lambda x: self.switch_case(False))
        self.show_answers.clicked.connect(self.show_answers_func)
        self.wordsearch_table.horizontalHeader().hide()
        self.wordsearch_table.verticalHeader().hide()
        self.wordsearch = None
        self.table_style = None

    def generate(self):
        try:
            words = [self.words_list.item(i).text()
                     for i in range(self.words_list.count())]
            if self.use_prediction.isChecked():
                size = predict_width_height(words)
                self.rows.setValue(size)
                self.columns.setValue(size)
            self.wordsearch = WordSearch(
                words, self.rows.value(), self.columns.value(), True)

            self.model = WordSearchModel(
                fill(deepcopy(self.wordsearch.grid)), self.uppercase.isChecked())
            self.wordsearch_table.setModel(self.model)
            self.show_answers_func()
            self.number_words.setText(
                str(self.wordsearch.output["number-words"]))
            self.number_placed_words.setText(
                str(self.wordsearch.output["number-words-placed"]))
            self.number_no_placed_words.setText(
                str(self.wordsearch.output["number-words-no-placed"]))
            self.number_letters.setText(
                str(self.wordsearch.output["number-letters"]))
            self.number_letters_in_words.setText(
                str(self.wordsearch.output["number-letter-words"]))
            self.number_random_letters.setText(
                str(self.wordsearch.output["number-random-letters"]))
            self.creation_time.setText(
                str(self.wordsearch.output["time-created"]))
            for col in range(self.model.columnCount()):
                self.wordsearch_table.setColumnWidth(col, 4)

            if self.wordsearch.output["number-words-no-placed"] >= 1:
                msg = QMessageBox.warning(self,
                                          "Wordsearch",
                                          "The following words were not placed try changing the dimensions:\n\n" +
                                          "\n".join(
                                              self.wordsearch.output["words-not-placed"]),
                                          QMessageBox.Ok | QMessageBox.Retry)

                if msg == QMessageBox.Retry:
                    self.generate()
        except Exception as e:
            msg = QMessageBox.warning(self, "Wordsearch", str(e))

    def switch_case(self, upper):
        if self.wordsearch is not None:
            self.wordsearch_table.setModel(None)
            self.model = WordSearchModel(
                fill(deepcopy(self.wordsearch.grid)), upper)
            self.wordsearch_table.setModel(self.model)
            self.show_answers_func()
            for col in range(self.model.columnCount()):
                self.wordsearch_table.setColumnWidth(col, 4)

    def show_answers_func(self):
        if self.wordsearch is not None:
            current_grid = remove_asterisks(deepcopy(self.wordsearch.grid)) if self.show_answers.isChecked(
            ) else fill(deepcopy(self.wordsearch.grid))
            self.wordsearch_table.setModel(None)
            self.model = WordSearchModel(
                current_grid, self.uppercase.isChecked())
            self.wordsearch_table.setModel(self.model)

            for col in range(self.model.columnCount()):
                self.wordsearch_table.setColumnWidth(col, 4)

    def set_title_font(self):
        fontdlg = QFontDialog(self)
        fontdlg.exec_()
        font = fontdlg.selectedFont()
        print(font.family(), font.pointSize(), font.weight())

    def set_letters_font(self):
        font, ok = QFontDialog(self).getFont()
        if ok:
            bold_dict = {
                "50": "normal",
                "75": "bold"
            }
            style = f"""
                font-family:{font.family()};
                font-size:{font.pointSize()}px;
                font-weight:{bold_dict[str(font.weight())]};
            """
            self.table_style = """QTableView { """+style+"}"
            self.letters_font_label.setText(f"""
            <p style="font-family:{font.family()};font-size:{font.pointSize()}px; font-weight:{bold_dict[str(font.weight())]};">{font.family()} {font.pointSize()} {bold_dict[str(font.weight())]}</p>
            """)
            self.wordsearch_table.setStyleSheet(style)

    def set_title_color(self):
        color, ok = QColorDialog(self).getColor()
        if ok:
            if self.table_style is not None:
                print(color.red(), color.green(), color.blue())

    def set_grid_color(self):
        colordlg = QColorDialog(self)
        colordlg.exec_()
        color = colordlg.selectedColor()
        print((color.red(), color.green(), color.blue()))

    def set_letters_color(self):
        color = QColorDialog(self).getColor()
        if color.isValid():
            if self.table_style is not None:
                self.table_style = "QTableView { " + \
                    f"\tcolor:rgb({color.red()},{color.green()},{color.blue()});"+"}"
            else:
                style = f"""
                        color:rgb({color.red()},{color.green()},{color.blue()});
                """
                self.table_style = """ 
                        QTableView { """+style+" }"
            self.wordsearch_table.setStyleSheet(self.table_style)
            print(self.table_style)

    def manage_styles(self):
        pass

    def export(self):
        if self.wordsearch is not None:
            dlg = Export(self)
            dlg.exec_()

    def import_words(self):
        dlg = ImportWords(self)
        dlg.exec_()

    def get_words(self, listwidget: QListWidget) -> list[str]:
        if listwidget.count() > 0:
            words = [listwidget.item(row).text()
                     for row in range(listwidget.count())]
            listwidget.clear()
            words = clean_words(words)
            return words
        return None

    def add_word(self):
        word, ok = QInputDialog.getText(
            self, "Wordsearch Words", "Enter New Word")
        if ok:
            if word != "":
                self.words_list.addItem(word)

    def edit_word(self):
        word = self.words_list.item(self.words_list.currentRow())
        if word is not None:
            text, ok = QInputDialog.getText(
                self, "Wordsearch words", "Edit the word", text=f"{word.text()}")
            if ok:
                word.setText(text)
        else:
            QMessageBox.warning(self, "Wordsearch words",
                                "select the word you wanna edit")

    def remove_word(self):
        word = self.words_list.currentRow()
        if word >= 0:
            self.words_list.takeItem(word)
        else:
            QMessageBox.warning(self, "Wordsearch words",
                                "select the word you wanna remove")

    def add_words_batch(self):
        dlg = BatchWords(self)
        dlg.exec_()

    def export_words(self):
        if self.words_list.count() >= 1:
            file, kind = QFileDialog.getSaveFileName(
                self, "Save", None, "CSV (*.csv)")
            if file:
                words = [self.words_list.item(row).text()
                         for row in range(self.words_list.count())]
                with open(file, "w") as f:
                    writer = csv.writer(f)
                    for word in words:
                        writer.writerow([word])
        else:
            QMessageBox.warning(self, "Wordsearch words", "No words to save!")


app = QApplication(sys.argv)
# app.setStyleSheet(load_stylesheet())
window = Window()
window.show()
app.exec_()
