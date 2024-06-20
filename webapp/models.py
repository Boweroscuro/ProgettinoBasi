from datetime import datetime
from webapp import db
from flask_login import UserMixin


UtentiIndirizzi = db.Table('utentiindirizzi',
    db.Column('idu', db.Integer, db.ForeignKey('utenti.idutente')),
    db.Column('idi', db.Integer, db.ForeignKey('indirizzi.idindirizzo'))
)
"""
UtentiProdotti = db.Table('utentiprodotti',
    db.Column('idu', db.Integer, db.ForeignKey('utenti.idutente')),
    db.Column('idp', db.Integer, db.ForeignKey('prodotti.idprodotto'))
) 
"""

class Utenti(db.Model, UserMixin):
    __tablename__ = 'utenti'

    idutente = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.Text, nullable = False)
    cognome = db.Column(db.Text, nullable = False)
    username = db.Column(db.Text, nullable = False)
    email = db.Column(db.Text, nullable = False)
    password_hash = db.Column(db.Text, nullable= False)
    privilegi = db.Column(db.Boolean, nullable = False)
    isadmin = db.Column(db.Boolean, nullable = False)

    def get_id(self):
        return self.idutente
    
    indirizzo_ass = db.relationship('Indirizzi', secondary = UtentiIndirizzi, backref=db.backref('utente_ass'))
    prodotto_carrello = db.relationship('CarrelloProdotto', backref='utente')


class Indirizzi(db.Model):
    __tablename__ = 'indirizzi'

    idindirizzo = db.Column(db.Integer, primary_key = True)
    via = db.Column(db.Text, nullable = False)
    numero = db.Column(db.Integer, nullable= False)
    cap = db.Column(db.Integer, nullable= False)
    città = db.Column(db.Text, nullable = False)
    isdefault = db.Column(db.Boolean, nullable = False)


class Categorie(db.Model):
    __tablename__ = 'categorie'

    idcategoria = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.Text, nullable = False)
    immagine = db.Column(db.LargeBinary, nullable = False)
    idgenitore = db.Column(db.Integer, db.ForeignKey('categorie.idcategoria'))

class Prodotti(db.Model):
    __tablename__ = 'prodotti'

    idprodotto = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.Text, nullable = False)
    costo = db.Column(db.Numeric, nullable= False)
    quantità = db.Column(db.Integer, nullable= False)
    immagine = db.Column(db.LargeBinary)
    descrizione = db.Column(db.Text, nullable = False)
    marca = db.Column(db.Text, nullable = False)

    idu = db.Column(db.Integer, db.ForeignKey('utenti.idutente'))
    idc = db.Column(db.Integer, db.ForeignKey('categorie.idcategoria'))


class Ordini(db.Model):
    __tablename__ = 'ordini'

    idordine = db.Column(db.Integer, primary_key = True)
    metodo_di_pagamento = db.Column(db.Text, nullable = False)
    stato = db.Column(db.Text, nullable = False)
    dataordine = db.Column(db.Date, nullable = False, default=datetime.now().date)
    completato = db.Column(db.Boolean, nullable = False)

    idcp = db.Column(db.Integer, db.ForeignKey('carrello_prodotto.idcp'), nullable=False)

class Recensioni(db.Model):
    __tablename__ = 'recensioni'

    idrecensione = db.Column(db.Integer, primary_key = True)
    voto = db.Column(db.Integer, nullable = False)
    commento = db.Column(db.Text, nullable = False)

class CarrelloProdotto(db.Model):
    __tablename__ = 'carrello_prodotto'

    idcp = db.Column(db.Integer, primary_key=True)
    idu = db.Column(db.Integer, db.ForeignKey('utenti.idutente'), nullable=False)
    idp = db.Column(db.Integer, db.ForeignKey('prodotti.idprodotto'), nullable=False)
    quantità = db.Column(db.Integer, nullable=False, default=1)

    prodotto = db.relationship('Prodotti', backref='carrello_prodotti')

class Storici(db.Model):
    __tablename__ = 'storici'

    idor = db.Column(db.Integer,  db.ForeignKey('ordini.idordine'), primary_key = True)
    idpr = db.Column(db.Integer, db.ForeignKey('prodotti.idprodotto'), primary_key = True)
    idu = db.Column(db.Integer, db.ForeignKey('utenti.idutente'), nullable = False)
    qta = db.Column(db.Integer, nullable=False, default=1)
    pagato = db.Column(db.Integer, nullable=False)

    prodotto = db.relationship('Prodotti', backref='prodotti')