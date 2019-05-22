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
#removed selenium dependency and improving faster scraping time- removed linkedin support
# options = webdriver.FirefoxOptions()
# options.add_argument('-headless')
# profile = webdriver.FirefoxProfile()
# profile.set_preference("dom.disable_open_during_load", False)
# driver = webdriver.Firefox(firefox_binary=r'C:\Program Files\Mozilla Firefox\firefox.exe' , executable_path=r'D:\Downloads\geckodriver.exe', firefox_options=options, firefox_profile=profile)
conn = sqlite3.connect('JobDBa.db')
cur = conn.cursor()
# job_titles = ["Data+Analyst", "Data+Scientist", "Data+Engineer", "Big+Data", "Machine+Learning+Engineer"]
# locations = ['Greater+Toronto+Area%2C+ON', "Vancouver%2C+BC"]

#https://www.indeed.ca/jobs?q=Data+Analyst&l=Greater+Toronto+Area%2C+ON , sample link

#scrape indeed from indeed.ca
def indeedca_scrape(job_titles, locations):
    indeed_url = 'https://www.indeed.ca' #base url
    cur.execute('CREATE TABLE IF NOT EXISTS [Jobs Indeed]([Job title] TEXT, [Company] TEXT, [Location] TEXT, [Description] TEXT, UNIQUE([Description])) ') #only allow unique descriptions to be stored
    pglnklst = []
    for location in locations:
        for job in job_titles:
            pgnm = []
            for x in range(0,400, 20): #400 applications per category
                pgnm.append('&start='+str(x)) #url syntax
            for nm in pgnm:
                urlbuild = indeed_url+"/jobs?q=" + job + '&l=' + location + nm
                n = requests.get(urlbuild) 
                soup = BeautifulSoup(n.text,'lxml')
                links = soup.find_all('div',class_='title')
                for row in links:
                    link = row.find('a', href=True)
                    pglnklst.append(link['href'])
    nodup = list(set(pglnklst)) #remove duplicates from urllist, shorten run time
    print(len(nodup))
    for ex in nodup:
        st = requests.get(indeed_url+ex)
        soup = BeautifulSoup(st.text, 'lxml')
        title = soup.find('h3',class_='icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title')
        company = soup.find('div', class_='icl-u-lg-mr--sm icl-u-xs-mr--xs')
        location = soup.find('span',class_='jobsearch-JobMetadataHeader-iconLabel')
        description = soup.find('div', id='jobDescriptionText')
        try:
            nxtrow = [title.text, company.text, location.text, description.text] #if empty skip insert into database, pass over webpages that were not accessed correctly
        except:
            pass
        else:
            cur.execute('INSERT OR IGNORE INTO [Jobs Indeed]([Job Title], [Company], [Location], [Description]) Values(?,?,?,?)',nxtrow)
            conn.commit()
#scraped indeed.com
def indeedusa_scrape(job_titles, locations):
    indeed_url = 'https://www.indeed.com'
    cur.execute('CREATE TABLE IF NOT EXISTS [Jobs Indeed]([Job title] TEXT, [Company] TEXT, [Location] TEXT, [Description] TEXT, UNIQUE([Description])) ')
    pglnklst = []
    
    for location in locations:
        for job in job_titles:
            pgnm = []
            for x in range(0,500, 20):
                pgnm.append('&start='+str(x))
            for nm in pgnm:
                urlbuild = indeed_url+"/jobs?q=" + job + '&l=' + location + nm
                n = requests.get(urlbuild)
                soup = BeautifulSoup(n.text,'lxml')
                links = soup.find_all('div',class_='title') 
                for row in links:
                    link = row.find('a', href=True)
                    pglnklst.append(link['href'])
    nodup = list(set(pglnklst))
    print(len(pglnklst))
    print(len(nodup))
    for ex in nodup:
        st = requests.get(indeed_url+ex)
        soup = BeautifulSoup(st.text, 'lxml')
        title = soup.find('h3',class_='icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title')
        company = soup.find('div', class_='icl-u-lg-mr--sm icl-u-xs-mr--xs')
        
        i1 = soup.find('div', class_='jobsearch-DesktopStickyContainer')
        try:
            i2 = i1.find_all('div')
        except:
            pass
        else:
            try:
                i3 = i2[0].find('div')
            except:
                pass
            else:
                try:
                    i4 = i3.find_all('div')
                except:
                    pass
                else:
                    location = i4[len(i4)-1]
                    description = soup.find('div', id='jobDescriptionText') #try,excepts to prevent issues with accessing content stopping scraper
                    try:
                        nxtrow = [title.text, company.text, location.text, description.text]
                    except:
                        pass
                    else:
                        cur.execute('INSERT OR IGNORE INTO [Jobs Indeed]([Job Title], [Company], [Location], [Description]) Values(?,?,?,?)',nxtrow)
                        conn.commit()

    
indeedusa_scrape(job_titles,locations)

if __name__ == "__main__":
    job_titles = ["Data+Analyst", "Data+Scientist", "Data+Engineer", "Big+Data", "Machine+Learning+Engineer"]
    locations = ['New+York%2C+NY', "San+Francisco%2C+CA", 'Austin%2C+TX', 'Chicago%2C+IL', 'Silicon+Valley%2C+CA', 'Los+Angeles%2C+CA','Boston%2C+MA', 'Houston%2C+TX','Dallas-Fort+Worth%2C+TX','Seattle%2C+WA','Columbus%2C+OH']
    indeedusa_scrape(job_titles,locations)