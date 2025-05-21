from flask import Flask, render_template
from flask import request, redirect, url_for
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer,CHAR, update
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists #import to check if database exists


#Base has to go before all the code!
Base = declarative_base()
#=====================================PERSON CLASS=======================
class Person(Base):
  __tablename__ = "people"

  ssn = Column("ssn", Integer, primary_key=True)
  firstname = Column("firstname", String)
  lastname = Column("lastname", String)
  gender = Column("gender", CHAR)
  age = Column("age", Integer)

  def __init__(self, ssn, first, last, gender, age):
    self.ssn = ssn
    self.firstname = first
    self.lastname = last
    self.gender = gender
    self.age = age

  def get_ssn(self):
    return self.ssn

  def get_firstname(self):
    return self.firstname

  def get_lastname(self):
    return self.lastname

  def get_gender(self):
    return self.gender

  def get_age(self):
    return self.age  
    
  def set_firstname(self, fname):
    self.firstname = fname
    
  

  def __repr__(self):
    return f"({self.ssn}) {self.firstname} {self.lastname} ({self.gender}, {self.age})"
#=====================================THING CLASS=======================
class Thing(Base):
  __tablename__ = "things"

  tid = Column("tid", Integer, primary_key=True)
  description = Column("description", String)
  owner = Column(Integer, ForeignKey("people.ssn"))

  def __init__(self, tid, description, owner):
    self.tid = tid
    self.description = description
    self.owner = owner

  def __repr__(self):
    return f"({self.tid}) {self.description} owned by {self.owner}"
#==================================MAIN CLASS================================
#Database stuff
db_url = "sqlite:///mydb.db" #variable for database URL
engine = create_engine(db_url, echo=True)

#Create the database or use existing one
if database_exists(db_url):
  print("data base exists - carry on and do stuff") #in a real use case this would be you program just carrying on!
  Base.metadata.create_all(bind=engine) #create a new connection to the database and open a session
  Session = sessionmaker(bind=engine)
  session = Session()
  results=session.query(Thing, Person).filter(Thing.owner == Person.ssn).filter(Person.firstname == "Sallie").all()
  for r in results:
    print(r)
else: #database does not exist so add some data
  print("database does not exist - so create it and add some data")
  Base.metadata.create_all(bind=engine)

  Session = sessionmaker(bind=engine)
  session = Session()

  p1 = Person(1, "Sallie", "Weiss", "F", 24)
  p2 = Person(2, "Henry", "Kemp", "M", 36)
  p3 = Person(3, "Harris", "Kemp", "M", 21)
  p4 = Person(4, "Ridwan", "Mcqrath", "M", 31)
  p5 = Person(5, "Honey", "Norton", "F", 47)

  session.add(p1)
  session.add(p2)
  session.add(p3)
  session.add(p4)
  session.add(p5)
  session.commit()

  t1 = Thing(1, "Keyboard", p5.ssn)
  t2 = Thing(2, "Mouse", p4.ssn)
  t3 = Thing(3, "Microphone", p3.ssn)
  t4 = Thing(4, "Monitor", p2.ssn)
  t5 = Thing(5, "Speaker", p1.ssn)
  t6 = Thing(6, "Desk Camera", p5.ssn)
  t7 = Thing(7, "Cellphone", p4.ssn)
  t8 = Thing(8, "Laptop", p3.ssn)
  t9 = Thing(9, "Docking Station", p2.ssn)
  t10 = Thing(10, "Headphones", p1.ssn)
  session.add(t1)
  session.add(t2)
  session.add(t3)
  session.add(t4)
  session.add(t5)
  session.add(t6)
  session.add(t7)
  session.add(t8)
  session.add(t9)
  session.add(t10)
  session.commit()
  print("SUCCESS database created and data added")

app = Flask(__name__)

# basic route
@app.route('/')
def root():
    return render_template('home.html', page_title='HOME')

# about route - called by PEOPLE in the nav bar and returning
# information about the site
@app.route('/people')  # note the leading slash, it’s important
def people():
  Session = sessionmaker(bind=engine)
  session = Session()
  results=session.query(Person).all() 
  print("People are ")
  print(results)
  return render_template('people.html', page_title='PEOPLE', query_results = results)

#Thing route
@app.route('/things')  # note the leading slash, it’s important
def things():
  Session = sessionmaker(bind=engine)
  session = Session()
  results=session.query(Thing).all() 
  print("Things are ")
  print(results)
  return render_template('things.html', page_title='THINGS', query_results = results)

#Who owns what route
@app.route('/who_owns_what')  # note the leading slash, it’s important
def who_own_what():
  Session = sessionmaker(bind=engine)
  session = Session()
  results=session.query(Thing, Person).filter(Thing.owner == Person.ssn).all()
  print("Things and owners are ")
  print(results)
  return render_template('who_owns_what.html', page_title='WHO OWNS WHAT', query_results = results)


#Adding a person is quite easy. Get the data from the form, as the values are always strings, convert ssn and age to ints, create a person object, add to the database and commit.
#No validation takes place  -this is something to add.
@app.route('/add_person', methods=['POST', 'GET'])  # note the leading slash, it’s important
def add_person():
  if request.method == "POST":
       # getting input with name = fname in HTML form
       first_name = request.form.get("fname")
       last_name = request.form.get("lname")
       ssn = request.form.get("ssn")
       age = request.form.get("age")
       gender = request.form.get("gender")
       print ("Your name is "+first_name + " " + last_name + " " + ssn + " " + age + " " + gender)
    #Create a new connection and session
       Base.metadata.create_all(bind=engine)
       Session = sessionmaker(bind=engine)
       session = Session()
       ssn = int(ssn) #as data from the form is txt
       age = int(age)
    #Create a person object
       p = Person(ssn, first_name, last_name, gender, age)
    #Add to the database
       session.add(p)
       print("Person added" + "ssn")
       session.commit()    
  return render_template("add_person.html")


#This route is where the SSN of the person to be edited is entered. It uses a redirect with the ssn as a parameter
#to create a custom URL the SSN is passed to the update page. This creates a page /update/<SSN>
#that contains the details of the person to edit
@app.route('/edit_person', methods=['POST', 'GET'])  # note the leading slash, it’s important
def edit_person():
  if request.method == "POST":
    ssn = request.form.get("ssn")
    print("ssn requested is - from edit method - " + ssn)
    return redirect(url_for('update', ids = ssn))
    
  else:
    print("did not redirect")
    return render_template("edit_person.html",page_title='EDIT A PERSON')

@app.route('/update/<ids>', methods=['POST', 'GET'])


#Update is used to update a database entry or delete a database entry. A custom page is created on the fly
#for a person when the SSN is passed from edit_person().
#First the person details are got as an object from the DB using SQLalchemy - create a person object.
#Next, (last line of this function) the update page is rendered by passing fname, lname etc to update.html
#If values are edited, they are saved by e.g. person.firstname = request.form['fname'] - which gets
#the edited value from the form and sets a person attribute. The session is commited and a redirect to 'people'
#so that you can see the edit
#If delete is pressed, the person object is deleted using session.delete(person)
def update(ids):
  print(ids)
  Base.metadata.create_all(bind=engine)
  Session = sessionmaker(bind=engine)
  session = Session()
  # getting input with ssn = ssn in HTML form
  ssn = ids
  print("ssn requested is ... " + ssn)
  ssn = int(ssn)
  

  person = session.query(Person).filter(Person.ssn == ssn).first()
  fname = person.get_firstname()
  print(fname) #check getter method works
  lname = person.get_lastname()
  gender = person.get_gender()
  age = person.get_age()
  #Above are just examples - we don't actually use them in the form below

  if request.method == 'POST': #Check which button is clicked
    
    if request.form['edit_button'] =="Save": #Save pressed, so update the details. request.form['edit_button'] checks the value of the button.
      print("Save clicked - update")
      person.firstname = request.form['fname']# Get the fanme from the form and set it. In SQLalchemy we can directly edit an objects attributes!
      print( "Got the first name")
      person.lastname = request.form['lname']
      print( "Last Name is " + lname)      
      person.gender = request.form['gender']
      print( "Gender is " + gender)
      #person.ssn = request.form['int'] ssn is a primary key - do not change
      age = int(request.form['age'])
      person.age = age
      session.commit()
      return redirect(url_for('people', page_title="PEOPLE"))   
      
    elif request.form['edit_button'] =="Delete":# Delete so delete the person
      print("Delete clicked  -update")
      session.delete(person)
      session.commit()
      print("deleted person with id " + ids)
      return redirect(url_for('people', page_title="PEOPLE"))
      
  print("sending variables from update")
  #Return statement below is run the first time the page is loaded.
  return render_template("update.html",page_title='UPDATE A PERSON', ids=ssn, Fname = fname, Lname = lname, Gender = gender, Age = age)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
