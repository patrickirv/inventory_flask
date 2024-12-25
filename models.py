from database import db
from datetime import datetime
import pytz
# Usa `db` de Flask-SQLAlchemy en lugar de `declarative_base`
LOCAL_TIMEZONE = pytz.timezone("America/Lima")

class Product(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(6), nullable=False, unique=True)
    nombre = db.Column(db.String, nullable=False)
    categoria = db.Column(db.String, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_ingreso = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    ventas = db.relationship('Sale', back_populates='producto')
    
    def __init__(self, nombre, categoria, precio, cantidad):
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.cantidad = cantidad

    def generar_codigo(self):
        self.codigo = str(self.id).zfill(6)

class Sale(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TIMEZONE))

    producto = db.relationship('Product', back_populates="ventas")

    def __init__(self, producto_id, cantidad, fecha=None):
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.fecha = fecha or datetime.now(LOCAL_TIMEZONE)