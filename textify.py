import datetime
import time
import sqlite3
import pandas as pd
import numpy as np
import sklearn as sk
import scipy as spy
import matplotlib.pyplot as plt
import seaborn as sns
import nltk

conn = sqlite3.connect('Jobs.db')
cur = conn.cursor()

cur.execute('SELECT * FROM [Jobs Indeed Data+Analyst]')
data = cur.fetchall()
df = pd.DataFrame(data=data, columns=['Job Title', 'Company','Location','Description'])
df['Job Search'] = 'Data Analyst'
print(df)
