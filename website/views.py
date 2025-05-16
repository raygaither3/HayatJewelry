from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from .models import Cart, Product, Review
from . import db
from .forms import SearchForm
from sqlalchemy import or_

from website.forms import ReviewForm


views = Blueprint('views', __name__)  # Create a Blueprint object


@views.route('/')
def home():

    new_arrivals = Product.query.order_by(Product.created_at.desc()).limit(8).all()

    
    return render_template("home.html", new_arrivals=new_arrivals, cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])



@views.route('/products/<category>')
def products_by_category(category):
    products = Product.query.filter_by(category=category.capitalize()).all()
    return render_template(
        "products.html",
        products=products,
        selected_category=category.capitalize(),
        cart=Cart.query.filter_by(customer_id=current_user.id).all()
        if current_user.is_authenticated else []
    )


@views.route('/product/<int:product_id>')
def product_detail(product_id):

    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()
    average_rating = db.session.query(db.func.avg(Review.rating)).filter_by(product_id=product_id).scalar()

    if reviews:
        reviews = sorted(reviews, key=lambda x: x.created_at, reverse=True)
    else:
        reviews = []

    if average_rating:
        average_rating = round(average_rating, 1)

    return render_template('product_detail.html', product=product, reviews=reviews, cart=Cart.query.filter_by(customer_id=current_user.id).all()
        if current_user.is_authenticated else [])

  


@views.route('/product/<int:product_id>')
def submit_review(product_id):
    form = ReviewForm()
    if form.validate_on_submit():
        new_review = Review(
            product_id=product_id,
            customer_id=current_user.id,
            rating=int(form.rating.data),
            review_text=form.review_text.data
        )
        db.session.add(new_review)
        db.session.commit()
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('product_detail', product_id=product_id))
    return render_template('submit_review.html', form=form)
 

@views.context_processor
def inject_search_form():
    return dict(search_form=SearchForm())





@views.route('/search', methods=['GET', 'POST'])
def search():
    search_query = request.args.get('query') or request.form.get('search')

    if search_query:
        results = Product.query.filter(
            or_(
                Product.product_name.ilike(f'%{search_query}%'),
                Product.description.ilike(f'%{search_query}%'),
                Product.category.ilike(f'%{search_query}%')
            )
        ).all()

        if results:
            return render_template('search.html', results=results, query=search_query)
        else:
            flash("No results found for your search.", "info")
            return redirect('/')
    return redirect('/')