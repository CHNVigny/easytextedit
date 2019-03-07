#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys

from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QClipboard, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog, QFontDialog, QColorDialog

from Qt5.editor import editorUI


class Editor(QMainWindow, editorUI.Ui_MainWindow):
    def __init__(self):
        super(Editor, self).__init__()
        self.setupUi(self)
        # 将textEdit设置为窗口的中心部件
        self.setCentralWidget(self.textEdit)

        # 定义判断文本是否已经保存，是否是第一次保存的变量以及文件保存路径
        self.is_saved = True
        self.is_first_saved = True
        self.filepath = ""
        # 剪贴板以及QMimeData类
        self.mime_data = QMimeData()
        self.clipboard = QApplication.clipboard()
        assert isinstance(self.clipboard, QClipboard)
        # 程序打开时状态栏要显示的状态
        self.statusbar.showMessage("Ready to Compose")

        self.filenew.triggered.connect(self.newfile)
        self.fileopen.triggered.connect(self.openfile)
        self.filesave.triggered.connect(lambda: self.savefile(self.textEdit.toHtml()))
        self.othersave.triggered.connect(lambda: self.saveAsfile(self.textEdit.toHtml()))
        self.close_action.triggered.connect(self.close_func)

        self.copy_action.triggered.connect(self.copy_func)
        self.cut_action.triggered.connect(self.cut_func)
        self.paste_action.triggered.connect(self.paste_func)
        self.font_action.triggered.connect(self.font_func)
        self.color_action.triggered.connect(self.color_func)

        self.aboutQt_action.triggered.connect(self.about_func)

        self.textEdit.textChanged.connect(self.change_func)

    def change_func(self):
        # if self.textEdit.toPlainText():
        #     self.is_saved = False
        # else:
        #     self.is_saved = True
        self.is_saved = False

    def newfile(self):
        # 新建前我们要判断当前文本是否有保存
        if not self.is_saved:
            choice = QMessageBox.question(self, "保存", "您想要保存当前文件吗？",
                                          QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                self.savefile(self.textEdit.toHtml())
                self.textEdit.clear()
            elif choice == QMessageBox.No:
                self.textEdit.clear()
            else:
                pass
        else:
            self.textEdit.clear()
        self.is_saved = True
        self.is_first_saved = True
        pass

    def openfile(self):
        # 打开新文件前我们要判断当前文本是否有保存
        if not self.is_saved:
            choice = QMessageBox.question(self, "保存", "您想要保存当前文件吗？",
                                          QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                self.savefile(self.textEdit.toHtml())
                self.filepath, ok = QFileDialog.getOpenFileName(self, '打开文件', './', "Files(*.html *.txt *.log)")
                if ok and self.filepath:
                    with open(self.filepath, 'r') as f:
                        self.textEdit.setText(f.read())
                    self.is_saved = True
                    self.is_first_saved = False
            elif choice == QMessageBox.No:
                self.filepath, ok = QFileDialog.getOpenFileName(self, '打开文件', './', "Files(*.html *.txt *.log)")
                if ok and self.filepath:
                    with open(self.filepath, 'r') as f:
                        self.textEdit.setText(f.read())
                    self.is_saved = True
                    self.is_first_saved = False
            else:
                pass
        else:
            self.filepath, ok = QFileDialog.getOpenFileName(self, '打开文件', './', "Files(*.html *.txt *.log)")
            if ok and self.filepath:
                with open(self.filepath, 'r') as f:
                    self.textEdit.setText(f.read())
                self.is_saved = True
                self.is_first_saved = False
        pass

    def savefile(self, text):
        if self.is_first_saved:
            self.saveAsfile(text)
        else:
            try:
                with open(self.filepath, 'w') as f:
                    f.write(text)
                self.is_saved = True
            except OSError as e:
                print(e.strerror)
        pass

    def saveAsfile(self, text):
        self.filepath, ok = QFileDialog.getSaveFileName(self, '保存文件', './', "Files(*.txt *.html *.log)")
        if ok and self.filepath:
            with open(self.filepath, 'w') as f:
                f.write(text)
            self.is_saved = True
            self.is_first_saved = False
        pass

    def close_func(self):
        if not self.is_saved:
            choice = QMessageBox.question(self, '关闭', "您将要退出，是否保存当前文件",
                                          QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                self.savefile(self.textEdit.toHtml())
                self.close()
            elif choice == QMessageBox.No:
                self.close()
            else:
                pass
        else:
            self.close()
        pass

    def copy_func(self):
        # 由于我们的记事本涉及到颜色，所以不能调用QTextEdit的toPlainText()方法，因为该方法获取的是纯文本，
        # 所以颜色会丢失掉。应该要调用toHtml()方法保留颜色；
        # self.text_edit.textCursor()方法可以获取到文本编辑框当前的指针(类型为QTextCursor)，
        # 此时再调用selection()方法可以获取到指针当前所选择的内容，但此时的类型为QTextDocumentFragment，
        # 我们需要再调用toHtml()方法来获取到文本内容。
        self.mime_data.setHtml(self.textEdit.textCursor().selection().toHtml())
        self.clipboard.setMimeData(self.mime_data)
        pass

    def cut_func(self):
        self.mime_data.setHtml(self.textEdit.textCursor().selection().toHtml())
        self.clipboard.setMimeData(self.mime_data)
        self.textEdit.textCursor().removeSelectedText() # 移除文本
        pass

    def paste_func(self):
        # insetHtml()将剪贴板中的文本插入(该方法会在指针位置插入文本)
        assert isinstance(self.clipboard, QClipboard)
        if self.clipboard.mimeData().hasHtml():
            self.textEdit.insertHtml(self.clipboard.mimeData().html())
        pass

    def font_func(self):
        font, ok = QFontDialog().getFont()
        if ok:
            self.textEdit.setFont(font)
        pass

    def color_func(self):
        color = QColorDialog().getColor()
        assert isinstance(color, QColor)
        if color.isValid():
            self.textEdit.setTextColor(color)
        pass

    def about_func(self):
        QMessageBox.aboutQt(self, 'About Qt')
        pass

    def closeEvent(self, e):
        if not self.is_saved:
            choice = QMessageBox.question(self, '关闭', "您将要退出，是否保存当前文件",
                                          QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                self.savefile(self.textEdit.toHtml())
                e.accept()
            elif choice == QMessageBox.No:
                e.accept()
            else:
                e.ignore()
        else:
            e.accept()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Editor()
    win.show()
    sys.exit(app.exec_())
