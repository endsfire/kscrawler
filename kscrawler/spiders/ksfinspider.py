# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup,NavigableString
import re
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from kscrawler.items import DATABASE, CrawlUrls, ProjectFinalItem
import logging

class KsfinspiderSpider(scrapy.Spider):
	name = "ksfinspider"
	project_live = "Project-state-live"
	project_ended = "Project-ended-true"
	project_successful = "Project-state-successful"
	project_failed = "Project-state-failed"
	project_canceled = "Project-state-canceled"
	project_suspended = "Project-state-suspended"
	
	def __init__(self):
		engine = create_engine(URL(**DATABASE))
		self.Session = sessionmaker(bind=engine)
		
	def start_requests(self):
		session = self.Session()
		try:
			urls = session.query(CrawlUrls.url)
		except:
			raise
		finally:
			session.close()
		
		for u in urls:
			yield scrapy.Request(u.url)
		
	def parse(self,response):
		soup = BeautifulSoup(response.body,"lxml")
		state = soup.find(id="main_content")["class"]
		if self.project_successful in state:
			return self.parse_success(soup,response.url)
			#yield scrapy.Request(response.url+"/description",callback=self.parse_success_description)
		elif self.project_failed in state:
			return self.parse_failed(soup,response.url, "Project-state-failed")
		elif self.project_canceled in state:
			return self.parse_failed(soup,response.url, "Project-state-canceled")
		
	def parse_success(self,soup,url):
		itemF = ProjectFinalItem()
		
		try:
			hf_sec = soup.find("section",class_ ="NS_projects__hero_spotlight")

			stats_sec = hf_sec.find("div",class_="NS_projects__spotlight_stats")
			backers = stats_sec.b.string
			pledged = stats_sec.span.string
			
			backers = "".join(re.findall('\d+',backers))
			pledged = "".join(re.findall('\d+.',pledged))
			
			itemF["url"] = url
			itemF["backers"] = int(backers.replace(',',''))
			itemF["pledged"] = float(pledged.replace(',',''))
			itemF["endStatus"] = "Project-state-successful"
		except:
			logging.error("Unable to parse URL:",url)
		finally:
			return itemF
	
	def parse_success_description(self,response):
		soup = BeautifulSoup(response.body,"lxml")
		
		locCatTag_sec = soup.find("div",class_="NS_projects__category_location").strings
		locCatTag = []
		for s in locCatTag_sec:
			if(len(s.strip()) > 0):
				locCatTag.append(s.strip())
		
		location = locCatTag[0]
		category = locCatTag[1]
		
		badges = []
		for b in locCatTag[2:]:
			badges.append(b)

		for b in badges:
			print(b)
		
		goal_sec = soup.find("div",class_="NS_projects__description_section")
		if(goal_sec != None):
			goal_sec = goal_sec.find("div",class_="mb6")
			if(goal_sec != None):
				goal_sec = goal_sec.find(text=re.compile("pledged of")).parent
				if(goal_sec != None):
					goal_sec = goal_sec.find("span")
					goal = "".join(re.findall('\d+.',goal_sec.string))
		
		rewards_sec = soup.find("div",class_="NS_projects__rewards_list").find_all("li")
		for r in rewards_sec:
			self.rewards_data(r)
	
	def parse_failed(self, soup, url, status):
		itemF = ProjectFinalItem()
		
		try:
			hf_sec = soup.find("section",class_ ="NS_projects__hero_funding")
			backers = hf_sec.find("div",id="backers_count").string
			pledged = hf_sec.find("div",id="pledged").data.string
			pledged = "".join(re.findall('\d+.',pledged))
			
			itemF["url"] = url
			itemF["backers"] = int(backers.replace(',',''))
			itemF["pledged"] = float(pledged.replace(',',''))
			itemF["endStatus"] = status
		except:
			logging.error("Unable to parse URL:",url)
		finally:
			return itemF