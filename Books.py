from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, Category, Item

engine = create_engine('sqlite:///database_setup.db')
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




# Create user
User1 = User(name="Ghada", email="Classgh@Gmail.com")
session.add(User1)
session.commit()


# Book Category #1
category1 = Category(user_id=1, name="Fiction")

session.add(category1)
session.commit()

BookItem1 = Item(user_id=1, title="Kafka on the Shore", author="Haruki Murakami", category=category1)

session.add(BookItem1)
session.commit()

BookItem2 = Item(user_id=1, title="Sharp Objects", author="Gillian Flynn", category=category1)

session.add(BookItem2)
session.commit()

BookItem3 = Item(user_id=1, title="The Girl on the Train", author="Paula Hawkins", category=category1)

session.add(BookItem3)
session.commit()

# Book Category #2

category2 = Category(user_id=1, name="Inspirational")

session.add(category2)
session.commit()

BookItem1 = Item(user_id=1, title="If I Could Tell You Just One Thing", author="Richard Reed", category=category2)

session.add(BookItem1)
session.commit()

BookItem2 = Item(user_id=1, title="The Alchemist", author="Paulo Coelho", category=category2)

session.add(BookItem2)
session.commit()


BookItem3 = Item(user_id=1, title="Tuesdays with Morrie", author="Mitch Albom", category=category2)

session.add(BookItem3)
session.commit()


# Book Category #3

category3 = Category(user_id=1, name="Literature")

session.add(category3)
session.commit()

BookItem1 = Item(user_id=1, title="To Kill a Mockingbird", author="Harper Lee", category=category3)

session.add(BookItem1)
session.commit()


BookItem2 = Item(user_id=1, title="Animal Farm", author="George Orwell", category=category3)

session.add(BookItem2)
session.commit()

print "Books items Added!"

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
