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
# options.add_argument('-headless')
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
        driver.get(urlbuild)
        try:
            a = driver.find_element_by_xpath('//*[@class="jobs-search-two-pane__results jobs-search-two-pane__results--responsive display-flex"]')
        except NoSuchElementException:
            print('Nay')
            pass
        else:
            print(len(a))
            print('Yay')

    
    # joblistnodup = list(set(joblist))
    # print(len(joblist))
    # print(len(joblistnodup))
    # print(gonecount)


    driver.close()

# linkedin_scrape(job_titles[0], locations[0])

r = requests.get('https://www.linkedin.com/jobs/view/1024618539/')
time.sleep(1)
soup = BeautifulSoup(r.text, 'lxml')
div = soup.find_all('div')
count=0
for row in div:
    print(row.text)
    print('')
    print(count)
    print('_______________________________________________________________________________________________________________')
    print('')
    count+=1

print(div[10].prettify())

# title = div[10].find('h1',class_='topcard_title')
# print(title.text)
# company = div[10].find('a')
# print(company.text)
# location = div[10].find('span',class_='topcard__flavor topcard__flavor--bullet')
# print(location.text)  

job_titles = [r'data%20analyst', r'data%20science', r'big%20data', r'machine%20learning%20engineer', r'data%20engineer']
locations = [r'Toronto%2C%20Ontario%2C%20Canada',r'Vancouver%2C%20British%20Columbia%2C%20Canada', r'San%20Francisco%2C%20California']
#https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=Toronto%2C%20Ontario%2C%20Canada&locationId=PLACES.ca.2-1-0-1080&start25 sample linkedin link
def linkedin_scrape(job_titles, locations):
    url = r"https://www.linkedin.com/jobs/search/"
    
    for location in locations:
        for job in job_titles:
            cur.execute('CREATE TABLE IF NOT EXISTS [Jobs Linkedin ' + job +']([Job title] TEXT, [Company] TEXT, [Location] TEXT, [Description] TEXT, UNIQUE([Description])) ')
            pgnm = []
            for x in range(0,125, 25):
                pgnm.append('&start'+str(x))
            for nm in pgnm:
                urlbuild = url + '?keywords=' + job + '&location=' + location + nm
                driver.get(urlbuild)
                time.sleep(2)
                row = driver.find_elements_by_class_name('job-card-search__title artdeco-entity-lockup__title ember-view')
                for link in row:
                    link.click()
                    time.sleep(1)
                    try:
                        driver.find_element_by_class_name('jobs-details__main-content jobs-details__main-content--single-pane full-width relative')
                    except NoSuchElementException:
                        pass
                    else:
                        jobcont = driver.find_element_by_id('jobs-details__main-content jobs-details__main-content--single-pane full-width relative')
                        cont = jobcont.get_attribute('innerHTML')
                        soup = BeautifulSoup(cont, 'lxml')
                        title = soup.find('h1', class_='jobs-details-top-card__job-title t-20 t-black t-normal')
                        
                        company = soup.find('a', class_='jobs-details-top-card__company-url ember-view')
                        location = soup.find('span', class_='jobs-details-top-card__bullet')
                        print(title.text)
                        print(company.text)
                        print(location.text)
                        jobcont = driver.find_element_by_class_name('jobs-box__html-content jobs-description-content__text t-14 t-black--light t-normal')
                        cont = jobcont.get_attribute('innerHTML')
                        soup = BeautifulSoup(cont, 'lxml')
                        desc = soup.find('span')
                        try:
                            jobinfo = [title.text, company.text, location.text, desc.text]
                        except:
                            pass
                        else:
                            print(jobinfo)
                            cur.execute('INSERT OR IGNORE INTO [Jobs Linkedin ' +job+']([Job Title], [Company], [Location], [Description]) Values(?,?,?,?)',jobinfo)
                            conn.commit()
    driver.close()
