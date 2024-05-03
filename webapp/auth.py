from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    return render_template("login.html")


@auth.route('/logout')
def logout():
    return "<p>Logout</p>"

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method=='POST':
        nome = request.form.get('nome')
        cognome = request.form.get('cognome')
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(nome) < 2:
            flash('First Name must be greater than 1 characters.', category='error')
        elif password1 != password2:
            flash('Passwords dont\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_utente = Utenti(nome = nome, cognome = cognome, username = username, email = email, password_hash = generate_password_hash(password1), privilegi = True)
            db.session.add(new_utente)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

            
    return render_template("sign_up.html")


@auth.route('/sign-in')
def sign_in():
    return "<p>sign_in</p>"
    