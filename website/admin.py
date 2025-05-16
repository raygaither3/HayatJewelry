import os
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from .forms import ProductInventoryForm, UpdateOrderStatusForm
from werkzeug.utils import secure_filename
from .models import Customer, Order, OrderItem, Product, ProductImage
from . import db
from flask import current_app

admin = Blueprint('admin', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']



@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id != 1:
        return abort(403)

    form = ProductInventoryForm()
    if form.validate_on_submit():
        # Create the product first (without setting the picture yet)
        new_item = Product(
            product_name=form.product_name.data,
            price=form.price.data,
            sale_price=form.sale_price.data,
            description=form.description.data,
            category=form.category.data,  
            quantity=form.quantity.data,
        )
        db.session.add(new_item)
        db.session.flush()  # important: get new_item.id

        uploaded_files = form.product_images.data
        first_image_filename = None

        for upload in uploaded_files:
            if upload and allowed_file(upload.filename):
                filename = secure_filename(upload.filename)
                dest = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                upload.save(dest)

                # Save each image to ProductImage
                img = ProductImage(
                    product_id=new_item.id,
                    image_url=filename
                )
                db.session.add(img)

                # Save the filename of the first upload
                if not first_image_filename:
                    first_image_filename = filename

        # After uploading all images, set the first one as the main product picture
        if first_image_filename:
            new_item.product_picture = first_image_filename

        # Final commit
        try:
            db.session.commit()
            flash(f"'{new_item.product_name}' added!", 'success')
            return redirect(url_for('admin.add_shop_items'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {e}', 'danger')

    return render_template('add-shop-items.html', form=form)




@admin.route('/store-items')
@login_required
def shop_items():
    if current_user.id != 1:
        return abort(403)
    items = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('shop_items.html', items=items)



@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id != 1:
        return render_template('404.html'), 403

    # 1) load the product
    item = Product.query.get_or_404(item_id)

    # 2) use obj=item so the form fields start filled-in
    form = ProductInventoryForm(obj=item)
    # file-upload fields shouldn’t be required here
    form.product_images.validators = []

    if form.validate_on_submit():
        # 3) populate the simple fields back onto the model
        form.populate_obj(item)

        # 4) handle any newly uploaded **single** image for product_picture
        file = request.files.get('product_picture')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            dest = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(dest)
            item.product_picture = filename

            # optionally also record it in ProductImage
            img = ProductImage(product_id=item.id, image_url=filename)
            db.session.add(img)

        # 5) commit everything
        db.session.commit()
        flash(f"Product #{item.id} updated!", "success")
        return redirect(url_for('admin.shop_items'))

    return render_template(
        'update_items.html',
        form=form,
        item=item
    )



@admin.route('/delete-item/<int:item_id>')
@login_required
def delete_item(item_id):
    if current_user.id != 1:
        return abort(403)

    item = Product.query.get_or_404(item_id)
    try:
        # Delete associated order items first
        order_items = OrderItem.query.filter_by(product_id=item.id).all()
        for order_item in order_items:
            db.session.delete(order_item)

        # Delete image files & records
        for img in item.images:
            path = os.path.join(UPLOAD_FOLDER, img.image_url)
            if os.path.exists(path):
                os.remove(path)
            db.session.delete(img)

        # Delete the product itself
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('admin.shop_items'))



@admin.route('/delete-product-image/<int:image_id>', methods=['POST'])
@login_required
def delete_product_image(image_id):
    if current_user.id != 1:
        return abort(403)

    img = ProductImage.query.get_or_404(image_id)
    try:
        # delete file from disk
        path = os.path.join(UPLOAD_FOLDER, img.image_url)
        if os.path.exists(path):
            os.remove(path)
        # delete db record
        db.session.delete(img)
        db.session.commit()
        flash('Image deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {e}', 'danger')

    return redirect(request.referrer or url_for('admin.shop_items'))



@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.id != 1:
        return render_template('404.html')

    orders = Order.query.order_by(Order.created_at.desc()).all()

    # Create a form per order ID
    forms = {order.id: UpdateOrderStatusForm(status=order.status) for order in orders}

    return render_template('view_orders.html', orders=orders, forms=forms)



@admin.route('/update-order-status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    if current_user.id != 1:
        abort(403)

    form = UpdateOrderStatusForm()
    order = Order.query.get_or_404(order_id)

    if form.validate_on_submit():
        order.status = form.status.data
        db.session.commit()
        flash(f"Order #{order.id} status updated to '{order.status.title()}'", "success")

    return redirect(url_for('admin.order_view'))



@admin.route('/customers')
@login_required
def display_customers():
    if current_user.id != 1:
        return render_template('404.html')

    customers = Customer.query.order_by(Customer.created_at.desc()).all()  # Retrieve all customers
    return render_template('customers.html', customers=customers)


@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id != 1:
        return render_template('404.html')

    return render_template('admin.html')