import flask_login
#import flask_loginmanager
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from flask_mongoengine import mongoengine
from flask_wtf import FlaskForm, Form
from wtforms import RadioField
from wtforms.validators import DataRequired
from flask_login import UserMixin, LoginManager
from wtforms import Form, BooleanField, StringField, PasswordField, IntegerField, validators, DateTimeField, DecimalField, FileField, SubmitField, SelectField, DateField
from wtforms.validators import ValidationError, Length, EqualTo, InputRequired, Email, DataRequired
from flask_wtf.file import FileField, FileRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, logout_user, login_manager, LoginManager, current_user, user_logged_out, user_logged_in, login_required, logout_user
from flask_mongoengine import MongoEngine, Document
import flask
#from flask_loginmanager import LoginManager
from flask_login import LoginManager
from flask_mongoengine.wtf import model_form
from werkzeug.utils import secure_filename
import os
import urllib.request
import hashlib

app = Flask("__name__")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'NSH'
app.config['MONGODB_SETTINGS'] = {
    'db': 'Car',
    'host': 'localhost',
    'port': 27017
}
app.config['SESSION_MONGODB'] = MongoEngine
Session(app)
db = MongoEngine()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Users(db.Document, UserMixin):
    name = db.StringField(required=True)
    email = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    phone = db.IntField(required=True)
    gender = db.StringField(required=True)
    age = db.IntField(required=True)
    Licence = db.ImageField()

class Booking(db.Document):
    carId = db.StringField(required=True)
    from_date = db.DateField(required=True)
    to_date = db.DateField(required=True)

class HomeForm(FlaskForm):
    name = StringField('What is your name?')
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    name = StringField('User name', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)])
    password2 = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    phone = IntegerField('Phone Number', validators=[InputRequired()])
    age = IntegerField('Age', validators=[InputRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[InputRequired()])
    licence = FileField('Licence Image')


class ImageForm(FlaskForm):
    images = [FileField('Image %d' % i) for i in range(1, 4)]

class BookingForm(FlaskForm):
    carId = StringField('Car ID', validators=[DataRequired()])
    from_date = DateField('Start Date', validators=[DataRequired()])
    to_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
@login_manager.user_loader
def load_user(user_id):
    return Users.objects(pk=user_id).first()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    form = RegisterForm()
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('home.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.objects(name=form.name.data).first()
        if user is not None:
            if user.password == form.password.data:
                login_user(user)
                session['name'] = form.name.data
                flash(f'Welcome, {user.name}! You have been logged in to SaHi Car Rentals successfully.')
                return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = Users(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
            phone=form.phone.data,
            gender=form.gender.data,
            age=form.age.data,
            Licence=request.files['licence']
        )
        user.save()
        session['email'] = form.email.data
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/display_cars', methods=['GET', 'POST'])
@login_required
def display_cars():
    form = ImageForm()
    return render_template('display_cars.html', form=form)

@app.route('/add_booking', methods=['GET', 'POST'])
@login_required
def add_booking():
    form = BookingForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.validate_on_submit():
            booking = Booking(carId=form.carId.data, from_date=form.from_date.data, to_date=form.to_date.data)
            booking.save()
            session['booking_id'] = str(booking.id)
            flash('Booking successful!')
        return redirect(url_for('index'))
    return render_template('add_booking.html', form=form)


@app.route('/logout', methods = ['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)




