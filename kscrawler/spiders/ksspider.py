import scrapy
from bs4 import BeautifulSoup,NavigableString
import re
from kscrawler.items import ProjectItem,ProjectTierItem,ProjectDailyItem
from datetime import datetime
import logging

class KickStartSpider(scrapy.Spider):
	name = "ksspider"
	#start_urls = ["https://www.kickstarter.com/discover/categories/technology?sort=newest"]
	start_urls = ["https://www.kickstarter.com/discover/categories/art?sort=newest","https://www.kickstarter.com/discover/categories/comics?sort=newest","https://www.kickstarter.com/discover/categories/crafts?sort=newest","https://www.kickstarter.com/discover/categories/dance?sort=newest","https://www.kickstarter.com/discover/categories/design?sort=newest","https://www.kickstarter.com/discover/categories/fashion?sort=newest","https://www.kickstarter.com/discover/categories/film%20&%20video?sort=newest","https://www.kickstarter.com/discover/categories/food?sort=newest","https://www.kickstarter.com/discover/categories/games?sort=newest","https://www.kickstarter.com/discover/categories/journalism?sort=newest","https://www.kickstarter.com/discover/categories/music?sort=newest","https://www.kickstarter.com/discover/categories/photography?sort=newest","https://www.kickstarter.com/discover/categories/publishing?sort=newest","https://www.kickstarter.com/discover/categories/technology?sort=newest","https://www.kickstarter.com/discover/categories/theater?sort=newest"]
	#start_urls = ["https://www.kickstarter.com/projects/239620361/the-night-time-monsters","https://www.kickstarter.com/projects/1336921824/uniker-helper-lassistant-dalerte-cercles-dentraide"]
	project_live = "Project-state-live"
	project_ended = "Project-ended-true"
	project_successful = "Project-state-successful"
	project_failed = "Project-state-failed"
	project_canceled = "Project-state-canceled"
	
	def parse(self,response):
		soup = BeautifulSoup(response.body,"lxml")
		main = soup.find_all("p",class_="project-profile-byline")
		projects = soup.find_all("li",class_="project")
		
		urls = []
		for p in projects:
			if(p.find("p",class_="project-profile-byline") == None):
				urls.append(p.find("a")["href"].split("?")[0])
		for u in urls:
			yield scrapy.Request("https://www.kickstarter.com"+u,callback=self.parse_type)
		
		if(len(main) < 20):
			if(re.search("&page",response.url) == None):
				page = response.url+"&page=2"
			else:
				tNum = re.findall(r'\d+',response.url)
				pageNum = int(tNum[len(tNum)-1])
				nPage = re.search("&page",response.url)
				page = response.url[:nPage.end()+1]
				page = page + str(pageNum+1)
			
			yield scrapy.Request(page)
	
	def parse_type(self,response):
		soup = BeautifulSoup(response.body,"lxml")
		state = soup.find(id="main_content")["class"]
		
		if self.project_live in state:
			yield self.parse_live(soup,response.url)
	'''
	def parse(self,response):
		soup = BeautifulSoup(response.body,"lxml")
		urlResponse = response.url
	'''
	def parse_live(self,soup,urlResponse):
		pItem = ProjectItem()
		dItem = ProjectDailyItem()
		
		try:
			pItem["url"] = urlResponse
			pItem["date"] = datetime.now().date()
			hf_sec = soup.find("section",class_ ="NS_projects__hero_funding")
			title_sec = hf_sec.find("div",class_ ="NS_projects__header")
			title = title_sec.h2.a.string
			author = title_sec.find("p").find("a").string

			backers = hf_sec.find("div",id="backers_count").string
			pledged = hf_sec.find("div",id="pledged").data.string
			pledged = "".join(re.findall('\d+.',pledged))
			goal = hf_sec.find(text=re.compile("pledged of")).parent.find(class_="money").string
			goal = "".join(re.findall('\d+',goal))
			end_date = hf_sec.find("span",id="project_duration_data")["data-end_time"]
			end_date = datetime.strptime("".join(end_date.rsplit(":",1)),"%Y-%m-%dT%H:%M:%S%z")
			
			creator_sec = hf_sec.find("div",class_="NS_projects__creator")
			created = creator_sec.find(text=re.compile("created"))
			if(re.match("First",created)):
				created = "1"
			else:
				created = "".join(re.findall('\d+',created))
			backed = creator_sec.find(text=re.compile("backed"))
			backed = "".join(re.findall('\d+',backed))
			
			twitter = creator_sec.find(text=re.compile("twitter"))
			facebook = creator_sec.find(text=re.compile("facebook"))
			if(twitter != None):
				twitter = twitter.parent["href"]
				pItem["twitter"] = twitter
			if(facebook != None):
				facebook = facebook.parent["href"]
				pItem["facebook"] = facebook
			
			locCatTag_sec = hf_sec.find("div",class_="NS_projects__category_location").strings
			locCatTag = []
			for s in locCatTag_sec:
				if(len(s.strip()) > 0):
					locCatTag.append(s.strip())
			
			location = locCatTag[0]
			category = locCatTag[1]
			
			badges = []
			for b in locCatTag[2:]:
				badges.append(b)
			
			pItem["badges"] = []
			for b in badges:
				pItem["badges"].append(b)
			
			pItem["rewards"] = []
			
			rewards_sec = soup.find("div",class_="NS_projects__rewards_list").ol.find_all("li",recursive=False)
			
			for r in rewards_sec:
				pItem["rewards"].append(dict(self.rewards_data(r)))
			
			dItem["backers"] = backers
			dItem["pledged"] = pledged
			
			pItem["title"] = title
			pItem["author"] = author
			pItem["goal"] = goal
			pItem["endDate"] = end_date
			pItem["created"] = created
			pItem["backed"] = backed
			pItem["location"] = location
			pItem["category"] = category
			pItem["daily"] = [dict(dItem)]
			
		except:
			logging.error("Unable to parse URL:",urlResponse)
			
		finally:
			return pItem
		
	def rewards_data(self,reward):
		rItem = ProjectTierItem()
		cost = reward.find(text=re.compile("USD"))
		
		if(cost == None):
			cost = reward.find(class_="pledge__amount").string
		
		cost = "".join(re.findall('\d+.',cost))
		rBackers = reward.find("span",class_="pledge__backer-count").find(text=re.compile("backer"))
		rBackers = "".join(re.findall('\d+',rBackers))
		limited = reward.find("span",class_="pledge__limit")
		
		if(limited != None):
			left = limited.string.strip().split("of ")
			if(len(left) > 1):
				limited = "".join(re.findall('\d+',limited.string.strip().split("of ")[1]))
			else:
				limited = rBackers
		else:
			limited = '0'
		
		rItem["costBracket"]  = cost
		rItem["backers"] = rBackers
		rItem["limit"] = limited
		
		return rItem