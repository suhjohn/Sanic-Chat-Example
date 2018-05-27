import os

from backend.app import app


def main(debug=False, run=True):
    if run:
        app.run(host="0.0.0.0", port=8000, workers=1, debug=debug)


if __name__ == '__main__':
    debug = bool(int(os.environ.get('DEBUG', 0)))
    main(debug=debug)
