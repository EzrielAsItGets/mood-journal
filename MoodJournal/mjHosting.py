from flask import Flask, redirect, url_for, render_template, request, session, flash, Markup
from random import randrange
import mjJournaling
import mjUtil

app = Flask(__name__)
app.secret_key = "403qtnv4q-mnqu4-,b5[o.lsh.pqmcq8m.htlm5ipwimtjvq80[-4.bwmhnr3,,po0-7=-,rmv23[0m6lm3HU3JA;S,.MGSM4QTQ"

@app.route("/", methods=["POST", "GET"])
def home():
    if "user" in session: # If the user is authenticated, render the home page.
        if "view" in session:
            session.pop("view", None)

        if request.method == "POST": # On a POST request, discern which option the user selected and redirect accordingly.
            selection = request.form["entry"] # Save the user's entry selection as session data for the view page.
            if selection == "Create":
                return redirect(url_for("create"))
            elif selection == "Logout":
                session.pop("user", None)
                return redirect(url_for("login"))
            else:
                session["view"] = selection
                return redirect(url_for("view"))

        else: # On a GET request, construct the home page using the user's entries as buttons.
            entries = mjJournaling.getAllEntries(session["user"])
            return render_template("index.html", content=entries)

    else: # If the user is not authenticated, redirect to the login page.
        return redirect(url_for("login"))

@app.route("/login", methods=["POST","GET"])
def login():
    if "user" in session:
        return redirect(url_for("home"))
    else:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if username and password:
                if(mjUtil.authorize(username, password)):
                    session["user"] = username
                    return redirect(url_for("home"))
            flash("Invalid Account!")

        return render_template("login.html")

@app.route("/create", methods=["POST", "GET"])
def create():
    if "user" in session:
        if request.method == "POST":
            entry = request.form["content"]
            id = mjJournaling.createEntry(entry, session["user"])
            mjUtil.addEntry(session["user"], id)
            return redirect(url_for("home"))

        else:
            return render_template("create.html")

    else:
        return redirect(url_for("login"))

@app.route("/view", methods=["POST", "GET"])
def view():
    if "user" in session:
        if "view" in session:
            if request.method == "POST":
                id = session["view"]
                mjJournaling.deleteEntry(id)
                mjUtil.removeEntry(session["user"], id)
                return redirect(url_for("home"))
            else:
                id = session["view"]
                cont = mjJournaling.getEntry(id)
                return render_template("view.html", content=cont)
        else:
            return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
	app.run()