from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():

    app = Flask(__name__, template_folder = 'templates')

    username = 'fra'
    password = 'fra'
    database = 'ecommerce'
    #indirizzo = 'localhost'
    indirizzo = '100.96.1.2'
    port = '5432'

    app.config['SECRET_KEY'] = 'charizardteracrystal'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{username}:{password}@{indirizzo}:{port}/{database}"

    db.init_app(app)

    from .models import Utenti

    from .auth import auth
    from .views import views
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Utenti.query.get(id)

    return app






