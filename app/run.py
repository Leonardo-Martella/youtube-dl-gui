import sys

from app.application import Application


def main():
    app = Application(sys.argv)
    app.run()


if __name__ == "__main__":
    main()
