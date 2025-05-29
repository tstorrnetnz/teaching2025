import email_validator
from flask import Flask, render_template, redirect, url_for, request
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer,CHAR
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists #import to check if database exists
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, IntegerField, PasswordField, SubmitField, EmailField, validators
from wtforms.validators import InputRequired, Length, ValidationError, NumberRange, Email

from flask_bcrypt import Bcrypt

#Base has to go before all the code!
Base = declarative_base()


#=====================================PERSON CLASS=======================
#Note that the Person class MUST have the id as a key column. This is used by the UserMixin import to identify the user. This class has the email address and password stored as attributes. Other code stores the password in an encrypted form, so that it cannot be used if the database is hacked.
class Person(Base, UserMixin):
  __tablename__ = "people"

  id = Column("id", Integer, primary_key=True)
  firstname = Column("firstname", String)
  lastname = Column("lastname", String)
  gender = Column("gender", CHAR)
  age = Column("age", Integer)
  username = Column(String(80), unique=True, nullable=False)
  email = Column(String(120), unique=True, nullable=False)
  pwd = Column(String(300), nullable=False, unique=True)


  def __init__(self, id, first, last, gender, age, username, email, pwd):
    self.id = id
    self.firstname = first
    self.lastname = last
    self.gender = gender
    self.age = age
    self.username = username
    self.email = email
    self.pwd = pwd

 

  #def get_id(self):
   # return str(self.ssn) #required method for user_login() - must return a string

  def get_firstname(self):
    return self.firstname

  def get_lastname(self):
    return self.lastname

  def get_gender(self):
    return self.gender

  def get_age(self):
    return self.age

  def get_pwd(self):
    return self.pwd

  def set_firstname(self, fname):
    self.firstname = fname

  def set_username(self, username):
    self.username = username
    
  def set_email(self, email):
    self.email = email

  def set_pwd(self, pwd):
    self.pwd = pwd
  

  def __repr__(self):
    return f"({self.id}) {self.firstname} {self.lastname} ({self.gender}, {self.age}, {self.username}, {self.email}, {self.pwd})"
#=====================================REGISTER FORM CLASS=======================
#This class holds the WTForm details for the register form. Each of these fields is used to create a new person when they register.
class RegisterForm(FlaskForm):
  useremail = EmailField(label = ('Email'), validators=[InputRequired(), Length(max=60), Email()], render_kw={"placeholder": "Email"})
 
  password = PasswordField(label = ('Password'),validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})

  id = IntegerField('Number',validators=[InputRequired(), NumberRange(min=1, max=1000)], render_kw={"placeholder": "id"})
  
  firstname = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Firstname"})

  lastname = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Lastname"})

  username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
  
  gender = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Gender"})

  age = IntegerField('Number',validators=[InputRequired(), NumberRange(min=10, max=110)], render_kw={"placeholder": "Age"})
  
  submit = SubmitField("Register")


  
  def validate_email(self, email):
    existing_user_email = Person.query.filter_by(email=email.data).first()
    if existing_user_email:
      raise ValidationError("That email address already exists. Please choose a different one")
#=====================================LOGIN FORM CLASS=======================
class LoginForm(FlaskForm):
  useremail = EmailField('Email', validators=[InputRequired(), Length(max=60), validators.Email()], render_kw={"placeholder": "Email"})
  password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
  submit = SubmitField("Login")
#=====================================DATABASE STUFF=======================
#Database stuff
db_url = "sqlite:///database.db" #variable for database URL
engine = create_engine(db_url, echo=True)
if database_exists(db_url):
  print("data base exists - carry on and do stuff") #in a real use 
else: #database does not exist so add some data
    print("database does not exist - so create it and add some data")
    Base.metadata.create_all(bind=engine)
#=====================================APP STUFF=======================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
print("login_manager")
login_manager.login_view = "login"
print("login_manager completed")


@login_manager.user_loader
def load_user(user_id):
  Session = sessionmaker(bind=engine)
  session = Session()
  return session.get(Person,user_id)

# basic route
@app.route('/')
def root():
    return render_template('home.html', page_title='HOME')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
      Session = sessionmaker(bind=engine)
      session = Session()
      person = session.query(Person).filter_by(email = form.useremail.data).first()
      if person:
        if bcrypt.check_password_hash(person.pwd, form.password.data):
          print("password OK")
          login_user(person)
          print("logged in")
          return redirect(url_for('dashboard'))
      
    return render_template('login.html', page_title='login', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html', page_title='DASHBOARD')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
      hashed_password = bcrypt.generate_password_hash(form.password.data)
      new_person = Person(id=form.id.data,first=form.firstname.data, last=form.lastname.data, gender=form.gender.data, age = form.age.data, username = form.username.data, email = form.useremail.data, pwd = hashed_password)
      Session = sessionmaker(bind=engine)
      session = Session()
      session.add(new_person)
      session.commit()
      print("SUCCESS new person created and data added")
      return redirect(url_for('login'))
    return render_template('register.html', page_title='REGISTER',form=form)
  #=====================================RUN CODE=======================
if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=8080)