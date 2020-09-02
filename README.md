# youtube-dl-gui
A GUI app for downloading video/audio from the web using youtube-dl (https://github.com/ytdl-org/youtube-dl). Developed and tested on macOS Catalina 10.15.5 (not tested on Windows).

# Advantages over the CLI
The app provides sensible defaults, so you won't have to re-type everything and the most useful options are easily accessible from the GUI.
Here are the settings available (and customizable) from the app:
* output directory
* file name template (defaults to '%(title)s – %(uploader)s.%(ext)s', refer to youtube-dl's documentation for more information)
* timeout (not very useful)
* SSL Certificate Verification (may be useful if your check certificates aren't valid and you don't have the time to fix the issue immediately)
* format selector expressions
  * for video files (sensible default)
  * for audio-only downloads (sensible default)
* wether to download the entire playlist if available or just the single file

# Disadvantages
More advanced options are not available from within the app and you will have to use the CL version of youtube-dl.

# Note
The 'download history' (and 'private mode') functionality has not been implemented yet.
