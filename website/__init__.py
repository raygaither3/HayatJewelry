import os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from dotenv import load_dotenv

from .config import DevelopmentConfig, ProductionConfig
from .extensions import db, mail, csrf, migrate
from .forms import SearchForm

# Blueprint imports
from .views import views
from .auth import auth
from .admin import admin
from .cart_routes import cart_routes
from .order_routes import order_routes
from .info_routes import info
from .stripe_webhook import stripe_webhook

load_dotenv()

def create_app():
    app = Flask(__name__)
    Bootstrap5(app)

    # Load appropriate config
    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        print("🚀 Using ProductionConfig")
        app.config.from_object(ProductionConfig)
    else:
        print("🧪 Using DevelopmentConfig")
        app.config.from_object(DevelopmentConfig)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Init extensions
    csrf.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Setup login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import Customer

    @login_manager.user_loader
    def load_user(user_id):
        return Customer.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(views)
    app.register_blueprint(admin)
    app.register_blueprint(cart_routes)
    app.register_blueprint(order_routes)
    app.register_blueprint(info)
    app.register_blueprint(stripe_webhook)

    # Global context processor for search
    @app.context_processor
    def inject_search_form():
        return dict(search_form=SearchForm())

    # Custom error pages
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    return app