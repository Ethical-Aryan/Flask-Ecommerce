// ============================================================================
// Shopping Cart Logic (localStorage persistence)
// ============================================================================

function getCart() {
    try {
        return JSON.parse(localStorage.getItem('eshop_cart') || '[]');
    } catch (e) {
        return [];
    }
}

function saveCart(cart) {
    localStorage.setItem('eshop_cart', JSON.stringify(cart));
    updateCartUI();
}

function updateCartUI() {
    const cart = getCart();
    const totalCount = cart.reduce((sum, item) => sum + (parseInt(item.quantity) || 1), 0);

    // Update cart badge counters across the navbar
    document.querySelectorAll('#cart-counter').forEach(el => {
        el.textContent = totalCount;
    });

    const modalBody = document.getElementById('cart-modal-body');
    const totalPriceEl = document.getElementById('cart-total-price');
    const checkoutBtn = document.getElementById('checkout-btn');

    if (!modalBody) return;

    if (cart.length === 0) {
        modalBody.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-cart-x fs-1 text-secondary mb-3 d-block"></i>
                <h5 class="fw-bold text-light">Your cart is empty</h5>
                <p class="text-muted small">Explore our products and click "Add" to start shopping!</p>
            </div>
        `;
        if (totalPriceEl) totalPriceEl.textContent = '$0.00';
        if (checkoutBtn) checkoutBtn.disabled = true;
        return;
    }

    if (checkoutBtn) checkoutBtn.disabled = false;

    let total = 0;
    let html = '<div class="table-responsive"><table class="table table-dark table-borderless align-middle mb-0"><tbody>';

    cart.forEach((item, index) => {
        const price = parseFloat(item.price) || 0;
        const qty = parseInt(item.quantity) || 1;
        const itemTotal = price * qty;
        total += itemTotal;

        const imgSrc = item.image && item.image.trim() !== '' 
            ? item.image 
            : 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500';

        html += `
            <tr class="border-bottom border-secondary border-opacity-25">
                <td style="width: 65px;">
                    <img src="${imgSrc}" alt="${item.title}" class="rounded-3" style="width: 52px; height: 52px; object-fit: cover;">
                </td>
                <td>
                    <div class="fw-semibold text-light">${item.title}</div>
                    <small class="text-muted">$${price.toFixed(2)} each</small>
                </td>
                <td style="width: 130px;">
                    <div class="input-group input-group-sm">
                        <button type="button" class="btn btn-outline-secondary text-light px-2" onclick="changeQty(${index}, -1)">-</button>
                        <span class="input-group-text bg-dark text-light border-secondary px-3">${qty}</span>
                        <button type="button" class="btn btn-outline-secondary text-light px-2" onclick="changeQty(${index}, 1)">+</button>
                    </div>
                </td>
                <td class="text-end fw-bold text-info" style="width: 95px;">
                    $${itemTotal.toFixed(2)}
                </td>
                <td class="text-end" style="width: 40px;">
                    <button type="button" class="btn btn-sm text-danger p-0 border-0 bg-transparent" onclick="removeFromCart(${index})" title="Remove item">
                        <i class="bi bi-trash fs-5"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    modalBody.innerHTML = html;
    if (totalPriceEl) totalPriceEl.textContent = `$${total.toFixed(2)}`;
}

function addToCart(product) {
    const cart = getCart();
    const cleanPrice = parseFloat(String(product.price).replace(/[^0-9.]/g, '')) || 0;
    const existing = cart.find(item => String(item.id) === String(product.id) && item.title === product.title);

    if (existing) {
        existing.quantity = (parseInt(existing.quantity) || 1) + 1;
    } else {
        cart.push({
            id: product.id,
            title: product.title,
            price: cleanPrice,
            image: product.image || '',
            quantity: 1
        });
    }

    saveCart(cart);
    showToast(`"${product.title}" added to cart!`);
}

function changeQty(index, delta) {
    const cart = getCart();
    if (cart[index]) {
        cart[index].quantity = (parseInt(cart[index].quantity) || 1) + delta;
        if (cart[index].quantity <= 0) {
            cart.splice(index, 1);
        }
        saveCart(cart);
    }
}

function removeFromCart(index) {
    const cart = getCart();
    if (cart[index]) {
        const removed = cart.splice(index, 1);
        saveCart(cart);
        if (removed.length > 0) {
            showToast(`Removed "${removed[0].title}" from cart`);
        }
    }
}

function clearCart() {
    if (confirm('Are you sure you want to clear your cart?')) {
        saveCart([]);
        showToast('Cart cleared');
    }
}

function checkoutCart() {
    const cart = getCart();
    if (cart.length === 0) return;
    alert('Thank you for your order! Your purchase was successful.');
    saveCart([]);
    const modalEl = document.getElementById('cartModal');
    if (modalEl) {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    }
}

function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-message');
    if (toast && toastMsg) {
        toastMsg.textContent = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateCartUI();

    // Re-render cart whenever the cart modal is shown
    const cartModal = document.getElementById('cartModal');
    if (cartModal) {
        cartModal.addEventListener('show.bs.modal', () => {
            updateCartUI();
        });
    }

    // Global listener for .add-cart-btn
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('.add-cart-btn');
        if (btn) {
            const rawPrice = btn.getAttribute('data-price') || '0';
            const product = {
                id: btn.getAttribute('data-id') || Date.now(),
                title: btn.getAttribute('data-title') || 'Product',
                price: parseFloat(String(rawPrice).replace(/[^0-9.]/g, '')) || 0,
                image: btn.getAttribute('data-image') || ''
            };
            addToCart(product);
        }
    });
});
