from bs4 import BeautifulSoup
import time
import sqlite3
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
import pandas as pd
"""Webdriver Setup and SQL Setup"""

options = webdriver.FirefoxOptions()
options.add_argument('-headless')
profile = webdriver.FirefoxProfile()
# profile.set_preference("dom.disable_open_during_load", False)
driver = webdriver.Firefox(firefox_binary=r'C:\Program Files\Mozilla Firefox\firefox.exe' , executable_path=r'D:\Downloads\geckodriver.exe', firefox_options=options, firefox_profile=profile)
conn = sqlite3.connect('Jobs.db')
cur = conn.cursor()

job_titles = [r'data%20analyst', r'data%20science', r'big%20data', r'machine%20learning%20engineer', r'data%20engineer']
locations = [r'Toronto%2C%20Ontario%2C%20Canada',r'Vancouver%2C%20British%20Columbia%2C%20Canada', r'San%20Francisco%2C%20California']
#https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=Toronto%2C%20Ontario%2C%20Canada&locationId=PLACES.ca.2-1-0-1080&start25 sample linkedin link
def linkedin_scrape(job_titles, locations):
    url = r"https://www.linkedin.com/jobs/search/"
    cur.execute('CREATE TABLE IF NOT EXISTS [Jobs Linkedin ' + job_titles +']([Job title] TEXT, [Company] TEXT, [Location] TEXT, [Description] TEXT, UNIQUE([Description])) ')
    pgnm = []
    joblist = []
    gonecount=0
    for x in range(0,125, 25):
        pgnm.append('&start='+str(x))
    for nm in pgnm: 
        urlbuild = url + '?keywords=' + job_titles + '&location=' + locations + nm
        print(urlbuild)
        req = requests.get(urlbuild)
        time.sleep(1)
        soup = BeautifulSoup(req.text,'lxml')
        a = soup.find_all('li', class_='result-card job-result-card result-card--with-hover-state')
        for x in a:
            link = x.find('a', href=True)
            try:
                joblist.append(link['href'])
            except:
                gonecount+=1
    joblistnodup = list(set(joblist))
    print(len(joblist))
    print(len(joblistnodup))
    print(gonecount)


    driver.close()

linkedin_scrape(job_titles[0], locations[0])