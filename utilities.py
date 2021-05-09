import redisDB
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Register the user with the provided username. Returns True if successful, False if the name already exists.
def register(username, password):
    if not isUser(username):
        user = {}
        user['pw'] = password
        user['entries'] = '{}'
        user['bl'] = '{}'
        redisDB.r.hmset(name=username, mapping=user)
        return True
    else:
        return False

# Delete the account associated with username. Iterate through the user's entry list, deleting all entries as well.
def deleteAccount(username):
    entries = redisDB.toString(redisDB.r.hget(username, "entries"))
    eList = entries[1:-1].split(", ")
    for entry in eList:
        redisDB.r.delete(entry)

    redisDB.r.delete(username)

# Authorize user login if credentials match those in database. Returns True if successful, false otherwise.
def authorize(id, pw):
    if redisDB.r.hget(id, 'pw'):
        if pw == redisDB.toString(redisDB.r.hget(id, 'pw')):
            return True

    return False

# Checks if the specified username exists in the database.
def isUser(username):
    if redisDB.r.hgetall(username):
        return True
    else:
        return False

# Adds the given entry to the given user's entry list.
def addEntry(username, id):
    entries = redisDB.toString(redisDB.r.hget(username, 'entries'))
    if entries != "{}":
        entries = entries[0:-1] + ', ' + id + '}'
    else:
        entries = '{' + id + '}'
    redisDB.r.hset(username, 'entries', entries)

# Removes the given entry from the given user's entry list. Returns True if successful, False otherwise.
def removeEntry(username, id):
    entries = redisDB.toString(redisDB.r.hget(username, 'entries'))
    eList = entries[1:-1].split(', ')
    if id in eList: # Check that the entry to be removed exists in the list.
        eList.remove(id)
        entries = '{' + ', '.join(eList) + '}'
        redisDB.r.hset(username, 'entries', entries)
        return True
    else:
        return False
    
# Add user specified by listed to the blacklist of username. Returns True if successful, False if the user is already blacklisted.
def addBListed(username, listed):
    if not isBListed(username, listed):
        blacklist = redisDB.toString(redisDB.r.hget(username, 'bl'))
        if blacklist != "{}":
            blacklist = blacklist[0:-1] + ', ' + listed + '}'
        else:
            blacklist = '{' + listed + '}'
        redisDB.r.hset(username, 'bl', blacklist)
        return True
    else:
        return False

# Remove user specified by listed from the blacklist of username. Returns True if successful, False if the user is not already blacklisted.
def removeBListed(username, listed):
    if isBListed(username, listed):
        blacklist = redisDB.toString(redisDB.r.hget(username, 'bl'))
        bList = blacklist[1:-1].split(', ')
        bList.remove(listed)
        blacklist = '{' + ', '.join(bList) + '}'
        redisDB.r.hset(username, 'bl', blacklist)
        return True
    else:
        return False

# Return the blacklist of username.
def getBList(username):
    return redisDB.toString(redisDB.r.hget(username, "bl"))

# Check if user specified by listed is on the blacklist of user specified by username.
def isBListed(username, listed):
    blacklist = redisDB.toString(redisDB.r.hget(username, 'bl'))
    bList = blacklist[1:-1].split(', ')
    if listed in bList:
        return True
    else:
        return False

# Shares the entry specified by id to the user specified by user.
# Note: Attempts to share an entry must first be checked for validity before calling shareEntry().
def shareEntry(username, id):
    entries = redisDB.toString(redisDB.r.hget(username, "entries"))
    eList = entries[1:-1].split(", ")
    if entries != '{}':
        eList = entries[1:-1].split(", ")
    else:
        eList = []

    # Check if this entry has already been sent with different permissions.
    eid = '#' + id[1:]
    mid = '$' + id[1:]
    sid = '%' + id[1:]
    if eid in eList:
        eList.remove(eid)
    elif mid in eList:
        eList.remove(mid)
    elif sid in eList:
        eList.remove(sid)
    
    eid = '#' + id[1:] # Add the # indicator to distinguish access level.
    eList.append(eid)
    entries = '{' + ', '.join(eList) + '}'
    redisDB.r.hset(username, 'entries', entries)

# Shares the entry specified by id to the user specified by user, including the entry's mood score.
# Note: Attempts to share an entry must first be checked for validity before calling shareMood().
def shareMood(username, id):
    entries = redisDB.toString(redisDB.r.hget(username, "entries"))
    if entries != '{}':
        eList = entries[1:-1].split(", ")
    else:
        eList = []

    # Check if this entry has already been sent with different permissions.
    eid = '#' + id[1:]
    mid = '$' + id[1:]
    sid = '%' + id[1:]
    if eid in eList:
        eList.remove(eid)
    elif mid in eList:
        eList.remove(mid)
    elif sid in eList:
        eList.remove(sid)

    eList.append(mid)
    entries = '{' + ', '.join(eList) + '}'
    redisDB.r.hset(username, 'entries', entries)

# Shares the entry specified by id to the user specified by user, including the entry's mood score and matched song.
# Note: Attempts to share an entry must first be checked for validity before calling shareSong().
def shareSong(username, id):
    entries = redisDB.toString(redisDB.r.hget(username, "entries"))
    eList = entries[1:-1].split(", ")
    if entries != '{}':
        eList = entries[1:-1].split(", ")
    else:
        eList = []

    # Check if this entry has already been sent with different permissions.
    eid = '#' + id[1:]
    mid = '$' + id[1:]
    sid = '%' + id[1:]
    if eid in eList:
        eList.remove(eid)
    elif mid in eList:
        eList.remove(mid)
    elif sid in eList:
        eList.remove(sid)

    eList.append(sid)
    entries = '{' + ', '.join(eList) + '}'
    redisDB.r.hset(username, 'entries', entries)


# Retrieves the information on a song based on its URI.
def getSong(URI):
    scope = 'user-library-read'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    song_info = sp.track(track_id = URI)

    for dictionary in song_info['album']['artists']:
        try:
            dictionary['name']
        except KeyError:
            pass

    song_name = str(song_info['name']) + ' by ' + str(dictionary['name'])

    return song_name


# Updates the user's current mood and song to the last created entry.
def updateCurrent(username, id):
    redisDB.r.hset(username, 'current', id)


# Gets the user's current mood and song.
def getCurrent(username):
    current = redisDB.r.hget(username, 'current')
    
    if current != None:
        return str(current, 'utf-8')
    else:
        return None

# Validates username input on the registration page by checking for invalid first characters.
def validateString(username):
    invalidchars = ['"', "'", '{', '}', '!', '#', '$', '%', '_', ' ']

    if username[0] in invalidchars:
        return False
    else:
        return True