from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file, g, jsonify
from datetime import timedelta

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = "asdfghjkl"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phillyhops.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=5)

db = SQLAlchemy(app)


class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key= True)
    username = db.Column(db.String(100))
    dob = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, username, dob, email, password):
        self.username = username
        self.dob = dob
        self.email = email
        self.password = password


class Favorites(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    beer_id = db.Column(db.Integer)
    location_id = db.Column(db.Integer)

    def __init__(self, user_id, beer_id, location_id):
        self.user_id = user_id
        self.beer_id = beer_id
        self.location_id = location_id


class Beer(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    brewery = db.Column(db.String(100))
    desc = db.Column(db.String(100))
    image = db.Column(db.String(100))

    def __init__(self, name, brewery, desc, image):
        self.name = name
        self.brewery = brewery
        self.desc = desc
        self.image = image


class Location(db.Model):
    _id = db.Column("id", db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    desc = db.Column(db.String(100))
    image = db.Column(db.String(100))

    def __init__(self, name, location, desc, image):
        self.name = name
        self.location = location
        self.desc = desc
        self.image = image


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/locations')
def locations():
    return render_template("locationlist.html")


@app.route('/beers')
def beers():
    return render_template('beerlist.html')


@app.route('/api/beers')
def api_beers():
    beer = Beer.query.all()
    return jsonify([{
            'id': d._id,
            'name': d.name,
            'brewery': d.brewery,
            'desc': d.desc,
            'image': d.image
        } for d in beer])


@app.route('/api/locations')
def api_locations():
    location = Location.query.all()
    return jsonify([{
        'id': d._id,
        'name': d.name,
        'location': d.location,
        'desc': d.desc,
        'image': d.image
    }for d in location])


@app.route('/api/search', methods=['GET', 'POST'])
def api_getAll():

    items = []

    location = Location.query.all()
    beer = Beer.query.all()

    for item in location:
        items.append(item)
    for item in beer:
        items.append(item)

    print(items)
    return jsonify([{
        'name': d.name,
        'desc': d.desc,
        'image': d.image
    }for d in items])


@app.route('/api/favorite', methods=['GET', 'POST'])
def api_favorite():
    if "username" in session:

        user_found = Users.query.filter_by(username=session["username"]).first()

        if request.form['name'] == 'beer_id':
            beer_id = request.form['id']
            db.session.add(Favorites(user_found._id, beer_id, None))
            db.session.commit()
            return "", 204

        if request.form['name'] == 'location_id':
            location_id = request.form['id']
            db.session.add(Favorites(user_found._id, None, location_id))
            db.session.commit()
            return "", 204
    else:
        flash("Need to be signed in to favorite")
        return render_template(url_for("login"))


@app.route('/api/getFavorites')
def api_getFavorites():
    user_found = Users.query.filter_by(username=session["username"]).first()

    items = []

    favorites = Favorites.query.filter_by(user_id=user_found._id)

    for favorite in favorites:
        if favorite.location_id is None:
            beer = Beer.query.filter_by(_id=favorite.beer_id).first()
            items.append(beer)
        elif favorite.beer_id is None:
            location = Location.query.filter_by(_id=favorite.location_id).first()
            items.append(location)

    return jsonify([{
        'id': d._id,
        'name': d.name,
        'desc': d.desc,
        'image': d.image
    }for d in items])



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/register', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        dob = request.form['dob']
        pwd = request.form['pwd']
        confirmpwd = request.form['confirmpwd']

        user_found = Users.query.filter_by(email=email).first()
        if user_found:
            flash("Account already exists.")
            return render_template("register.html")
        else:
            new_usr = Users(username, dob, email, pwd)
            db.session.add(new_usr)
            db.session.commit()
            flash("Account Created")
            return redirect(url_for("login"))
    else:
        if "username" in session:
            return redirect(url_for("user"))
        return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.permanent = True
        username = request.form["username"]
        pwd = request.form["pwd"]

        user_found = Users.query.filter_by(username=username).first()

        if str(user_found.password) == str(pwd):
            session["username"] = username
            return redirect(url_for("user"))
        else:
            return redirect(url_for("login"))
    else:
        if "username" in session:
            #print(session)
            return redirect(url_for("user"))
        return render_template("login.html")


@app.route('/user', methods=['GET', 'POST'])
def user():
    if "username" in session:
        print(session)
        username = session["username"]
        return render_template("profile.html", username=username)
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
