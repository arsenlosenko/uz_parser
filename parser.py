#!/usr/bin/env python3

import requests
import datetime

data_dict ={ 
        'from': 'Вінниця',
        'to':'Київ',
        'date':'2018-03-10',
        'time':'00:00',
        'get_tpl':1
        }

def get_city_code(city_name):
    city_search_url = 'https://booking.uz.gov.ua/train_search/station/'
    cities = requests.get(city_search_url,params={'term': city_name})
    cities_json = cities.json()
    city_data = list(filter(lambda x: x['title'] == city_name, cities_json))
    city_code = city_data[0]['value']
    return city_code

def retrieve_trains_data(data_dict):
    train_data_url = 'https://booking.uz.gov.ua/train_search/'
    from_city_code = get_city_code(data_dict['from'])
    to_city_code = get_city_code(data_dict['to'])
    data_dict['from'] = from_city_code
    data_dict['to'] = to_city_code
    train_data = requests.post(train_data_url, data=data_dict)
    return train_data.json()

def parse_train_data(data_dict):
    train_data = retrieve_trains_data(data_dict)
    trains_list = train_data['data']['list']
    for train in trains_list:
        train_data_dict = {
                'from': data_dict['from'],
                'to': data_dict['to'],
                'train': train['num'],
                'date': data_dict['date'],
                'wagon_num': 1,
                'wagon_type': "П",
                'wagon_class': "Д",
                'cached_scheme[]': "П01"
            }
        retrieve_wagon_data(train_data_dict)

def retrieve_wagon_data(train_data_dict):
    wagon_data_url = 'https://booking.uz.gov.ua/train_wagon/'
    wagon_data = requests.post(wagon_data_url, data=train_data_dict)
    wagon_data_json = wagon_data.json()
    if 'error' in wagon_data_json.keys() and train_data_dict['wagon_num'] <= 15:
        train_data_dict['wagon_num'] += 1
        retrieve_wagon_data(train_data_dict)
    print(wagon_data_json)


if __name__ == "__main__":
    parse_train_data(data_dict)

