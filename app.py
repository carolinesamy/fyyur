#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import Date, cast
from datetime import date
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# Done: connect to a local postgresql database
migrate = Migrate(app,db)
session=db.Session()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows= db.relationship('Show',backref='Venue')

    # Done: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows= db.relationship('Show',backref='Artist')

    def __repr__(self):
        return f'<Artist {self.id} {self.name} ({self.shows}>'
    # Done: implement any missing fields, as a database migration using Flask-Migrate

# Done Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
     __tablename__='Show'

     id=db.Column(db.Integer,primary_key=True)
     start_time = db.Column(db.DateTime , nullable=False)
     artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
     venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)

     def __repr__(self):
         return f'<Show {self.id} {self.start_time} {self.artist_id} {self.venue_id}>'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  cities=Venue.query.with_entities(Venue.city,Venue.state).group_by(Venue.city ,Venue.state).all()
  # print(cities)
  # print(cities[0][0])
  for city in cities:
      s={}
      venues=Venue.query.filter(Venue.state==city[1])
      s['city']=city[0]
      s['state']=city[1]
      s['venues']=venues
      data.append(s)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search=request.form.get('search_term','')
  venues=Venue.query.filter(Venue.name.ilike('%'+search+'%'))
  venues_count=venues.count()
  response={
     "count": venues_count,
     "data": venues
   }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue= Venue.query.get(venue_id)
  past_shows=Show.query.join(Artist).join(Venue).with_entities(Show.start_time, Show.artist_id,Artist.image_link.label('artist_image_link'),Artist.name.label('venue_name')).filter(cast(Show.start_time,Date) < date.today(), Venue.id==venue_id)
  upcoming_shows=Show.query.join(Artist).join(Venue).with_entities(Show.start_time, Show.artist_id,Artist.image_link.label('artist_image_link'),Artist.name.label('artist_name')).filter(cast(Show.start_time,Date) >= date.today() , Venue.id==venue_id)
  data={}
  data['id']=venue.id
  data['name']=venue.name
  data['city']=venue.city
  data['state']=venue.state
  data['phone']=venue.phone
  data['facebook_link']=venue.facebook_link
  data['image_link']=venue.image_link
  data['facebook_link']=venue.facebook_link
  data['past_shows']=past_shows
  data['upcoming_shows']=upcoming_shows
  data['past_shows_count']=past_shows.count()
  data['upcoming_shows_count']=upcoming_shows.count()

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Done: insert form data as a new Venue record in the db, instead
  name=request.form.get('name','')
  city=request.form.get('city','')
  state=request.form.get('state','')
  phone=request.form.get('phone','')
  address=request.form.get('address','')
  image_link=request.form.get('image_link','')
  facebook_link=request.form.get('facebook_link','')
  if(name == '' or state =='' ):
      error = "Name Field and State Field is required"
      flash('An error'+error+'. Venue ' + name + ' could not be listed.')
  else:
      try:
          new_venue=Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link)
          db.session.add(new_venue)
          db.session.commit()
           # on successful db insert, flash success
          flash('Venue ' + new_venue.name + ' was successfully listed!')
      except:
          # Done: on unsuccessful db insert, flash an error instead.
          flash('An error occurred. Venue ' + name + ' could not be listed.')
          db.session.rollback()
          print(sys.exc_info())
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Done: replace with real data returned from querying the database
  data=Artist.query.order_by('id').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search=request.form.get('search_term','')
  atrists=Artist.query.filter(Artist.name.ilike('%'+search+'%'))
  atrists_count=atrists.count()
  response={
     "count": atrists_count,
     "data": atrists
   }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist=Artist.query.get(artist_id)
  past_shows=Show.query.join(Artist).join(Venue).with_entities(Show.start_time, Show.artist_id,Show.venue_id,Artist.image_link.label('artist_image_link'),Venue.name.label('venue_name')).filter(cast(Show.start_time,Date) < date.today(), Artist.id==artist_id)
  upcoming_shows=Show.query.join(Artist).join(Venue).with_entities(Show.start_time, Show.artist_id,Show.venue_id,Artist.image_link.label('artist_image_link'),Venue.name.label('venue_name')).filter(cast(Show.start_time,Date) >= date.today() , Artist.id==artist_id)
  # data=[]
  data={}
  data['id']=artist.id
  data['name']=artist.name
  data['genres']=artist.genres
  data['city']=artist.city
  data['state']=artist.state
  data['phone']=artist.phone
  data['facebook_link']=artist.facebook_link
  data['image_link']=artist.image_link
  data['facebook_link']=artist.facebook_link
  data['past_shows']=past_shows
  data['upcoming_shows']=upcoming_shows
  data['past_shows_count']=past_shows.count()
  data['upcoming_shows_count']=upcoming_shows.count()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # Done: insert form data as a new Venue record in the db, instead
  # Done: modify data to be the data object returned from db insertion
  name=request.form.get('name','')
  city=request.form.get('city','')
  state=request.form.get('state','')
  phone= str(request.form.get('phone',''))
  genres_list=request.form.getlist('genres')
  genres='';
  if len(genres_list) != 0:
      genres= ','.join(genres_list)
  image_link=request.form.get('image_link','')
  facebook_link=request.form.get('facebook_link','')
  if(name == '' or state =='' ):
      error = "Name Field and State Field is required"
      flash('An error '+error+'. Artist ' + name + ' could not be listed.')
  else:
      try:
          new_artist=Artist(name=name, city=city,state=state, phone=phone, genres=genres, image_link=image_link,  facebook_link=facebook_link)
          db.session.add(new_artist)
          db.session.commit()
           # on successful db insert, flash success
          flash('Artist ' + new_artist.name + ' was successfully listed!')
      except:
          # Done: on unsuccessful db insert, flash an error instead.
          flash('An error occurred. Artist ' + name + ' could not be listed.')
          db.session.rollback()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data2=(session.query(Show, Artist, Venue).join(Artist).join(Venue)).all()
  data = Show.query.join(Artist).join(Venue).with_entities(Show.start_time, Show.artist_id,Show.venue_id,Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link'),Venue.name.label('venue_name') )
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # Done: insert form data as a new Show record in the db, instead
  # TODO: valid form
  artist_id=request.form.get('artist_id')
  venue_id=request.form.get('venue_id')
  start_time=request.form.get('start_time','')
  try:
      new_show=Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(new_show)
      db.session.commit()
       # on successful db insert, flash success
      flash('Show was successfully listed!')
  except:
      # Done: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
      print(sys.exc_info())
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
