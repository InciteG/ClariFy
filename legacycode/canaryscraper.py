from bs4 import BeautifulSoup
import time
import sqlite3
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
"""Webdriver Setup and SQL Setup"""
chrome_options = Options()
chrome_options.binary_location = r"C:\Users\Gary_Guo\AppData\Local\Google\Chrome SxS\Application\chrome.exe"
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(r"C:\Users\Gary_Guo\AppData\Local\Google\Chrome SxS\Application\chromedriver.exe", chrome_options=chrome_options)
driver.implicitly_wait(4)
conn = sqlite3.connect('Jobs.db')
cur = conn.cursor()
job_titles = ["Data Analyst"]
locations = ['Greater Toronto Area, ON']
#https://www.indeed.ca/jobs?q=Data+Analyst&l=Greater+Toronto+Area%2C+ON , sample link
indeed_url = 'https://www.indeed.ca'
cur.execute('CREATE TABLE IF NOT EXISTS [Jobs Indeed In] ([Job title], [Company], [Location], [Description]) ')
cur.execute('CREATE TABLE IF NOT EXISTS [Jobs] ([Job title], [Company], [Location], [Date Scraped], [Date Posted], [Source], [Description]) ')
conn.commit()
def indeed_req(job_titles,locations):
    pgnm = []
    for x in range(0,100, 20):
        pgnm.append('&start='+str(x))
    print(pgnm)
    pglist=[]
    count= 0 
    for nm in pgnm:
        pglist = []
        urlbuild = indeed_url+"/jobs?q=" + 'Data+Analyst' + '&l=' + 'Greater+Toronto+Area%2C+ON' + nm
        pg = requests.get(urlbuild)
        soup = BeautifulSoup(pg.text,'lxml')
        ho = soup.find_all('div', class_='title')
        for item in ho:
            a = item.find('a')
            s = set(pglist)
            lna = a.get('href')
            pglist.append(lna)
            # print(lna)
            # print(set)
            # if lna in s:
            #     pass
            # else:
            #     pglist.append(lna)
    print(len(pglist))

    # for lnk in pglist:
    #     pginfo = []
    #     driver.get(indeed_url + lnk)
    #     pgcont = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[3]/div/div/div[1]/div[1]')
    #     soup = BeautifulSoup(pgcont.get_attribute('innerHTML'), 'lxml')
    #     jobtitle = soup.find('h3', class_='icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title').text
    #     company = soup.find('div', class_='icl-u-lg-mr--sm icl-u-xs-mr--xs').text
    #     location = soup.find('span', class_='jobsearch-JobMetadataHeader-iconLabel').text
    #     content = soup.find('div', id='jobDescriptionText').text
    #     pginfo.append(jobtitle) 
    #     pginfo.append(company)
    #     pginfo.append(location)
    #     pginfo.append(content)
    #     print(pginfo)

        
        


    driver.close()

    

indeed_req('Data Analyst', 'Greater Toronto Area, ON')
#https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=Toronto%2C%20Ontario%2C%20Canada&locationId=PLACES.ca.2-1-0-1080&start25 sample linkedin link
def linkedin_scrape(job_titles, locations):
    url = r"https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=Toronto%2C%20Ontario%2C%20Canada&locationId=PLACES.ca.2-1-0-1080"
    cur.execute('CREATE TABLE IF NOT EXISTS [Jobs Linkedin ' + job +']([Job title] TEXT, [Company] TEXT, [Location] TEXT, [Description] TEXT, UNIQUE([Description])) ')
    for job in job_titles:
        for location in locations:
            pgnm = []
            for x in range(0,125, 25):
                pgnm.append('&start'+str(x))
            print(pgnm)
            for nm in pgnm:
                urlbuild = url + '?keywords=' + job + '&location=' + location + nm
                driver.get(urlbuild)
                row = driver.find_elements_by_class_name('job-card-search__title artdeco-entity-lockup__title ember-view')
                for link in row:
                    link.click()
                    time.sleep(1)
                try:
                    driver.find_element_by_class('jobs-details__main-content jobs-details__main-content--single-pane full-width relative')
                except NoSuchElementException:
                    pass
                else:
                    jobcont = driver.find_element_by_id('jobs-details__main-content jobs-details__main-content--single-pane full-width relative')
                    cont = jobcont.get_attribute('innerHTML')
                    soup = BeautifulSoup(cont, 'lxml')
                    title = soup.find('h1', class_='jobs-details-top-card__job-title t-20 t-black t-normal')
                    company = soup.find('a', class_='jobs-details-top-card__company-url ember-view')
                    location = soup.find('span', class_='jobs-details-top-card__bullet')
                    jobcont = driver.find_element_by_class_name('jobs-box__html-content jobs-description-content__text t-14 t-black--light t-normal')
                    cont = jobcont.get_attribute('innerHTML')
                    soup = BeautifulSoup(cont, 'lxml')
                    desc = soup.find('span')
                    try:
                        jobinfo = [title.text, company.text, location.text, desc.text]
                    except:
                        pass
                    else:
                        cur.execute('INSERT OR IGNORE INTO [Jobs Linkedin ' +job+']([Job Title], [Company], [Location], [Description]) Values(?,?,?,?)',jobinfo)
                        conn.commit()


job_titles = [r'data%20analyst', r'data%20science', r'big%20data', r'machine%20learning%20engineer', r'data%20engineer']
locations = [r'Toronto%2C%20Ontario%2C%20Canada',r'Vancouver%2C%20British%20Columbia%2C%20Canada', r'San%20Francisco%2C%20California']
# def indeed_scrape(job_titles, locations):
#     driver.get('https://www.indeed.ca')
#     i1 = driver.find_element_by_xpath('//*[@id="text-input-what"]')
#     i1.clear()
#     i1.send_keys(job_titles[0])
#     i2 = driver.find_element_by_xpath('//*[@id="text-input-where"]')
#     driver.find_element_by_xpath('//*[@id="text-input-where"]').clear()
#     i2t = i2.get_attribute("value")
#     for i in list(i2t):
#         i2.send_keys(Keys.BACK_SPACE)
#     i2.send_keys(locations[0])
#     i2.submit()
#     search_content = driver.find_element_by_xpath('//*[@id="resultsCol"]')
#     chtml = search_content.get_attribute("innerHTML")
#     # soup = BeautifulSoup(chtml,'lxml')
#     # row = soup.find_all('div', class_='jobsearch-SerpJobCard unifiedRow row result clickcard')
#     # linktitle = []
#     # for item in row:
#     #     title = item.find('div', class_='title')
#     #     print(title)
#     #     an = title.find('a')
#     #     link = an.get('href')
#     #     print(link)
#     row = driver.find_elements_by_class_name('jobsearch-SerpJobCard unifiedRow row result clickcard')
#     for item in row:
#         ih = item.get_attribute('innerHTML')
#         iz = BeautifulSoup(ih, 'lxml')
#         print(iz.text)
#     driver.close()
    


# indeed_scrape(job_titles,locations)