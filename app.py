# import the Flask class from the flask module
from flask import Flask, render_template, redirect, \
    url_for, request, session, flash, json
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
            flash('Acess Denied !!')
            return redirect(url_for('login'))
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in session and session['user'] == 'Admin':
            return f(*args, **kwargs)
        else:
            flash('Acess Denied !!')
            return redirect(url_for('login'))
    return wrap

# use decorators to link the function to a url
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    #form = UserReportsForm.FromList(Report.query.filter_by(uid = current_user.uid).all())
    return render_template('welcome.html',user=current_user)  # render a template

@app.route('/home/report/<int:rid>/data', methods=['GET','POST'])
@login_required
def home_report_data(rid):
    report = Report.query.filter_by(rid = rid).first()
    if report.uid != current_user.uid:
        return app.response_class(response="{}",status=404,mimetype="application/json")
    
    return app.response_class(response=report.report,status=200,mimetype='application/json')

@app.route('/home/report/<int:rid>/', methods=['GET','POST'])
@login_required
def home_report(rid):
    report = Report.query.filter_by(rid = rid).first()
    if report.uid != current_user.uid:
        return redirect(url_for("home"))

    return render_template('report.html',user=current_user,report=report)


@app.route('/home/report/<int:rid>/delete', methods=['GET','POST'])
@login_required
def home_report_delete(rid):
    #TODO: Ensure uid is not admin uid
    res = Report.query.filter_by(rid = rid)

    if res.first().uid != current_user.uid:
        return app.response_class(response="{}",status=404,mimetype="application/json")

    res.delete()    
    db.session.commit()
    return redirect(url_for('home'))
    


@app.route('/home/report/insert/', methods=['GET','POST'])
@login_required
def home_report_insert():
    form = ReportForm(request.form,csrf_enabled = False)
    if form.validate_on_submit() and is_unity_request():
        db.session.add(Report(int(form.eid.data),form.report.data,current_user.uid))
        db.session.commit()
        return render_json({"status":"ok"})


    return redirect(url_for('home'))

    



@app.route('/admin/home', methods=['GET', 'POST'])
@admin_required
def admin_home():
    error = None
    form = AdminListForm(request.form, csrf_enabled = False)

    for user in db.session.query(User).all():
        form.users.append_entry(AdminRowForm.FromUser(user))

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

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(uid = uid).first()
        username = user.username
        
        user.password = bcrypt.generate_password_hash(request.form['password'])
        db.session.commit()
        return redirect(url_for('admin_home'))
    return render_template('reset.html',form = form, error = error, username = username, uid = uid)


@app.route('/admin/home/<int:uid>/delete', methods=['GET','POST'])
@admin_required
def user_delete(uid):
    #TODO: Ensure uid is not admin uid
    User.query.filter_by(uid = uid).delete()
    db.session.commit()
    return redirect(url_for('admin_home'))


def render_json(data,status=200):
    return app.response_class(
        response=json.dumps(data),
        status=status,
        mimetype='application/json')

def is_unity_request():
    return request.headers["User-Agent"].startswith("UnityPlayer")

# route for handling the login page logic
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm(request.form, csrf_enabled = False)

    def redoThisForm(error=None):        
        return render_template('login.html',form = form, error=error) if not is_unity_request() \
            else render_json({"status":"failed","reason":str(error)})

    if request.method != 'POST':
        return redoThisForm()

    if not form.validate_on_submit():
        return redoThisForm("Invalid username or password")

    user = User.query.filter_by(username = request.form['username']).first()

    if user is None or not bcrypt.check_password_hash(user.password,request.form['password']):
        return redoThisForm("Invalid username or password")

    session['user'] = request.form['username']
    login_user(user)
    flash('You were logged in.')

    if is_unity_request():
        return render_json({"status":"ok"})

    if session['user'] == 'Admin':
        return redirect(url_for("admin_home"))

    return redirect(url_for('home'))


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