import redisDB

def authorize(id, pw):
    if pw == str(redisDB.r.hget(id, 'pw'), 'utf-8'):
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

# Removes the given entry from the given user's entry list.
def removeEntry(username, id):
    entries = str(redisDB.r.hget(username, 'entries'), 'utf-8')
    eList = entries[1:-1].split(', ')
    if id in eList:
        eList.remove(id)
        entries = '{' + ', '.join(eList) + '}'
        redisDB.r.hset(username, 'entries', entries)
    
# Add user specified by listed to the blacklist of username.
def addBListed(username, listed):
    blacklist = str(redisDB.r.hget(username, 'bl'), 'utf-8')
    if blacklist != "{}":
        blacklist = blacklist[0:-1] + ', ' + listed + '}'
    else:
        blacklist = '{' + listed + '}'
    redisDB.r.hset(username, 'bl', blacklist)

# Remove user specified by listed from the blacklist of username.
def removeBListed(username, listed):
    blacklist = str(redisDB.r.hget(username, 'bl'), 'utf-8')
    bList = blacklist[1:-1].split(', ')
    if listed in bList:
        bList.remove(listed)
        blacklist = '{' + ', '.join(bList) + '}'
        redisDB.r.hset(username, 'bl', blacklist)

# Return the blacklist of username.
def getBList(username):
    return str(redisDB.r.hget(username, "bl"), 'utf-8')