import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
from models import Product, Sale
from sqlalchemy import func
from database import db

def recommend_purchases():
    # Extraer productos de la base de datos utilizando SQLAlchemy
    products_data = pd.read_sql(db.session.query(Product).statement, db.session.bind)
    
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

def get_top_selling_category():
    result = db.session.query(
        Product.categoria,
        func.sum(Sale.cantidad).label('total_sales')
    ).join(Sale, Product.id == Sale.producto_id) \
     .group_by(Product.categoria) \
     .order_by(func.sum(Sale.cantidad).desc()) \
     .first()

    return result.categoria if result else "N/A"

def get_sales_today():
    today = datetime.today().strftime('%Y-%m-%d')
    result = db.session.query(Sale, Product.nombre, Product.precio) \
               .join(Product, Sale.producto_id == Product.id) \
               .filter(Sale.fecha.startswith(today)) \
               .all()
    
    return result

def get_total_products():
    total_products = db.session.query(func.count(Product.id)).scalar()  # Cuenta todos los productos
    return total_products

def get_low_stock_items():
    low_stock_threshold = 10
    low_stock_count = db.session.query(func.count(Product.id)) \
                                .filter(Product.cantidad < low_stock_threshold) \
                                .scalar()  # Cuenta los productos con stock bajo
    return low_stock_count

def get_top_category():
    top_category = db.session.query(Product.categoria, func.sum(Product.cantidad)) \
                            .group_by(Product.categoria) \
                            .order_by(func.sum(Product.cantidad).desc()) \
                            .first()  # categoría con mayor cantidad de productos
    return top_category[0] if top_category else "N/A"

def get_total_sales():
    total_sales = db.session.query(func.sum(Product.precio * Product.cantidad)).scalar()  # Total ventas
    return total_sales if total_sales else 0

def get_critical_low_stock_items():
    critical_stock_threshold = 3  # umbral crítico de stock
    critical_items = db.session.query(Product.nombre, Product.cantidad) \
                               .filter(Product.cantidad <= critical_stock_threshold) \
                               .all()  # productos con stock bajo
    return critical_items
