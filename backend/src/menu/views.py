import datetime

from flask import abort, Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError, NoResultFound

from menu.models import Day, MealProvider, db


bp = Blueprint("views", __name__)


@bp.after_request
def after_request(response):
    if current_app.env == "development":
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    return response


@bp.route("/upcoming")
def index():
    today = datetime.date.today()
    meals = {}
    for offset in range(7):
        meals[str(today + datetime.timedelta(days=offset))] = Day.query.filter(Day.date == today + datetime.timedelta(days=offset)).one_or_none()
    return jsonify(meals)


@bp.route("/d/<date:date>")
def get_day(date: datetime.date):
    return jsonify(Day.query.filter(Day.date == date).one_or_none())


@bp.route("/d/<date:date>", methods=["POST", "PUT"])
def update_day(date: datetime.date):
    if (day := Day.query.filter(Day.date == date).one_or_none()) is None:
        day = Day(date=date)
        db.session.add(day)
    else:
        day.date = date
    if "meal" in request.form:
        day.meal = request.form["meal"] or None
    if "source_id" in request.form and request.form["source_id"]:
        try:
            day.source_id = int(request.form["source_id"]) or None
        except ValueError:
            current_app.logger.exception("bad source ID: %r", request.form["source_id"])
            abort(400)
    try:
        db.session.commit()
    except IntegrityError:
        current_app.logger.exception("failed to update day: %r", day)
        abort(400)
    return jsonify(day)


@bp.route("/p")
def get_providers():
    return jsonify(MealProvider.query.all())


@bp.route("/p/<int:id>")
def get_provider(id: int):
    return jsonify(MealProvider.query.filter(MealProvider.id == id).one_or_none())


@bp.route("/p", methods=["POST"])
def new_provider():
    provider = MealProvider(name=request.form["name"])
    db.session.add(provider)
    try:
        db.session.commit()
    except IntegrityError:
        abort(400)
    return jsonify(provider)


@bp.route("/p/<int:id>", methods=["PUT"])
def update_provider(id: int):
    try:
        provider = MealProvider.query.filter(MealProvider.id == id).one()
    except NoResultFound:
        abort(400)
    if "name" in request.form:
        provider.name = request.form["name"]
    db.session.commit()
    return jsonify(provider)
