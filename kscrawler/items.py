# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, DateTime, MetaData

DATABASE = {
	'drivername' : 'postgres',
	'host' : 'localhost',
	'port' : '5432',
	'username' : 'kscrawl',
	'password' : 'kickcrawl',
	'database' : 'kickstarter'
}

DeclarativeBase = declarative_base(metadata=MetaData(schema='crawler'))

class Projects(DeclarativeBase):
	__tablename__ = "project"
	
	url = Column('url',String, primary_key=True)
	title = Column('title', String)
	author = Column('author', String)
	goal = Column('goal', Float)
	endDate = Column('enddate', DateTime)
	created = Column('created', Integer)
	backed = Column('backed', Integer)
	location = Column('location', String)
	category = Column('category', String)

class ProjectsDaily(DeclarativeBase):
	__tablename__ = "project_daily"
	
	date = Column('date', Date, primary_key=True)
	url = Column('url', String, primary_key=True)
	backers = Column('backers', Integer)
	pledged = Column('pledged', Float)

class ProjectsRewards(DeclarativeBase):
	__tablename__ = "project_rewards"
	
	url = Column('url',String, primary_key=True)
	costbracket = Column('costbracket',Float, primary_key=True)
	limit = Column('backerlimit',Integer, primary_key=True)

class ProjectsRewardsDaily(DeclarativeBase):
	__tablename__ = "project_rdaily"
	
	date = Column('date', Date, primary_key=True)
	url = Column('url', String, primary_key=True)
	costbracket = Column('costbracket', Float, primary_key=True)
	limit = Column('backerlimit',Integer)
	backers = Column('backers', Integer)

class CrawlUrls(DeclarativeBase):
	__tablename__ = "crawl_urls"
	
	url = Column('url', String, primary_key=True)
	
class ProjectsFinal(DeclarativeBase):
	__tablename__ = "project_fdaily"
	
	url = Column('url', String, primary_key=True)
	backers = Column("backers", Integer)
	pledged = Column('pledged', Float)
	endStatus = Column('end_status', String)
	
class KscrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ProjectItem(scrapy.Item):
	url = scrapy.Field()
	date = scrapy.Field()
	title = scrapy.Field()
	author = scrapy.Field()
	goal = scrapy.Field()
	#startDate = scrapy.Field()
	endDate = scrapy.Field()
	#cancDate = scrapy.Field()
	created = scrapy.Field()
	backed = scrapy.Field()
	twitter = scrapy.Field()
	facebook = scrapy.Field()
	location = scrapy.Field()
	category = scrapy.Field()
	badges = scrapy.Field()
	rewards = scrapy.Field()
	daily = scrapy.Field()

class ProjectDailyItem(scrapy.Item):
	backers = scrapy.Field()
	pledged = scrapy.Field()

class ProjectTierItem(scrapy.Item):
	costBracket = scrapy.Field()
	backers = scrapy.Field()
	limit = scrapy.Field()
	
class ProjectFinalItem(scrapy.Item):
	url = scrapy.Field()
	backers = scrapy.Field()
	pledged = scrapy.Field()
	endStatus = scrapy.Field()