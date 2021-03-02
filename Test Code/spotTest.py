import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, redirect, url_for, render_template, request, session, flash, Markup
from random import randrange

app = Flask(__name__)
app.secret_key = "403qtnv4q-mnqu4-,b5[o.lsh.pqmcq8m.htlm5ipwimtjvq80[-4.bwmhnr3,,po0-7=-,rmv23[0m6lm3HU3JA;S,.MGSM4QTQ"

playlist = ['<iframe src="https://open.spotify.com/embed/track/5TxY7O9lFJJrd22FmboAXe" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', '<iframe src="https://open.spotify.com/embed/track/64Kk49W8HFh22diWSBVxCr" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', '<iframe src="https://open.spotify.com/embed/track/4VbxZbS5Vrwr8nnHCFBiXx" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>']

@app.route("/", methods=["POST", "GET"])
def home():
    track = playlist[randrange(3)]
    return render_template("index.html", content = Markup(track))

if __name__ == "__main__":
	app.run()

#scope = "user-library-read"

#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = '2c347209b77449179a23b34de1d9bfa3', client_secret = 'b08c052d36124228ab2531ffae7bf73a', redirect_uri = 'http://localhost:8080', scope=scope))

# results = sp.current_user_saved_tracks()
# for idx, item in enumerate(results['items']):
#    track = item['track']
#    print(idx, track['artists'][0]['name'], " – ", track['name'])

#stock = sp.track(track_id = '5TxY7O9lFJJrd22FmboAXe')

#print(stock['external_urls'])
