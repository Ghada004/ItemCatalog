#!/usr/bin/env python
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BookCategory, BookItem, User
# New imports for this step #2
from flask import session as login_session
import random
import string
# IMPORTS FOR THIS STEP #5
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# import oauth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)



CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "ItemCatalog"

# Connect to Database and create database session
engine = create_engine('sqlite:///database_setup.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

         # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['photo'] = data['photo']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

        # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['photo']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['photo']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


#bookCategory = {'name': 'Fiction', 'id':'1'}
#bookCategories = [{'name': 'Fiction', 'id':'1'},{'name': 'Inspirational', 'id':'2'},{'name': 'Literature', 'id':'3'}]
#Category item = [{'id': '1', 'title': 'Kafka on the Shore','Author':'Haruki Murakami'}, {'id': '2', 'title': 'If I Could Tell You Just One Thing','Author':'Richard Reed'}, {'id': '3', 'title': 'TO KILL A MOCKINGBIRD ','Author':'Harper Lee'}]


# BookCategory - bookItem
# JSON APIs to view Book Category Information
@app.route('/bookCategory/<int:bookCategory_id>/bookItem/JSON')
def bookCategoryJSON(bookCategory_id):
    bookCategory = session.query(BookCategory).filter_by(id=bookCategory_id).one()
    items = session.query(BookItem).filter_by(bookCategory_id=bookCategory_id).all()
    return jsonify(BookItem=[i.serialize for i in items])

@app.route('/bookCategory/<int:bookCategory_id>/bookItem/<int:bookItem_id>/JSON')
def menuItemJSON(bookCategory_id, BookItem_id):
    Book_Item = session.query(BookItem).filter_by(id=BookItem_id).one()
    return jsonify(Book_Item=Book_Item.serialize)


@app.route('/bookCategory/JSON')
def bookCategoriesJSON():
    bookCategories = session.query(BookCategory).all()
    return jsonify(bookCategories=[b.serialize for b in bookCategories])

# SHOW All Book Categories

@app.route('/')
@app.route('/bookCategory/')
def showBookCategory():
    bookCategories = session.query(BookCategory).order_by(asc(BookCategory.name))
    if 'username' not in login_session:
        return render_template('publicCategory.html', bookCategories=bookCategories)
    else:
        return render_template('bookCategories.html', bookCategories=bookCategories)


# Create a new Book Category
@app.route('/bookCategory/new', methods=['GET','POST'])
def newBookCategory():
    if 'username' not in login_session:
        return redirect ('/login')
    if request.method == 'POST':
        newBookCategory = BookCategory(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newBookCategory)
        session.commit()
        return redirect(url_for('showBookCategory'))
    else:
        return render_template('newBookCategory.html')
# return This page will be for making a new Book Category


# Edit a Book Category
@app.route('/bookCategory/<int:bookCategory_id>/edit', methods=['GET', 'POST'])
def editBookCategory(bookCategory_id):
    editBookCategory = session.query(BookCategory).filter_by(id=bookCategory_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editBookCategory.user_id != login_session ['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this Book Category. Please create your own Category in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editBookCategory.name = request.form['name']
            flash('bookCategory Successfully Edited %s' % editBookCategory.name)
            return redirect(url_for('showBookCategory'))
        else:
            return render_template('editBookCategory.html', bookCategory=editBookCategory)
# return This page will be for editing Category


# Delete a Book Category
@app.route('/bookCategory/<int:bookCategory_id>/delete/', methods=['GET', 'POST'])
def deleteBookCategory(bookCategory_id):
    bookCategoryDelete = session.query(BookCategory).filter_by(id=bookCategory_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if deleteBookCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this book Category. Please create your own book Category in order to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(bookCategoryDelete)
        flash('%s Successfully Deleted' % deleteBookCategory.name)
        session.commit()
        return redirect(url_for('showBookCategory', bookCategory_id=bookCategory_id))
    else:
        return render_template('deleteCategory.html', bookCategory=bookCategoryDelete)
    # return This page will be for deleting Category

# show a Book Category items
@app.route('/bookCategory/<int:bookCategory_id>/')
@app.route('/bookCategory/<int:bookCategory_id>/bookItem/')
def showCategoryItem(bookCategory_id):
    bookCategory = session.query(BookCategory).filter_by(id=bookCategory_id).one()
    creator = getUserInfo(restaurant.user_id)
    items = session.query(BookItem).filter_by(bookCategory_id=bookCategory_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicBookCategory.html', items=items, bookCategory=bookCategory, creator=creator)
    else:
        return render_template('category.html', items=items, bookCategory=bookCategory, creator=creator)



# Create a new Book Category item

@app.route('/bookCategory/<int:bookCategory_id>/bookItem/new/', methods=['GET', 'POST'])
def newBookItem(bookCategory_id):
    if 'username' not in login_session:
        return redirect('/login')
    bookCategory = session.query(BookCategory).filter_by(id=bookCategory_id).one()
    if login_session['user_id'] != bookCategory.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add Book items to this  Category. Please create your own Book in order to add items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        newItem = bookItem(title=request.form['title'], author=request.form['author'], bookCategory_id=bookCategory_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCategoryItem', bookCategory_id=bookCategory_id))
    else:
        return render_template('newcategoryitem.html', bookCategory_id=bookCategory_id)

    return render_template('newcategoryitem.html', bookCategory=bookCategory)
    # return 'This page is for making a new Book item for Category

# Edit a Book item
@app.route('/bookCategory/<int:bookCategory_id>/bookItem/<int:bookItem_id>/edit', methods=['GET', 'POST'])
def editCategoryItem(bookCategory_id, bookItem_id):
    editedItem = session.query(bookItem).filter_by(id=bookItem_id).one()
    bookCategory = session.query(BookCategory).filter_by(id=bookCategory_id).one()
    if login_session['user_id'] != bookCategory.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit menu Book to this Category. Please create your own Book in order to edit items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['author']:
            editedItem.author = request.form['author']
        session.add(editedItem)
        session.commit()
        flash('Book Item Successfully Edited')
        return redirect(url_for('showCategoryItem', bookCategory_id=bookCategory_id))
    else:

        return render_template(
            'edititem.html', bookCategory_id=bookCategory_id, bookItem_id=item_id, bookItem=editedItem)
    # return This page is for editing Book item

# Delete a menu item
@app.route('/bookCategory/<int:bookCategory_id>/item/<int:bookItem_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(bookCategory_id, bookItem_id):
    if 'username' not in login_session:
        return redirect('/login')
    bookCategory = session.query(BookCategory).filter_by(id=bookCategory_id).one()
    itemDelete = session.query(cbookItem).filter_by(id=bookItem_id).one()
    if login_session['user_id'] != bookCategory.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete Book items to this Category. Please create your own Book in order to delete items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showCategoryItem', bookCategory_id=bookCategory_id))
    else:
        return render_template('deleteItem.html', bookItem=itemDelete)
    # return "This page is for deleting item

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        flash("You have successfully been logged out.")
        return redirect(url_for('showBookCategory'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showBookCategory'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
