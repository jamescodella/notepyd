import sys, os, yaml
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QPlainTextEdit, QTextEdit, QStatusBar, QToolBar, QVBoxLayout, QWidgetAction, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFontDatabase, QIcon, QKeySequence, QAction
from PyQt6.QtPrintSupport import QPrintDialog

class Notepyd(QMainWindow): #QMainWindow is parent class
    def __init__(self):
        super().__init__()

        with open('./assets/config.yaml') as f: # load configuration file 
            self.config = yaml.safe_load(f)

        self.setWindowTitle('Notepyd')
        self.setWindowIcon(QIcon(self.config['icons']['main']))
        self.app_width = self.geometry().width()
        self.app_height =  self.geometry().height()
        self.resize(self.screen_width, self.screen_height)
        self.fileTypes = 'Text Document (*.txt);; Python (*.py);; Markdown (*.md)'
        self.path = None
        print(self.config['icons']['new file'])
        QFontDatabase.systemFont

        font_selection = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont) # grab fixed fonts from your computer
        font_selection.setPointSize(self.config['font']['size'])

        app_layout = QVBoxLayout()
        app_layout.setContentsMargins(1,1,1,1)

        # editor
        self.editor_pane = QTextEdit()
        self.editor_pane.setFont(font_selection)
        app_layout.addWidget(self.editor_pane)
        
        # status bar
        self.statusBar = self.statusBar()

        # app container
        app_container = QWidget()
        app_container.setLayout(app_layout)
        self.setCentralWidget(app_container)

        # Menubar
        self.menuBar().setNativeMenuBar(False)
        self.menuBar().setFixedHeight(20)

        # *** ACTIONS ****

        # *** FILE MENU ***

        file_menu = self.menuBar().addMenu('&File') #& used to create shortcut on letter

        new_file_action =  self.create_action(self, self.config['icons']['new file'], 'New file', 'New file', lambda: self.new_file())
        new_file_action.setShortcut(QKeySequence('Ctrl+N'))

        open_file_action = self.create_action(self, self.config['icons']['open'], 'Open...', 'Open file', lambda: self.open_file())
        open_file_action.setShortcut(QKeySequence('Ctrl+O'))

        save_file_action = self.create_action(self, self.config['icons']['save'], 'Save', 'Save file', lambda: self.save_file())
        save_file_action.setShortcut(QKeySequence('Ctrl+S'))

        save_as_file_action = self.create_action(self, self.config['icons']['save as'], 'Save as', 'Save file as...', lambda: self.save_file_as())
        save_as_file_action.setShortcut(QKeySequence('Ctrl+Shift+S'))

        file_menu.addActions([new_file_action, open_file_action, save_file_action, save_as_file_action])

        # Print 
        print_action = self.create_action(self, self.config['icons']['print'], 'Print', 'Print file', lambda: self.print_file())
        print_action.setShortcut(QKeySequence('Ctrl+P'))
        file_menu.addAction(print_action)

        # *** EDIT MENU ***
        edit_menu = self.menuBar().addMenu('&Edit')

        undo_action = self.create_action(self, self.config['icons']['undo'], 'Undo', 'Undo', self.editor_pane.undo)
        redo_action = self.create_action(self, self.config['icons']['redo'], 'Redo', 'Redo', self.editor_pane.redo)
        cut_action = self.create_action(self, self.config['icons']['cut'], 'Cut', 'Cut', self.editor_pane.cut)
        copy_action = self.create_action(self, self.config['icons']['copy'], 'Copy', 'Copy', self.editor_pane.copy)
        paste_action = self.create_action(self, self.config['icons']['paste'], 'Paste', 'Paste', self.editor_pane.paste)
        select_all_action = self.create_action(self, self.config['icons']['select all'], 'Select all', 'Select all', self.editor_pane.selectAll)
        
        edit_menu.addActions([undo_action, redo_action, cut_action, copy_action, paste_action, select_all_action])

        # *** HELP MENU ***
        help_menu = self.menuBar().addMenu('&Help')

        about_action = self.create_action(self, self.config['icons']['about'], 'About', 'About notepyd', lambda: self.dialog_message('notepyd © 2021 James Codella', icon='informational'))
        
        help_menu.addActions([about_action])

        self.update_window_title()

    def new_file(self):
        self.path = None
        self.editor_pane.clear()
        self.update_window_title()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(parent = self, caption = 'Open file', directory = '', filter=self.fileTypes)

        if path:
            try:
                with open(path, 'r') as fi:
                    text = fi.read()
                    fi.close()
            except Exception as e:
                self.dialog_message(str(e))
            else:
                self.path = path
                self.editor_pane.setPlainText(text)
                self.update_window_title()
                
    def save_file(self):
        if self.path is None:
            self.save_file_as()
        else:
            try:
                text = self.editor.toPlainText()
                with open(self.path, 'w') as f:
                    f.write(text)
                    f.close()

            except Exception as e:
                self.dialog_message(str(e))

            return # will create file save method

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(parent = self, caption = 'Save file as...', directory = '', filter = self.fileTypes)

        text = self.editor_pane.toPlainText()

        if not path:
            return
        else:
            try:
                with open(path, 'w') as fi:
                    fi.write(text)
                    fi.close()
            except Exception as e:
                self.dialog_message(str(e))

            else:
                self.path = path
                self.update_window_title()

    def print_file(self):
        print_dialog = QPrintDialog()
        if print_dialog.exec():
            self.editor_pane.print(print_dialog.printer())

    def update_window_title(self):
        self.setWindowTitle('{0} - notepyd'.format(os.path.basename(self.path) if self.path else 'Untitled'))

    def dialog_message(self, message, icon=None):
        dialog = QMessageBox(self)
        dialog.setText(message)
        if icon is None:
            dialog.setIcon(QMessageBox.Icon.Critical)
        else:
            dialog.setIcon(QMessageBox.Icon.Information)

        dialog.show()
        
    def create_action(self, parent, icon_path, action_name, status_stip, action_method):
        action = QAction(QIcon(icon_path), action_name, parent)
        action.setStatusTip(status_stip)
        action.triggered.connect(action_method)
        return action
    
app = QApplication(sys.argv)
notepyd = Notepyd()
notepyd.show()
sys.exit(app.exec())
