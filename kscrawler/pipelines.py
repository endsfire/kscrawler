# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from kscrawler.items import Projects, ProjectItem, ProjectsDaily, ProjectsRewards, ProjectsRewardsDaily, ProjectsFinal, DATABASE

class KscrawlerPipeline(object):
	
	def __init__(self):
		engine = create_engine(URL(**DATABASE))
		self.Session = sessionmaker(bind=engine)
		
	def process_item(self, item, spider):
		session = self.Session()
		if(spider.name == "ksspider"):		
			try:
				if(session.query(Projects.url).filter_by(url=item["url"]).count() == 0):
					itemP = ProjectItem({"url":item["url"],"title":item["title"], "author":item["author"], "goal":float(item["goal"].replace(',','')), "endDate":item["endDate"], "created":int(item["created"].replace(',','')), "backed":int(item["backed"].replace(',','')), "location":item["location"], "category":item["category"]})
					project = Projects(**itemP)
					session.add(project)
					session.commit()
					for reward in item["rewards"]:
						itemR = {"url":item["url"],"costbracket":float(reward["costBracket"].replace(',','')),"limit":int(reward["limit"])}
						projectRewards = ProjectsRewards(**itemR)
						session.add(projectRewards)
						session.commit()
				if(session.query(ProjectsDaily.date, ProjectsDaily.url).filter_by(date=item["date"],url=item["url"]).count() == 0):
					itemD = {"date":item["date"], "url":item["url"], "backers":int(item["daily"][0]["backers"].replace(',','')), "pledged":float(item["daily"][0]["pledged"].replace(',',''))}
					projectDaily = ProjectsDaily(**itemD)
					session.add(projectDaily)
					session.commit()
				for reward in item["rewards"]:
					itemRD = {"date":item["date"],"url":item["url"],"costbracket":float(reward["costBracket"].replace(',','')),"limit":int(reward["limit"].replace(',','')),"backers":int(reward["backers"].replace(',',''))}
					projectRewardDaily = ProjectsRewardsDaily(**itemRD)
					session.add(projectRewardDaily)
					session.commit()
			except:
				session.rollback()
				raise
			finally:
				session.close()
		elif(spider.name == "ksfinspider"):
			
			try:
				if(session.query(ProjectsFinal.url).filter_by(url=item["url"]).count() == 0):
					projectFinal = ProjectsFinal(**item)
					session.add(projectFinal)
					session.commit()
			except:
				session.rollback()
				raise
			finally:
				session.close()
		return item