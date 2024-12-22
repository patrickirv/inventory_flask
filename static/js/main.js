document.addEventListener('DOMContentLoaded', function() {
    // Funcionalidad del botón de venta
    const sellButtons = document.querySelectorAll('.sell-btn');
    sellButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const quantity = prompt('Ingrese la cantidad a vender:', '1');
            
            if (quantity !== null && quantity !== '') {
                fetch('/sales', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `product_id=${productId}&quantity=${quantity}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        location.reload();
                    } else {
                        alert(data.message);
                    }
                });
            }
        });
    });

    // Cargar recomendaciones de compra
    const recommendationsDiv = document.getElementById('recommendations');
    if (recommendationsDiv) {
        fetch('/recommendations')
            .then(response => response.json())
            .then(data => {
                let html = '<ul>';
                data.forEach(item => {
                    html += `<li>${item.product_name}: Compra recomendada - ${item.recommended_purchase} unidades</li>`;
                });
                html += '</ul>';
                recommendationsDiv.innerHTML = html;
            });
    }
});

