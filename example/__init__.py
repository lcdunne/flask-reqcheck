from flask import Flask

from flask_reqcheck import ReqCheck

from .endpoints import endpoints

reqcheck = ReqCheck()


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(endpoints)
    reqcheck.init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
