from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha_ingreso = Column(String, nullable=False)

    def __init__(self, nombre, categoria, precio, cantidad):
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.cantidad = cantidad
        self.fecha_ingreso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Sale(Base):
    __tablename__ = 'ventas'

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.now)

    producto = relationship('Product', back_populates="ventas")

    def __init__(self, producto_id, cantidad):
        self.producto_id = producto_id
        self.cantidad = cantidad


# Relación en la clase Product
Product.ventas = relationship('Sale', back_populates='producto')
