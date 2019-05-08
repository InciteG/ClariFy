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
job_titles = ["Data+Analyst", "Data+Scientist", "Data+Engineer", "Big+Data", "Machine+Learning+Engineer"]
locations = ['Greater+Toronto+Area%2C+ON']
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
    
    for location in locations:
        for job in job_titles:
            cur.execute('CREATE TABLE IF NOT EXISTS [Jobs Indeed ' + job +']([Job title] TEXT, [Company] TEXT, [Location] TEXT, [Description] TEXT, UNIQUE([Description])) ')
            pgnm = []
            for x in range(0,100, 20):
                pgnm.append('&start='+str(x))
            for nm in pgnm:
                urlbuild = indeed_url+"/jobs?q=" + job + '&l=' + locations[0] + nm
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
    

def indeed_scrape_bsr(job_titles, locations):
    for job in job_titles:
        cur.execute('CREATE TABLE IF NOT EXISTS [Jobs Indeed ' + job +']([Job title] TEXT, [Company] TEXT, [Location] TEXT, [Description] TEXT, UNIQUE([Description])) ')
        pgnm = []
        for x in range(0,100, 20):
            pgnm.append('&start='+str(x))
        for nm in pgnm:
            urlbuild = indeed_url+"/jobs?q=" + job + '&l=' + locations[0] + nm
            n = requests.get(urlbuild)
            soup = BeautifulSoup(n.text,'lxml')
            links = soup.find_all('div',class_='title')
            pglnklst = []
            for row in links:
                link = row.find('a', href=True)
                pglnklst.append(link['href'])
            for ex in pglnklst:
                st = requests.get(indeed_url+ex)
                soup = BeautifulSoup(st.text, 'lxml')
                title = soup.find('h3',class_='icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title')
                company = soup.find('div', class_='icl-u-lg-mr--sm icl-u-xs-mr--xs')
                location = soup.find('span',class_='jobsearch-JobMetadataHeader-iconLabel')
                description = soup.find('div', id='jobDescriptionText')
                try:
                    jobinfo = [title.text, company.text, location.text, description.text]
                except:
                    pass
                else:
                    cur.execute('INSERT OR IGNORE INTO [Jobs Indeed ' +job+']([Job Title], [Company], [Location], [Description]) Values(?,?,?,?)',jobinfo)
                    conn.commit()
    

start_time = time.time()
indeed_scrape_bsr(job_titles,locations)
tot = time.time()-start_time
print(f'Beautifulsoup/Requests time: {tot}')
start_time = time.time()
indeed_scrape(job_titles,locations)
tot = time.time()-start_time
print(f'Selenium time: {tot}')

#Beautifulsoup/Requests time: 434.57191586494446
#Selenium time: 937.4061963558197
#Time test between methods for 500 search results 
