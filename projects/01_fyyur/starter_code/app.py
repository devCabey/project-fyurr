#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from operator import length_hint
import sys
import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for, abort
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from server import app, db
from models import Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


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
    # TODO: replace with real venues data.
    #   num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = {}
    error = False
    try:
        data = Venue.query.all()
    except:
        error = True
    finally:
        if error:
            return abort(500)
        else:
            return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {}
    error = False
    try:
        venueData = Venue.query.filter(Venue.name.like(
            '%' + request.form.get('search_term')+'%')).all()

        response = {
            "count": length_hint(venueData),
            "data": venueData
        }
    except:
        error = True
    finally:
        if error:
            abort(500)
        else:
            return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = {}
    past_shows = []
    upcoming_shows = []
    error = False
    try:
        venue_shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time, Artist.name, Artist.image_link, Venue.image_link, Venue.name).join(
            Artist, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id).all()

        print(venue_shows)

        for show in venue_shows:
            if show.start_time < datetime.now():
                past_shows.append({
                    "artist_id": show[0],
                    "artist_name": show[3],
                    "artist_image_link": show[5],
                    "start_time": show[2]
                })
            else:
                upcoming_shows.append({
                    "artist_id": show[0],
                    "artist_name": show[3],
                    "artist_image_link": show[5],
                    "start_time": show[2]
                })

        venue_data = Venue.query.filter_by(id=venue_id).first()

        data = {
            "id": venue_data.id,
            "name": venue_data.name,
            "genres": venue_data.genres,
            "city": venue_data.city,
            "state": venue_data.state,
            "phone": venue_data.phone,
            "website": venue_data.website_link,
            "facebook_link": venue_data.facebook_link,
            "seeking_talent": venue_data.seeking_talent,
            "seeking_description": venue_data.seeking_description,
            "image_link": venue_data.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }

    except:
        error = True
    finally:
        if error:
            print(sys.exc_info())
            return abort(500)
        else:
            return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    data = {}
    error = False
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        image_link = request.form.get('image_link')
        genres = request.form.getlist('genres')
        facebook_link = request.form.get('facebook_link')
        website_link = request.form.get('website_link')

        seeking_description = request.form.get('seeking_description')
        if request.form.get('seeking_talent') == 'y':
            seeking_talent = True

        else:
            seeking_talent = False
        data = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres,
                     facebook_link=facebook_link, website_link=website_link, seeking_description=seeking_description, seeking_talent=seeking_talent)
        db.session.add(data)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        if error:
            return abort(500)
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
            return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # licking that button delete it from the db then redirect the user to the homepage
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        if error:
            return abort(500)
        else:
            return redirect(url_for('venue'))


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = {}
    error = False
    try:
        data = Artist.query.all()
    except:
        error = True
    finally:
        if error:
            return abort(500)
        else:
            return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    error = False
    response = {}
    try:

        artistData = Artist.query.filter(Artist.name.like(
            '%' + request.form.get('search_term')+'%')).all()
        response = {
            "count": length_hint(artistData),
            "data": artistData
        }
    except:
        error = True
    finally:
        if error:
            abort(500)
        else:
            return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    data = {}
    past_shows = []
    upcoming_shows = []
    error = False
    try:
        artist_shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time, Artist.name, Artist.image_link, Venue.image_link, Venue.name).join(
            Artist, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id).all()
        for show in artist_shows:
            if show.start_time < datetime.now():
                past_shows.append({"venue_id": show[1],
                                   "venue_name": show[6],
                                   "venue_image_link": show[4],
                                   "start_time": show[2]
                                   })
            else:
                upcoming_shows.append({"venue_id": show[1],
                                       "venue_name": show[6],
                                       "venue_image_link": show[4],
                                       "start_time": show[2]
                                       })

        artist = Artist.query.filter_by(id=artist_id).first()
        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }
        print(past_shows)
    except:
        error = True
    finally:
        if error:
            return abort(500)
        else:
            return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    data = Artist.query.filter_by(id=artist_id).first()
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    try:
        artist = Artist.query.get(artist_id)
        print(request.form.get('name'))
        if artist.name != request.form.get('name'):
            artist.name = request.form.get('name')

        if artist.city != request.form.get('city'):
            artist.city = request.form.get('city')

        if artist.state != request.form.get('state'):
            artist.state = request.form.get('state')

        if artist.phone != request.form.get('phone'):
            artist.phone = request.form.get('phone')

        if artist.genres != request.form.getlist('genres'):
            artist.genres = request.form.getlist('genres')

        if artist.facebook_link != request.form.get('facebook_link'):
            artist.facebook_link = request.form.get('facebook_link')

        if artist.image_link != request.form.get('image_link'):
            artist.image_link = request.form.get('image_link')

        if artist.website_link != request.form.get('website_link'):
            artist.website_link = request.form.get('website_link')

        if request.form.get('seeking_venue') == 'y':

            artist.seeking_venue = True

        else:
            artist.seeking_venue = False

        if artist.seeking_description != request.form.get('seeking_description'):
            artist.seeking_description = request.form.get(
                'seeking_description')

        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()
        if error:
            abort(500)
        else:
            return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    data = Venue.query.filter_by(id=venue_id).first()
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    try:
        venue = Venue.query.get(venue_id)
        print(venue)
        if venue.name != request.form.get('name'):
            venue.name = request.form.get('name')

        if venue.city != request.form.get('city'):
            venue.city = request.form.get('city')

        if venue.state != request.form.get('state'):
            venue.state = request.form.get('state')

        if venue.phone != request.form.get('phone'):
            venue.phone = request.form.get('phone')

        if venue.genres != request.form.getlist('genres'):
            venue.genres = request.form.getlist('genres')

        if venue.facebook_link != request.form.get('facebook_link'):
            venue.facebook_link = request.form.get('facebook_link')

        if venue.image_link != request.form.get('image_link'):
            venue.image_link = request.form.get('image_link')

        if venue.website_link != request.form.get('website_link'):
            venue.website_link = request.form.get('website_link')

        if request.form.get('seeking_talent') == 'y':

            venue.seeking_talent = True

        else:
            venue.seeking_talent = False

        if venue.seeking_description != request.form.get('seeking_description'):
            venue.seeking_description = request.form.get(
                'seeking_description')
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()
        if error:
            abort(500)
        else:
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
    # TODO: insert form data as a new Venue record in the db, instead
    data = {}
    error = False
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        image_link = request.form.get('image_link')
        genres = request.form.getlist('genres')
        facebook_link = request.form.get('facebook_link')
        website_link = request.form.get('website_link')

        seeking_description = request.form.get('seeking_description')
        if request.form.get('seeking_venue') == 'y':
            seeking_venue = True

        else:
            seeking_venue = False

        # TODO: modify data to be the data object returned from db insertion
        data = Artist(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres,
                      facebook_link=facebook_link, website_link=website_link, seeking_description=seeking_description, seeking_venue=seeking_venue)
        db.session.add(data)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()
        if error:
            return abort(500)
        else:
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
            return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = {}
    error = False

    try:
        data = db.session.query(Show.artist_id, Show.venue_id, Show.start_time, Artist.name, Artist.image_link, Venue.name).join(
            Artist, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id).all()
    except:
        error = True
        print(sys.exc_info())
    finally:
        if error:
            return abort(500)
        else:
            return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    data = {}
    error = False
    try:
        venue = request.form.get('venue_id')
        artist = request.form.get('artist_id')
        start = request.form.get('start_time')

        # TODO: insert form data as a new Show record in the db, instead
        data = Show(venue_id=venue, artist_id=artist, start_time=start)
        db.session.add(data)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()
        if error:
            return abort(500)
        else:
            # on successful db insert, flash success
            flash('Show was successfully listed!')
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Show could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
