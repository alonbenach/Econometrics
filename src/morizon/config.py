import datetime


price_patterns = {
    'full_price': '^(.*)zł$',
    'per_meter_price': '^(.*)zł/m²?$',
}

dates = {
    'dzisiaj': datetime.datetime.today().strftime('%d %m %Y'),
    'wczoraj': (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%d %m %Y'),
}

params_patterns = {
    'rooms': '(.*)pok*',
    'footprint': '([0-9, ]*)m2',
    ('floor', 'floors_total'): '(?:piętro )?(parter|[0-9]+)/([0-9]+)',
    'floor': '(?:piętro )?(parter|[0-9]+)',
}



SEARCH_URL = 'https://www.morizon.pl/mieszkania/warszawa/{district}/?ps%5Bnumber_of_rooms_from%5D=2&page={page}'

UPDATE_URL = 'https://www.morizon.pl/mieszkania/warszawa/{district}/?ps%5Bnumber_of_rooms_from%5D=2&ps%5Bdate_filter%5D=7'