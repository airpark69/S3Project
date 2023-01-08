import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()

class API_RESULTS(db.Model):
    __tablename__ = 'api_results'
    id = db.Column(db.Integer, primary_key=True)
    input_value = db.Column(db.String(100))
    pred_category = db.Column(db.String(100))
    pred_origin = db.Column(db.Float)
    pred_trend = db.Column(db.Float)
    use_time = db.Column(db.TIMESTAMP)

class CORPUS(db.Model):
    __tablename__ = 'corpus'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2000), unique=True)
    category = db.Column(db.String(50))
    g_time = db.Column(db.TIMESTAMP)