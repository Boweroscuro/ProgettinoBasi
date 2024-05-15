from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .models import Categorie, Prodotti

views = Blueprint('views', __name__)

@views.route('/') 
@login_required
def home():

    categorie = Categorie.query.filter_by(idgenitore=None).all()
    
    search = request.args.get('search')
    categorie = request.args.get('categoria')

    if search:
        # Esegui una ricerca generica per i prodotti che corrispondono al termine di ricerca
        #prodotti = Prodotti.query.filter(Prodotti.nome.ilike(f'%{search}%')).all()
        categorie = Categorie.query.filter(Categorie.nome.ilike(f'%{search}%') , Categorie.idgenitore.is_(None)).all()
    
    else:
        # Nessuna ricerca specificata, mostra tutti i prodotti
        categorie = Categorie.query.filter(Categorie.idgenitore.is_(None)).all()

    return render_template("home.html", utente = current_user, categorie = categorie)
"""elif categoria:
        categoria_selezionata = Categorie.query.filter_by(nome=categoria).first()
        if categoria_selezionata:
            # Esegui una ricerca per i prodotti che hanno l'idgenitore uguale all'id della categoria selezionata
            prodotti = Prodotti.query.filter_by(idc=categoria_selezionata.idcategoria).all()
        else:
            prodotti = []  # Categoria non trovata, restituisci una lista vuota"""



