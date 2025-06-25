from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from .models import Cart, Order, OrderItem
from . import db
from .forms import CheckoutForm
import stripe
from flask import current_app
from datetime import datetime


order_routes = Blueprint('order_routes', __name__)


@order_routes.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)

    # Make sure user owns the order
    if order.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('main.home'))  # or wherever makes sense

    # Check if order is eligible for cancellation
    if order.status not in ['pending', 'processing']:
        flash('This order can no longer be canceled.', 'warning')
        return redirect(url_for('orders.view_order', order_id=order.id))

    # Cancel the order
    order.status = 'canceled'
    db.session.commit()

    flash('Your order has been canceled.', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))




@order_routes.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    form = CheckoutForm()

    # Always get cart items and total — needed for both GET and POST
    cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items) if cart_items else 0

    if request.method == 'POST' and form.validate_on_submit():
        # Get form data
        full_name = form.full_name.data
        email = form.email.data
        phone = form.phone.data
        address = f"{form.address.data}, {form.city.data}, {form.state.data} {form.zip_code.data}, {form.country.data}"
        notes = form.notes.data

        if not cart_items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for('cart_routes.cart'))

        # Create Stripe session
        line_items = []
        for item in cart_items:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.product_name,
                    },
                    'unit_amount': int(item.product.price * 100),
                },
                'quantity': item.quantity,
            })

        # Add flat-rate shipping
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'USPS Flat Rate Shipping',
                },
                'unit_amount': 499,
            },
            'quantity': 1,
        })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=email,
            line_items=line_items,
            mode='payment',
            success_url=url_for('order_routes.stripe_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('order_routes.checkout', _external=True),
            metadata={
                'user_id': current_user.id,
                'full_name': full_name,
                'phone': phone,
                'address': address,
                'notes': notes
            }
        )

        return redirect(session.url, code=303)

    return render_template('checkout.html', form=form, cart_items=cart_items, total=total)

@order_routes.route('/checkout/success')
@login_required
def stripe_success():
    session_id = request.args.get('session_id')  # Stripe will send this
    if not session_id:
        flash("Missing session ID from Stripe.", "danger")
        return redirect(url_for('views.home'))

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        metadata = session.metadata
    except Exception as e:
        flash(f"Could not retrieve payment session: {e}", "danger")
        return redirect(url_for('views.home'))

    # Get user/cart info
    user_id = int(metadata['user_id'])
    full_name = metadata['full_name']
    phone = metadata['phone']
    address = metadata['address']
    notes = metadata.get('notes', '')

    cart_items = Cart.query.filter_by(customer_id=user_id).all()
    if not cart_items:
        flash("No items found in cart. Order not created.", "danger")
        return redirect(url_for('views.home'))

    total = sum(item.product.price * item.quantity for item in cart_items)
    new_order = Order(
        customer_id=user_id,
        full_name=full_name,
        email=session.customer_email,  # comes from Stripe
        phone=phone,
        shipping_address=address,
        notes=notes,
        status="Paid",
        total=total,
        timestamp=datetime.utcnow()
    )
    db.session.add(new_order)
    db.session.flush()

    for item in cart_items:
        db.session.add(OrderItem(
            order_id=new_order.id,
            product_id=item.product.id,
            quantity=item.quantity,
            price_each=item.product.price
        ))
        item.product.quantity -= item.quantity
        db.session.delete(item)

    db.session.commit()

    flash("🎉 Order placed successfully!", "success")
    return render_template('order_success.html', order=new_order)


@order_routes.route('/success')
@login_required
def stripe_quick_success():
    flash("Payment successful! Your order is being processed.", "success")
    return render_template('success.html')


@order_routes.route('/confirmation/<int:order_id>')
@login_required
def confirmation(order_id):
    order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first()

    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('views.home'))

    order_items = OrderItem.query.filter_by(order_id=order.id).all()

    return render_template('confirmation.html', order=order, order_items=order_items)

    


@order_routes.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    return render_template('orders.html', orders=orders)
