import os
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from .forms import SearchForm
from flask_migrate import Migrate
from dotenv import load_dotenv


load_dotenv()
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def create_database():
    db.create_all()
    print("Created Database!")


def create_app():
    app = Flask(__name__)
    Bootstrap5(app)
    app.config['SECRET_KEY'] = 'secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    uploads_path = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    os.makedirs(uploads_path, exist_ok=True)
    app.config['UPLOAD_FOLDER']      = uploads_path
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

    csrf.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404
    

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return Customer.query.get(int(user_id))


    from .views import views
    from .auth import auth
    from .admin import admin
    from .models import Customer
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

    
    # with app.app_context():
    #     create_database()
    
    return app