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
from flask_migrate import Migrate
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
migrate = Migrate(app, db)

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
        cal = db.Column(db.String(100))
        training = db.Column(db.String(100))
        times=db.Column(db.String(100))


    class Cardio( db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name=db.Column(db.String(100))
        video=db.Column(db.String(1000))
        gif=db.Column(db.String(1000))
        trainer_name=db.Column(db.String(100))
        description=db.Column(db.String(1000))
    class Back( db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name=db.Column(db.String(100))
        video=db.Column(db.String(1000))
        gif=db.Column(db.String(1000))
        trainer_name=db.Column(db.String(100))
        description=db.Column(db.String(1000))
    class Crossfit( db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name=db.Column(db.String(100))
        video=db.Column(db.String(1000))
        gif=db.Column(db.String(1000))
        trainer_name=db.Column(db.String(100))
        description=db.Column(db.String(1000))
    class Power_lifting( db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name=db.Column(db.String(100))
        video=db.Column(db.String(1000))
        gif=db.Column(db.String(1000))
        trainer_name=db.Column(db.String(100))
        description=db.Column(db.String(1000))




    db.create_all()


class MyModelView(ModelView):
    def is_accessible(self):
            return True

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Back, db.session))
admin.add_view(MyModelView(Crossfit, db.session))
admin.add_view(MyModelView(Power_lifting, db.session))
admin.add_view(MyModelView(Cardio, db.session))
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
        sender_email = 'ibrahimfakhreyams@gmail.com'  # Your Gmail address
        app_password = 'qszc jcyr amyi vckn'  # The app password generated in step 2

        subject = 'confirmation from add fit '
        body = f' we are glade to  have anew client like you , HI{ name } your subscription starts from {datetime.now()} it will end {new_user.due_Date} you can enjoy all our products from this moment '

        # Set up the MIME
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = request.form.get("email")
        message['Subject'] = subject

        # Attach the body to the email
        message.attach(MIMEText(body, 'plain'))

        # Connect to Google's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            # Log in using your Gmail credentials
            server.login(sender_email, app_password)
            # Send the email
            server.sendmail(sender_email, request.form.get("email"), message.as_string())



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
@app.route("/forget",methods=["GET","POST"])
def forget():
    if request.method =="POST":
        email=request.form.get("email")
        user=User.query.filter_by(email=email).first()
        if user:
            sender_email = 'ibrahimfakhreyams@gmail.com'  # Your Gmail address
            app_password = 'qszc jcyr amyi vckn'  # The app password generated in step 2

            subject = 'confirmation from add fit '
            link=f"http://127.0.0.1:5000/resetpassword/{user.id}"

            body = f"to reset the password click in this link{link}"

            # Set up the MIME
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = request.form.get("email")
            message['Subject'] = subject

            # Attach the body to the email
            message.attach(MIMEText(body, 'plain'))

            # Connect to Google's SMTP server
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                # Log in using your Gmail credentials
                server.login(sender_email, app_password)
                # Send the email
                server.sendmail(sender_email, request.form.get("email"), message.as_string())
            return "email sent successfully "
    return render_template("reset.html")
@app.route("/resetpassword/<int:user_id>",methods=["GET","POST"])
def resetpassword(user_id):
    if request.form=="POST":

        target= User.query.filter_by(id=user_id).first()
        if target:

            target.password=request.form.get("password")
            db.session.commit()
            return redirect("/login")
    return render_template("password.html")


@app.route("/training")
def training():
    return render_template("class.html")
@app.route("/training_description/<name>")
def des(name):
    target=None
    if name=="Cardio":
        target=Cardio.query.all()


    return render_template("des.html",target=target)
if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)