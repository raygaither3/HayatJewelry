from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from website.email_utils import send_reset_email
from . import db
from .forms import LoginForm, PasswordChangeForm, ReviewForm, SignUpForm,RequestResetForm, ResetPasswordForm
from .models import Customer, Product, Review
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError



auth = Blueprint('auth', __name__)



@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        username = form.username.data.strip()
        password1 = form.password1.data
        password2 = form.password2.data
        phone_number = form.phone_number.data.strip()

        if password1 != password2:
            flash("Passwords do not match", category="error")
            return render_template("sign_up.html", form=form)

        new_customer = Customer(
            email=email,
            username=username,
            password=password2,
            phone_number=phone_number
        )

        try:
            db.session.add(new_customer)
            db.session.commit()
            flash('Account Created Successfully. You can now log in.', category="success")
            return redirect('/login')

        except IntegrityError as e:
            db.session.rollback()
            if "UNIQUE constraint failed" in str(e.orig):
                flash("Email or username already exists.", category="error")
            else:
                flash(f"Account not created: {str(e)}", category="error")
        except Exception as e:
            db.session.rollback()
            flash(f"Unexpected error: {str(e)}", category="error")

        # Clear form fields after failure
        form.email.data = ''
        form.username.data = ''
        form.password1.data = ''
        form.password2.data = ''
        form.phone_number.data = ''
        
    return render_template("sign_up.html", form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        password = form.password.data

        # Case-insensitive search (optional, only if your DB might have uppercase emails)
        customer = Customer.query.filter(func.lower(Customer.email) == email).first()

        if customer and customer.verify_password(password=password):
            login_user(customer)
            return redirect('/')  # Redirect to home page after login

        flash('Incorrect Email or Password')
        return redirect('/login')

    return render_template("login.html", form=form)
        

    return render_template("login.html", form=form)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')



@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    customer = Customer.query.get(customer_id)
    return render_template('profile.html', customer=customer)


@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):  # Verify current password
            if new_password == confirm_new_password:
                customer.password = confirm_new_password
                db.session.commit()
                flash('Password has been updated successfully')
                return redirect(f'/profile/{customer.id}')
            else:
                flash('New passwords do not match!!')
        else:
            flash('Current password is incorrect')

    return render_template('change_password.html', form=form, customer=customer)


@auth.route('/submit-review/<int:product_id>', methods=['GET', 'POST'])
@login_required
def submit_review(product_id):
    form = ReviewForm()
    product = Product.query.get(product_id)

    if form.validate_on_submit():
        rating = form.rating.data
        review_text = form.review_text.data

        new_review = Review()
        new_review.rating = rating
        new_review.review_text = review_text
        new_review.product_id = product.id
        new_review.customer_id = current_user.id

        db.session.add(new_review)
        db.session.commit()

        flash('Review submitted successfully')
        return redirect(f'/product/{product.id}')

    return render_template('submit_review.html', form=form, product=product)


@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('A password reset email has been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_request.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    user = Customer.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_token.html', form=form)

