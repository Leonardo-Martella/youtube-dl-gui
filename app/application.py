import os.path
import threading

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QApplication

from app.about.dialog import AboutDialog
from app.main.download import DownloaderThread
from app.main.window import MainWindow
from app.preferences.dialog import PreferencesDialog
from app.preferences.utils import PreferencesConfig


class Application(QApplication):
    """The application class.

    window: MainWindow
        the application main window (which contains the ui)
    dl_thread: DownloaderThread
        the thread object responsible for downloading files
    check_queue_item_done: QTimer
        a timer which calls a method to check wether one or more items
        can be removed from the Download Queue QListWidget
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
        Create the downloader thread.
        Connect the 'check_queue_item_done' timer to the appropriate slot.
        """
        super().__init__(args)
        self.window = MainWindow()
        self.window.show()

        self.window.actionAbout.triggered.connect(self.action_about)
        self.window.actionPreferences.triggered.connect(self.action_preferences)
        self.window.actionQuit.triggered.connect(self.action_quit)

        self.window.addToDownloadQueuePushButton.clicked.connect(self.add_to_download_queue)

        self.dl_thread = DownloaderThread()
        self.dl_thread.start()

        self.check_queue_item_done = QTimer()
        self.check_queue_item_done.timeout.connect(self.check_download_tasks_done)
        self.check_queue_item_done.start(500)

    @pyqtSlot()
    def add_to_download_queue(self):
        """Add the url (which is in the input line edit) to the download queue."""
        url = self.window.urlLineEdit.text()
        if url:
            config = PreferencesConfig()
            private = self.window.privateModeCheckBox.isChecked()
            playlists = self.window.downloadPlaylistsCheckBox.isChecked()
            audio = self.window.audioDownloadOptionRadioButton.isChecked()
            yt_dl_options = {
                "outtmpl": os.path.join(config["output_directory"], config["name_template"]),
                "format": config["audio_format_selector"] if audio else config["video_format_selector"],
                "noplaylist": not playlists,
                "socket_timeout": config["timeout", int],
                "nocheckcertificate": not config["check_certificate", bool],
            }
            self.dl_thread.put((url, private, yt_dl_options), block=False)
            self.window.downloadQueueListWidget.addItem(self.format_queue_item(url, private, playlists, audio))
            threading.Thread(target=self.window.urlLineEdit.clear).start()

    @pyqtSlot()
    def check_download_tasks_done(self):
        tasks_done = self.dl_thread.get_tasks_done(reset=True)
        for _ in range(tasks_done):
            self.window.downloadQueueListWidget.takeItem(0)

    @pyqtSlot()
    def action_about(self):
        """Open the about dialog."""
        self.about = AboutDialog()
        self.about.show()

    @pyqtSlot()
    def action_preferences(self):
        """Open the preferences dialog."""
        self.preferences = PreferencesDialog()
        self.preferences.show()

    @pyqtSlot()
    def action_quit(self):
        """Quit the application."""
        self.quit()

    @staticmethod
    def format_queue_item(url, private, playlists, audio):
        """Format a 'download queue' item.

        Parameters
        ----------
        url: str
            the url added to the queue
        private: bool
            wether the download is private or not
        playlists: bool
            wether the download has been set to download playlists
        audio: bool
            wether the download has been set to download just the audio

        Returns
        -------
        the formatted item to add to the queue as a string
        """
        if not any((private, playlists, audio)):
            return url
        options_info = []
        for option, info in ((private, "private mode enabled"), (audio, "audio-only"),
                             (playlists, "will download playlist if available")):
            if option:
                options_info.append(info)
        return url + f" ({', '.join(options_info)})"
