import os
import tempfile
import time
import secrets
import sys
import unittest
import unittest.mock  # else raises AttributeError: module 'unittest' has no attribute 'mock'
import youtube_dl.utils

from app.main.download import DownloaderThread, stop_event, internet_is_available, Queue


msg = "Please make sure you have an active internet connection before running these tests."
sys.stdout.write("\n" + msg.upper() + "\n\n")


class TestInternetIsAvailable(unittest.TestCase):
    """Test the 'internet_is_available' function."""

    def mock_successful_http_request(*args, **kwargs):
        """Mock a succesful http request by not doing anything (ie by not throwing any error)."""
        pass

    def mock_unsuccessful_http_request(*args, **kwargs):
        """Mock an unsuccessful http request by raising an exception."""
        raise Exception("No internet")

    def test_successful_request(self):
        """Test that internet_is_available returns True if the request is successful."""
        with unittest.mock.patch("http.client.HTTPConnection.request", self.mock_successful_http_request):
            self.assertTrue(internet_is_available())

    def test_unsuccessful_request(self):
        """Test that internet_is_available returns False if the request fails."""
        with unittest.mock.patch("http.client.HTTPConnection.request", self.mock_unsuccessful_http_request):
            self.assertFalse(internet_is_available())


def mock_download(func):
    """Mock the download method of the downloader thread object.

    This decorator should only be used on TestDownloaderThread class methods.
    """
    def wrapper(self, *args, **kwargs):
        def fake_download_func(*_, **__):
            time.sleep(self.MOCK_DOWNLOAD_TIME)
        self.dl_t.download = fake_download_func
        return func(self, *args, **kwargs)
    return wrapper


class TestQueue(unittest.TestCase):
    """Test the Queue class, which is a subclass of queue.Queue."""

    def setUp(self):
        """Set up the necessary attributes for testing."""
        self.queue = Queue()

    def prepare_queue(self, N):
        """Fill the queue with items, retrieve them and call 'task_done'."""
        for i in range(N):
            self.queue.put(i, block=False)
        for _ in range(N):
            _ = self.queue.get(block=False)
            self.queue.task_done()

    def test_tasks_done_increment(self):
        """Check that '_tasks_done' gets incremented when calling 'task_done'."""
        N = 37
        self.prepare_queue(N)

        self.assertEqual(self.queue._tasks_done, N)

    def test_get_tasks_done(self):
        """Test the 'get_tasks_done' method."""
        N = 46
        self.prepare_queue(N)

        self.assertEqual(self.queue.get_tasks_done(), N)
        self.assertEqual(self.queue._tasks_done, N)

        self.assertEqual(self.queue.get_tasks_done(reset=True), N)
        self.assertEqual(self.queue.get_tasks_done(), 0)
        self.assertEqual(self.queue._tasks_done, 0)


class TestDownloaderThread(unittest.TestCase):
    """Test the DownloaderThread class, which is responsible for downloading files.

    Attributes
    ----------
    dl_t: DownloaderThread
        an instance of the DownloaderThread class we are testing
    sample_links: list[str]
        some sample links to use for testing
    MOCK_DOWNLOAD_TIME: float
        the duration in seconds of a mock download for testing
    """

    MOCK_DOWNLOAD_TIME = 0.1

    def setUp(self):
        """Set up the necessary attributes for testing."""
        self.dl_t = DownloaderThread()
        self.sample_links = ["https://www.youtube.com/watch?v=oYtNf0HEQxw",
                             "https://www.youtube.com/watch?v=r5WDqwHi6UQ",
                             "https://www.youtube.com/watch?v=I27iSmBXZ0o",
                             "https://www.youtube.com/watch?v=4An0ndagZsQ"]

    def test_download(self):
        """Test the 'download' method.

        Only check if the file has actually been downloaded and if the appropriate
        exceptions are raised. More complex checks on the downloaded file don't
        make sense here since it is handled by the youtube_dl.YoutubeDL class
        (which has already been tested by its devs). The 'download history'
        functionality is in a separate module (though it is used by the
        DownloaderThread class), so it isn't tested here through the 'private' arg
        of the 'download' method.
        """
        # check file exists
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            options = {
                "outtmpl": os.path.join(tmp_dir_path, "test_video.%(ext)s"),
                "format": "worst[ext=mp4]",
                "noplaylist": True,
                "quiet": True,  # don't output anything to not clutter up the output of the tests
            }
            self.dl_t.download(self.sample_links[-1], True, options)
            self.assertTrue(os.path.exists(os.path.join(tmp_dir_path, "test_video.mp4")))

        # check raises youtube_dl.utils.DownloadError on invalid or inexistent link
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            options = {
                "outtmpl": os.path.join(tmp_dir_path, "test_video.%(ext)s"),
                "format": "worst[ext=mp4]",
                "noplaylist": True,
                "quiet": True,  # don't output anything to not clutter up the output of the tests
            }

            # redirect stderr to prevent an error (which warns about the invalidity of the url)
            # from getting printed when running this test (despite the 'quiet' option)
            sys.stderr = open(os.devnull, 'w')

            with self.assertRaises(youtube_dl.utils.DownloadError):
                self.dl_t.download("invalid url", True, options)

            with self.assertRaises(youtube_dl.utils.DownloadError):
                self.dl_t.download("https://www.youtube.com/watch?v=" + secrets.token_hex(20), True, options)

            sys.stderr = sys.__stderr__  # reset stderr (and implicitly close devnull file)

    @mock_download
    def test_stop_event(self):
        """Test the 'stop_event' which stops the thread."""
        for link in self.sample_links:
            self.dl_t.put((link, True, {}))

        self.dl_t.start()
        time.sleep(1.5 * self.MOCK_DOWNLOAD_TIME)
        stop_event.set()
        time.sleep(2 * self.MOCK_DOWNLOAD_TIME)
        # check that the third link hasn't been downloaded
        self.assertEqual(self.sample_links[2], self.dl_t.get(block=False)[0])

    @mock_download
    def test_run(self):
        """Test the 'run' method."""
        N_links = len(self.sample_links)
        for _ in range(N_links):
            self.dl_t.put((self.sample_links.pop(0), True, {}))

        self.dl_t.start()
        time.sleep(3.5 * self.MOCK_DOWNLOAD_TIME)
        self.assertEqual(len(self.sample_links), 0)
