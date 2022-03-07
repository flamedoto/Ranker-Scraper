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


def roundfunction(value,roundlen):
	nextnumber = "0"
	FinalValue = value
	for i in range(len(value),0,-1):
		if len(FinalValue) == roundlen:
			break
		if int(value[i-1]) > 4:
			nextnumber = int(value[i-2]) + 1
			FinalValue = FinalValue[:i-2] +str(nextnumber)+ FinalValue[i-3:]
			FinalValue= FinalValue[0:i-1]
		else:
			FinalValue=FinalValue[0:i-1]

	return FinalValue


URL = 'https://www.ranker.com/list/celebrities-with-stage-names/celebrity-lists?ref=browse_list&l=1'

## Defining options for chrome browser
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
Browser = webdriver.Chrome(executable_path = "chromedriver",options = options)

Browser.get(URL)
a = Browser.find_element_by_xpath("//script[@id='__NEXT_DATA__']")


dataspans = Browser.find_elements_by_xpath("//div[@class='stats_main__13tlb']//span")
Date = dataspans[0].text.replace('Updated','')
ArticleViews = ''
for data in dataspans:
	if 'views' in data.text.lower():
		ArticleViews = data.text.lower().replace('views','')

ab= dateparser.parse(Date)
print(type(ab))
lastword = ''
if 'k' in ArticleViews:
	lastword = 'K'
elif 'm' in ArticleViews:
	lastword = 'm'

numbers = re.findall(r'\d+', ArticleViews)
#print(ArticleViews)



number = ''.join(numbers)
#number = numbers[0]
if number is not "":
	b = a.get_attribute('innerHTML')
	#print(b)
	b= b.split(',')
	#b = b.split(":")
	for c in b:
		d = c.split(":")
		#print(d[0])
		#print(d[0].lower().replace('"',''))
		if d[0].lower().replace('"','') == 'viewcount':
			#print('a')
			#print(len(number.rstrip('0')))
			funcmatch = roundfunction(d[1],len(number.rstrip('0')))
			print(funcmatch,d[1])
			if funcmatch == number:
				if lastword == 'k':
					#checklen = d[1].replace(number,'')
					if len(d[1]) > 3 and len(d[1]) < 7: 
						ArticleViews = d[1]
				elif lastword == 'm':
					#checklen = d[1].replace(number,'')
					if len(d[1]) > 6 and len(d[1]) < 10: 
						ArticleViews = d[1]
				elif lastword == 'b':
					#checklen = d[1].replace(number,'')
					print(d)
					if len(d[1]) > 10 and len(d[1]) < 14: 
						ArticleViews = d[1]
				else:
					ArticleViews = d[1]


print(ArticleViews)