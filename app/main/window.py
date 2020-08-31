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

        # default option is to download video
        self.ui.videoDownloadOptionRadioButton.setChecked(True)
        self.ui.audioDownloadOptionRadioButton.setChecked(False)

        # default option is to not download playlists
        self.ui.downloadPlaylistsCheckBox.setChecked(True)

    def __getattr__(self, name):
        """Access the ui elements more easily."""
        return getattr(self.ui, name)
