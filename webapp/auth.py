from io import BytesIO
from flask import Blueprint, jsonify, render_template, request, flash, redirect, send_file, url_for
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
            utente = Utenti(nome = nome, cognome = cognome, username = username, email = email, password_hash = generate_password_hash(password1), privilegi = privilegi, indirizzo_ass = [], isadmin = False)
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

        indirizzo = Indirizzi(via=via, numero=numero, cap=cap, città = citta, isdefault = True)
        indirizzo.utente_ass.append(n_utente)
        db.session.add(indirizzo)
        db.session.commit()
        
        login_user(n_utente, remember = True)
        flash('Account creato!', category='success')
        return redirect(url_for('views.home'))

    return render_template('sign_up2.html', utente = current_user)

@auth.route('/aggiungi_indirizzo', methods=['GET', 'POST'])
@login_required 
def aggiungi_indirizzo():
    if request.method == 'POST':
        via = request.form.get('via')
        numero = request.form.get('numero')
        cap = request.form.get('cap')
        citta = request.form.get('citta')

        indirizzo = Indirizzi(via=via, numero=numero, cap=cap, città = citta, isdefault = False)
        indirizzo.utente_ass.append(current_user)
        db.session.add(indirizzo)
        db.session.commit()
        
        flash('Indirizzo aggiunto!', category='success')
        return redirect(url_for('auth.aggiungi_indirizzo'))

    return render_template('aggiungi_indirizzo.html', utente = current_user)


@auth.route('/profilo')
@login_required  
def user_profile():
    return render_template('profilo.html', utente = current_user)

@auth.route('/hvenditori', methods=['GET', 'POST'])
@login_required
def hvenditori():

    prodotti = Prodotti.query.filter_by(idu=current_user.idutente).all()
    
    return render_template('hvenditori.html', utente=current_user, prodotti = prodotti)

@auth.route('/eliminaprodotto/<int:idprodotto>', methods=['POST'])
@login_required
def eliminaprodotto(idprodotto):
    prodotto = Prodotti.query.get_or_404(idprodotto)
    if prodotto.idu != current_user.idutente:
        flash('Non sei autorizzato a eliminare questo prodotto.', category='error')
        return redirect(url_for('auth.hvenditori'))
    
    db.session.delete(prodotto)
    db.session.commit()
    flash('Prodotto eliminato con successo.', category='success')
    return redirect(url_for('auth.hvenditori'))

@auth.route('/immagine/<int:idprodotto>')
def get_immagine(idprodotto):
    prodotto = Prodotti.query.get_or_404(idprodotto)
    return send_file(BytesIO(prodotto.immagine), mimetype='image/jpeg')

@auth.route('/prodotto/<int:idprodotto>')
@login_required
def prodotto(idprodotto):

    prodotto = Prodotti.query.get_or_404(idprodotto)
    
    return render_template('prodotto.html', utente = current_user, prodotto = prodotto)

@auth.route('/aggcarrello/<int:idprodotto>', methods=['GET', 'POST'])
@login_required
def aggcarrello(idprodotto):
    prodotto = Prodotti.query.get_or_404(idprodotto)

    # Controlla se il prodotto è già nel carrello dell'utente
    carrello_prodotto = CarrelloProdotto.query.filter_by(idu=current_user.idutente, idp=idprodotto).first()

    if prodotto.quantità <= 0:
        flash(f'Il prodotto "{prodotto.nome}" non è disponibile in quantità sufficiente.', 'error')
        return redirect(url_for('auth.prodotto', idprodotto=idprodotto))
 
    if carrello_prodotto:
        # Se il prodotto è già nel carrello, incrementa la quantità
        carrello_prodotto.quantità += 1
        flash(f'Quantità di "{prodotto.nome}" nel carrello: {carrello_prodotto.quantità}', 'success')
    else:
        # Se il prodotto non è nel carrello, aggiungilo con quantità 1
        carrello_prodotto = CarrelloProdotto(idu=current_user.idutente, idp=idprodotto, quantità=1)
        db.session.add(carrello_prodotto)
        flash(f'Prodotto "{prodotto.nome}" aggiunto al carrello!', 'success')

    db.session.commit()
    return redirect(url_for('auth.prodotto', idprodotto=idprodotto))
    #return render_template('prodotto.html', utente = current_user, prodotto = prodotto)


@auth.route('/aggprodotto', methods=['GET', 'POST'])
@login_required
def aggprodotto():
    if request.method == 'POST':
        nome = request.form.get('nome')
        costo = request.form.get('costo')
        descrizione = request.form.get('descrizione')
        quantità = request.form.get('quantità')
        immagine = request.files['immagine']
        marca = request.form.get('marca')
        categoria = request.form.get('categoria') 
        sottocategoria = request.form.get('sottocategoria')

        error = False
        if not nome or len(nome) <= 2 or len(nome) > 30:
            flash('Il nome del prodotto deve essere compreso tra 2 e 30 caratteri', category='error')
            error = True
        if not descrizione or len(descrizione) > 100:
            flash('La descrizione deve contenere massimo 100 caratteri', category='error')
            error = True
        try:
            costo = float(costo)
            if costo <= 0:
                flash('Il costo deve essere un numero maggiore di zero', category='error')
                error = True
        except ValueError:
            flash('Il costo deve essere un numero valido', category='error')
            error = True
        if not quantità.isdigit() or int(quantità) <= 0:
            flash('La quantità deve essere un numero intero maggiore di zero', category='error')
            error = True
        else:
            quantità = int(quantità)

        categoria = Categorie.query.get(categoria)
        if not categoria:
            flash('Categoria non valida', category='error')
            error = True

        if not error:
            # Aggiungere il prodotto solo se non ci sono errori
            prodotto = Prodotti(
                immagine=immagine.read(), 
                nome=nome, 
                costo=costo, 
                descrizione=descrizione, 
                quantità=quantità, 
                marca=marca, 
                idu=current_user.idutente, 
                idc=sottocategoria)
            
            db.session.add(prodotto)
            db.session.commit()
            flash('Prodotto aggiunto!', category='success')
            return redirect(url_for('auth.hvenditori', utente=current_user))
        
    categorie = Categorie.query.filter(Categorie.idgenitore.is_(None)).all()

    return render_template('aggprodotto.html', utente = current_user, categorie=categorie)

@auth.route('/get_sottocategorie')
def get_sottocategorie():
    categoria_id = request.args.get('categoria_id')
    sottocategorie = Categorie.query.filter_by(idgenitore=categoria_id).all()
    sottocategorie_list = [{'id': s.idcategoria, 'nome': s.nome} for s in sottocategorie]
    return jsonify(sottocategorie=sottocategorie_list)


@auth.route('/homeprodot/<int:idcategoria>') 
@login_required
def homeprodot(idcategoria):

    categoria_padre = Categorie.query.filter_by(idcategoria=idcategoria).first()  # Ottieni la categoria corrente

    categorie_ids = [idcategoria]
    
    if categoria_padre.idgenitore is None:  # Se la categoria non ha un genitore, è una categoria principale
        categorie_figlie = Categorie.query.filter_by(idgenitore=idcategoria).all()
        prodotti = Prodotti.query.filter(Prodotti.idc.in_([c.idcategoria for c in categorie_figlie])).all()
        categorie_ids.extend([c.idcategoria for c in categorie_figlie])
        
    else:  # Se la categoria ha un genitore, è una sottocategoria
        prodotti = Prodotti.query.filter(Prodotti.idc == idcategoria).all()  # Mostra solo i prodotti della sottocategoria
        categorie_figlie = Categorie.query.filter_by(idgenitore=idcategoria).all()
    
    #da qui
    search = request.args.get('search')
    selected_categoria = request.args.get('categoria')

    prodotti_query = Prodotti.query.filter(Prodotti.idc.in_(categorie_ids))

    if search:
        # Esegui una ricerca generica per i prodotti che corrispondono al termine di ricerca
        prodotti_query = prodotti_query.filter(Prodotti.nome.ilike(f'%{search}%'))

    if selected_categoria:
        # Ottieni tutti gli ID delle sottocategorie nidificate sotto la categoria selezionata
        sottocategorie_ids = get_all_subcategories(selected_categoria)
        sottocategorie_ids.append(selected_categoria)  # Aggiungi anche la categoria selezionata stessa
        # Filtra i prodotti per l'ID della categoria selezionata e tutte le sue sottocategorie
        prodotti_query = prodotti_query.filter(Prodotti.idc.in_(sottocategorie_ids))

    prodotti = prodotti_query.all()
    
    # Nessuna ricerca specificata, mostra tutti i prodotti
    categorie = Categorie.query.filter(Categorie.idgenitore.is_(None)).all()
    
    return render_template("homeprodot.html", utente = current_user, prodotti=prodotti, categorie = categorie, idcategoria = idcategoria, categorie_figlie=categorie_figlie)

def get_all_subcategories(categoria_id):
    """ Ottieni tutti gli ID delle sottocategorie nidificate sotto la categoria specificata """
    sottocategorie_ids = []
    queue = [categoria_id]

    while queue:
        current_id = queue.pop(0)
        sottocategorie = Categorie.query.filter_by(idgenitore=current_id).all()
        for sottocategoria in sottocategorie:
            sottocategorie_ids.append(sottocategoria.idcategoria)
            queue.append(sottocategoria.idcategoria)

    return sottocategorie_ids


@auth.route('/aggcategoria', methods=['GET', 'POST'])
@login_required
def aggcategoria():
    if request.method == 'POST':
        nome = request.form.get('nome')
        immagine = request.files['immagine']
        idgenitore = request.form.get('idgenitore')  # Aggiunto per ottenere l'id del genitore dalla form

        if idgenitore == '':
            idgenitore = None

        # Creiamo una nuova istanza di Categorie
        nuova_categoria = Categorie(nome=nome, immagine=immagine.read(), idgenitore=idgenitore)

        # Aggiungiamo la nuova categoria al database
        db.session.add(nuova_categoria)
        db.session.commit()

        flash('Categoria aggiunta!', category='success')
        return redirect(url_for('auth.aggcategoria'))
    
    # Ottieni tutte le categorie principali per visualizzarle nella form
    categorie_principali = Categorie.query.all()

    return render_template('aggcategoria.html', utente=current_user, categorie_principali=categorie_principali)

@auth.route('/immaginecat/<int:idcategoria>')
def get_immagine_cat(idcategoria):
    categoria = Categorie.query.get_or_404(idcategoria)
    return send_file(BytesIO(categoria.immagine), mimetype='image/jpeg')

@auth.route('/carrello', methods=['GET', 'POST'])
def carrello():
    carrello_prodotti = db.session.query(CarrelloProdotto).filter_by(idu=current_user.idutente).all()
    subtotal = sum(item.prodotto.costo * item.quantità for item in carrello_prodotti)
    tax = subtotal /10  # Supponiamo una tassa del 10%
    grand_total = subtotal + tax
    return render_template('carrello.html',  utente=current_user, carrello_prodotti=carrello_prodotti, tax=tax, grand_total=grand_total)

@auth.route('/updatecart/<int:idprodotto>', methods=['POST'])
@login_required   
def updatecart(idprodotto):

    prodotto = Prodotti.query.get_or_404(idprodotto)
    carrello_prodotto = CarrelloProdotto.query.filter_by(idu=current_user.idutente, idp=idprodotto).first()
    nuova_quantita = int(request.form['quantità'])

    if nuova_quantita <= 0:
        flash('La quantità deve essere maggiore di zero.', 'error')
        return redirect(url_for('auth.carrello'))

    if nuova_quantita > prodotto.quantità:
        flash(f'Non ci sono abbastanza "{prodotto.nome}" disponibili in magazzino.', 'error')
        return redirect(url_for('auth.carrello'))
    
    
    carrello_prodotto.quantità = nuova_quantita
    db.session.commit()
    flash(f'Quantità di "{carrello_prodotto.prodotto.nome}" aggiornata a {nuova_quantita}', 'success')
    return redirect(url_for('auth.carrello'))

@auth.route('/deleteitem/<int:id>', methods=['GET'])
@login_required
def deleteitem(id):
    carrello_prodotto = CarrelloProdotto.query.get_or_404(id)
    nome_prodotto = carrello_prodotto.prodotto.nome
    db.session.delete(carrello_prodotto)
    db.session.commit()
    flash(f'Prodotto "{nome_prodotto}" rimosso dal carrello', 'success')
    return redirect(url_for('auth.carrello'))

@auth.route('/clearcart')
@login_required
def clearcart():
    CarrelloProdotto.query.filter_by(idu=current_user.idutente).delete()
    db.session.commit()
    flash('Carrello svuotato', 'success')
    return redirect(url_for('auth.carrello'))

"""
@auth.route('/updateordine/<int:idordine>', methods=['POST'])
def updateordine(idordine):
    ordine = Ordini.query.get_or_404(idordine)
    nuovo_stato = request.form.get('stato')
    if nuovo_stato:
        ordine.stato = nuovo_stato
        db.session.commit()
        flash('Stato dell\'ordine aggiornato con successo', 'success')
    else:
        flash('Errore durante l\'aggiornamento dello stato dell\'ordine', 'danger')
    return redirect(url_for('auth.controllo_ordini'))
"""
# Delete Order
@auth.route('/deleteordine/<int:idordine>', methods=['GET', 'POST'])
def deleteordine(idordine):
    ordine = Ordini.query.get_or_404(idordine)
    db.session.delete(ordine)
    db.session.commit()
    flash('Ordine eliminato con successo', 'success')
    return redirect(url_for('auth.carrello', idordine=ordine.idordine))





@auth.route('/checkout')
@login_required
def checkout():
    # Recupera il carrello dell'utente corrente (presumibilmente già autenticato)
    carrello = CarrelloProdotto.query.filter_by(idu=current_user.idutente).first()

    if not carrello:
        flash('Il carrello dell\'utente è vuoto.', 'error')
        return redirect(url_for('auth.carrello'))

    # Crea un nuovo ordine utilizzando i dati del carrello
    nuovo_ordine = Ordini( 
        metodo_di_pagamento='metodo_scelto_dall_utente',  # Sostituire con il metodo effettivo
        stato ='in_attesa',  # Stato iniziale dell'ordine
        idcp = carrello.idcp 
    )


    try:
        # Aggiungi l'ordine al database
        db.session.add(nuovo_ordine)
        db.session.commit()
        flash('Ordine creato con successo!', 'success')

    except Exception as e:
        db.session.rollback()
        flash('Si è verificato un errore durante la creazione dell\'ordine.', 'error')
        return redirect(url_for('auth.carrello'))


    return redirect(url_for('auth.controllo_ordini', idordine = nuovo_ordine.idordine))


# Controllo Ordini
@auth.route('/controllo_ordini/<int:idordine>', methods=['GET', 'POST']) 
@login_required
def controllo_ordini(idordine): 
     
    ordine = Ordini.query.get_or_404(idordine)

    indirizzo = Indirizzi.query.filter(
    Indirizzi.utente_ass.any(idutente=current_user.idutente),  # Filtra per l'utente corrente nella relazione many-to-many
    Indirizzi.isdefault == True  # Filtra per isdefault impostato a True
    ).first()
    
    # Filtra gli ordini per l'utente corrente utilizzando il campo idu nel modello CarrelloProdotto
    carrello_prodotti = CarrelloProdotto.query.filter_by(idu=current_user.idutente).all()

    # Calcola la somma dei subtotali
    subtotal = sum(item.prodotto.costo * item.quantità for item in carrello_prodotti)

    # Calcola la tassa (supponiamo il 10%)
    tax = subtotal / 10

    # Calcola il totale comprensivo di tassa
    grand_total = subtotal + tax

    totquantità = sum(item.quantità for item in carrello_prodotti) 

    return render_template('controllo_ordini.html', ordine=ordine, carrello_prodotti=carrello_prodotti, tax=tax, grand_total=grand_total, utente=current_user, totquantità = totquantità, indirizzo=indirizzo)

@auth.route('/storico')
@login_required
def storico_ordini():
    ordini = db.session.query(Ordini).filter_by(idu=current_user.idutente).all()
    return render_template('storico.html', ordini=ordini)