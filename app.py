# import the Flask class from the flask module
from flask import Flask, render_template, redirect, \
    url_for, request, session, flash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user,logout_user, current_user#, login_required
from forms import *
import os
import re

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
    return User.query.filter(User.uid == int(user_id)).first()

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in session and session['user'] != 'Admin':
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in session and session['user'] == 'Admin':
            return f(*args, **kwargs)
        else:
            flash('Admin need to login first.')
            return redirect(url_for('admin'))
    return wrap

# use decorators to link the function to a url
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    error = None
    print(request.headers)
    form = ReportForm(request.form,csrf_enabled = False)
    if form.validate_on_submit():
        new_report = Report(
            form.eid.data,
            form.report.data,
            current_user.uid
        )
        db.session.add(new_report)
        db.session.commit()
        flash('New entry was successfully posted. Thanks.')
        return redirect(url_for('home'))
    else:
        posts = db.session.query(Report).filter_by(uid=current_user.uid).all()
        usertype = current_user.usertype
        return render_template('index.html', posts=posts,usertype = usertype, form = form, error = error)  # render a template

@app.route('/admin/home', methods=['GET', 'POST'])
@admin_required
def admin_home():
    error = None
    print(request.headers)
    form = AdminListForm(request.form, csrf_enabled = False)
    admin = db.session.query(User).filter_by(username='Admin').first()
    all_users = db.session.query(User).filter(User.username!='Admin').all()
    admin_row_form = SuperAdminRowForm()
    admin_row_form.email = admin.email
    admin_row_form.uid = admin.uid
    admin_row_form.username = admin.username
    admin_row_form.gender = admin.gender
    admin_row_form.usertype = admin.usertype
    form.admin_user.append_entry(admin_row_form)
    for user in all_users:
        user_form = AdminRowForm()
        user_form.email = user.email
        user_form.uid = user.uid
        user_form.username = user.username
        user_form.gender = user.gender
        user_form.usertype = user.usertype
        form.users.append_entry(user_form)
    if request.method == 'POST':
        my_list = []
        my_other_list = []
        if request.form.get('admin_user-0-uid_admin') == 'admin_user-0-uid_admin':
            return redirect(url_for('pass_reset',uid = 1))
        else:
            for key in request.form:
                m = re.match("^users-[0-9]+-uid_user$",key)
                n = re.match("^users-[0-9]+-uid_user_delete$",key)
                if m:
                    my_list.append(key)
                if n:
                    my_other_list.append(key)
            for key in my_list:
                if request.form.get(key) == key:
                    # user_id = re.findall(r'\d+', key)
                    user_id = [int(s) for s in key.split('-') if s.isdigit()]
                    return redirect(url_for('pass_reset',uid = user_id[0]+2))
            for key in my_other_list:
                if request.form.get(key) == key:
                    user_id = [int(s) for s in key.split('-') if s.isdigit()]
                    return redirect(url_for('user_delete',uid = user_id[0]+2))
    return render_template('admin_index.html',form=form,error=error)

@app.route('/admin/home/usertype/update/<int:uid>/<type_user>',methods=['GET','POST'])
@admin_required
def usertype_update(uid,type_user):
    user = User.query.filter_by(uid = uid).first()
    user.usertype = type_user
    db.session.commit()
    return redirect(url_for('admin_home'))

@app.route('/admin/home/<int:uid>/reset', methods=['GET','POST'])
@admin_required
def pass_reset(uid):
    error = None
    form = ResetPassword(request.form, csrf_enabled = False)
    user = User.query.filter_by(uid = uid).first()
    username = user.username
    if request.method == 'POST':
        if form.validate_on_submit():
            user.password = bcrypt.generate_password_hash(request.form['password'])
            db.session.commit()
            return redirect(url_for('admin_home'))
    return render_template('reset.html',form = form, error = error, username = username, uid = uid)

@app.route('/report/<int:rid>', methods=['GET','POST'])
@login_required
def report_review(rid):
    report = Report.query.filter_by(rid = rid).first()
    exercise_name = get_exercise_name(report.eid)
    user_name = User.query.filter_by(uid = report.uid).first().username
    print(report.report)
    return render_template('report.html',report = report, ename = exercise_name, username = user_name)

def get_exercise_name(eid):
    exercise_names = ["KnobEx","TorqueEx","TorqueUDEx","pbdUGIBiopsyEx","pbdUGISnareEx","pbdUGIExamEx"]
    enumerated_ename = [[i,exercise_names[i-1]] for i in range(1,len(exercise_names)+1)]
    for i in range(0,len(enumerated_ename)):
        if eid == enumerated_ename[i][0]:
            return enumerated_ename[i][1]

@app.route('/admin/home/<int:uid>/delete', methods=['GET','POST'])
@admin_required
def user_delete(uid):
    User.query.filter_by(uid = uid).delete()
    db.session.commit()
    return redirect(url_for('admin_home'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error = None
    form = AdminForm(request.form, csrf_enabled = False)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username = 'Admin').first()
            if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
                session['user'] = 'Admin'
                login_user(user)
                flash('Admin has logged in!!')
                return redirect(url_for('admin_home'))
            else:
                error = 'Invalid password for Admin'
    return render_template('admin_login.html',form = form, error = error)

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template


# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form, csrf_enabled = False)
    if request.method == 'POST':
        if form.validate_on_submit():
            if (request.form['username'] != 'Admin'):
                user = User.query.filter_by(username = request.form['username']).first()
                if user is not None and bcrypt.check_password_hash(user.password,request.form['password']):
                    # if (request.form['username'] != 'admin') or request.form['password'] != 'admin':
                    session['user'] = request.form['username']
                    login_user(user)
                    flash('You were logged in.')
                    return redirect(url_for('home'))
            else:
                error = "Invalid username or password"
        else:
            error = 'Invalid username or password.'
    return render_template('login.html',form = form, error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    logout_user()
    flash('You were logged out.')
    return redirect(url_for('welcome'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(gender = '' ,usertype = 'Trainee', csrf_enabled = False)
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            gender=form.gender.data,
            usertype=form.usertype.data
        )
        db.session.add(user)
        db.session.commit()
        session['user'] = form.username.data
        login_user(user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))