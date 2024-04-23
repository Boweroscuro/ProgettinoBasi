from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():

    app = Flask(__name__, template_folder = 'templates')

    username = 'fra'
    password = 'fra'
    database = 'ecommerce'
    indirizzo = '100.96.1.2'
    port = '5432'

    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{username}:{password}@{indirizzo}:{port}/{database}"


    db.init_app(app)

    from routes import register_routes
    register_routes(app, db)
    
    migrate = Migrate(app, db)
    return app






