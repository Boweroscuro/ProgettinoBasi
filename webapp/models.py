from webapp import db
from flask_login import UserMixin


UtentiIndirizzi = db.Table('utentiindirizzi',
    db.Column('idu', db.Integer, db.ForeignKey('utenti.idutente')),
    db.Column('idi', db.Integer, db.ForeignKey('indirizzi.idindirizzo'))
)

class Utenti(db.Model, UserMixin):
    __tablename__ = 'utenti'

    idutente = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.Text, nullable = False)
    cognome = db.Column(db.Text, nullable = False)
    username = db.Column(db.Text, nullable = False)
    email = db.Column(db.Text, nullable = False)
    password_hash = db.Column(db.Text, nullable= False)
    privilegi = db.Column(db.Boolean)

    def get_id(self):
        return self.idutente
    
    indirizzo_ass = db.relationship('Indirizzi', secondary = UtentiIndirizzi, backref=db.backref('utente_ass'))


class Indirizzi(db.Model):
    __tablename__ = 'indirizzi'

    idindirizzo = db.Column(db.Integer, primary_key = True)
    via = db.Column(db.Text, nullable = False)
    numero = db.Column(db.Integer, nullable= False)
    cap = db.Column(db.Integer, nullable= False)
    città = db.Column(db.Text, nullable = False)


class Categorie(db.Model):
    __tablename__ = 'categorie'

    idcategoria = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.Text, nullable = False)

class Prodotti(db.Model):
    __tablename__ = 'prodotti'

    idprodotto = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.Text, nullable = False)
    costo = db.Column(db.Float, nullable= False)
    quantità = db.Column(db.Integer, nullable= False)
    immagine = db.Column(db.LargeBinary)
    descrizione = db.Column(db.Text, nullable = False)
    marca = db.Column(db.Text, nullable = False)

    idu = db.Column(db.Integer, db.ForeignKey('utenti.idutente'))


class Ordini(db.Model):
    __tablename__ = 'ordini'

    idordine = db.Column(db.Integer, primary_key = True)
    spedizione = db.Column(db.Text, nullable = False)
    metodo_di_pagamento = db.Column(db.Text, nullable = False)
    stato = db.Column(db.Text, nullable = False)

class Recensioni(db.Model):
    __tablename__ = 'recensioni'

    idrecensione = db.Column(db.Integer, primary_key = True)
    voto = db.Column(db.Integer, nullable = False)
    commento = db.Column(db.Text, nullable = False)
