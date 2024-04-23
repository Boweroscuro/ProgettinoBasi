from app import db

class Utenti(db.Model):
    __tablename__ = 'utenti'

    idutente = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.Text, nullable = False)
    cognome = db.Column(db.Text, nullable = False)
    username = db.Column(db.Text, nullable = False)
    email = db.Column(db.Text, nullable = False)
    password_hash = db.Column(db.Text, nullable= False)
    privilegi = db.Column(db.Boolean)

    def __repr__(self):
        return f'Utente con id {self.idutente}, nome {self.nome}, cognome {self.cognome}'

########################################################################################
"""
class Indirizzi(db.Model):
    __table__ = 'Indirizzi'

    id_indirizzo = db.Column(db.Integer, primary_key = True)
    indirizzo = db.Column(db.Text, nullable = False)
    numero = db.Column(db.Integer, nullable= False)
    città = db.Column(db.Text, nullable = False)
    cap = db.Column(db.Integer, nullable= False)
    stato = db.Column(db.Text, nullable = False)

    def __repr__(self):
        return f'Indirizzo con id {self.id_indirizzo}, indirizzo {self.indirizzo}, numero {self.numero}'

"""