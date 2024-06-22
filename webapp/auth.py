from io import BytesIO
from flask import Blueprint, jsonify, render_template, request, flash, redirect, send_file, url_for, request
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        utente = Utenti.query.filter_by(username = username).first() 
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
    
    indirizzo =  next((indirizzo for indirizzo in current_user.indirizzi_ass if indirizzo.isdefault), None)

    return render_template('profilo.html', utente = current_user, indirizzo = indirizzo)

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
    
    return render_template('prodotto.html', utente = current_user, prodotto = prodotto, request = request)


@auth.route('/aggcarrello/<int:idprodotto>', methods=['GET', 'POST'])
@login_required
def aggcarrello(idprodotto):
    prodotto = Prodotti.query.get_or_404(idprodotto)

    
    carrello_prodotto = CarrelloProdotto.query.filter_by(idu=current_user.idutente, idp=idprodotto).first()

    if prodotto.quantità <= 0:
        flash(f'Il prodotto "{prodotto.nome}" non è disponibile in quantità sufficiente.', 'error')
        return redirect(url_for('auth.prodotto', idprodotto=idprodotto))
 
    if carrello_prodotto:
        
        carrello_prodotto.quantità += 1
        flash(f'Quantità di "{prodotto.nome}" nel carrello: {carrello_prodotto.quantità}', 'success')
    else:
        
        carrello_prodotto = CarrelloProdotto(idu=current_user.idutente, idp=idprodotto, quantità=1)
        db.session.add(carrello_prodotto)
        flash(f'Prodotto "{prodotto.nome}" aggiunto al carrello!', 'success')

    db.session.commit()
    return redirect(url_for('auth.prodotto', idprodotto=idprodotto))


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

    categoria_padre = Categorie.query.filter_by(idcategoria=idcategoria).first() 

    categorie_ids = [idcategoria]
    
    if categoria_padre.idgenitore is None: 
        categorie_figlie = Categorie.query.filter_by(idgenitore=idcategoria).all()
        prodotti = Prodotti.query.filter(Prodotti.idc.in_([c.idcategoria for c in categorie_figlie])).all()
        categorie_ids.extend([c.idcategoria for c in categorie_figlie])
        
    else: 
        prodotti = Prodotti.query.filter(Prodotti.idc == idcategoria).all()  
        categorie_figlie = Categorie.query.filter_by(idgenitore=idcategoria).all()
    
    
    search = request.args.get('search')
    selected_categoria = request.args.get('categoria')
    """
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
    
    return render_template("homeprodot.html", utente = current_user, prodotti=prodotti, categorie = categorie, idcategoria = idcategoria, categorie_figlie=categorie_figlie, request = request)
    """
    sort_by = request.args.get('sort_by')
    min_cost = request.args.get('min_cost')
    max_cost = request.args.get('max_cost')

    prodotti_query = Prodotti.query.filter(Prodotti.idc.in_(categorie_ids))

    if search:
        prodotti_query = prodotti_query.filter(Prodotti.nome.ilike(f'%{search}%'))

    if selected_categoria:
        sottocategorie_ids = get_all_subcategories(selected_categoria)
        sottocategorie_ids.append(selected_categoria)  
        prodotti_query = prodotti_query.filter(Prodotti.idc.in_(sottocategorie_ids))

    if min_cost:
        prodotti_query = prodotti_query.filter(Prodotti.costo >= min_cost)

    if max_cost:
        prodotti_query = prodotti_query.filter(Prodotti.costo <= max_cost)

    if sort_by:
        if sort_by == 'nome':
            prodotti_query = prodotti_query.order_by(Prodotti.nome.asc())
        elif sort_by == 'costo':
            prodotti_query = prodotti_query.order_by(Prodotti.costo.asc())
    
    prodotti = prodotti_query.all()

    categorie = Categorie.query.filter(Categorie.idgenitore.is_(None)).all()

    return render_template("homeprodot.html", utente=current_user, prodotti=prodotti, categorie=categorie, idcategoria=idcategoria, categorie_figlie=categorie_figlie, request=request)
    
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
        idgenitore = request.form.get('idgenitore') 

        if idgenitore == '':
            idgenitore = None

        
        nuova_categoria = Categorie(nome=nome, immagine=immagine.read(), idgenitore=idgenitore)

       
        db.session.add(nuova_categoria)
        db.session.commit()

        flash('Categoria aggiunta!', category='success')
        return redirect(url_for('auth.aggcategoria'))
    
    
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
    tax = subtotal /10  
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

   
    carrello = CarrelloProdotto.query.filter_by(idu=current_user.idutente).first()

    if not carrello:
        flash('Il carrello dell\'utente è vuoto.', 'error')
        return redirect(url_for('auth.carrello'))

  
    nuovo_ordine = Ordini( 
        metodo_di_pagamento='metodo_scelto_dall_utente',  
        idcp = carrello.idcp,
        completato = False 
    )


    try:
        
        db.session.add(nuovo_ordine)
        db.session.commit()
        flash('Ordine creato con successo!', 'success')

    except Exception as e:
        db.session.rollback()
        flash('Si è verificato un errore durante la creazione dell\'ordine.', 'error')
        return redirect(url_for('auth.carrello'))


    return redirect(url_for('auth.controllo_ordini', idordine = nuovo_ordine.idordine))



@auth.route('/controllo_ordini/<int:idordine>', methods=['GET', 'POST']) 
@login_required
def controllo_ordini(idordine): 
     
    ordine = Ordini.query.get_or_404(idordine)

    indirizzo = next((indirizzo for indirizzo in current_user.indirizzi_ass if indirizzo.isdefault), None)
    
    
    carrello_prodotti = CarrelloProdotto.query.filter_by(idu=current_user.idutente).all()

  
    subtotal = sum(item.prodotto.costo * item.quantità for item in carrello_prodotti)

    
    tax = subtotal / 10

    
    grand_total = subtotal + tax

    totquantità = sum(item.quantità for item in carrello_prodotti) 

    return render_template('controllo_ordini.html', ordine=ordine, carrello_prodotti=carrello_prodotti, tax=tax, grand_total=grand_total, utente=current_user, totquantità = totquantità, indirizzo=indirizzo)



@auth.route('/completamento_ordine/<int:idordine>')
@login_required
def completamento_ordine(idordine):
    
    ordine = Ordini.query.get_or_404(idordine)

    carrello_prodotti = CarrelloProdotto.query.filter_by(idu=current_user.idutente).all()

    print(f"Trovati {len(carrello_prodotti)} prodotti nel carrello per l'ordine {ordine.idordine}")

    for item in carrello_prodotti:
        print(f"Processing item: {item.prodotto.nome}, Quantity: {item.quantità}, Cost: {item.prodotto.costo}")
        print(item.idp)
        storico = Storici(
            idor=ordine.idordine,
            idpr=item.prodotto.idprodotto,
            idu=current_user.idutente,
            qta=item.quantità,
            pagato=item.prodotto.costo,  
            consegna = False
        )

        db.session.add(storico)
    
        prodotto = Prodotti.query.get(item.idp)
        if prodotto:
            prodotto.quantità -= item.quantità  
    

    ordine.idcp = None
    CarrelloProdotto.query.filter_by(idu=current_user.idutente).delete() 
    
    db.session.commit()

    flash("Ordine completato con successo!", "success")
    return redirect(url_for('auth.storico_ordini', utente = current_user))


"""
@auth.route('/storico', methods=['GET'])
@login_required
def storico_ordini():

    ordini = (
        Storici.query
        .filter_by(idu=current_user.idutente)
        .all()
    )

    return render_template('storico.html', ordini=ordini, utente = current_user)
"""
    
@auth.route('/storico', methods=['GET'])
@login_required
def storico_ordini():
    # Trova tutti i record dello storico per l'utente corrente
    storici = Storici.query.filter_by(idu=current_user.idutente).all()

    # Dizionario per mappare ogni ordine ai suoi prodotti
    ordini_e_prodotti = {}
    for storico in storici:
        ordine_id = storico.idor
        prodotto = Prodotti.query.get(storico.idpr)
        ordine = Ordini.query.get(ordine_id)  # Assuming you have an Ordini model to get the order details

        prodotto_info = {
            'nome': prodotto.nome,
            'costo': prodotto.costo,
            'consegna': storico.consegna,
            'qta': storico.qta,
            'dataordine': ordine.dataordine  # Assuming ordine has a dataordine attribute
        }

        if ordine_id in ordini_e_prodotti:
            ordini_e_prodotti[ordine_id]['prodotti'].append(prodotto_info)
        else:
            ordini_e_prodotti[ordine_id] = {
                'dataordine': ordine.dataordine,
                'prodotti': [prodotto_info]
            }

    return render_template('storico.html', ordini=ordini_e_prodotti, utente=current_user)




@auth.route('/oggetti_venduti', methods=['GET', 'POST'])
@login_required
def oggetti_venduti():
    # Recupera tutti i prodotti dell'utente corrente
    prodotti_utente = Prodotti.query.filter_by(idu=current_user.idutente).all()
    
    # Dizionario per mappare ogni ordine ai suoi prodotti venduti
    ordini_e_prodotti = {}

    # Trovare tutti gli storici che contengono i prodotti dell'utente
    for prodotto in prodotti_utente:
        storici_prodotto = Storici.query.filter_by(idpr=prodotto.idprodotto).all()
        for storico in storici_prodotto:
            ordine_id = storico.idor
            # Se l'ordine è già nel dizionario, aggiungi il prodotto alla lista dei prodotti di quell'ordine
            if ordine_id in ordini_e_prodotti:
                ordini_e_prodotti[ordine_id][1].append((prodotto, storico.consegna))
            else:
                # Recupera l'ordine completo
                ordine_completo = Ordini.query.get(ordine_id)
                # Aggiungi una nuova chiave (ordine) con una lista contenente il prodotto
                ordini_e_prodotti[ordine_id] = (ordine_completo, [(prodotto, storico.consegna)])

    # Converte il dizionario in una lista di tuple per facilitarne l'iterazione nel template
    ordini_e_prodotti_lista = list(ordini_e_prodotti.values())

    # Rende il template 'oggetti_venduti.html' con le informazioni necessarie
    return render_template('oggetti_venduti.html', utente=current_user, ordini_e_prodotti=ordini_e_prodotti_lista)




@auth.route('/consegna_prodotto/<int:ordine_id>/<int:prodotto_id>', methods=['POST'])
@login_required
def consegna_prodotto(ordine_id, prodotto_id):
    storico = Storici.query.filter_by(idor=ordine_id, idpr=prodotto_id).first()
    if storico:
        storico.consegna = True
        db.session.commit()
        flash('Prodotto consegnato con successo!', 'success')
    else:
        flash('Prodotto non trovato.', 'danger')
    return redirect(url_for('auth.oggetti_venduti'))

@auth.route('/annulla_prodotto/<int:ordine_id>/<int:prodotto_id>', methods=['POST'])
@login_required
def annulla_prodotto(ordine_id, prodotto_id):
    storico = Storici.query.filter_by(idor=ordine_id, idpr=prodotto_id).first()
    if storico:
        prodotto = Prodotti.query.filter_by(idprodotto=prodotto_id).first()
        prodotto.quantità += storico.qta
        db.session.delete(storico)
        db.session.commit()
        flash('Prodotto annullato con successo!', 'success')
    else:
        flash('Prodotto non trovato.', 'danger')
    return redirect(url_for('auth.oggetti_venduti'))
