from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

DeclarativeBase = declarative_base()

def db_connect():
	return create_engine('sqlite:///test.db')
	
def create_project_table(engine):
	DeclarativeBase.metadata.create_all(engine)
	
class Projects(DeclarativeBase):
	__tablename__ = "project"
	
	title = Column('title', String, primary_key=True)
	author = Column('author', String)
	goal = Column('goal', String)
	endDate = Column('end_date', String)
	created = Column('created', String)
	backed = Column('backed', String)
	location = Column('location', String)
	category = Column('category', String)