import redis

r = redis.Redis(host = "redis-17190.c99.us-east-1-4.ec2.cloud.redislabs.com", port = "17190", password = "LDMwbQfGPmB8RRyDt3X4ZujdF8JguKAi")

# Authorize user login if credentials match those in database
def authorize(id, pw):
    if pw == str(r.hget(id, 'pw'), 'utf-8'):
        return True
    else:
        return False

# Adds the given entry to the given user's entry list.
def addEntry(username, id):
    entries = str(r.hget(username, 'entries'), 'utf-8')
    if entries != "{}":
        entries = entries[0:-1] + ', ' + id + '}'
    else:
        entries = '{' + id + '}'
    r.hset(username, 'entries', entries)

# Removes the given entry from the given user's entry list.
def removeEntry(username, id):
    entries = str(r.hget(username, 'entries'), 'utf-8')
    eList = entries[1:-1].split(', ')
    if id in eList:
        eList.remove(id)
        entries = '{' + ', '.join(eList) + '}'
        r.hset(username, 'entries', entries)
    
# Add user specified by listed to the blacklist of username.
def addBListed(username, listed):
    blacklist = str(r.hget(username, 'bl'), 'utf-8')
    if blacklist != "{}":
        blacklist = blacklist[0:-1] + ', ' + listed + '}'
    else:
        blacklist = '{' + listed + '}'
    r.hset(username, 'bl', blacklist)

# Remove user specified by listed from the blacklist of username.
def removeBListed(username, listed):
    blacklist = str(r.hget(username, 'bl'), 'utf-8')
    bList = blacklist[1:-1].split(', ')
    if listed in bList:
        bList.remove(listed)
        blacklist = '{' + ', '.join(bList) + '}'
        r.hset(username, 'bl', blacklist)

# Return the blacklist of username.
def getBList(username):
    return str(r.hget(username, "bl"), 'utf-8')