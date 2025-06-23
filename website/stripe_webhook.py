import json
from flask import Blueprint, request

stripe_webhook = Blueprint('stripe_webhook', __name__)

@stripe_webhook.route('/webhook', methods=['POST'])
def stripe_webhook_received():
    payload = request.data
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return '', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Create order in DB
        user_id = session['metadata']['user_id']
        full_name = session['metadata']['full_name']
        email = session['customer_email']
        phone = session['metadata']['phone']
        address = session['metadata']['address']
        notes = session['metadata']['notes']

        # Get cart items for the user
        cart_items = Cart.query.filter_by(customer_id=user_id).all()
        total = sum(item.product.price * item.quantity for item in cart_items)

        new_order = Order(
            customer_id=user_id,
            full_name=full_name,
            email=email,
            phone=phone,
            shipping_address=address,
            notes=notes,
            total=total,
            status="paid"
        )
        db.session.add(new_order)
        db.session.flush()

        for item in cart_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_each=item.product.price,
                size=item.size
            )
            db.session.add(order_item)

        # Clear cart
        Cart.query.filter_by(customer_id=user_id).delete()
        db.session.commit()

    return '', 200