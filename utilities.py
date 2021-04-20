import redisDB

# Authorize user login if credentials match those in database.
def authorize(id, pw):
    if pw == str(redisDB.r.hget(id, 'pw'), 'utf-8'):
        return True
    else:
        return False

# Checks if the specified username exists in the database.
def isUser(username):
    if redisDB.r.hgetall(username):
        return True
    else:
        return False

# Adds the given entry to the given user's entry list.
def addEntry(username, id):
    entries = str(redisDB.r.hget(username, 'entries'), 'utf-8')
    if entries != "{}":
        entries = entries[0:-1] + ', ' + id + '}'
    else:
        entries = '{' + id + '}'
    redisDB.r.hset(username, 'entries', entries)

# Removes the given entry from the given user's entry list. Returns True if successful, False otherwise.
def removeEntry(username, id):
    entries = str(redisDB.r.hget(username, 'entries'), 'utf-8')
    eList = entries[1:-1].split(', ')
    if id in eList: # Check that the entry to be removed exists in the list.
        eList.remove(id)
        entries = '{' + ', '.join(eList) + '}'
        redisDB.r.hset(username, 'entries', entries)
        return True
    else:
        return False
    
# Add user specified by listed to the blacklist of username.
def addBListed(username, listed):
    blacklist = str(redisDB.r.hget(username, 'bl'), 'utf-8')
    if blacklist != "{}":
        blacklist = blacklist[0:-1] + ', ' + listed + '}'
    else:
        blacklist = '{' + listed + '}'
    redisDB.r.hset(username, 'bl', blacklist)

# Remove user specified by listed from the blacklist of username. Returns True if successful, False otherwise.
def removeBListed(username, listed):
    blacklist = str(redisDB.r.hget(username, 'bl'), 'utf-8')
    bList = blacklist[1:-1].split(', ')
    if listed in bList: # Check that the user is blacklisted
        bList.remove(listed)
        blacklist = '{' + ', '.join(bList) + '}'
        redisDB.r.hset(username, 'bl', blacklist)
        return True
    else:
        return False

# Return the blacklist of username.
def getBList(username):
    return str(redisDB.r.hget(username, "bl"), 'utf-8')

# Checks if user specified by listed is on the blacklist of user specified by username.
def isBListed(username, listed):
    blacklist = str(redisDB.r.hget(username, 'bl'), 'utf-8')
    bList = blacklist[1:-1].split(', ')
    if listed in bList:
        return True
    else:
        return False

# Shares the entry specified by id to the user specified by user. Returns True if successful, False otherwise.
# Note: Attempts to share an entry must first be checked for validity before calling shareEntry().
def shareEntry(username, id):
    entries = str(redisDB.r.hget(username, "entries"), 'utf-8')
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
    
    if id not in eList: # Ensure the user is not attempting to send an entry that has already been shared.
        eid = '#' + id[1:] # Add the # indicator to distinguish access level.
        eList.append(eid)
        entries = '{' + ', '.join(eList) + '}'
        redisDB.r.hset(username, 'entries', entries)
        return True
    else:
        return False

# Shares the entry specified by id to the user specified by user, including the entry's mood score. Returns True if successful, False otherwise.
# Note: Attempts to share an entry must first be checked for validity before calling shareMood().
def shareMood(username, id):
    entries = str(redisDB.r.hget(username, "entries"), 'utf-8')
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

    if id not in eList: # Ensure the user is not attempting to send an entry that has already been shared.
        eList.append(mid)
        entries = '{' + ', '.join(eList) + '}'
        redisDB.r.hset(username, 'entries', entries)
        return True
    else:
        return False

# Shares the entry specified by id to the user specified by user, including the entry's mood score and matched song. Returns True if successful, False otherwise.
# Note: Attempts to share an entry must first be checked for validity before calling shareSong().
def shareSong(username, id):
    entries = str(redisDB.r.hget(username, "entries"), 'utf-8')
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

    if id not in eList: # Ensure the user is not attempting to send an entry that has already been shared.
        eList.append(sid)
        entries = '{' + ', '.join(eList) + '}'
        redisDB.r.hset(username, 'entries', entries)
        return True
    else:
        return False

#Retrieves the information on a song based on its URI.
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