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

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# Render the home page.
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


# Render the load entry page.
@app.route('/load', methods=["POST", "GET"])
def loadEntry():
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'view' in session:
        session.pop('view', None)

    template = '<iframe src="https://open.spotify.com/embed/track/5TxY7O9lFJJrd22FmboAXe" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
    entries = journaling.getAllEntries(session['user'])
    datelist = []
    authorlist = []
    authordate = []

    # Call each individual entry's information with the loop and extract information for front-end rendering.
    for entry in entries:
        info = journaling.getEntry(entry)
        if info != False:
            date = str(info.get('date'), 'utf-8') + ' - '
            datelist.append(date)
            author = str(info.get('author'), 'utf-8')
            authorlist.append(author)
        else:
            utilities.removeEntry(session['user'], entry)

    mergedlist = tuple(zip(datelist, authorlist))

    for item in mergedlist:
        authordate.append(''.join(item))

    content = dict(zip(entries, authordate)) # Combines each entry's UUID with its date and author in a dictionary data structure for front-end rendering

    if request.method == 'POST':
        selection = request.form['entry']
        session['view'] = selection
        return redirect(url_for('viewEntry'))

    if 'song' in session:
        track = template.replace('5TxY7O9lFJJrd22FmboAXe', session['song'])
        return render_template('pages/load_entry.html', content=content, player=Markup(track))

    return render_template('pages/load_entry.html', content=content, player=Markup(template))


# Render the view entry page.
@app.route('/view', methods=["POST", "GET"])
def viewEntry():
    form = NetworkForm(request.form)

    if 'user' not in session:
        return redirect(url_for('login'))
    if 'view' not in session:
        return redirect(url_for('loadEntry'))

    ID = session['view']
    entry = journaling.getEntry(ID)

    # Sharing functions allow incomplete entries, so the elements must be ensured to exist before rendering them on the page.
    if entry.get('song'):
        session['song'] = str(entry.get('song'), 'utf-8')
        template = '<iframe src="https://open.spotify.com/embed/track/5TxY7O9lFJJrd22FmboAXe" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
        track = template.replace('5TxY7O9lFJJrd22FmboAXe', session['song'])
        song = utilities.getSong(str(entry.get('song'), 'utf-8'))
    else:
        track = '<iframe src="https://open.spotify.com/embed/track/5TxY7O9lFJJrd22FmboAXe" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
        song = 'Not Shared'

    if entry.get('score'):
        mood = str(entry.get('score'), 'utf-8')
    else:
        mood = 'Not Shared'

    content = str(entry.get('entry'), 'utf-8')

    if request.method == 'POST':
        if request.form['action'] == 'Share':
            if session['user'] == str(entry.get('author'), 'utf-8'):           # Prevent sharing other people's entries
                username = form.name.data
                if(utilities.isUser(username)):                                # Prevent sharing with non-existent users
                    if username != session['user']:                            # Prevent sharing an entry with yourself
                        if not utilities.isBListed(username, session['user']): # Prevent blacklisted users from sharing
                            if request.form.get('mood'):
                                utilities.shareMood(username, ID)
                            elif request.form.get('song'):
                                utilities.shareSong(username, ID)
                            else:
                                utilities.shareEntry(username, ID)
        elif request.form['action'] == 'Delete':
            # Calling delete on a shared ID will not remove anything from the database, as shared IDs have flags to indicate they were shared.
            journaling.deleteEntry(ID)
            # The ID will be removed from the entry list, thus "un-sharing" it.
            utilities.removeEntry(session['user'], ID)
            return redirect(url_for('home'))

    return render_template('pages/view_entry.html', content=content, mood=mood, song=song, form=form, player=Markup(track))


# Render the share current page.
@app.route('/share', methods=["POST", "GET"])
def shareCurrent():
    form = NetworkForm(request.form)

    if 'user' not in session:
        return redirect(url_for('login'))
    if 'view' in session:
        session.pop('view', None)

    template = '<iframe src="https://open.spotify.com/embed/track/5TxY7O9lFJJrd22FmboAXe" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'

    if request.method == 'POST':
        if request.form['action'] == 'Share':
            username = form.name.data
            if(utilities.isUser(username)):                                # Prevent sharing with non-existent users
                if username != session['user']:                            # Prevent sharing an entry with yourself
                    if not utilities.isBListed(username, session['user']): # Prevent blacklisted users from sharing
                        current = utilities.getCurrent(session['user'])
                        if current != None:
                            utilities.shareSong(username, current)

    if 'song' in session:
        track = template.replace('5TxY7O9lFJJrd22FmboAXe', session['song'])
        return render_template('pages/share_current.html', form=form, player=Markup(track))

    return render_template('pages/share_current.html', form=form, player=Markup(template))

# Render the blacklist page.
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
        if username != session['user']:    # Prevent blacklisting yourself
            if utilities.isUser(username): # Prevent blacklisting a non-existent user
                if request.form['action'] == 'Add':
                    utilities.addBListed(session['user'], username) #TODO: incorporate the return for error message
                    return redirect(url_for('blacklist'))
                elif request.form['action'] == 'Delete':
                    utilities.removeBListed(session['user'], username) #TODO: incorporate the return for error messages
                    return redirect(url_for('blacklist'))

    strblacklist = utilities.getBList(session['user'])
    strblacklist = strblacklist.replace('{', '')
    strblacklist = strblacklist.replace('}', '')
    blacklist = strblacklist.split(', ')

    if 'song' in session:
        track = template.replace('5TxY7O9lFJJrd22FmboAXe', session['song'])
        return render_template('pages/blacklist.html', blacklist=blacklist, form=form, player=Markup(track))

    return render_template('pages/blacklist.html', blacklist=blacklist, form=form, player=Markup(template))


# Render the create entry page.
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
        utilities.updateCurrent(session['user'], ID)
        return redirect(url_for('home'))

    if 'song' in session:
        track = template.replace('5TxY7O9lFJJrd22FmboAXe', session['song'])
        return render_template('pages/create_entry.html', form=form, player=Markup(track))

    return render_template('pages/create_entry.html', form=form, player=Markup(template))


# Render the login page.
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


# Logs out the user and purges session data.
@app.route('/logout')
def logout():
    if 'song' in session:
        session.pop('song', None)

    if 'view' in session:
        session.pop('view', None)

    if 'user' in session:
        session.pop('user', None)
        return redirect(url_for('login'))


# Render the registration page.
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
        utilities.register(username, password) # TODO: use the return to flash an error message
        return redirect(url_for('login'))
        
    return render_template('forms/register.html', form=form)


# Render the delete account page.
@app.route('/delete', methods=["POST", "GET"])
def delete():
    form = LoginForm(request.form)

    if 'user' in session:
        return redirect(url_for('home'))

    if 'view' in session:
        session.pop('view', None)

    if request.method == 'POST':
        username = form.name.data
        password = form.password.data
        if utilities.authorize(username, password):
            utilities.deleteAccount(username)
            return redirect(url_for('register'))

    return render_template('forms/delete.html', form=form)


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
