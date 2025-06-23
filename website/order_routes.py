from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from .models import Cart, Order, OrderItem
from . import db
from .forms import CheckoutForm
import stripe
from flask import current_app


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
                        'name': item.product.name,
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
            success_url=url_for('order_routes.stripe_success', _external=True),
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

@order_routes.route('/success')
@login_required
def stripe_success():
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





# @order_routes.route.route('/place-order')
# @login_required
# def place_order():
#     customer_cart = Cart.query.filter_by(customer_link=current_user.id)
#     if customer_cart:
#         try:
#             total = 0
#             for item in customer_cart:
#                 total += item.product.current_price * item.quantity

#             service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
#             create_order_response = service.collect.mpesa_stk_push(phone_number=254708374149, email=current_user.email,
#                                                         amount=total + 5, narrative='Purchase of Goods')
            

#             for item in customer_cart:
#                 new_order = Order()  # Define new_order here
#                 new_order.quantity = item.quantity
#                 new_order.price = item.product.current_price
#                 new_order.status = create_order_response['invoice']['state'].capitalize()
#                 new_order.payment_id = create_order_response['id']

#                 new_order.product_link = item.product_link
#                 new_order.customer_link = item.customer_link

#                 db.session.add(new_order)

#                 product = Product.query.get(item.product_link)
#                 product.in_stock -= item.quantity

#                 db.session.delete(item)

#                 db.session.commit()

#             flash('Order Placed Successfully')

#             return redirect('/orders')
        
#         except Exception as e:
#             print(e)
#             flash('Order not placed')
#             return redirect('/')
        
#     else:
#         flash('Your cart is Empty')
#         return redirect('/')