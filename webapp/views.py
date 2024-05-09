from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Prodotti

views = Blueprint('views', __name__)

@views.route('/') 
@login_required
def home():

    prodotti = Prodotti.query.all()
    return render_template("home.html", utente = current_user, prodotti = prodotti)
