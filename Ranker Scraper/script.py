import time
from tqdm import tqdm
import sys
import random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import *
import re
import os
from datetime import datetime
from bs4 import BeautifulSoup as bs4
import dateparser
import urllib.request
import requests
import pandas as pd
import math
from selenium.webdriver.common.action_chains import ActionChains



class Ranker():


	#Main URl
	URL = 'https://www.ranker.com/tags/entertainment'

	## Defining options for chrome browser
	options = webdriver.ChromeOptions()
	options.add_argument("--ignore-certificate-errors")
	Browser = webdriver.Chrome(executable_path = "chromedriver",options = options)


	#Excel file declaration
	ExcelFile = pd.ExcelWriter('data.xlsx')


	#Total rows in excel file
	Rows = 0 

	#Per Page Article on HTML source code 
	ArticlePerPage = 16
	#Press takes to scroll single page is 1 , 2 is just in case 
	ScrollPerPage = 2
	#Total Article User Wants
	TotalArticle = 1000


	#Calculating Total time 'End' button will be pressed
	totalscrolls = int(math.ceil((TotalArticle / ArticlePerPage) * ScrollPerPage))


	#This function will go to Main url  and find select tag and body tag.
	def getsubcats(self):
		self.Browser.get(self.URL)


		time.sleep(4)


		#Select Tag
		subcats = Select(self.Browser.find_element_by_xpath("//select[@id='browseItems__filter']"))

		#Body Tag
		element = self.Browser.find_element_by_tag_name("body")

		return subcats,element

	def subcats(self):
		#subcats = Select Tag , element = Body Tag.
		subcats,element = self.getsubcats()

		#Get total options present in the select tag
		TotalSubCats = len(subcats.options)

		print("Extracting Article URLs...")

		#Iterate through each option in select tag
		for i in range(TotalSubCats):
			#if its first iteration skip it because first will always be 'all categories'
			if i == 0:
				continue
			#if its not second iteration call getsubcats function to go back to homepage and to find select and body tag again
			elif i is not 1:
				subcats,element = self.getsubcats()

			#
			while True:
				#Select option from select tag by its index
				subcats.select_by_index(i)
				#Get a category name by the selected index of select tag
				cat = (subcats.first_selected_option).text
				#Sleep 3 sec to let it load
				time.sleep(3)
				#Press tab to go to BODY
				element.send_keys(Keys.TAB)
				#Iterate loop till totalscroll and press END button on each scroll
				for k in range(self.totalscrolls):
					#Pressing  END button
					element.send_keys(Keys.END)

					time.sleep(0.7)
					#Checking if the total article founds are greater or equals to 1000 if it is break the loop
					#Finding article tags
					tagscheck = self.Browser.find_elements_by_xpath("//article[@id='browseItems']//a")
					if len(tagscheck) >= 1000:
						break

				#Check if article found are equals to 12 if they are repeat the operation again if not break the loop
				taglen = len(self.Browser.find_elements_by_xpath("//article[@id='browseItems']//a"))
				if taglen != 12:
					break
				else:
					#calling getsubcats function again to reload page and find select and body tag again
					subcats,element = self.getsubcats()


			#Finding article tags 
			tags = self.Browser.find_elements_by_xpath("//article[@id='browseItems']//a")
			#Extracting URLs from article tags
			urls = self.ScrapeArticleUrls(tags)

			#Scraping data from each artcle and saving it to excel file parameters are 'URLS ' and 'Category Name'
			self.DataScrape(urls,cat)



	def DataScrape(self,urls,cat):
		for url in tqdm(urls):
			self.Browser.get(url)
			#Sleep 3 sec on each url load
			time.sleep(3)

			#finding article title if is not available then skip the iteration

			try:
				ArticleTitle = self.Browser.find_element_by_xpath("//h1[@class='title_name__1HfHT']").text
			except:
				continue



			#Get all the span in stats divs in which date , view ,votes are store
			dataspans = self.Browser.find_elements_by_xpath("//div[@class='stats_main__13tlb']//span")
			#First one of it will always be date if there is any
			Date = dataspans[0].text.replace('Updated','')
			#Checking that the text is actually date or not, by parsing it to dateparser 
			DateCheck = dateparser.parse(Date)
			#if None then date is not avaiable
			if DateCheck == None:
				Date = ""

			#Article views 
			ArticleViews = ''
			#iterate through the all spans found
			for data in dataspans:
				#check if anyone of them contains views in there text if does then store it in article view variable
				if 'views' in data.text.lower():
					ArticleViews = data.text.lower().replace('views','')
			#view type is K M B thousands millions billions
			viewtpye = ''
			if 'k' in ArticleViews:
				viewtpye = 'K'
			elif 'm' in ArticleViews:
				viewtpye = 'm'

			#Extracting all digits from article view string
			numbers = re.findall(r'\d+', ArticleViews)
			#print(ArticleViews)
			#concating all  extracted digits
			number = ''.join(numbers)


			# if number is not empty
			if number is not "":
				#Find the script tag in which count views is available
				ScriptTag = self.Browser.find_element_by_xpath("//script[@id='__NEXT_DATA__']")


				#Get script tags innerHTML
				subtags = ScriptTag.get_attribute('innerHTML')
				#Spliting innerHTML by comma , to separate all values
				subtags= subtags.split(',')

				#iterating through all the separate values 
				for c in subtags:

					#Split separate value by col : to get key and value
					temp = c.split(":")
					# zero index will be key and one index will be value
					#check if viewcount is in key
					if temp[0].lower().replace('"','') == 'viewcount':
						#Reason for this is that, there are total 50-55 keys named viewcount in the script
						#if its in the key then round integer value :::::  246287 will be rounded of to the number len present in span tag view which is 246.3=2463 
						RoundValue = self.roundfunction(temp[1],len(number))
						#if both rounded number and number from span tag are same 
						if RoundValue == number:
							#check if its K M B
							if viewtpye == 'k':
								#if its k check it has 4 min and 6 max digits in it
								if len(temp[1]) > 3 and len(temp[1]) < 7: 
									ArticleViews = temp[1]
							elif viewtpye == 'm':
								#if its k check it has 7 min and 9 max digits in it
								if len(temp[1]) > 6 and len(temp[1]) < 10: 
									ArticleViews = temp[1]
							elif viewtpye == 'b':
								#if its b check it has 10 min and 13 max digits in it
								if len(temp[1]) > 9 and len(temp[1]) < 14: 
									ArticleViews = temp[1]
							else:
								#if its in hundreds
								ArticleViews = temp[1]
			else:
				ArticleViews = ""


			#Writing data to excel file
			self.ExcelWrite(Date,ArticleViews,ArticleTitle,cat)



	def ScrapeArticleUrls(self,tags):
		urls= []
		#Extracting href attribute from article tag 
		for tag in tags:
			urls.append(tag.get_attribute('href'))
		print("Total Articles Found : ",len(tags))
		return urls




	def roundfunction(self,value,roundlen):
		nextnumber = "0"
		FinalValue = value

		#Iterating loop in reverse
		for i in range(len(value),0,-1):
			#if final value len is equals to required len then break the loop
			if len(FinalValue) == roundlen:
				break
			#normal rounding method if value is greater than 5 add 1 to next value 
			if int(value[i-1]) > 4:

				nextnumber = int(value[i-2]) + 1
				FinalValue = FinalValue[:i-2] +str(nextnumber)+ FinalValue[i-3:]
				FinalValue= FinalValue[0:i-1]
			#if value is less than 5 pass
			else:
				FinalValue=FinalValue[0:i-1]

		return FinalValue


	def ExcelWrite(self,Date,ArticleViews,ArticleTitle,cat):
		df = pd.DataFrame({"Data": [Date],"Title": [ArticleTitle],"Views": [ArticleViews],"Category": [cat]})
		#If first entry in excel
		if self.Rows == 0:
			df.to_excel(self.ExcelFile,index=False,sheet_name='Data')
			self.Rows = self.ExcelFile.sheets['Data'].max_row
		else:
			df.to_excel(self.ExcelFile,index=False,sheet_name='Data',header=False,startrow=self.Rows)
			self.Rows = self.ExcelFile.sheets['Data'].max_row


		self.ExcelFile.save()

cr = Ranker()
cr.subcats()