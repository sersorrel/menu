from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class MealProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id!r}, name={self.name!r})"

    def __json__(self):
        return {"id": self.id, "name": self.name}


class Day(db.Model):
    date = db.Column(db.Date, primary_key=True)
    meal = db.Column(db.String(100))
    source_id = db.Column(db.Integer, db.ForeignKey(MealProvider.id))
    source = db.relationship(MealProvider)

    def __repr__(self):
        return f"{type(self).__name__}(date={self.date!r}, meal={self.meal!r}, source={self.source!r})"

    def __json__(self):
        return {"date": self.date.isoformat(), "meal": self.meal, "source_id": self.source_id, "source": self.source}
