import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import func
from models import Product, Sale
from datetime import datetime
from database import db_session

def recommend_purchases(db):
    products_data = pd.read_sql('SELECT * FROM productos', db.bind)
    
    X = products_data[['precio', 'cantidad']]
    y = products_data['cantidad']
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    predictions = model.predict(X)
    
    recommendations = []
    for i, pred in enumerate(predictions):
        if pred < products_data.iloc[i]['cantidad']:
            recommendations.append({
                'product_id': products_data.iloc[i]['id'],
                'product_name': products_data.iloc[i]['nombre'],
                'recommended_purchase': int(products_data.iloc[i]['cantidad'] - pred)
            })
    
    return recommendations

def get_top_selling_category(db):
    result = db.query(
        Product.categoria,
        func.sum(Sale.cantidad).label('total_sales')
    ).join(Sale, Product.id == Sale.producto_id) \
     .group_by(Product.categoria) \
     .order_by(func.sum(Sale.cantidad).desc()) \
     .first()

    return result.categoria if result else "N/A"


def get_sales_today(db):
    today = datetime.today().strftime('%Y-%m-%d')
    result = db.query(Sale, Product.nombre, Product.precio) \
               .join(Product, Sale.producto_id == Product.id) \
               .filter(Sale.fecha.startswith(today)) \
               .all()
    
    return result


def get_total_products():
    session = db_session()
    total_products = session.query(func.count(Product.id)).scalar()  # Cuenta todos los productos
    session.close()
    return total_products

def get_low_stock_items():
    low_stock_threshold = 10
    session = db_session()
    low_stock_count = session.query(func.count(Product.id)).filter(Product.cantidad < low_stock_threshold).scalar()  # Cuenta los productos con stock bajo
    session.close()
    return low_stock_count

def get_top_category():
    session = db_session()
    top_category = session.query(Product.categoria, func.sum(Product.cantidad)) \
                          .group_by(Product.categoria) \
                          .order_by(func.sum(Product.cantidad).desc()) \
                          .first()  # Obtiene la categoría con mayor cantidad de productos
    session.close()
    return top_category[0] if top_category else "N/A"

def get_total_sales():
    session = db_session()
    total_sales = session.query(func.sum(Product.precio * Product.cantidad)).scalar()  # Total ventas
    session.close()
    return total_sales if total_sales else 0

def get_critical_low_stock_items():
    critical_stock_threshold = 3  # Establecer el umbral crítico de stock
    session = db_session()
    
    # Obtener los productos con stock menor o igual a 3
    critical_items = session.query(Product.nombre, Product.cantidad) \
                            .filter(Product.cantidad <= critical_stock_threshold) \
                            .all()
    session.close()
    return critical_items
