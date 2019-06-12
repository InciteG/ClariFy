from bs4 import BeautifulSoup
import time
import datetime
import requests
import pandas as pd
"""Webdriver Setup and SQL Setup"""

#scrape indeed from indeed.ca
def indeedca_scrape(job_titles):
    indeed_url = 'https://www.indeed.ca' #base url
    pglnklst = []
    locations = ['Greater+Toronto+Area%2C+ON']
    for location in locations:
        for job in job_titles:
            pgnm = []
            for x in range(0, 20, 20): #40 applications per category
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
    nlist = []
    for ex in nodup:
        st = requests.get(indeed_url+ex)
        soup = BeautifulSoup(st.text, 'lxml')
        title = soup.find('h3',class_='icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title')
        company = soup.find('div', class_='icl-u-lg-mr--sm icl-u-xs-mr--xs')
        location = soup.find('span',class_='jobsearch-JobMetadataHeader-iconLabel')
        description = soup.find('div', id='jobDescriptionText')
        try:
            nxtrow = [title.text, company.text, location.text, description.text, indeed_url+ex] #if empty skip insert into database, pass over webpages that were not accessed correctly
        except:
            pass
        else:
            nlist.append(nxtrow)
    return pd.DataFrame(data=nlist, columns=['Job Title','Company','Location','Description','URL'])