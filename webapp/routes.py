from flask import render_template, request
from .models import *

def register_routes(app, db):

    @app.route('/', methods=['GET', 'POST'])
    
    def index():
        i1 = Indirizzi.query.first()
        return i1.__repr__()