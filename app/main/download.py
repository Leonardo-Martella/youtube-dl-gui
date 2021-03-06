import http.client
import queue  # don't use queue.Queue since we subclass it later
import threading
import time

import youtube_dl


def internet_is_available():
    """Return wether an internet connection is available or not."""
    conn = http.client.HTTPConnection("www.google.com", timeout=3)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()


stop_event = threading.Event()  # stops the download thread (waits for current download to finish)


class Queue(queue.Queue):
    """A subclass of queue.Queue, which counts the number of tasks done.

    Attributes
    ----------
    _tasks_done: int
        a counter of the number of calls to the 'task_done' function,
        it represents the number of tasks done

    Please refer to the documentation for queue.Queue from the Python Standard
    Library for more information on the attributes and methods of queue.Queue.

    Examples
    --------
    >>> q = Queue()
    >>> for i in range(4):
    ...     q.put(i)
    ...
    >>> for _ in range(4):
    ...     item = q.get()
    ...     # process item
    ...     q.task_done()
    ...
    >>> tasks_done = q.get_tasks_done()
    >>> tasks_done, q._tasks_done
    (4, 4)
    >>> tasks_done = q.get_tasks_done(reset=True)
    >>> tasks_done, q._tasks_done
    (4, 0)
    """

    def __init__(self, maxsize=0):
        """Initialize the superclass and create the '_tasks_done' attribute."""
        super().__init__(maxsize)
        self._tasks_done = 0

    def task_done(self, *args, **kwargs):
        """Override the 'task_done' method to increment '_tasks_done'."""
        self._tasks_done += 1
        return super().task_done(*args, **kwargs)

    def get_tasks_done(self, reset=False):
        """Return the number of tasks done (as an integer).

        Parameters
        ----------
        reset: bool
            wether or not to reset the number of tasks done
        """
        tasks_done = self._tasks_done  # save current value in case we reset
        if reset:
            self._tasks_done = 0
        return tasks_done


class DownloaderThread(threading.Thread):
    """The thread class responsible for downloading files.

    Attributes
    ----------
    queue: queue.Queue[tuple[str, bool, dict[str, Any]]]
        a FIFO queue of the items to download, which are tuples of:
        url, private_mode, yt_dl_options (please refer to the explanations
        for the 'download' static method of this class)

    Examples
    --------
    >>> dl_thread = DownloaderThread()
    >>> dl_thread.start()  # start thread
    >>> url = "https://www.youtube.com/......"  # the video to download
    >>> private = False
    >>> prefs = {
        # the options to give to the youtube_dl.YoutubeDL class
        # see the youtube_dl docs for this
    }
    >>> item = (url, private, prefs)
    # prefer block=False or 'put_nowait' since queue size is infinite,
    # so it raises an error immediately if there is a problem.
    >>> dl_thread.put(item, block=False)  # or dl_thread.put_nowait(item)
    # thread starts downloading, you can continue adding items to the queue.
    # when you want to stop it (actually stops after current download finishes).
    >>> stop_event.set()
    """

    def __init__(self):
        """Initialize the threading.Thread base class and the queue object."""
        super().__init__()
        self.queue = Queue()

    def run(self):
        """The function to be run by the thread once it is started.

        Notes
        -----
        This function should not be called by the user, it is called internally
        by the thread object. Use thread.start(), don't use thread.run().
        """
        while not stop_event.is_set():
            try:
                link, private_mode, prefs = self.queue.get(block=False)
            except queue.Empty:
                time.sleep(0.1)
            else:
                while True:
                    try:
                        self.download(link, private_mode, prefs)
                    except youtube_dl.utils.DownloadError:
                        if not internet_is_available():  # no connection -> wait and retry
                            time.sleep(1)
                        else:  # url or options are probably invalid
                            break  # proceed to next item
                    else:
                        break
                self.queue.task_done()

    @staticmethod
    def download(url, private, yt_dl_options):
        """Download the file at the given url.

        Parameters
        ----------
        url: str
            the url of the file to download
        private: bool
            save the url in the download history if True, else not
        yt_dl_options: dict[str, Any]
            a dictionary of options passed directly to the YoutubeDL object during initialization

        Raises
        ------
        youtube_dl.utils.DownloadError
            if the download fails (e.g invalid url or network connection error)
            use the 'internet_is_available' function to determine if it is a connection error
        """
        # TODO(implement 'private')
        with youtube_dl.YoutubeDL(yt_dl_options) as dl:
            dl.download([url])

    def __getattr__(self, name):
        """Access attributes of self.queue directly."""
        return getattr(self.queue, name)
