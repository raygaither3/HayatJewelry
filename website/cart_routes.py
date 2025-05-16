from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from .models import Cart, Product, Wishlist
from . import db



cart_routes = Blueprint('cart_routes', __name__)  # Create a Blueprint object


def calculate_cart_total(cart_items):
    return sum(item.product.price * item.quantity for item in cart_items)



@cart_routes.route('/add-to-wishlist/<int:item_id>', methods=['GET', 'POST'], endpoint='add_to_wishlist')
@login_required
def add_to_wishlist(item_id):
    item_to_add = Product.query.get(item_id)

    if not item_to_add:
        flash("Product not found!", "danger")
        return redirect(request.referrer)

    item_exists = Wishlist.query.filter_by(product_id=item_id, customer_id=current_user.id).first()

    if item_exists:
        flash(f'{item_to_add.product_name} already in wishlist')

        return redirect(request.referrer)

    new_wishlist_item = Wishlist(
        product_id=item_to_add.id,
        customer_id=current_user.id
    )

    try:
        db.session.add(new_wishlist_item)
        db.session.commit()
        flash(f'{item_to_add.product_name} added to wishlist')
    except Exception as e:
        print('Item not added to wishlist', e)
        flash('Item has not been added to wishlist')

    return redirect(request.referrer)



@cart_routes.route('/add-to-cart/<int:item_id>', methods=['POST'], endpoint='add_to_cart')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)

    if not item_to_add:
        flash("Product not found!", "danger")
        return redirect(request.referrer)

    # Get the size from the form, if it's a ring.
    size = request.form.get('size')  # Will be None for non-rings

    # Check if the item already exists in the cart with the same size (if applicable)
    item_exists = Cart.query.filter_by(
        product_id=item_id, customer_id=current_user.id, size=size).first()

    if item_exists:
        try:
            item_exists.quantity += 1
            item_exists.total = item_exists.product.price * item_exists.quantity
            db.session.commit()
            flash(f'Quantity of {item_exists.product.product_name} (size: {size or "N/A"}) has been updated')

        except Exception as e:
            print(e)
            flash(f'Quantity of {item_exists.product.product_name} not updated')

    else:
        new_cart_item = Cart(
            quantity=1,
            total=item_to_add.price * 1,
            product_id=item_to_add.id,
            customer_id=current_user.id,
            size=size  # Add the size to the cart item if it's a ring
        )
        try:
            db.session.add(new_cart_item)
            db.session.commit()
            flash(f'{item_to_add.product_name} (size: {size or "N/A"}) added to cart')
        except Exception as e:
            print('Item not added to cart', e)
            flash('Item has not been added to cart')

    # 🛒 Check if this came from wishlist
    from_wishlist = request.form.get('from_wishlist')
    if from_wishlist:
        wishlist_item = Wishlist.query.filter_by(product_id=item_id, customer_id=current_user.id).first()
        if wishlist_item:
            try:
                db.session.delete(wishlist_item)
                db.session.commit()
                flash('Item removed from wishlist')
            except Exception as e:
                print('Failed to remove from wishlist', e)
                flash('Could not remove item from wishlist', 'danger')

    return redirect(request.referrer)



@cart_routes.route('/move-all-to-cart', methods=['POST'])
@login_required
def move_all_to_cart():
    wishlist_items = Wishlist.query.filter_by(customer_id=current_user.id).all()

    if not wishlist_items:
        flash('Your wishlist is empty!', 'info')
        return redirect(request.referrer)

    try:
        for item in wishlist_items:
            # Check if the product is already in cart
            cart_item = Cart.query.filter_by(product_id=item.product.id, customer_id=current_user.id).first()
            if cart_item:
                cart_item.quantity += 1
                cart_item.total = cart_item.product.price * cart_item.quantity
            else:
                new_cart_item = Cart(
                    quantity=1,
                    total=item.product.price,
                    product_id=item.product.id,
                    customer_id=current_user.id
                )
                db.session.add(new_cart_item)

            # Remove from wishlist
            db.session.delete(item)

        db.session.commit()
        flash('All wishlist items moved to cart!', 'success')
    except Exception as e:
        print('Error moving all items:', e)
        flash('There was a problem moving your items.', 'danger')

    return redirect(request.referrer)


@cart_routes.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    
    amount = calculate_cart_total(cart)

    return render_template('cart.html', cart=cart, amount=amount, total=amount)


@cart_routes.route('/pluscart', methods=['GET'])
@login_required
def plus_cart():
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.get(cart_id)

    if cart_item and cart_item.customer_id == current_user.id:
        cart_item.quantity += 1
        db.session.commit()

        cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
        amount = sum(item.product.price * item.quantity for item in cart_items)
        total = amount + 10

        return jsonify({
            'quantity': cart_item.quantity,
            'amount': f"${amount:.2f}",
            'total': f"${total:.2f}"
        })

    return jsonify({'error': 'Item not found'}), 404


@cart_routes.route('/minuscart', methods=['GET'])
@login_required
def minus_cart():
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.get(cart_id)

    if cart_item and cart_item.customer_id == current_user.id:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            db.session.commit()
        else:
            db.session.delete(cart_item)
            db.session.commit()

        cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
        amount = sum(item.product.price * item.quantity for item in cart_items)
        total = amount + 10

        return jsonify({
            'quantity': cart_item.quantity if cart_item in db.session else 0,
            'amount': f"${amount:.2f}",
            'total': f"${total:.2f}"
        })

    return jsonify({'error': 'Item not found'}), 404

  

@cart_routes.route('/removecart', methods=['GET'])
@login_required
def remove_cart():
    cart_id = request.args.get('cart_id')
    print("Cart ID received:", cart_id)
    cart_item = Cart.query.get(cart_id)

    cart_item = Cart.query.get(cart_id)

    if not cart_item:
        return jsonify({'error': 'Item not found'}), 404

    if cart_item and cart_item.customer_id == current_user.id:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            db.session.commit()
        else:
            db.session.delete(cart_item)
            db.session.commit()

        # Recalculate updated totals
        cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
        amount = sum(item.product.price * item.quantity for item in cart_items)
        total = amount + 10  # for example: $10 shipping or tax

        return jsonify({
            'amount': f"${amount:.2f}",
            'total': f"${total:.2f}"
        })

    return jsonify({'error': 'Item not found'}), 404



@cart_routes.route('/empty-cart', methods=['POST'])
@login_required
def empty_cart():
    try:
        # Delete all items from the cart for the current user
        Cart.query.filter_by(customer_id=current_user.id).delete()
        db.session.commit()
        flash("Your cart has been emptied.", "success")
    except Exception as e:
        print("Error emptying cart:", e)
        flash("There was an issue emptying your cart.", "danger")

    return redirect(url_for('cart_routes.show_cart'))  # Redirect back to the cart page



@cart_routes.route('/wishlist')
@login_required
def show_wishlist():
    wishlist = Wishlist.query.filter_by(customer_id=current_user.id).all()
    return render_template('wishlist.html', wishlist=wishlist)



@cart_routes.route('/wishlist/move/<int:item_id>', methods=['POST'])
@login_required
def move_to_cart(item_id):
    wishlist_item = Wishlist.query.get_or_404(item_id)

    if wishlist_item.customer_id != current_user.id:
        flash("Unauthorized action.")
        return redirect(url_for('cart_routes.show_wishlist'))

    # Get product from wishlist item
    product = wishlist_item.product

    # Check if item already in cart
    existing_cart_item = Cart.query.filter_by(customer_id=current_user.id, product_id=product.id).first()
    if existing_cart_item:
        existing_cart_item.quantity += wishlist_item.quantity
    else:
        new_cart_item = Cart(
            customer_id=current_user.id,
            product_id=product.id,
            quantity=wishlist_item.quantity
        )
        db.session.add(new_cart_item)

    # Remove from wishlist
    db.session.delete(wishlist_item)
    db.session.commit()

    flash("Item moved to cart.")
    return redirect(url_for('cart_routes.show_wishlist'))


@cart_routes.route('/remove-from-wishlist/<int:item_id>', methods=['POST'])
@login_required
def remove_from_wishlist(item_id):
    wishlist_item = Wishlist.query.get_or_404(item_id)

    if wishlist_item.customer_id != current_user.id:
        return {"error": "Unauthorized"}, 403

    try:
        db.session.delete(wishlist_item)
        db.session.commit()
        return {"success": True}, 200
    except Exception as e:
        print('Failed to remove wishlist item:', e)
        return {"error": "Failed to delete item"}, 500