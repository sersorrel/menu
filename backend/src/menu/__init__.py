from datetime import date
from pathlib import Path

from flask import Flask, json
from sqlalchemy import event
from sqlalchemy.engine import Engine
from werkzeug.routing import BaseConverter, ValidationError

from menu.models import db
from menu import views


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "__json__"):
            return o.__json__()
        return super().default(o)


class DateConverter(BaseConverter):
    regex = r"\d\d\d\d-\d\d-\d\d"

    def to_python(self, value: str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValidationError

    def to_url(self, value: date):
        return str(value)


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if app.env == "development":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/menu.sqlite"
    db.init_app(app)
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:"):
        def _fk_pragma_on_connect(dbapi_con, con_record):
            dbapi_con.execute('pragma foreign_keys=ON')
        with app.app_context():
            from sqlalchemy import event
            event.listen(db.engine, 'connect', _fk_pragma_on_connect)
    with app.app_context():
        db.create_all()
    app.json_encoder = JSONEncoder
    app.url_map.converters["date"] = DateConverter
    app.register_blueprint(views.bp, url_prefix="/api")
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    return app
