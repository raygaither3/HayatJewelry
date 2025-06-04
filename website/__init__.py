import os
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template
from flask_login import LoginManager
from .forms import SearchForm
from dotenv import load_dotenv
from .config import DevelopmentConfig, ProductionConfig
from .extensions import db, mail, csrf, migrate

load_dotenv()  # Load environment variables from .env

def create_database():
    db.create_all()
    print("Created Database!")

def create_app():
    app = Flask(__name__)
    Bootstrap5(app)

    # Load the appropriate config based on FLASK_ENV
    if os.environ.get("FLASK_ENV") == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    csrf.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import Customer

    @login_manager.user_loader
    def load_user(user_id):
        return Customer.query.get(int(user_id))

    from .views import views
    from .auth import auth
    from .admin import admin
    from .cart_routes import cart_routes
    from .order_routes import order_routes

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')
    app.register_blueprint(cart_routes, url_prefix='/')
    app.register_blueprint(order_routes, url_prefix='/')

    @app.context_processor
    def inject_search_form():
        return dict(search_form=SearchForm())

    # Optional: create DB in dev mode
    # with app.app_context():
    #     create_database()

    return app