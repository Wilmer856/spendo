from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify
from flask_bcrypt import Bcrypt
from app import app
from forms import LoginForm, RegisterForm, UpdateUserForm, ChangePasswordForm, AddTransactionForm, ApplyFilterForm
from flask_login import login_required, login_user, logout_user, current_user
from models import db
from models import User, Transaction
from datetime import datetime
from sqlalchemy import cast, Date
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

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
            flash('Invalid username or password', "danger")
    return render_template("login.html", form = form, username=username, password=password) # pass in the data

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    #TODO Add transaction category when earning money
    #TODO Add final dashboard graphs
    form = AddTransactionForm()

    transactions = Transaction.query.filter(Transaction.user_id == current_user.id).all()

    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    total_balance = total_income - total_expenses

    current_month = datetime.now().strftime('%Y-%m')
    transactions_this_month = [
        t for t in transactions if t.date.strftime('%Y-%m') == current_month
    ]

    total_income_this_month = sum(t.amount for t in transactions_this_month if t.amount > 0)
    total_expenses_this_month = sum(abs(t.amount) for t in transactions_this_month if t.amount < 0)

    query = Transaction.query.filter(Transaction.user_id == current_user.id)
    query = query.order_by(Transaction.date.desc()).limit(5).all()

    for transaction in query:
        transaction.date = transaction.date.strftime('%Y/%m/%d')

    return render_template('dashboard.html', 
        form=form, 
        recent_transactions=query, total_balance=total_balance,
        total_income_this_month=total_income_this_month,
        total_expenses_this_month=total_expenses_this_month
    )


@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out!")
    return redirect(url_for('login'))

@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    #TODO Add default profile pic with Initials
    form = UpdateUserForm()
    password_form = ChangePasswordForm()

    if request.method == "POST":
        current_user.username = request.form["username"]
        current_user.email = request.form["email"]
        current_user.first_name = request.form["first_name"]
        current_user.last_name = request.form["last_name"]
        current_user.set_full_name()
        try:
            db.session.commit()
            flash("User updated successfully", "success")
            return render_template('profile.html', form=form, password_form=password_form)
        except:
            flash("Error: Looks like there was an issue updating your profile", "danger")
            return render_template('profile.html', form=form, password_form=password_form)
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    return render_template('profile.html', form = form, password_form=password_form)

@app.route('/profile/update_pass', methods=["POST"])
@login_required
def change_password():
    
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")

    if not current_password or not new_password:
        flash('Error: Missing required fields!', "danger")
        return redirect(url_for("profile"))
    
    if current_user and current_user.check_password(current_password):
        current_user.set_password(new_password)
        db.session.commit()
        flash("Password updated successfully!", "success")
    else:
        flash("Incorrect current password!", "danger")
    
    return redirect(url_for("profile"))


@app.route('/profile/delete', methods=["POST"])
@login_required
def delete_profile():

    if not current_user:
        flash("Error: No user is logged in")
        return redirect(url_for('login'))
    
    user_id = current_user.id
    user = User.query.get(user_id)

    if user:
        Transaction.query.filter_by(user_id=Transaction.user_id).delete()

        db.session.delete(user)
        db.session.commit()

        logout_user()
        flash("Your account has been deleted successfully", "success")

        return redirect(url_for('login'))
    
    flash("Error: User not found.", "danger")
    return redirect(url_for("profile"))


@app.route('/reports', methods=["GET", "POST"])
@login_required
def reports():
    #TODO Add Income vs Expenses since now we have that data
    transactions = Transaction.query.filter(Transaction.user_id == current_user.id, Transaction.amount < 0).all()
    df = pd.DataFrame([(t.category, abs(t.amount), t.date) for t in transactions], columns=["category", "amount", "date"])
    
    img_data = {}
    
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.strftime('%Y-%m')

        # Expenses by Category (Bar Chart)
        plt.figure(figsize=(6, 4))
        category_spending = df.groupby("category")["amount"].sum().reset_index()
        category_spending = category_spending.sort_values(by="amount", ascending=False)
        sns.barplot(data=category_spending, x="amount", y="category", palette="viridis")
        plt.xlabel("Total Spending ($)")
        plt.ylabel("Category")
        plt.title("Expenses by Category")

        buff = io.BytesIO()
        plt.savefig(buff, format='png', bbox_inches='tight')
        buff.seek(0)
        img_data["expenses_by_category"] = base64.b64encode(buff.read()).decode('utf-8')
        plt.close()
        buff.close()

        # Monthly Spending Trends (Line Chart)
        plt.figure(figsize=(6, 4))
        monthly_trends = df.groupby("date")["amount"].sum().reset_index()
        sns.lineplot(data=monthly_trends, x="date", y="amount", marker="o", color="blue")
        plt.xlabel("Month")
        plt.ylabel("Total Spending ($)")
        plt.title("Monthly Spending Trends")
        plt.xticks(rotation=45)

        buff = io.BytesIO()
        plt.savefig(buff, format='png', bbox_inches='tight')
        buff.seek(0)
        img_data["monthly_trends"] = base64.b64encode(buff.read()).decode('utf-8')
        plt.close()
        buff.close()

        # Top Spending Categories (Bar Chart)
        plt.figure(figsize=(6, 4))
        category_counts = df["category"].value_counts().reset_index()
        category_counts.columns = ["category", "count"]
        sns.barplot(data=category_counts, x="count", y="category", palette="coolwarm")
        plt.xlabel("Number of Transactions")
        plt.ylabel("Category")
        plt.title("# of Transactions by Category")

        buff = io.BytesIO()
        plt.savefig(buff, format='png', bbox_inches='tight')
        buff.seek(0)
        img_data["top_spending_categories"] = base64.b64encode(buff.read()).decode('utf-8')
        plt.close()
        buff.close()

    return render_template("reports.html", img_data=img_data)

@app.route('/transactions', methods=["GET", "POST"])
@login_required
def transactions():
    filter_form = ApplyFilterForm()

    page = request.args.get("page", 1, type=int)
    per_page = 5

    category = filter_form.category.data
    date = filter_form.date.data
    min_amount = filter_form.min_amount.data
    max_amount = filter_form.max_amount.data

    query = Transaction.query.filter(Transaction.user_id == current_user.id)

    # Apply filters only if form has values
    if category and category != "All":
        query = query.filter(Transaction.category == category)
    if date:
        query = query.filter(cast(Transaction.date, Date) == date)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)

    transactions_paginated = query.order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    for transaction in transactions_paginated.items:
        transaction.date = transaction.date.strftime('%Y/%m/%d')

    edit_forms = {}
    for transaction in transactions_paginated.items:
        form = AddTransactionForm(obj=transaction)
        form.amount.data = "{:.2f}".format(transaction.amount)
        form.category.data = transaction.category
        edit_forms[transaction.id] = form

    return render_template(
        "transactions.html",
        filter_form=filter_form,
        edit_forms=edit_forms,  # Pass dictionary of forms
        transactions_dict=transactions_paginated.items,
        pagination=transactions_paginated
    )
   
@app.route('/api/transactions', methods=["POST"])
@login_required
def add_transaction():
    category = request.form.get("category")
    amount = request.form.get("amount")

    try:
        transaction = Transaction(user_id=current_user.id, category=category, amount= amount, description = request.form.get('description', ''))
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('dashboard'))
    except:
        flash("Error adding new transaction!")
        return redirect(url_for('dashboard'))
    
@app.route('/api/transactions/edit/<int:transaction_id>', methods=["POST"])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    # Get updated values from form
    category = request.form.get("category")
    amount = request.form.get("amount")
    description = request.form.get("description")

    if category:
        transaction.category = category
    if amount:
        transaction.amount = float(amount)
    if description:
        transaction.description = description

    db.session.commit()
    flash("Transaction updated successfully!", "success")
    
    return redirect(url_for('transactions'))

@app.route('/api/transactions/delete/<int:transaction_id>', methods=["POST"])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    if transaction:
        db.session.delete(transaction)
        db.session.commit()

        flash("Transaction deleted successfully!", "success")
    
    return redirect(url_for('transactions'))