#Books DB

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, BookCategory, BookItem

engine = create_engine('sqlite:///bookcategorywithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()




# Create dummy user
User1 = User(name="Alex", email="Alex@example.com",
             photo='https://app.box.com/s/c1rfi7yyc55umhs4z6tgi69wudur2vrf')
session.add(User1)
session.commit()


# Book Category #1
category1 = BookCategory(user_id=1, name="Fiction")

session.add(category1)
session.commit()

BookItem1 = BookItem(user_id=1, title="Kafka on the Shore", author="Haruki Murakami", bookCategory=category1)

session.add(BookItem1)
session.commit()

BookItem2 = BookItem(user_id=1, title="harp Objects", author="Gillian Flynn", bookCategory=category1)

session.add(BookItem2)
session.commit()

BookItem3 = BookItem(user_id=1, title="The Girl on the Train", author="Paula Hawkins", bookCategory=category1)

session.add(BookItem3)
session.commit()

# Book Category #2

category2 = BookCategory(user_id=1, name="Inspirational")

session.add(category2)
session.commit()

BookItem1 = BookItem(user_id=1, title="If I Could Tell You Just One Thing", author="Richard Reed", bookCategory=category2)

session.add(BookItem1)
session.commit()

BookItem2 = BookItem(user_id=1, title="The Alchemist", author="Paulo Coelho", bookCategory=category2)

session.add(BookItem2)
session.commit()


BookItem3 = BookItem(user_id=1, title="Tuesdays with Morrie", author="Mitch Albom'", bookCategory=category2)

session.add(BookItem3)
session.commit()


# Book Category #3

category3 = BookCategory(user_id=1, name="Literature")

session.add(category2)
session.commit()

BookItem1 = BookItem(user_id=1, title="TO KILL A MOCKINGBIRD", author="Harper Lee", bookCategory=category3)

session.add(BookItem1)
session.commit()


BookItem2 = BookItem(user_id=1, title="Animal Farm", author="George Orwell", bookCategory=category3)

session.add(BookItem2)
session.commit()

print "Books items!"

# bookCategory = {'name': 'Fiction', 'id':'1'}

# bookCategories = [{'name': 'Fiction', 'id':'1'},{'name': 'Inspirational', 'id':'2'},{'name': 'Literature', 'id':'3'}]


# Category item = [{'id': '1', 'title': 'Kafka on the Shore','Author':'Haruki Murakami'},
# {'id': '1', 'title': 'Sharp Objects','Author':'Gillian Flynn'},
# {'id': '1', 'title': 'The Girl on the Train','Author':'Paula Hawkins'},
# {'id': '2', 'title': 'If I Could Tell You Just One Thing','Author':'Richard Reed'},
# {'id': '2', 'title': 'The Alchemist','Author':'Paulo Coelho'},
# {'id': '2', 'title': 'Tuesdays with Morrie','Author':'Mitch Albom'},
# {'id': '3', 'title': 'TO KILL A MOCKINGBIRD','Author':'Harper Lee'},
# {'id': '3', 'title': 'Animal Farm','Author':'George Orwell'}
# {'id': '3', 'title': 'The Picture of Dorian Gray','Author':'Oscar Wilde  '}]
