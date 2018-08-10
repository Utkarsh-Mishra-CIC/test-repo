from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SelectField, TextAreaField, StringField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class LoginForm(FlaskForm):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = TextField(
        'username',
        validators=[DataRequired(), Length(min=3, max=25)]
    )
    email = TextField(
        'email',
        validators= [DataRequired(), Email(message=None), Length(min=6, max=40)]
    )
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(), EqualTo('password', message='Passwords must match.')
        ]
    )
    gender = SelectField(
        'Gender',
        choices=[('Male', 'Male'), ('Female', 'Female'), ('', 'Select')]
    )
    usertype = StringField ('User Type',render_kw={'readonly': True})

class AdminForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])

class ReportForm(FlaskForm):
    eid = TextField('EID', validators=[DataRequired()])
    report = TextAreaField(
        'Report',render_kw={"rows": 11, "cols": 70}, validators=[DataRequired()])

class AdminRowForm(FlaskForm):
    uid = TextField('UID', render_kw={'readonly':True})
    username = TextField('Username',render_kw={'readonly':True})
    email = TextField('Email',render_kw={'readonly':True})
    gender = TextField('Gender', render_kw={'readonly':True})
    usertype = SelectField(
        'User Type',
        choices=[('Trainee','Trainee'),('Expert','Expert')]
    )

class SuperAdminRowForm(FlaskForm):
    uid = TextField('UID', render_kw={'readonly':True})
    username = TextField('Username',render_kw={'readonly':True})
    email = TextField('Email',render_kw={'readonly':True})
    gender = TextField('Gender', render_kw={'readonly':True})
    usertype = TextField('User Type', render_kw={'readonly':True})

class AdminListForm(FlaskForm):
    admin_user = FieldList(FormField(SuperAdminRowForm))
    users = FieldList(FormField(AdminRowForm))

class ResetPassword(FlaskForm):
    password = PasswordField('Password',validators=[DataRequired(), Length(min=6, max=25)])
    confirm = PasswordField('Confirm',validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])