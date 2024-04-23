from flask import render_template, request
from models import *

def register_routes(app, db):

    @app.route('/', methods=['GET', 'POST'])
    
    def index():
        u1 = Utenti.query.first()
        return u1.__repr__()