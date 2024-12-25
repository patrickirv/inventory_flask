// Variables para carrito
let cart = {};
let totalPrice = 0;

function searchProducts() {
    const searchText = document.getElementById('search-bar').value.toLowerCase();
    const products = document.querySelectorAll('.product-card');
    let foundProducts = false;

    products.forEach(product => {
        const name = product.dataset.name.toLowerCase();
        const category = product.dataset.category.toLowerCase();

        if (name.includes(searchText) || category.includes(searchText)) {
            product.style.display = "block";  // Mostrar producto
            foundProducts = true;
        } else {
            product.style.display = "none";  // Ocultar producto
        }
    });

    // Si no se encuentran productos
    if (foundProducts) {
        document.getElementById('products-list').style.display = "block";
    } else {
        document.getElementById('products-list').style.display = "none";
    }
}

// Función para agregar productos al carrito
document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', (e) => {
        const productId = e.target.dataset.id;
        const productName = e.target.dataset.name;
        const productPrice = parseFloat(e.target.dataset.price);

        // Agregar producto al carrito o aumentar la cantidad si ya existe
        if (cart[productId]) {
            cart[productId].qty += 1;
        } else {
            cart[productId] = { name: productName, price: productPrice, qty: 1 };
        }

        // Actualizar carrito
        updateCart();
    });
});

// Función para actualizar la cantidad de un producto en el carrito
function updateQty(productId, value) {
    const newQty = Math.max(1, value);  // no sea menor a 1
    cart[productId].qty = newQty;
    updateCart();
}

// Función para eliminar un producto del carrito
function removeProduct(productId) {
    const productPrice = cart[productId].price * cart[productId].qty;
    delete cart[productId];
    totalPrice -= productPrice;  // Actualizar el total cuando se elimina un producto
    updateCart();
}

// Función para actualizar el carrito
function updateCart() {
    const cartSummary = document.getElementById('cart-summary');
    cartSummary.innerHTML = "";  // Limpiar resumen del carrito
    totalPrice = 0;

    Object.keys(cart).forEach(productId => {
        const product = cart[productId];
        totalPrice += product.price * product.qty;

        cartSummary.innerHTML += `
            <div class="border-b pb-4">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="font-medium">${product.name}</p>
                        <div class="text-sm text-gray-600">Cantidad:
                            <input type="number" value="${product.qty}" min="1" onchange="updateQty('${productId}', this.value)" class="w-12 text-center">
                        </div>
                    </div>
                    <button onclick="removeProduct('${productId}')">Eliminar</button>
                </div>
            </div>
        `;
    });

    // Actualizar precio total
    document.getElementById('total-price').textContent = totalPrice.toFixed(2);
}

// Actualizar el historial de ventas
function updateSalesHistory() {
    const salesHistoryList = document.getElementById('sales-history');
    salesHistoryList.innerHTML = "";  // Limpiar historial de ventas

    salesHistory.forEach(sale => {
        salesHistoryList.innerHTML += `
            <li>
                <strong>Fecha:</strong> ${sale.date} | 
                <strong>Cliente:</strong> ${sale.customer} | 
                <strong>Total:</strong> S/.${sale.total}
            </li>
        `;
    });
}

// Confirmación de venta y envío de datos
$('#confirmarVentaBtn').click(function(event) {
    event.preventDefault();  // Evitar que el formulario se envíe automáticamente

    if (Object.keys(cart).length > 0) {
        // Preparar los datos de la venta con los campos correctos de la base de datos
        const saleData = {
            productos: Object.keys(cart).map(productId => {
                const producto = cart[productId];
                return {
                    id: productId,  // Asegúrate de enviar el ID del producto
                    codigo: producto.codigo,  // Añadir el código del producto
                    nombre: producto.name,  // Cambiar 'name' a 'nombre'
                    precio: producto.price,  // Cambiar 'price' a 'precio'
                    cantidad: producto.qty  // Cambiar 'qty' a 'cantidad'
                };
            })
        };

        console.log("Datos de la venta a enviar:", saleData);  // Verifica los datos antes de enviarlos al backend

        // Enviar los datos al backend
        $.ajax({
            url: '/realizar_venta',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(saleData),  // Enviar carrito con solo los datos necesarios
            success: function(response) {
                console.log("Respuesta del backend:", response);  // Verifica la respuesta del backend
                alert("Venta confirmada con éxito. Total: S/." + response.total);
                cart = {};  // Vaciar el carrito después de la venta
                updateCart();  // Actualizar la interfaz del carrito
            },
            error: function(error) {
                console.error("Error en la solicitud:", error);  // Verifica los errores en la solicitud
                alert("Hubo un error: " + error.responseJSON.error);
            }
        });
    } else {
        alert("Por favor, añade productos al carrito.");
    }
});