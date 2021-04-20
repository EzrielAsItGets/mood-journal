import redisDB
import uuid
import datetime
import random
import spotipy
from google.cloud import language_v1

# Get the entry specified by id.
def getEntry(id):
    acc = id[0]                # Access level indicator
    sub = '_' + id[1:]         # The id to submit to the database
    entry = redisDB.r.hgetall(sub)
    entryDict = {}             # A dictionary to hold the information to which the user is allowed access
    if entry:
        if acc == '#':         # Just entry shared
            entryDict['date'] = entry[b'date']
            entryDict['entry'] = entry[b'entry']
            entryDict['author'] = entry[b'author']
        elif acc == '$':       # Entry and mood score shared
            entryDict['date'] = entry[b'date']
            entryDict['entry'] = entry[b'entry']
            entryDict['author'] = entry[b'author']
            entryDict['score'] = entry[b'score']
        else:                  # Either the whole thing was shared or this is the user's own entry
            entryDict['date'] = entry[b'date']
            entryDict['entry'] = entry[b'entry']
            entryDict['author'] = entry[b'author']
            entryDict['score'] = entry[b'score']
            entryDict['song'] = entry[b'song']

        return entryDict

    else:
        return False

# Return a list of all entry IDs visible to useredisDB.r.
def getAllEntries(username):
    entries = str(redisDB.r.hget(username, "entries"), 'utf-8')
    eList = entries[1:-1].split(", ")

    return eList

# Create a new journal entry key-value pair in the database with the content specified by entry and the author specified by author.
def createEntry(entry, author):
    date = str(datetime.datetime.now())
    score = getAnalysis(entry)
    song = matchSong(score)

    entryDict = {"date": date, "entry": entry, "score": score, "song": song, "author": author}

    id = str(uuid.uuid4())
    date = str(datetime.date.today())
    id = "_" + date + '|' + str(id) # Convert ID to a string prepended by an underscore (an identifier to distinguish users and entries in the database)
    while redisDB.r.hgetall(id): # uuid4 has a small (but real) chance to generate two identical IDs. This check ensures that an entry in the database never gets overwritten.
        id = str(uuid.uuid4())
        id = "_" + str(id)

    redisDB.r.hset(name=id, mapping=entryDict)

    return id

# Remove the entry specified by id from the database.
def deleteEntry(id):
    redisDB.r.delete(id)

# Calls Google Cloud's Natural Language Processing API to analyze and provide a sentiment score to a journal entry.
def getAnalysis(entry):
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=entry, type_=language_v1.Document.Type.PLAIN_TEXT)

    response = client.analyze_sentiment(document=document)

    sentiment = response.document_sentiment
    score = round(sentiment.score, 1)

    return score

# Matches the sentiment score of a journal entry to a song in the database.
def matchSong(score):
    strscore = '!' + str(score)
    if redisDB.r.get(strscore):
        strsonglist = str(redisDB.r.get(strscore), encoding='utf-8')
        songlist = strsonglist.split(', ')
        song = random.choice(songlist)
        return song
    else:
        for i in range (1, 9): # If the score is not found in the songs database, it will modify the passed score until one is found
            i /= 10
            newscore = score + i
            strscore = '!' + str(newscore)
            if redisDB.r.get(strscore):
                strsonglist = str(redisDB.r.get(strscore), encoding='utf-8')
                songlist = strsonglist.split(', ')
                song = random.choice(songlist)
                return song
            else:
                newscore = score - i
                strscore = '!' + str(newscore)
                if redisDB.r.get(strscore):
                    strsonglist = str(redisDB.r.get(strscore), encoding='utf-8')
                    songlist = strsonglist.split(', ')
                    song = random.choice(songlist)
                    return song
            score = newscore
            i *= 10