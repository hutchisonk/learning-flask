from flask import Flask, render_template, request, session, redirect, url_for
from models import db, User, Place
from forms import SignupForm, LoginForm, AddressForm

# this file routes URLs to the right place, connects to the database, and is kind of the heart of the application

# part of the boilerplate code - defining the "app"
app = Flask(__name__)

# configures the connection to from the flask sqlalchemy extension
# (imported above) to the postgresql database (which we set up in the terminal)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/learningflask'
# we imported db from models, where db is just an empty/unmodified instance of sqlalchemy
db.init_app(app)

# If a secret key is set, cryptographic components can use this to sign cookies and other things.
# Set this to a complex random value when you want to use the secure cookie for instance.
# This attribute can also be configured from the config with the SECRET_KEY configuration key. Defaults to None.
app.secret_key = "development-key"

# route home directory paths to the template index.html
@app.route("/")
def index():
    # flask will look for templates in the 'templates' folder
    return render_template("index.html", session=session)

# routing "about" page
@app.route("/about")
def about():
    return render_template("about.html")

# routing "signup page"
# this can handle both GET and POST methods
@app.route("/signup", methods=['GET', 'POST'])
def signup():

    # this checks if someone is logged in by seeing if
    # there is an "email" item in the session object (?)
    # if so, we're already loggest in so just go to the home page
    if "email" in session:
        # session is a Flask extension that we imported
        return redirect(url_for("home"))

    # in this function the variable form is an instance of SignupForm, which
    # we imported from our forms.py. it has 3 StringFields, 1 PasswordField and a submitfield
    form = SignupForm()

    # if the method is POST, and the form isn't 100% validated, then bring us back to the signup form template, which
    # will then have error messages highlighting the appropriate fields
    if request.method == "POST":
        if form.validate() == False:
            return render_template('signup.html', form=form,session=session)
        else:
            # if the form does validate (a function through WTForms)
            # then newuser variable is instantiated as an instance of the User class imported from models.py
            newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)

            # this is how sqlalchemy adds to the database
            db.session.add(newuser)
            db.session.commit()

            # this sets session['email'] to be the email the user entered into the form that we set as a property of newuser
            session["email"] = newuser.email
            # send that b***h home
            return redirect(url_for("home"))
    elif request.method == "GET":
        # if it's just a regular get request and the url isnt trying to POST anything then just send them the signup form
        return render_template('signup.html', form=form, session=session)

# when you go to /home
@app.route("/home", methods=["GET", "POST"])
def home():
    # if the user is not logged in, send them to log in. this "protects" the home page
    if "email" not in session:
        return redirect(url_for("login"))

    # in this function, form refers to an instance of address form that we imported from our forms.py
    form = AddressForm()
    # so we can access these two things later.
    places = []

    #default coordinates to start with on the map
    #first_load = 1
    my_coordinates = (39.281496, -76.6119114)
    # if the url is POSTing something
    if request.method == "POST":
        # if the form doesn' validate, try again
        if form.validate() == False:
            return render_template("home.html", form=form, session=session, first_load=1)
        else:
            # if the form validates, get address from form
            address = form.address.data
            # query nearby locations
            # p is an instance of the Place class that we import from the models
            p = Place()
            # coordinates reset to
            my_coordinates = p.address_to_latlng(address)
            places = p.query(address)

            # if (my_coordinates == (39.281496, -76.6119114)):
            #     first_load = 0
            #return results
            return render_template("home.html", form=form, my_coordinates=my_coordinates, places=places, session=session, first_load=0)

    elif request.method == "GET":
        return render_template("home.html", form=form, my_coordinates=my_coordinates, places=places, session=session,first_load=1)

@app.route("/login", methods=["GET", "POST"])
def login():
    if "email" in session:
        # you're already logged in, go /home
        return redirect(url_for("home"))
    # this form refers to the LoginForm
    form = LoginForm()

    # for sending the form:
    if request.method == "POST":
        if form.validate == False:
            return render_template('login', form=form, session=session)
        else:
            # email and pw are as input to the form
            email = form.email.data
            password = form.password.data

            # talking to the DB: user is the result of querying the database for the email we want
            user = User.query.filter_by(email=email).first()

            # if the user (email) exists in the database, and the password works
            # (check_pw is a method of the User model we defined in models.py)
            if user is not None and user.check_password(password):
                # then the session 'email' is set to the login email
                session["email"] = form.email.data
                # and we're redirected home
                return redirect(url_for("home"))
            else:
                # otherwise reload login page
                return redirect(url_for("login"))
    elif request.method == "GET":
        return render_template("login.html", form=form, session=session)
    return render_template('login.html', form=form, session=session)

@app.route("/logout")
def logout():
    # remove "email" from session
    session.pop("email", None)
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
