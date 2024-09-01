from flask import Flask

from .endpoints import endpoints


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(endpoints)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
