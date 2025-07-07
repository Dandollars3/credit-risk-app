from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('New Password (optional)', validators=[
        Optional(),
        Length(min=8),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\\W)', message="Include uppercase, lowercase, and a symbol.")
    ])
    submit = SubmitField('Update')
