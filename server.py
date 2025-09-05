import json
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    url_for
    )


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    """
    Validate a club's email submitted for login and render the welcome page
    This endpoint expects POST form data with an ``email`` field. The value is
    trimmed and lowercased, then matched case-insensitively against the in-memory
    ``clubs`` list. If the email is missing or unknown, a flash message is queued
    and the index page is rendered with HTTP 400.

    Returns:
        flask.Response: 
            - 200 OK with ``welcome.html`` when a matching club is found. 
              Template context includes ``club`` (dict) and ``competitions`` (list).
            - 400 Bad Request with ``index.html`` when the email is missing or unknown.

    Notes:
        - Intended for browser form submissions (``application/x-www-form-urlencoded``
          or ``multipart/form-data``).
        - Uses ``flash()`` to display error messages in templates.
    """
    email = request.form['email']

    if not email:
        flash("Email manquant.")
        return render_template('index.html'), 400

    email = email.strip().lower()
    club = next((c for c in clubs if c.get('email', '').lower() == email), None)

    if not club:
        flash("Adresse e-mail inconnue.")
        return render_template('index.html'), 400
    
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    places_required = int(request.form['places'])
    if places_required > 12:
        flash("You cannot book more than 12 places per competition.")
        return render_template('booking.html', club=club, competition=competition)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-places_required
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))