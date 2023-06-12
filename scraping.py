# script for scraping and cleaning ufc data

import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import random

base_url = "http://www.ufcstats.com/statistics/events/completed?page=all"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(base_url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

event_links = []
for a in soup.select('td.b-statistics__table-col a'):
    event_links.append(a['href'])

def parse_event_page(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Event name
    event_name = soup.find('h2').text

    # Extracting the table with all the fights
    table = soup.find('table', {'class': 'b-fight-details__table'})

    fight_data = []

    # Parsing each row in the table
    for index, row in enumerate(table.find_all('tr')[1:]):  # skipping the header row
        cols = row.find_all('td')

        # Split names using the HTML 'p' tag
        names = cols[1].find_all('p')
        a_fighter = names[0].get_text(strip=True) if len(names) > 1 else ""
        b_fighter = names[1].get_text(strip=True) if len(names) > 1 else ""

        # Similarly for other data columns, we need to correctly identify the HTML tags
        # and extract data from them
        a_KD = cols[2].find_all('p')[0].get_text(strip=True) if len(cols[2].find_all('p')) > 1 else ""
        b_KD = cols[2].find_all('p')[1].get_text(strip=True) if len(cols[2].find_all('p')) > 1 else ""
        a_STR = cols[3].find_all('p')[0].get_text(strip=True) if len(cols[2].find_all('p')) > 1 else ""
        b_STR = cols[3].find_all('p')[1].get_text(strip=True) if len(cols[2].find_all('p')) > 1 else ""
        a_TD = cols[4].find_all('p')[0].get_text(strip=True) if len(cols[2].find_all('p')) > 1 else ""
        b_TD = cols[4].find_all('p')[1].get_text(strip=True) if len(cols[2].find_all('p')) > 1 else ""
        a_SUB = cols[5].find_all('p')[0].get_text(strip=True) if len(cols[2].find_all('p')) > 1 else ""
        b_SUB = cols[5].find_all('p')[1].get_text(strip=True) if len(cols[2].find_all('p')) > 1 else ""

        # fighter links
        links = cols[1].find_all('a')
        a_fighter_link = links[0]['href'] if links else None
        b_fighter_link = links[1]['href'] if len(links) > 1 else None

        details = {
            'fight_number': event_name,
            # change to fighter A and fighter B
            # 'winner': cols[0].get_text(strip=True), # Does not make sense for this data collection
            'a_fighter': a_fighter,
            'b_fighter': b_fighter,
            'a_KD': a_KD,
            'b_KD': b_KD,
            'a_STR': a_STR,
            'b_STR':b_STR,
            'a_TD': a_TD,
            'b_TD':b_TD,
            'a_SUB': a_SUB,
            'b_SUB':b_SUB,
            'a_fighter_link': a_fighter_link,
            'b_fighter_link': b_fighter_link
        }

        fight_data.append(details)

    return fight_data

all_fights = []

for link in event_links[1:25]:
    all_fights.extend(parse_event_page(link))
    print('parsed: '+ link)
    time.sleep(random.uniform(1, 7))

df = pd.DataFrame(all_fights)

df = df.drop(['fight_number', 'a_fighter_link', 'b_fighter_link'], axis=1)

# Add a column to represent the winner, with the winner as 1 and the loser as 0
df['winner'] = 1

# Copy the dataframe and flip the a/b columns
df_flipped = df.copy()
df_flipped.columns = df.columns.str.replace('a_', 'temp_').str.replace('b_', 'a_').str.replace('temp_', 'b_')
df_flipped['winner'] = 0

# Concatenate the original and flipped dataframes
df = pd.concat([df, df_flipped])

# Randomly shuffle the rows
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

df.head(n=15)