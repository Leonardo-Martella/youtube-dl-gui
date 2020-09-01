import sys

from app.application import Application
from app.main.download import stop_event


def main():
    app = Application(sys.argv)
    try:
        rc = app.exec_()
    except Exception:
        rc = 1
    finally:
        stop_event.set()
        print("set stop_event")
        sys.exit(rc)


if __name__ == "__main__":
    main()
