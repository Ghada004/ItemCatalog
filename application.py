from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BookCategory, BookItem

app = Flask(__name__)

engine = create_engine('sqlite:///database_setup.db')
#,connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



# log in route

#bookCategory = {'name': 'Fiction', 'id':'1'}
#bookCategories = [{'name': 'Fiction', 'id':'1'},{'name': 'Inspirational', 'id':'2'},{'name': 'Literature', 'id':'3'}]
#Category item = [{'id': '1', 'title': 'Kafka on the Shore','Author':'Haruki Murakami'}, {'id': '2', 'title': 'If I Could Tell You Just One Thing','Author':'Richard Reed'}, {'id': '3', 'title': 'TO KILL A MOCKINGBIRD ','Author':'Harper Lee'}]


# BookCategory - bookItem

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

# All Book Categories

@app.route('/')
@app.route('/bookCategory/')
def showBookCategory():
    bookCategories = session.query(BookCategory).all()
    return render_template('bookCategories.html', bookCategories=bookCategories)



# Create a new Book Category
@app.route('/bookCategory/new', methods=['GET','POST'])
def newBookCategory():
    if request.method == 'POST':
        newBookCategory = BookCategory(name=request.form['name'])
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
    if request.method == 'POST':
        if request.form['name']:
            editBookCategory.name = request.form['name']
            return redirect(url_for('showBookCategory'))
        else:
            return render_template('editBookCategory.html', bookCategory=editBookCategory)
# return This page will be for editing Category


# Delete a Book Category
@app.route('/bookCategory/<int:bookCategory_id>/delete/', methods=['GET', 'POST'])
def deleteBookCategory(bookCategory_id):
    bookCategoryDelete = session.query(BookCategory).filter_by(id=bookCategory_id).one()
    if request.method == 'POST':
        session.delete(bookCategoryDelete)
        session.commit()
        return redirect(url_for('showBookCategory', bookCategory_id=bookCategory_id))
    else:
        return render_template(
            'deleteCategory.html', bookCategory=bookCategoryDelete)
    # return This page will be for deleting Category

# show a Book Category items
@app.route('/bookCategory/<int:bookCategory_id>/')
@app.route('/bookCategory/<int:bookCategory_id>/bookItem/')
def showCategoryItem(bookCategory_id):
    bookCategory = session.query(BookCategory).filter_by(id=bookCategory_id).one()
    items = session.query(BookItem).filter_by(bookCategory_id=bookCategory_id).all()
    return render_template('category.html', items=items, bookCategory=bookCategory)
    # return This page is the item for Book category


# Create a new Book Category item

@app.route('/bookCategory/<int:bookCategory_id>/bookItem/new/', methods=['GET', 'POST'])
def newBookItem(bookCategory_id):
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
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['author']:
            editedItem.author = request.form['author']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showCategoryItem', bookCategory_id=bookCategory_id))
    else:

        return render_template(
            'edititem.html', bookCategory_id=bookCategory_id, bookItem_id=item_id, bookItem=editedItem)
    # return This page is for editing Book item

# Delete a menu item
@app.route('/bookCategory/<int:bookCategory_id>/item/<int:bookItem_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(bookCategory_id, bookItem_id):
    itemDelete = session.query(cbookItem).filter_by(id=bookItem_id).one()
    if request.method == 'POST':
        session.delete(itemDelete)
        session.commit()
        return redirect(url_for('showCategoryItem', bookCategory_id=bookCategory_id))
    else:
        return render_template('deleteItem.html', bookItem=itemDelete)
    # return "This page is for deleting item


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
