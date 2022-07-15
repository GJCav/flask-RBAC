import eventlet
from eventlet import wsgi


DEBUG = True

if not DEBUG:
    eventlet.monkey_patch()

from app import app


if __name__ == "__main__":
    if DEBUG:
        app.run(debug=True, port=9876)
    else:
        wsgi.server(eventlet.listen(("", 9876)), app)