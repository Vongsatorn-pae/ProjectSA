from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# สร้าง instance ของ SQLAlchemy และ LoginManager
db = SQLAlchemy()
login_manager = LoginManager()
