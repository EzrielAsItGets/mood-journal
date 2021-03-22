import redis

r = redis.Redis(host = "redis-17190.c99.us-east-1-4.ec2.cloud.redislabs.com", port = "17190", password = "LDMwbQfGPmB8RRyDt3X4ZujdF8JguKAi")

# Authorize user login if credentials match those in database
def authorize(id, pw):
    if pw == str(r.hget(id, "pw"), 'utf-8'):
        return True
    else:
        return False

# Adds the given entry to the given user's entry list.
def addEntry(username, id):
    entries = str(r.hget(username, "entries"), 'utf-8')
    entries = entries[0:-1] + ", " + id + "}"
    r.hset(username, "entries", entries)

# Removes the given entry from the given user's entry list.
def removeEntry(username, id):
    entries = str(r.hget(username, "entries"), 'utf-8')
    eList = entries[1:-1].split(", ")
    if id in eList:
        eList.remove(id)
        entries = '{' + ', '.join(eList) + '}'
        r.hset(username, "entries", entries)
    
