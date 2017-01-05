from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

import geocoder
import urllib
import json

#instantiate database?
db = SQLAlchemy()

# the base class for all your sqlalchemy models is called db.Model
class User(db.Model):
    #structure of the User table within the db
  __tablename__ = 'users'
  uid = db.Column(db.Integer, primary_key = True)
  firstname = db.Column(db.String(100))
  lastname = db.Column(db.String(100))
  email = db.Column(db.String(120), unique=True)
  pwdhash = db.Column(db.String(54))

  #method for initiating a user
  def __init__(self, firstname, lastname, email, password):
    self.firstname = firstname.title()
    self.lastname = lastname.title()
    self.email = email.lower()
    self.set_password(password)

  # store a hashed password, not the plaintext
  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)

  #for checking if a password is correct
  def check_password(self, password):
    return check_password_hash(self.pwdhash, password)


#fetching and organizing the geographic information
class Place(object):
    #translate meters to walking time
  def meters_to_walking_time(self, meters):
    # 80 meters is one minute walking time
    return int(meters / 80)

    # this will be the link to the item on wikipedia so the user can click through for more information
  def wiki_path(self, slug):
    return urllib.parse.urljoin("http://en.wikipedia.org/wiki/", slug.replace(' ', '_'))

# using geocoder to translate an address to latitude and longitude
  def address_to_latlng(self, address):
    g = geocoder.google(address)
    return (g.lat, g.lng)

#query wikipedia with our user's translated lat-long search term
  def query(self, address):
    lat, lng = self.address_to_latlng(address)
    #the path to communicate with the wikipedia API for a given search term
    query_url = 'https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gsradius=5000&gscoord={0}%7C{1}&gslimit=20&format=json'.format(lat, lng)
    #receive the reques
    g = urllib.request.urlopen(query_url)
    #read results into json
    results = g.read()
    #close the request
    g.close()

    #bytes vs string, json vs urllib
    #load the data
    data = json.loads(results.decode('utf-8'))
    #str_response = results.readall().decode('utf-8')
    #data = json.loads(str_response)
    #data = json.loads(results)

    places = []
    #if there's something in the data
    if "query" in data:
        #for each place under data.query.geosearch result
      for place in data['query']['geosearch']:
          #setting variables from data
        name = place['title']
        meters = place['dist']
        lat = place['lat']
        lng = place['lon']

        wiki_url = self.wiki_path(name)
        walking_time = self.meters_to_walking_time(meters)

        #using variables to define an obhect of place names
        d = {
          'name': name,
          'url': wiki_url,
          'time': walking_time,
          'lat': lat,
          'lng': lng
        }
        #appending object to a list
        places.append(d)

      return places
    else:
        #probably don't need this but this was from trying to test out another feature, dont feel like troubleshooting atm
      #places.append(1)
      return places
