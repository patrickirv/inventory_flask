from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import init_db, get_db
from models import Product, Sale
from ml_utils import recommend_purchases, get_top_selling_category, get_sales_today, get_total_products, get_low_stock_items, get_top_category, get_total_sales, get_critical_low_stock_items
from datetime import datetime, timedelta

app = Flask(__name__)

# Inicializa la base de datos
with app.app_context():
    init_db()

# Funciones para obtener datos desde la base de datos
@app.route('/')
def dashboard():
    total_products = get_total_products()
    low_stock_items = get_low_stock_items()
    top_category = get_top_category()
    total_sales = get_total_sales()
    critical_stock_items = get_critical_low_stock_items()

    return render_template('dashboard.html', 
                           total_products=total_products, 
                           low_stock_items=low_stock_items, 
                           top_category=top_category, 
                           total_sales=total_sales,
                           critical_stock_items=critical_stock_items)

@app.route('/inventory')
def inventory():
    db = get_db()
    products = db.query(Product).all()
    return render_template('inventory.html', products=products)

@app.route('/products', methods=['GET', 'POST'])
def products():
    db = get_db()

    if request.method == 'POST':
        # Detectar si es una operación de edición
        if 'edit_product' in request.form:
            product_id = int(request.form['product_id'])
            product = db.query(Product).get(product_id)
            product.nombre = request.form['nombre']
            product.cantidad = int(request.form['cantidad'])
            product.precio = float(request.form['precio'])
            product.categoria = request.form['categoria']
            db.commit()

        # Detectar si es una operación de eliminación
        elif 'delete_product' in request.form:
            product_id = int(request.form['product_id'])
            product = db.query(Product).get(product_id)
            db.delete(product)
            db.commit()

        # Si es una operación de creación de un producto
        else:
            nombre = request.form['nombre']
            cantidad = int(request.form['cantidad'])
            precio = float(request.form['precio'])
            categoria = request.form['categoria']
            new_product = Product(nombre=nombre, cantidad=cantidad, precio=precio, categoria=categoria)
            db.add(new_product)
            db.commit()

        return redirect(url_for('products'))

    # Obtener todos los productos para mostrarlos
    products = db.query(Product).all()
    return render_template('products.html', products=products)

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    db = get_db()
    
    # Obtener productos con stock bajo (menos de 10 unidades)
    low_stock = db.query(Product).filter(Product.cantidad < 10).all()
    
    # Obtener la categoría más vendida
    top_category = get_top_selling_category(db)
    
    # Variable para las ventas
    sales_today = []
    total_sales_day = 0

    # Lógica para determinar el período de ventas
    if request.method == 'POST':
        selected_period = request.form['period']

        if selected_period == 'today':
            sales_today = db.query(Sale).filter(Sale.fecha.like(f'{datetime.now().strftime("%Y-%m-%d")}%')).all()

        elif selected_period == 'month':
            start_date = datetime.now() - timedelta(days=30)
            sales_today = db.query(Sale).filter(Sale.fecha >= start_date).all()

        elif selected_period == '3months':
            start_date = datetime.now() - timedelta(days=90)
            sales_today = db.query(Sale).filter(Sale.fecha >= start_date).all()

        elif selected_period == '6months':
            start_date = datetime.now() - timedelta(days=180)
            sales_today = db.query(Sale).filter(Sale.fecha >= start_date).all()

        elif selected_period == 'year':
            start_date = datetime.now() - timedelta(days=365)
            sales_today = db.query(Sale).filter(Sale.fecha >= start_date).all()

        elif selected_period == 'custom':
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            sales_today = db.query(Sale).filter(Sale.fecha >= start_date, Sale.fecha <= end_date).all()

        # Calcular el total de ventas
        total_sales_day = sum(sale.cantidad * sale.producto.precio for sale in sales_today)

    return render_template('reports.html', 
                           low_stock=low_stock, 
                           top_category=top_category, 
                           sales=sales_today, 
                           total_sales_day=total_sales_day)

@app.route('/sales', methods=['POST'])
def sales():
    db = get_db()

    # Datos enviados desde el cliente (carrito)
    cart = request.json['cart']
    customer_name = request.json['customer_name']
    customer_email = request.json['customer_email']

    if not cart:
        return jsonify({'success': False, 'message': 'El carrito está vacío'})

    total_price = 0

    # Procesar cada producto en el carrito
    for product_id, item in cart.items():
        product = db.query(Product).get(product_id)
        if product and product.cantidad >= item['qty']:
            # Actualizar cantidad del producto en inventario
            product.cantidad -= item['qty']
            db.commit()

            # Registrar la venta en la tabla de ventas
            sale = Sale(product_id=product_id, cantidad=item['qty'])
            db.add(sale)
            db.commit()

            # Calcular el total
            total_price += product.precio * item['qty']
        else:
            return jsonify({'success': False, 'message': f'Stock insuficiente para {item["name"]}'})

    # Aquí puedes agregar la lógica para almacenar los datos del cliente si es necesario

    return jsonify({'success': True, 'message': 'Venta registrada exitosamente', 'total_price': total_price})

@app.route('/recommendations')
def recommendations():
    db = get_db()
    recommendations = recommend_purchases(db)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
