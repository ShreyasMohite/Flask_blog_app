from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_mail import Mail
import os



app=Flask(__name__)




app.config["SECRET_KEY"]="IJNEWMDC893IWECJN"
app.config["SQLALCHEMY_DATABASE_URI"]='mysql://root:''@localhost/testdb'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config['MAIL_SERVER']="smtp.gmail.com"
app.config['MAIL_PORT']=465
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']="youremail"
app.config['MAIL_PASSWORD']="yourpassword"


db=SQLAlchemy(app)
login_manager=LoginManager(app)
login_manager.login_view="Login"
bcrypt=Bcrypt(app)
ma=Marshmallow(app)
mail=Mail(app)



from flaskblog import routes
from flaskblog import models
