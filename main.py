import json
import os
from datetime import datetime, timedelta

import requests
from flask import Flask, render_template, redirect, url_for, flash, abort, request, current_app, jsonify, make_response, \
    Response


from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
import uuid

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # Check if user is in paid_user table
    user = User.query.get(int(user_id))
    if user:
        return user
    # If not, check if user is in free_user table

    # If user is not in either table, return None
    return None

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():


    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100), unique=True)
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        email = db.Column(db.String(100))
        role = db.Column(db.String(100), default="user")
        pay = db.Column(db.Boolean(), default=False)
        message = db.Column(db.String(1000))
        starting_day = db.Column(db.DateTime)
        due_Date = db.Column(db.DateTime)
        delegate = db.Column(db.DateTime)
        weight=db.Column(db.String(100))
        tall=db.Column(db.String(100))
        age=db.Column(db.String(100))
        health=db.Column(db.String(100))
        numbers=db.Column(db.String(100))
        member=db.Column(db.String(100))
        adress=db.Column(db.String(100))
    db.create_all()


class MyModelView(ModelView):
    def is_accessible(self):
            return True

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
@app.route("/")
def start():
    return render_template("index.html")
@app.route('/r', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get data from the form
        name = request.form.get('Name')
        phone = request.form.get('phone')
        gender = request.form.get('Gender')
        email = request.form.get('email')
        username = request.form.get('Username')
        password = request.form.get('Password')
        weight = request.form.get('weight')
        tall = request.form.get('tall')
        age = request.form.get('age')
        health_condition = request.form.get('health')
        subscription = request.form.get('monthly') or request.form.get('yearly')

        # Create a new User instance and set joining date to the current date
        new_user = User(
            name=name,
            phone=phone,
            password=password,
            email=email,
            weight=weight,
            tall=tall,
            age=age,
            health=health_condition,
            starting_day=datetime.now()
            # Add other fields as needed
        )

        # Calculate due date based on subscription type
        if subscription == 'monthly':
            new_user.due_Date = datetime.now() + timedelta(days=30)
        elif subscription == 'yearly':
            new_user.due_Date = datetime.now() + timedelta(days=365)

        db.session.add(new_user)
        db.session.commit()

        # Redirect to the login page after successful registration
        return redirect(url_for('login'))

    # If it's a GET request, render the registration form
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')

        user = User.query.filter_by(phone=phone).first()

        if user and user.password == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your phone and password.', 'error')
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
       if current_user.is_authenticated:
            # Render the dashboard for the authenticated user
             return render_template('dashboard.html')
       else:
            # Redirect to the login page if not authenticated
             return redirect(url_for('login'))
if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)