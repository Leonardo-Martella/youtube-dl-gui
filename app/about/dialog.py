from PyQt5.QtWidgets import QDialog

from app.about.ui import Ui_AboutDialog


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
