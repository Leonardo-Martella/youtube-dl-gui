from PyQt5.QtWidgets import QMainWindow

from app.main.ui import Ui_MainWindow


class MainWindow(QMainWindow):
    """The application's main window."""

    def __init__(self, parent=None):
        """Initialize the main window.

        Create and set up the main window's user interface.
        """
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def __getattr__(self, name):
        """Use composition for easier access to the ui elements."""
        return getattr(self.ui, name)
