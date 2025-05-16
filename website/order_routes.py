from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from .models import Cart, Order, OrderItem
from . import db
from .forms import CheckoutForm




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
    form = CheckoutForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Get form data
        full_name = form.full_name.data
        email = form.email.data
        phone = form.phone.data
        address = f"{form.address.data}, {form.city.data}, {form.state.data} {form.zip_code.data}, {form.country.data}"
        notes = form.notes.data

        # Get cart items
        cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
        if not cart_items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for('cart_routes.cart'))

        # Calculate total
        total = sum(item.product.price * item.quantity for item in cart_items)

        # Create Order
        new_order = Order(
            customer_id=current_user.id,
            full_name=full_name,
            email=email,
            phone=phone,
            shipping_address=address,
            notes=notes,
            total=total,
            status="pending"
        )
        db.session.add(new_order)
        db.session.flush()  # To get order ID

        # Add OrderItems
        for item in cart_items:
            order_item = OrderItem(
            order_id   = new_order.id,
            product_id = item.product_id,
            quantity   = item.quantity,
            price_each = item.product.price,
            size       = item.size,
            )
            db.session.add(order_item)

        # Clear cart
        Cart.query.filter_by(customer_id=current_user.id).delete()

        db.session.commit()
        flash("Order placed successfully!", "success")
        return redirect(url_for('order_routes.confirmation', order_id=new_order.id))

    return render_template('checkout.html', form=form)


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