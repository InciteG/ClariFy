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
profile.set_preference("dom.disable_open_during_load", False)
driver = webdriver.Firefox(firefox_binary=r'C:\Program Files\Mozilla Firefox\firefox.exe' , executable_path=r'D:\Downloads\geckodriver.exe', firefox_options=options, firefox_profile=profile)
conn = sqlite3.connect('Jobs.db')
cur = conn.cursor()
job_titles = ["Data+Analyst", "Data+Scientist", "Data+Engineer", "Big+Data", "Machine+Learning+Engineer"]
locations = ['Greater+Toronto+Area%2C+ON', "Vancouver,+BC"]
cur.execute('CREATE TABLE IF NOT EXISTS [Jobs Indeed In]([Job title] TEXT, [Company] TEXT, [Location] TEXT, [Description] TEXT, UNIQUE([Description])) ')
cur.execute('CREATE TABLE IF NOT EXISTS [Jobs] ([Job title], [Company], [Location], [Date Scraped], [Date Posted], [Source], [Description]) ')
conn.commit()
#https://www.indeed.ca/jobs?q=Data+Analyst&l=Greater+Toronto+Area%2C+ON , sample link
indeed_url = 'https://www.indeed.ca'
# def indeed_req(job_titles,locations):
#     pglist = []
#     urlbuild = indeed_url+"/jobs?q=" + 'Data+Analyst' + '&l=' + 'Greater+Toronto+Area%2C+ON'
#     pg = requests.get(urlbuild)
#     soup = BeautifulSoup(pg.text,'lxml')
#     ho = soup.find_all('div', class_='title')
#     for item in ho:
#         a = item.find('a')
#         pglist.append(a.get('href'))
    
#     for lnk in pglist:
#         driver.get(indeed_url + lnk)
#         time.sleep(5)
    

# indeed_req('Data Analyst', 'Greater Toronto Area, ON')
# search_content = driver.find_element_by_xpath('//*[@id="resultsCol"]')
    # chtml = search_content.get_attribute("innerHTML")
    # soup = BeautifulSoup(chtml,'lxml')
    # row = soup.find_all('div', class_='jobsearch-SerpJobCard unifiedRow row result clickcard')
    # linktitle = []
    # for item in row:
    #     title = item.find('div', class_='title')
    #     print(title)
    #     an = title.find('a')
    #     link = an.get('href')
    #     print(link)
def indeed_scrape(job_titles, locations):
    for job in job_titles:
        cur.execute('CREATE TABLE IF NOT EXISTS [Jobs Indeed ' + job +']([Job title] TEXT, [Company] TEXT, [Location] TEXT, [Description] TEXT, UNIQUE([Description])) ')
        pgnm = []
        for x in range(0,100, 20):
            pgnm.append('&start='+str(x))
        for nm in pgnm:
            urlbuild = indeed_url+"/jobs?q=" + job + '&l=' + locations[0] + nm
            print(urlbuild)
            driver.get(urlbuild)
            try:
                driver.find_element_by_xpath('//*[@id="popover-close-link"]')
            except NoSuchElementException:
                pass
            else:
                driver.refresh()
            row = driver.find_elements_by_class_name('title')
            for item in row:
                item.click()
                time.sleep(1)
                try:
                    driver.find_element_by_id('vjs-container')
                except NoSuchElementException:
                    pass
                else:
                    jobcont = driver.find_element_by_id('vjs-container')
                    cont = jobcont.get_attribute('innerHTML')
                    soup = BeautifulSoup(cont, 'lxml')
                    title = soup.find('div', id='vjs-jobtitle')
                    company = soup.find('span', id='vjs-cn')
                    location = soup.find('span', id='vjs-loc')
                    desc = soup.find('div', id='vjs-desc')
                    try:
                        jobinfo = [title.text, company.text, location.text, desc.text]
                    except:
                        pass
                    else:
                        cur.execute('INSERT OR IGNORE INTO [Jobs Indeed ' +job+']([Job Title], [Company], [Location], [Description]) Values(?,?,?,?)',jobinfo)
                        conn.commit()

            
    driver.close()
    


# indeed_scrape(job_titles,locations)



job_titles = [r'data%20analyst', r'data%20science', r'big%20data', r'machine%20learning%20engineer', r'data%20engineer']
locations = [r'Toronto%2C%20Ontario%2C%20Canada',r'Vancouver%2C%20British%20Columbia%2C%20Canada', r'San%20Francisco%2C%20California']
#https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=Toronto%2C%20Ontario%2C%20Canada&locationId=PLACES.ca.2-1-0-1080&start25 sample linkedin link
def linkedin_scrape(job_titles, locations):
    url = r"https://www.linkedin.com/jobs/search/"
    
    for job in job_titles:
        cur.execute('CREATE TABLE IF NOT EXISTS [Jobs Linkedin ' + job +']([Job title] TEXT, [Company] TEXT, [Location] TEXT, [Description] TEXT, UNIQUE([Description])) ')
        for location in locations:
            pgnm = []
            for x in range(0,125, 25):
                pgnm.append('&start'+str(x))
            for nm in pgnm:
                urlbuild = url + '?keywords=' + job + '&location=' + location + nm
                driver.get(urlbuild)
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

linkedin_scrape(job_titles, locations)

