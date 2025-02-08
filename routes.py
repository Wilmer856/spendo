from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_bcrypt import Bcrypt
from app import app
from forms import LoginForm, RegisterForm, UpdateUserForm
from flask_login import login_required, login_user, logout_user
from models import db
from models import User

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
            user = User(username=form.username.data, email=form.email.data)
            password = form.password.data
            user.set_password(password)

            db.session.add(user)
            db.session.commit()
            username = form.username.data
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
    username = session.pop('username', None)
    return render_template('dashboard.html', username = username)


@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out!")
    return redirect(url_for('login'))

@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    return render_template('profile.html')

@app.route('/profile/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit_profile(id):
    #TODO Add validation to check if username or email is not taken
    form = UpdateUserForm()
    user_profile = User.query.get_or_404(id)
    if request.method == "POST":
        user_profile.username = request.form["username"]
        user_profile.email = request.form["email"]
        try:
            db.session.commit()
            flash("User updated successfully")
            return redirect(url_for('profile'))
        except:
            flash("Error: Looks like there was an issue updating your profile")
            return render_template('edit_profile.html')
    form.username.data = user_profile.username
    form.email.data = user_profile.email
    return render_template("edit_profile.html", form=form, user_profile=user_profile)
