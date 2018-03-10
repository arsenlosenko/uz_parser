#!/usr/bin/env python3

import aiohttp
import asyncio
import async_timeout

CITY_SEARCH_URL = 'https://booking.uz.gov.ua/train_search/station/'
TRAIN_DATA_URL = 'https://booking.uz.gov.ua/train_search/'
WAGON_DATA_URL = 'https://booking.uz.gov.ua/train_wagon/'

data_dict ={ 
        'from': 'Вінниця',
        'to':'Київ',
        'date':'2018-03-12',
        'time':'00:00',
        'get_tpl':1
        }

async def async_get(url, data):
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(10):
            async with session.get(url, params=data) as resp:
                return resp.json()

async def async_post(url, data):
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(10):
            async with session.post(url, data=data) as resp:
                return resp.json()

async def get_city_code(city_name):
    cities_json = await async_get(CITY_SEARCH_URL, {'term': city_name})
    city_data = list(filter(lambda x: x['title'] == city_name, await cities_json))
    city_code = city_data[0]['value']
    return city_code

async def retrieve_trains_data(data_dict):
    data_dict['from'] = await get_city_code(data_dict['from'])
    data_dict['to'] = await get_city_code(data_dict['to'])
    train_data = await async_post(TRAIN_DATA_URL, data=data_dict)
    return await train_data
    
async def parse_train_data(data_dict):
    train_data = await retrieve_trains_data(data_dict)
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
        await retrieve_wagon_data(train_data_dict)

async def retrieve_wagon_data(train_data_dict):
    wagon_data = await async_post(WAGON_DATA_URL, data=train_data_dict)
    wagon_data_json = await wagon_data
    if 'error' in wagon_data_json.keys() and train_data_dict['wagon_num'] <= 15:
        train_data_dict['wagon_num'] += 1
        await retrieve_wagon_data(train_data_dict)
    print(wagon_data_json)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parse_train_data(data_dict))
