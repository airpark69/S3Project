import os
import csv
from flask import Flask
import schedule
from app.functions import instaCrawl
from .config import config
from app.functions.db_models import db

def create_app():
    ## insta 크롤링 주기함수
    schedule.every().day.at("03:00").do(instaCrawl.Setting_all_corpus)
    #######


    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    
    from app.views.main_views import main_bp
    from app.views.data_views import data_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(data_bp, url_prefix='/api')
    
    app.app_context().push()
    db.init_app(app)
    db.create_all()

    return app
    

