import time
import re
import pandas as pd

import requests
from bs4 import BeautifulSoup

from tqdm.auto import tqdm


from src.morizon.config import price_patterns, params_patterns, dates
from src.common import NULL_INT, SLEEP_TIME, cleanup_number


def parse_results_page(page_results, links=None):
    if links is None:
        links = set()
    elif not isinstance(links, set):
        links = set(links)
    database = []
    for record in page_results:
        attrs = {}
        link = record.find('a', href=True)['href']
        link = link.split('?')[0]
        if link in links:
            continue
        attrs['link'] = 'https://www.morizon.pl' + link
        attrs['title'] = record.find('span', class_='offer__title').getText().strip()

        for i in record.find('div', class_='offer-price'):
            price = i.getText().strip()
            for price_type, pattern in price_patterns.items():
                m = re.match(pattern, price)
                if m is not None:
                    price_val = m.group(1)
                    attrs[price_type] = cleanup_number(price_val)
                    break
        params_list = record.find('div', class_='property-info')
        if params_list is None:
            continue

        for param in params_list.getText().split('•'):
            for param_type, pattern in params_patterns.items():
                m = re.match(pattern, param)
                if m is not None:
                    param_val = m.groups()
                    if isinstance(param_type, tuple):
                        for param_type_i, param_val_i in zip(param_type, param_val):
                            attrs[param_type_i] = param_val_i
                    else:
                        assert len(param_val) == 1, param_type
                        attrs[param_type] = param_val[0]
                    break
        database.append(attrs)
    return database


def add_details(database):
    full_details = []

    for url in tqdm(database['link']):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # gmap = soup.find('div', class_='GoogleMap')
        details = {'link': url}
        for row in soup.find_all('div', class_='detailed-information__row'):
            colname = row.find('div', class_='detailed-information__cell--label').getText().lower().replace(' ', '_')
            value = row.find('div', class_='detailed-information__cell--value').getText()
            details[colname] = value

        full_details.append(details)

        time.sleep(SLEEP_TIME)

    full_details = pd.DataFrame(full_details)

    database = pd.merge(database, full_details, on='link', how='outer')

    return database


def create_database(url, links=None):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all('div', class_='offer')
    database = parse_results_page(results, links)
    database = pd.DataFrame(database)
    if (len(database) == 0) or ('full_price' not in database.columns):
        return pd.DataFrame()

    database = database.dropna(subset=['full_price'])
    database = add_details(database)

    if 'floor' in database:
        database['floor'] = database['floor'].str.replace('parter', '0', regex=False)
    for colname in ('rooms', 'footprint', 'floor', 'floors_total', 'rok_budowy'):
        if colname not in database:
            database[colname] = NULL_INT
        else:
            nul_idx = database[colname].isnull()
            database.loc[nul_idx, colname] = NULL_INT
        database[colname] = database[colname].astype('int16')

    mapping = {
        date_str: f'{i+1:02d}'
        for i, date_str in enumerate(
            ['sty', 'lut', 'mar', 'kwi', 'maj', 'cze', 'lip', 'sie', 'wrz', 'paź', 'lis', 'gru'])
    }

    date = database['data_dodania']
    date = date.replace(dates)
    date = date.str.split('.', expand=True)

    date = pd.to_datetime(date[2] + '-' + date[1] + '-' + date[0])
    database['date'] = pd.to_datetime(date)
    database['location'] = database.title.str.split(', ').str[-1].str.replace('\xa0', ' ', regex=False)
    database['page'] = 'morizon'
    return database
