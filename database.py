from flask_sqlalchemy import SQLAlchemy

# Inicialización de la base de datos con Flask-SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    # Configura la base de datos con la URI y las configuraciones de Flask
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Administrator/Desktop/soft sqlite/productos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)