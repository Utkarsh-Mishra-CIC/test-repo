# import the Flask class from the flask module
from flask import Flask, render_template, redirect, \
    url_for, request, session, flash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required , logout_user, current_user
from forms import LoginForm, RegisterForm, MessageForm
import os

# create the application object, pass it into Bcrypt for hashing
app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

# config
app.config.from_object('config.DevelopmentConfig')

# create the sqlalchemy object
db = SQLAlchemy(app)

# import db schema
from models import *

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

# # login required decorator
# def login_required(f):
#     @wraps(f)
#     def wrap(*args, **kwargs):
#         if 'logged_in' in session:
#             return f(*args, **kwargs)
#         else:
#             flash('You need to login first.')
#             return redirect(url_for('login'))
#     return wrap


# use decorators to link the function to a url
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    error = None
    form = MessageForm(request.form)
    if form.validate_on_submit():
        new_message = BlogPost(
            form.title.data,
            form.description.data,
            current_user.id
        )
        db.session.add(new_message)
        db.session.commit()
        flash('New entry was successfully posted. Thanks.')
        return redirect(url_for('home'))
    else:
        posts = db.session.query(BlogPost).all()
        return render_template('index.html', posts=posts, form = form, error = error)  # render a template


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template


# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            print('iamhere2')
            user = User.query.filter_by(name = request.form['username']).first()
            if user is not None and bcrypt.check_password_hash(user.password,request.form['password']):
            # if (request.form['username'] != 'admin') or request.form['password'] != 'admin':
                # session['logged_in'] = True
                login_user(user)
                flash('You were logged in.')
                return redirect(url_for('home'))
            else:
                error = 'Invalid username or password.'
    return render_template('login.html',form = form, error=error)


@app.route('/logout')
@login_required
def logout():
    # session.pop('logged_in', None)
    logout_user()
    flash('You were logged out.')
    return redirect(url_for('welcome'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))