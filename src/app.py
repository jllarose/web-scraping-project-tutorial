import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

url = "https://ycharts.com/companies/TSLA/revenues"

response = requests.get(url)

if response.status_code == 200:
    html_content = response.text
    print("HTML content downloaded successfully.")
else:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    request = requests.get(url, headers = headers)
    time.sleep(10)
    response = request.text

soup = BeautifulSoup(response, 'html.parser')

revenue_table = soup.find('table')

if revenue_table:
    print("Revenue table found.")
else:
    print("Could not find the revenue table.")

# Extract all rows and columns from the table
rows = revenue_table.find_all('tr')


# Prepare data for the DataFrame
data = []
for row in rows:
    columns = row.find_all('td')  # Adjust based on the table's structure
    data.append([col.text.strip() for col in columns])

# Create a Pandas DataFrame
df = pd.DataFrame(data, columns=['Date', 'Revenue'])
# print(df)

df= df.dropna()
df['Revenue'] = df['Revenue'].replace({'\$': '', ',': ''})

def convert_to_float(value):
    if 'B' in value:
        return float(value.replace('B', '')) * 1e9
    elif 'M' in value:  # Just in case there are 'M' for millions
        return float(value.replace('M', '')) * 1e6
    else:
        return float(value)

df['Revenue'] = df['Revenue'].apply(convert_to_float)
df.head()


# Step 5

con = sqlite3.connect('tesla_revenue.db')
cursor = con.cursor()

cursor.execute('''
               CREATE TABLE IF NOT EXISTS revenue (
                Date TEXT,
               Revenue REAL
               
               )
               ''')

df.to_sql('revenue', con, if_exists='append', index=False)
con.commit()
con.close()


# Step 6: Visualize the Data

fig, axis = plt.subplots(figsize = (10, 5))

df["Date"] = pd.to_datetime(df["Date"])
df["Revenue"] = df["Revenue"].astype('float')
sns.lineplot(data = df, x = "Date", y = "Revenue")

plt.tight_layout()

plt.show()