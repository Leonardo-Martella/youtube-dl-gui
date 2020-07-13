import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication

from app.main.window import MainWindow
from app.about.dialog import AboutDialog
from app.preferences.dialog import PreferencesDialog


class Application(QApplication):
    """The application class.

    window: MainWindow
        the application main window (which contains the ui)
    about: AboutDialog
        the about dialog, set as a property because otherwise the
        reference is lost and the dialog is never shown
    preferences: PreferencesDialog
        the preferences dialog, set as a property because otherwise the
        reference is lost and the dialog is never shown
    """
    def __init__(self, args):
        """Initialize the application instance.

        Create and show the main window associated with the application.
        Connect the actions to the appropriate slots.
        """
        super().__init__(args)
        self.window = MainWindow()
        self.window.show()

        self.window.ui.actionAbout.triggered.connect(self.actionAbout)
        self.window.ui.actionPreferences.triggered.connect(self.actionPreferences)
        self.window.ui.actionQuit.triggered.connect(self.actionQuit)

    def run(self):
        """Start the application."""
        sys.exit(self.exec_())

    @pyqtSlot()
    def actionAbout(self):
        """Open the about dialog."""
        self.about = AboutDialog()
        self.about.show()

    @pyqtSlot()
    def actionPreferences(self):
        """Open the preferences dialog."""
        self.preferences = PreferencesDialog()
        self.preferences.show()

    @pyqtSlot()
    def actionQuit(self):
        """Quit the application."""
        self.quit()
