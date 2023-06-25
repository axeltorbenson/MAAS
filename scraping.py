import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import random

def extract_html(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_content  = BeautifulSoup(response.content, 'html.parser')
        return html_content
    except Exception as e:
        print("Failed to fetch the URL", url, ":", e)

base_url = "http://www.ufcstats.com/statistics/events/completed?page=all"

try:
    html_content = extract_html(base_url)
    event_links = []
    for a in html_content.select('td.b-statistics__table-col a'):
        event_links.append(a['href'])
except Exception as e:
    print("Failed to scrape the base url:", e)

def parse_table_row(cols, col_number, sub_row_number):
    # sub_row_number is either 0 or 1. Each "row" has 2 rows in it
    row = cols[col_number].find_all('p')
    return row[sub_row_number].get_text(strip=True) if len(cols[col_number].find_all('p')) > 1 else ""

def parse_event_page(event_html):
    # event name
    event_name = event_html.find('h2').get_text(strip=True)

    # Extracting the table with all the fights
    table = event_html.find('table', {'class': 'b-fight-details__table'})

    fight_data = []

    # skip header row
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        details = {
            # main details of the fight

            ####
            # Need to include date next time I scrape
            ####

            'fight_link': row.get('data-link'),
            'event_name': event_name,
            'first_fighter_name': parse_table_row(cols, 1, 0),
            'second_fighter_name': parse_table_row(cols, 1, 1),
            'first_fighter_KD': parse_table_row(cols, 2, 0),
            'second_fighter_KD': parse_table_row(cols, 2, 1),
            'first_fighter_STR': parse_table_row(cols, 3, 0),
            'second_fighter_STR':parse_table_row(cols, 3, 1),
            'first_fighter_TD': parse_table_row(cols, 4, 0),
            'second_fighter_TD':parse_table_row(cols, 4, 1),
            'first_fighter_SUB': parse_table_row(cols, 5, 0),
            'second_fighter_SUB':parse_table_row(cols, 5, 1),
            'first_fighter_fighter_link': cols[1].find_all('a')[0]['href'] if len(cols[1].find_all('a')) > 1 else None,
            'second_fighter_fighter_link': cols[1].find_all('a')[1]['href'] if len(cols[1].find_all('a')) > 1 else None
        }
        
        time.sleep(random.uniform(0.5, 3))

        # the rest of this function clicks into the fight specific page and gets more detailed info
        fight_html = extract_html(details['fight_link'])

        # method of victory and time format (number of possible rounds)
        details['method'] = fight_html.find('i', style="font-style: normal").get_text(strip=True)

        items = fight_html.find_all(class_='b-fight-details__text-item')

        for item in items:
            label = item.find(class_='b-fight-details__label').text.strip()
            if label == 'Time format:':
                # Extract the text that follows the label
                details['time_format'] = item.text.replace(label, '').strip()
                break


        fight_tables = fight_html.find_all('table', {'class': 'b-fight-details__table js-fight-table'})

        # TOTALS table
        totals_table = fight_tables[0]
        for index, row in enumerate(totals_table.find_all('tr', {'class': 'b-fight-details__table-row'})[1:]):
            cols = row.find_all('td', {'class': 'b-fight-details__table-col'})
            details[f'first_fighter_round_{index+1}_KD'] = parse_table_row(cols, 1, 0)
            details[f'second_fighter_round_{index+1}_KD'] = parse_table_row(cols, 1, 1)
            details[f'first_fighter_round_{index+1}_SIG_STR'] = parse_table_row(cols, 2, 0)
            details[f'second_fighter_round_{index+1}_SIG_STR'] = parse_table_row(cols, 2, 1)
            details[f'first_fighter_round_{index+1}_TOT_STR'] = parse_table_row(cols, 4, 0)
            details[f'second_fighter_round_{index+1}_TOT_STR'] = parse_table_row(cols, 4, 1)
            details[f'first_fighter_round_{index+1}_TD'] = parse_table_row(cols, 5, 0)
            details[f'second_fighter_round_{index+1}_TD'] = parse_table_row(cols, 5, 1)
            details[f'first_fighter_round_{index+1}_SUB'] = parse_table_row(cols, 7, 0)
            details[f'second_fighter_round_{index+1}_SUB'] = parse_table_row(cols, 7, 1)
            details[f'first_fighter_round_{index+1}_REV'] = parse_table_row(cols, 8, 0)
            details[f'second_fighter_round_{index+1}_REV'] = parse_table_row(cols, 8, 1)
            details[f'first_fighter_round_{index+1}_CTRL'] = parse_table_row(cols, 9, 0)
            details[f'second_fighter_round_{index+1}_CTRL'] = parse_table_row(cols, 9, 1)

        # SIGNIFICANT STRIKES table
        sig_strikes_table = fight_tables[1]
        for index, row in enumerate(sig_strikes_table.find_all('tr', {'class': 'b-fight-details__table-row'})[1:]):
            cols = row.find_all('td', {'class': 'b-fight-details__table-col'})
            details[f'first_fighter_round_{index+1}_HEAD'] = parse_table_row(cols, 3, 0)
            details[f'second_fighter_round_{index+1}_HEAD'] = parse_table_row(cols, 3, 1)
            details[f'first_fighter_round_{index+1}_BODY'] = parse_table_row(cols, 4, 0)
            details[f'second_fighter_round_{index+1}_BODY'] = parse_table_row(cols, 4, 1)
            details[f'first_fighter_round_{index+1}_LEG'] = parse_table_row(cols, 5, 0)
            details[f'second_fighter_round_{index+1}_LEG'] = parse_table_row(cols, 5, 1)
            details[f'first_fighter_round_{index+1}_DISTANCE'] = parse_table_row(cols, 6, 0)
            details[f'second_fighter_round_{index+1}_DISTANCE'] = parse_table_row(cols, 6, 1)
            details[f'first_fighter_round_{index+1}_CLINCH'] = parse_table_row(cols, 7, 0)
            details[f'second_fighter_round_{index+1}_CLINCH'] = parse_table_row(cols, 7, 1)
            details[f'first_fighter_round_{index+1}_GROUND'] = parse_table_row(cols, 8, 0)
            details[f'second_fighter_round_{index+1}_GROUND'] = parse_table_row(cols, 8, 1)        

        
        fight_data.append(details)

    return fight_data

fight_data_list = []
# I scraped until UFC 21, where fights started following modern round standards
for index, link in enumerate(event_links[1:629]):
    try:
        fight_data_list.extend(parse_event_page(extract_html(link)))
        print(f'parsed event {index}: '+ link)
        time.sleep(random.uniform(0.5, 2))

        # Save to CSV after every parse, in case of failure.
        df = pd.DataFrame(fight_data_list)
        df.to_csv("fight_data.csv", index=False)
    except Exception as e:
        print("Failed to parse event link", link, ":", e)

try:
    df = pd.DataFrame(fight_data_list)
    df.to_csv("fight_data.csv", index=False)
except Exception as e:
    print("Failed to save the data:", e)

def split_column(df, col):
    # Create a placeholder for NA values
    df[col].fillna('NA of NA', inplace=True)

    # make function to split column
    df[[f'{col}_landed', f'{col}_attempted']] = df[col].str.split(' of ', expand=True)
    df[[f'{col}_landed', f'{col}_attempted']] = df[[f'{col}_landed', f'{col}_attempted']].replace('NA', np.nan)

    # Convert columns to float type
    df[f'{col}_landed'] = df[f'{col}_landed'].astype(float)
    df[f'{col}_attempted'] = df[f'{col}_attempted'].astype(float)

    df.drop(col, axis=1, inplace=True)

    return df


cols_to_split = [
    'first_fighter_round_1_SIG_STR', 'second_fighter_round_1_SIG_STR', 'first_fighter_round_1_TOT_STR',
    'second_fighter_round_1_TOT_STR', 'first_fighter_round_1_TD', 'second_fighter_round_1_TD', 'first_fighter_round_2_SIG_STR',
    'second_fighter_round_2_SIG_STR', 'first_fighter_round_2_TOT_STR', 'second_fighter_round_2_TOT_STR', 'first_fighter_round_2_TD',
    'second_fighter_round_2_TD', 'first_fighter_round_3_SIG_STR', 'second_fighter_round_3_SIG_STR', 'first_fighter_round_3_TOT_STR',
    'second_fighter_round_3_TOT_STR', 'first_fighter_round_3_TD', 'second_fighter_round_3_TD', 'first_fighter_round_4_SIG_STR',
    'second_fighter_round_4_SIG_STR', 'first_fighter_round_4_TOT_STR', 'second_fighter_round_4_TOT_STR', 'first_fighter_round_4_TD',
    'second_fighter_round_4_TD', 'first_fighter_round_5_SIG_STR', 'second_fighter_round_5_SIG_STR', 'first_fighter_round_5_TOT_STR',
    'second_fighter_round_5_TOT_STR', 'first_fighter_round_5_TD', 'second_fighter_round_5_TD', 'first_fighter_round_1_HEAD',
    'second_fighter_round_1_HEAD', 'first_fighter_round_1_BODY', 'second_fighter_round_1_BODY', 'first_fighter_round_1_LEG',
    'second_fighter_round_1_LEG', 'first_fighter_round_1_DISTANCE', 'second_fighter_round_1_DISTANCE',
    'first_fighter_round_1_CLINCH', 'second_fighter_round_1_CLINCH', 'first_fighter_round_1_GROUND', 'second_fighter_round_1_GROUND',
    'first_fighter_round_2_HEAD', 'second_fighter_round_2_HEAD', 'first_fighter_round_2_BODY', 'second_fighter_round_2_BODY',
    'first_fighter_round_2_LEG', 'second_fighter_round_2_LEG', 'first_fighter_round_2_DISTANCE', 'second_fighter_round_2_DISTANCE',
    'first_fighter_round_2_CLINCH', 'second_fighter_round_2_CLINCH', 'first_fighter_round_2_GROUND', 'second_fighter_round_2_GROUND',
    'first_fighter_round_3_HEAD', 'second_fighter_round_3_HEAD', 'first_fighter_round_3_BODY', 'second_fighter_round_3_BODY',
    'first_fighter_round_3_LEG', 'second_fighter_round_3_LEG', 'first_fighter_round_3_DISTANCE', 'second_fighter_round_3_DISTANCE',
    'first_fighter_round_3_CLINCH', 'second_fighter_round_3_CLINCH', 'first_fighter_round_3_GROUND', 'second_fighter_round_3_GROUND',
    'first_fighter_round_4_HEAD', 'second_fighter_round_4_HEAD', 'first_fighter_round_4_BODY', 'second_fighter_round_4_BODY',
    'first_fighter_round_4_LEG', 'second_fighter_round_4_LEG', 'first_fighter_round_4_DISTANCE', 'second_fighter_round_4_DISTANCE',
    'first_fighter_round_4_CLINCH', 'second_fighter_round_4_CLINCH', 'first_fighter_round_4_GROUND', 'second_fighter_round_4_GROUND',
    'first_fighter_round_5_HEAD', 'second_fighter_round_5_HEAD', 'first_fighter_round_5_BODY', 'second_fighter_round_5_BODY',
    'first_fighter_round_5_LEG', 'second_fighter_round_5_LEG', 'first_fighter_round_5_DISTANCE', 'second_fighter_round_5_DISTANCE',
    'first_fighter_round_5_CLINCH', 'second_fighter_round_5_CLINCH', 'first_fighter_round_5_GROUND', 'second_fighter_round_5_GROUND'
    ]

for col in cols_to_split:
    split_column(df, col)

def convert_to_seconds(df, cols):
    # there is a single fight with "--" as the time. I manually replaced with NA
    for col in cols:
        df[col] = df[col].astype(str)

        # Replace 'nan' values with a placeholder
        df[col] = df[col].replace('nan', 'NA:NA')

        # Split the time on the colon
        time_split = df[col].str.split(':', expand=True)

        # Create a mask for rows that are not NA
        mask = df[col] != 'NA:NA'

        df.loc[mask, col] = time_split[0][mask].astype(int) * 60 + time_split[1][mask].astype(int)

        # Replace placeholders with NA
        df[col].replace('NA:NA', np.nan, inplace=True)

    return df

cols_to_seconds = [
    'first_fighter_round_1_CTRL',
    'second_fighter_round_1_CTRL',
    'first_fighter_round_2_CTRL',
    'second_fighter_round_2_CTRL',
    'first_fighter_round_3_CTRL',
    'second_fighter_round_3_CTRL',
    'first_fighter_round_4_CTRL',
    'second_fighter_round_4_CTRL',
    'first_fighter_round_5_CTRL',
    'second_fighter_round_5_CTRL'

]

df = convert_to_seconds(df, cols_to_seconds)

df['time_format'] = df['time_format'].astype(str).str.extract(r'^(\d+)')
df = df.rename(columns={'time_format':'number_of_rounds'})