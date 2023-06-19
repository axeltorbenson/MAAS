import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import random

def extract_html(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    html_content  = BeautifulSoup(response.content, 'html.parser')
    return html_content 

base_url = "http://www.ufcstats.com/statistics/events/completed?page=all"

html_content = extract_html(base_url)
event_links = []
for a in html_content.select('td.b-statistics__table-col a'):
    event_links.append(a['href'])

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
