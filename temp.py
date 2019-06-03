import sqlite3 
import pandas as pd 

conn = sqlite3.connect('JobDBa.db')
cur = conn.cursor()
cur.execute('SELECT * FROM [Jobs Indeed]')
data = cur.fetchall()
dfa = pd.DataFrame(data=data, columns=['Job Title', 'Company','Location','Description'])
dfa.to_csv('jobclust.csv')