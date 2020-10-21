from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from wtforms.validators import EqualTo,Email,DataRequired,Length,ValidationError
from flaskblog.models import User
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user


class RegisterForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired(),Length(min=2,max=35)])
    email=StringField("Email",validators=[DataRequired(),Email()])
    password=StringField("Password",validators=[DataRequired()])
    confirm_password=StringField("Confirm Password",validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Sign Up')

    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('UserName is Already Exist')

    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is Already Exist')



class LoginForm(FlaskForm):
    email=StringField("Email",validators=[DataRequired(),Email()])
    password=StringField("Password",validators=[DataRequired()])
    remember_me=BooleanField('Remember Me')
    submit=SubmitField('Login')





class ProfileUpdateForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired(),Length(min=2,max=35)])
    email=StringField("Email",validators=[DataRequired(),Email()])
    picture=FileField('update profile picture',validators=[FileAllowed(['jpeg','jpg','png'])])
    submit=SubmitField('Update')

    def validate_username(self,username):
        if username.data!=current_user.username:
            user=User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('UserName is Already Exist')

    def validate_email(self,email):
        if email.data!=current_user.email:
            user=User.query.filter_by(email=email.data).first()
            if user:       
                raise ValidationError('Email is Already Exist')



class PostForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    content=TextAreaField("Content",validators=[DataRequired()])
    submit=SubmitField("AddPost")


class UpdatePostForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    content=TextAreaField("Content",validators=[DataRequired()])
    submit=SubmitField("Update")



class RequestResetForm(FlaskForm):
    email=StringField("Email",validators=[DataRequired(),Email()])
    submit=SubmitField("Submit")

    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with this email please login first")


class ResetPasswordForm(FlaskForm):
    password=StringField("Password",validators=[DataRequired()])
    confirm_password=StringField("Confirm Password",validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField("Reset Password")

