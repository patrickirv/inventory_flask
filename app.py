from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import init_db, db
from ml_utils import recommend_purchases, get_top_selling_category, get_sales_today, get_total_products, get_low_stock_items, get_top_category, get_total_sales, get_critical_low_stock_items
from datetime import datetime, timedelta
from models import Product, Sale  # Importa tus modelos y la instancia de db
from datetime import datetime
from models import LOCAL_TIMEZONE
app = Flask(__name__)

# Inicio
init_db(app)

# Funciones para obtener datos desde la bd
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
    # Usamos db.session para consultar los productos
    products = db.session.query(Product).all()  # Obtiene todos los productos de la tabla 'productos'
    return render_template('inventory.html', products=products)

@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        if 'edit_product' in request.form:
            product_id = int(request.form['product_id'])
            product = db.session.query(Product).get(product_id)  # Usamos db.session.query
            product.nombre = request.form['nombre']
            product.cantidad = int(request.form['cantidad'])
            product.precio = float(request.form['precio'])
            product.categoria = request.form['categoria']
            db.session.commit()  # Usamos commit() de la sesión

        elif 'delete_product' in request.form:
            product_id = int(request.form['product_id'])
            product = db.session.query(Product).get(product_id)  # Usamos db.session.query
            db.session.delete(product)  # Usamos session.delete
            db.session.commit()  # Usamos commit() de la sesión

        else:
            nombre = request.form['nombre']
            cantidad = int(request.form['cantidad'])
            precio = float(request.form['precio'])
            categoria = request.form['categoria']
            new_product = Product(nombre=nombre, cantidad=cantidad, precio=precio, categoria=categoria)
            db.session.add(new_product)  # Usamos session.add
            db.session.commit()  # Usamos commit() de la sesión

        return redirect(url_for('products'))

    # Obtener todos los productos para mostrarlos
    products = db.session.query(Product).all()  # Usamos db.session.query
    return render_template('products.html', products=products)

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    # Consultas iniciales para obtener productos con stock bajo y la categoría más vendida
    low_stock = db.session.query(Product).filter(Product.cantidad < 10).all()
    top_category = get_top_selling_category()  # Usamos la función que ya tenías para obtener la categoría más vendida

    # Inicializamos las ventas y total de ventas del día
    sales_today = []
    total_sales_day = 0

    # Si el método es POST, obtenemos las ventas según el período seleccionado
    if request.method == 'POST':
        selected_period = request.form['period']

        # Filtrar ventas según el período seleccionado
        if selected_period == 'today':
            sales_today = db.session.query(Sale).filter(Sale.fecha.like(f'{datetime.now().strftime("%Y-%m-%d")}%')).all()

        elif selected_period == 'month':
            start_date = datetime.now() - timedelta(days=30)
            sales_today = db.session.query(Sale).filter(Sale.fecha >= start_date).all()

        elif selected_period == '3months':
            start_date = datetime.now() - timedelta(days=90)
            sales_today = db.session.query(Sale).filter(Sale.fecha >= start_date).all()

        elif selected_period == '6months':
            start_date = datetime.now() - timedelta(days=180)
            sales_today = db.session.query(Sale).filter(Sale.fecha >= start_date).all()

        elif selected_period == 'year':
            start_date = datetime.now() - timedelta(days=365)
            sales_today = db.session.query(Sale).filter(Sale.fecha >= start_date).all()

        elif selected_period == 'custom':
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            sales_today = db.session.query(Sale).filter(Sale.fecha >= start_date, Sale.fecha <= end_date).all()

        # Calcular el total de ventas en el período seleccionado
        total_sales_day = sum(sale.cantidad * sale.producto.precio for sale in sales_today)

    # Renderizar el template con los datos obtenidos
    return render_template('reports.html', 
                           low_stock=low_stock, 
                           top_category=top_category, 
                           sales=sales_today, 
                           total_sales_day=total_sales_day)

@app.route('/realizar_venta', methods=['POST'])
def realizar_venta():
    data = request.get_json()  # Recibe los datos enviados desde el frontend

    if not data.get('productos'):
        return jsonify({'error': 'No se recibieron productos.'}), 400

    total = 0
    try:
        # Empezar una transacción
        with db.session.begin():
            # Recorre los productos del carrito y realiza las ventas
            for producto_data in data['productos']:
                # Obtener el producto de la base de datos
                
                producto = Product.query.get(producto_data['id'])

                if not producto:
                    return jsonify({'error': f"Producto con ID {producto_data['id']} no encontrado."}), 404

                # Verificar si hay suficiente cantidad
                if producto.cantidad < producto_data['cantidad']:
                    return jsonify({'error': f"Cantidad insuficiente para {producto.nombre}."}), 400

                # Actualizar la cantidad en la tabla productos
                producto.cantidad -= producto_data['cantidad']
                total += producto.precio * producto_data['cantidad']

                # Insertar el registro de la venta en la tabla ventas
                nueva_venta = Sale(producto_id=producto.id, cantidad=producto_data['cantidad'], fecha=datetime.now(LOCAL_TIMEZONE))
                db.session.add(nueva_venta)

            # Confirmar los cambios en la base de datos
            db.session.commit()

        # Devolver la respuesta al frontend con el total
        return jsonify({'message': 'Venta registrada con éxito.', 'total': total}), 200

    except Exception as e:
        db.session.rollback()  # Revertir cualquier cambio en caso de error
        return jsonify({'error': str(e)}), 500


@app.route('/recommendations')
def recommendations():
    # Obtener las recomendaciones directamente con db.session
    recommendations = recommend_purchases()  # Ya no es necesario pasar db a la función
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
