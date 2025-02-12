from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify
from flask_bcrypt import Bcrypt
from app import app
from forms import LoginForm, RegisterForm, UpdateUserForm
from flask_login import login_required, login_user, logout_user, current_user
from models import db
from models import User, Transaction

# Page not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

@app.route('/register', methods=['GET','POST'])
def register():
    username = None
    form = RegisterForm()
    if form.validate_on_submit(): #validate data when submitted
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            user = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
            password = form.password.data
            user.set_password(password)

            db.session.add(user)
            db.session.commit()
        else:
            print("User already exist")
        form.username.data = ''
        form.email.data = ''
        form.password.data = ''
        return redirect(url_for('login'))
    return render_template("register.html", form = form) # pass in the data

@app.route('/login', methods=['GET','POST'])
def login():
    username = None
    password = None
    form = LoginForm()
    if form.validate_on_submit(): # validate data when submitted
        username = form.username.data
        password = form.password.data
        session['username'] = username

        form.username.data = ''
        form.password.data = ''
        # Query the database to found if user exists
        user = User.query.filter_by(username = username).first()
        # Check if user exists and checks if entered password matches
        if user and user.check_password(password):
            flash("Login successful!", "success")
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template("login.html", form = form, username=username, password=password) # pass in the data

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out!")
    return redirect(url_for('login'))

@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateUserForm()
    if request.method == "POST":
        current_user.username = request.form["username"]
        current_user.email = request.form["email"]
        current_user.first_name = request.form["first_name"]
        current_user.last_name = request.form["last_name"]
        current_user.set_full_name()
        try:
            db.session.commit()
            flash("User updated successfully")
            return redirect(url_for('profile'))
        except:
            flash("Error: Looks like there was an issue updating your profile")
            return render_template('edit_profile.html')
    form.username.data = current_user.username#user_profile.username
    form.email.data = current_user.email#user_profile.email
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    return render_template('profile.html', form = form)

@app.route('/reports', methods=["GET", "POST"])
@login_required
def reports():
    return render_template("reports.html")

@app.route('/transactions', methods=["GET", "POST"])
@login_required
def transactions():
    return render_template("transactions.html")

@app.route('/api/transactions', methods=["GET"])
@login_required
def get_transactions():
    category = request.args.get('category')
    date = request.args.get('date')
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)

    query = Transaction.query.filter_by(Transaction.user_id == current_user.id)

    if category:
        query = query.filter(Transaction.category == category)
    if date:
        query = query.filter(db.func.date(Transaction.date) == date)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)

    transactions = query.all()
    return jsonify([t.to_dict() for t in transactions]), 200

@app.route('/transaction', methods=["POST"])
def add_transaction():
    data = request.json()
    if not data or 'category' in data or 'amount' not in data:
        return jsonify({'error': 'Missing required fields'})

    n_transaction = Transaction(user_id=current_user.id, category=request['category'], amount= request['amount'], description = request.get('description', ''))

    db.session.add(n_transaction)
    db.session.commit()
    return jsonify(n_transaction.to_dict()), 201