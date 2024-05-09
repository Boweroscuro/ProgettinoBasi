from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        utente = Utenti.query.filter_by(username = username).first() #per fare query semplici
        if utente:
            if check_password_hash(utente.password_hash, password):
                flash('Utente autenticato!', category = 'success')
                login_user(utente, remember = True)
                return redirect(url_for('views.home'))
            else:
                flash('Password errata. Riprova', category='error')
        else:
            flash('Username non trovato.', category='error')

    return render_template("login.html", utente = current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method=='POST':
        nome = request.form.get('nome')
        cognome = request.form.get('cognome')
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        privilegi = request.form.get('privilegi')
        
        privilegi = True if request.form.get('privilegi') == 'venditore' else False

        utente = Utenti.query.filter_by(username = username).first()
        if utente:
            flash('Questo username esiste già.', category='error')
        if len(email) < 4:
            flash('Email deve essere più di 4 caratteri', category='error')
        elif len(nome) < 2:
            flash('Nome deve essere più di 1 carattere', category='error')
        elif len(cognome) < 2:
            flash('Cognome deve essere più di 1 carattere', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            utente = Utenti(nome = nome, cognome = cognome, username = username, email = email, password_hash = generate_password_hash(password1), privilegi = privilegi, indirizzo_ass = [])
            db.session.add(utente)
            db.session.commit()
            return redirect(url_for('auth.sign_up2' , user_id = utente.idutente))

    return render_template("sign_up.html", utente=current_user)

@auth.route('/sign_up2', methods=['GET', 'POST'])
def sign_up2():
    if request.method == 'POST':
        via = request.form.get('via')
        numero = request.form.get('numero')
        cap = request.form.get('cap')
        citta = request.form.get('citta')
        user_id = request.args.get('user_id')

        n_utente = Utenti.query.filter_by(idutente = user_id).first()

        indirizzo = Indirizzi(via=via, numero=numero, cap=cap, città = citta)
        indirizzo.utente_ass.append(n_utente)
        db.session.add(indirizzo)
        db.session.commit()
        
        login_user(n_utente, remember = True)
        flash('Account created!', category='success')
        return redirect(url_for('views.home'))

    return render_template('sign_up2.html', utente = current_user)

@auth.route('/hvenditori', methods=['GET', 'POST'])
@login_required
def hvenditori():

    prodotti = Prodotti.query.filter_by(idu=current_user.idutente).all()
    
    return render_template('hvenditori.html', utente=current_user, prodotti = prodotti)

@auth.route('/prodotto/<int:idprodotto>')
@login_required
def prodotto(idprodotto):

    prodotto = Prodotti.query.get_or_404(idprodotto)
    
    return render_template('prodotto.html', utente = current_user, prodotto = prodotto)


@auth.route('/aggprodotto', methods=['GET', 'POST'])
@login_required
def aggprodotto():
    if request.method == 'POST':
        nome = request.form.get('nome')
        costo = request.form.get('costo')
        descrizione = request.form.get('descrizione')
        quantità = request.form.get('quantità')
        immagine = request.args.get('immagine')
        marca = request.form.get('marca')
        
        prodotto = Prodotti(nome=nome, costo=costo, descrizione=descrizione, quantità = quantità, marca=marca, idu = current_user.idutente)
      
        db.session.add(prodotto)
        db.session.commit()
        
        flash('Prodotto aggiunto!', category='success')
        return redirect(url_for('auth.hvenditori' , utente=current_user))

    return render_template('aggprodotto.html', utente = current_user)
