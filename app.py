#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, redirect, url_for, render_template, request, session
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


@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'view' in session:
        session.pop('view', None)
    return render_template('pages/home.html')


@app.route('/load', methods=["POST", "GET"])
def loadEntry():
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'view' in session:
        session.pop('view', None)
    content = journaling.getAllEntries(session['user'])  
    if request.method == 'POST':
        selection = request.form['entry']
        session['view'] = selection
        return redirect(url_for('viewEntry'))
    return render_template('pages/load_entry.html', content=content)


@app.route('/view', methods=["POST", "GET"])
def viewEntry():
    form = NetworkForm(request.form)
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'view' not in session:
        return redirect(url_for('loadEntry'))
    ID = session['view']
    entry = journaling.getEntry(ID)
    content = str(entry.get('entry'), 'utf-8')
    mood = str(entry.get('score'), 'utf-8')
    song = str(entry.get('song'), 'utf-8')
    if request.method == 'POST':
        if request.form['action'] == 'Share':
            username = form.name.data
            utilities.shareEntry(username, ID)
            if request.form.get('mood'):
                utilities.shareMood(username, ID)
            if request.form.get('song'):
                utilities.shareSong(username, ID)
        elif request.form['action'] == 'Delete':
            journaling.deleteEntry(ID)
            utilities.removeEntry(session['user'], ID)
            return redirect(url_for('home'))
    return render_template('pages/view_entry.html', content=content, mood=mood, song=song, form=form)


@app.route('/create', methods=["POST", "GET"])
def createEntry():
    form = JournalForm(request.form)
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'view' in session:
        session.pop('view', None)
    if request.method == 'POST':
        entry = form.body.data
        ID = journaling.createEntry(entry, session['user'])
        utilities.addEntry(session['user'], ID)
        return redirect(url_for('home'))    
    return render_template('pages/create_entry.html', form=form)


@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm(request.form)
    if 'user' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = form.name.data
        password = form.password.data
        if utilities.authorize(username, password):
            session['user'] = username
            return redirect(url_for('home'))
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)
    

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
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
