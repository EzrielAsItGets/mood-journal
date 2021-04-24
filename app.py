#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, redirect, url_for, render_template, request, session, Markup
import logging
from logging import Formatter, FileHandler
from forms import *
import os
import journaling, utilities

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/', methods=["POST", "GET"])
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'view' in session:
        session.pop('view', None)
    template = '<iframe src="https://open.spotify.com/embed/track/5TxY7O9lFJJrd22FmboAXe" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
    if 'song' in session:
        track = template.replace('5TxY7O9lFJJrd22FmboAXe', session['song'])
        return render_template('pages/home.html', player=Markup(track))
    return render_template('pages/home.html', player=Markup(template))


@app.route('/load', methods=["POST", "GET"])
def loadEntry():
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'view' in session:
        session.pop('view', None)
    template = '<iframe src="https://open.spotify.com/embed/track/5TxY7O9lFJJrd22FmboAXe" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
    entries = journaling.getAllEntries(session['user'])
    datelist = []
    for entry in entries:
        info = journaling.getEntry(entry)
        date = str(info.get('date'), 'utf-8')
        datelist.append(date)
    content = dict(zip(entries, datelist))
    if request.method == 'POST':
        selection = request.form['entry']
        session['view'] = selection
        return redirect(url_for('viewEntry'))
    if 'song' in session:
        track = template.replace('5TxY7O9lFJJrd22FmboAXe', session['song'])
        return render_template('pages/load_entry.html', content=content, player=Markup(track))
    return render_template('pages/load_entry.html', content=content, player=Markup(template))


@app.route('/view', methods=["POST", "GET"])
def viewEntry():
    form = NetworkForm(request.form)
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'view' not in session:
        return redirect(url_for('loadEntry'))
    ID = session['view']
    entry = journaling.getEntry(ID)
    session['song'] = str(entry.get('song'), 'utf-8')
    template = '<iframe src="https://open.spotify.com/embed/track/5TxY7O9lFJJrd22FmboAXe" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
    track = template.replace('5TxY7O9lFJJrd22FmboAXe', session['song'])
    content = str(entry.get('entry'), 'utf-8')
    mood = str(entry.get('score'), 'utf-8')
    song = utilities.getSong(str(entry.get('song'), 'utf-8'))
    if request.method == 'POST':
        if request.form['action'] == 'Share':
            username = form.name.data
            if(utilities.isUser(username)):
                utilities.shareEntry(username, ID)
                if request.form.get('mood'):
                    utilities.shareMood(username, ID)
                if request.form.get('song'):
                    utilities.shareSong(username, ID)
        elif request.form['action'] == 'Delete':
            journaling.deleteEntry(ID)
            utilities.removeEntry(session['user'], ID)
            return redirect(url_for('home'))
    return render_template('pages/view_entry.html', content=content, mood=mood, song=song, form=form, player=Markup(track))


@app.route('/blacklist', methods=["POST", "GET"])
def blacklist():
    form = NetworkForm(request.form)
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'view' in session:
        session.pop('view', None)
    template = '<iframe src="https://open.spotify.com/embed/track/5TxY7O9lFJJrd22FmboAXe" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
    if request.method == 'POST':
        username = form.name.data
        if request.form['action'] == 'Add':
            if not utilities.isBListed(session['user'], username):
                utilities.addBListed(session['user'], username)
                return redirect(url_for('blacklist'))
        elif request.form['action'] == 'Delete':
            if not utilities.isBListed(session['user'], username):
                utilities.removeBListed(session['user'], username)
                return redirect(url_for('blacklist'))
    strblacklist = utilities.getBList(session['user'])
    strblacklist = strblacklist.replace('{', '')
    strblacklist = strblacklist.replace('}', '')
    blacklist = strblacklist.split(', ')
    if 'song' in session:
        track = template.replace('5TxY7O9lFJJrd22FmboAXe', session['song'])
        return render_template('pages/blacklist.html', blacklist=blacklist, form=form, player=Markup(track))
    return render_template('pages/blacklist.html', blacklist=blacklist, form=form, player=Markup(template))


@app.route('/create', methods=["POST", "GET"])
def createEntry():
    form = JournalForm(request.form)
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'view' in session:
        session.pop('view', None)
    template = '<iframe src="https://open.spotify.com/embed/track/5TxY7O9lFJJrd22FmboAXe" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
    if request.method == 'POST':
        entry = form.body.data
        ID = journaling.createEntry(entry, session['user'])
        utilities.addEntry(session['user'], ID)
        return redirect(url_for('home'))
    if 'song' in session:
        track = template.replace('5TxY7O9lFJJrd22FmboAXe', session['song'])
        return render_template('pages/create_entry.html', form=form, player=Markup(track))       
    return render_template('pages/create_entry.html', form=form, player=Markup(template))


@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm(request.form)
    if 'user' in session:
        return redirect(url_for('home'))
    if 'view' in session:
        session.pop('view', None)
    if request.method == 'POST':
        username = form.name.data
        password = form.password.data
        if utilities.authorize(username, password):
            session['user'] = username
            return redirect(url_for('home'))
    return render_template('forms/login.html', form=form)


@app.route('/logout')
def logout():
    if 'view' in session:
        session.pop('view', None)
    if 'user' in session:
        session.pop('user', None)
        return redirect(url_for('login'))


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm(request.form)
    if 'user' in session:
        return redirect(url_for('home'))
    if 'view' in session:
        session.pop('view', None)
    if request.method == 'POST':
        username = form.name.data
        password = form.password.data
        utilities.register(username, password)
        return redirect(url_for('login'))
    return render_template('forms/register.html', form=form)
    

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

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
