import redis
import uuid
import datetime
from google.cloud import language_v1

r = redis.Redis(host = "redis-17190.c99.us-east-1-4.ec2.cloud.redislabs.com", port = "17190", password = "LDMwbQfGPmB8RRyDt3X4ZujdF8JguKAi")

# Get the entry specified by id.
def getEntry(id):
    return r.hgetall(id)

# Return a list of all entry IDs visible to user.
def getAllEntries(user):
    entries = str(r.hget(user, "entries"), 'utf-8')
    eList = entries[1:-1].split(", ")

    return eList

# Create a new journal entry key-value pair in the database with the content specified by entry and the author specified by author.
def createEntry(entry, author):
    date = str(datetime.datetime.now())
    score = getAnalysis(entry)
    song = matchSong(entry)

    entryDict = {"date": date, "entry": entry, "score": score, "song": song, "author": author}

    id = str(uuid.uuid4())
    id = "_" + str(id) # Convert ID to a string prepended by an underscore (an identifier to distinguish users and entries in the database)
    while r.hgetall(id): # uuid4 has a small (but real) chance to generate two identical IDs. This check ensures that an entry in the database never gets overwritten.
        id = str(uuid.uuid4())
        id = "_" + str(id)

    r.hset(name=id, mapping=entryDict)

    return id

# Remove the entry specified by id from the database.
def deleteEntry(id):
    r.delete(id)

# To be changed upon API integration
def getAnalysis(entry):
    client = language_v1.LanguageServiceClient.from_service_account_json("Mood Journal-4c2d58f1d4d1.json")
    document = language_v1.Document(content=entry, type_=language_v1.Document.Type.PLAIN_TEXT)

    response = client.analyze_sentiment(document=document)

    sentiment = response.document_sentiment
    score = round(sentiment.score, 1)

    return score

def matchSong(entry):
    return "spotify:track:5SlKhaPcdIfSjpoM2QtM4C"