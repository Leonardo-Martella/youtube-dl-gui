import threading

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from app.preferences.ui import Ui_PreferencesDialog
from app.preferences.utils import PreferencesConfig


class PreferencesDialog(QDialog):
    """The preferences dialog (accessible via ⌘ + ,).

    ui: Ui_PreferencesDialog
        the user interface generated with Qt Designer and translated to python by pyuic5

    config: PreferencesConfig
        the config instance used for accessing the preferences config file

    Loading, saving and resetting the preferences config file
    is done on a new thread to avoid freezing the gui thread.
    """

    def __init__(self, parent=None):
        """Initialize the preferences dialog.

        Initialize and setup the ui.
        Set the items for the different combo boxes.
        Initialize the preferences config.
        Connect the necessary slots.
        Load the preferences.
        """
        super().__init__(parent)
        self.ui = Ui_PreferencesDialog()
        self.setupUi(self)

        self.config = PreferencesConfig()

        # NOTE(the Ok and Cancel buttons are connected to the reject and accept slots by default)
        self.resetDefaultSettingsPushButton.clicked.connect(self.on_reset_preferences)

        threading.Thread(target=self.load_preferences).start()

    def __getattr__(self, name):
        """Access the ui elements more easily."""
        return getattr(self.ui, name)

    @pyqtSlot()
    def accept(self):
        """Save the current preferences."""
        t = threading.Thread(target=self.save_preferences)
        t.start()
        t.join()
        threading.Thread(target=self.config.save).start()
        super().accept()

    @pyqtSlot()
    def on_reset_preferences(self):
        """Reset the preferences config, save it and close the dialog."""
        t = threading.Thread(target=self.config.reset)
        t.start()
        t.join()
        t = threading.Thread(target=self.config.save)
        t.start()
        t.join()
        self.close()

    def load_preferences(self):
        """Load the preferences from the config to the widgets."""
        self.outputDirectoryLineEdit.setText(self.config['output_directory'])
        self.defaultNameTemplateLineEdit.setText(self.config['name_template'])
        self.timeoutSpinBox.setValue(self.config['timeout', int])
        self.checkCertificateCheckBox.setChecked(self.config['check_certificate', bool])
        self.videoFormatSelectorLineEdit.setText(self.config['video_format_selector'])
        self.audioFormatSelectorLineEdit.setText(self.config['audio_format_selector'])

    def save_preferences(self):
        """Save the preferences to the config from the current state of the widgets."""
        self.config['output_directory'] = self.outputDirectoryLineEdit.text()
        self.config['name_template'] = self.defaultNameTemplateLineEdit.text()
        self.config['timeout'] = self.timeoutSpinBox.value()
        self.config['check_certificate'] = self.checkCertificateCheckBox.isChecked()
        self.config['video_format_selector'] = self.videoFormatSelectorLineEdit.text()
        self.config['audio_format_selector'] = self.audioFormatSelectorLineEdit.text()
