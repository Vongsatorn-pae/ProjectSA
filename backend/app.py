import yaml
from flask import Flask
from extensions import db, login_manager
import os

from controller.mainController import mainController
from controller.authController import authController
from controller.stockController import stockController
from controller.orderController import orderController

app = Flask(__name__, static_folder = "../frontend/static", template_folder="../frontend/view")

# กำหนด SECRET_KEY สำหรับการเข้ารหัสข้อมูลเซสชัน
app.config['SECRET_KEY'] = os.urandom(24)

# อ่านการตั้งค่าฐานข้อมูลจากไฟล์ config.yaml
with open('../database/config.yaml', 'r') as file:
    db_config = yaml.safe_load(file)

# สร้าง SQLALCHEMY_DATABASE_URI
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_config['mysql_user']}:{db_config['mysql_password']}@{db_config['mysql_host']}/{db_config['mysql_db']}"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/sa_farm_management'

# ตั้งค่า Flask-Login
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints
app.register_blueprint(mainController)
app.register_blueprint(authController)
app.register_blueprint(stockController)
app.register_blueprint(orderController)

if __name__ == '__main__':
    app.run(debug=True)
