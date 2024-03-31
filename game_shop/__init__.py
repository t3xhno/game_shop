import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://tex:?Keepout123@localhost/game_shop"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static"
app.secret_key = "h3ll0"
db = SQLAlchemy(app)

from game_shop import routes
