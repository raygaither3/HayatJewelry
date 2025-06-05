from flask import Blueprint, render_template

info = Blueprint('info', __name__)

@info.route('/shipping-returns')
def shipping_returns():
    return render_template('info/shipping_returns.html')

@info.route('/about')
def about():
    return render_template('info/about.html')

@info.route('/reviews')
def reviews():
    return render_template('info/reviews.html')

@info.route('/terms')
def terms():
    return render_template('info/terms.html')

@info.route('/privacy')
def privacy():
    return render_template('info/privacy.html')

@info.route('/faqs')
def faqs():
    return render_template('info/faqs.html')