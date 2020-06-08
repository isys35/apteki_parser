import requests
from bs4 import BeautifulSoup as BS
from urllib.parse import quote
import csv_writer
from history_writer import *
import time
import xml_writer
import sys

KEYS_FOR_SEARCHING = 'qwertyuiopasdfghjklzxcvbnm1234567890йцукенгшщзхъфывапролджэячсмитьбю'


def get_initial_data():
    with open('stolichniki_data/initial_data.txt', 'r', encoding='cp1251') as txt:
        rows = txt.read().split('\n')
        apteks = []
        for row in rows:
            splited_row = row.split(';')
            aptek = {'url': splited_row[0], 'address': splited_row[1]}
            apteks.append(aptek)
        return apteks


def keys_for_seaching():
    return [quote(key) for key in list(KEYS_FOR_SEARCHING)]


def parsing_meds(resp):
    soup = BS(resp, 'lxml')
    table = soup.select_one('.table.products-list-in-store')
    if not table:
        return
    meds_soup = table.select('tr')
    meds = []
    for med_soup in meds_soup:
        if med_soup.select_one('.store-info'):
            title = med_soup.select_one('.store-info').select_one('a').text
            id = med_soup.select_one('.store-info').select_one('a')['href'].split('/')[-1]
            if id not in load_file(r'stolichniki_data/parsed_med'):
                print(title, id)
                product_prices = med_soup.select_one('.product-price').select('.price-block')
                product_prices_num = []
                for product_price in product_prices:
                    price_txt = product_price.text.replace('\n', '').replace(u'\xa0', ' ')
                    if 'Цена по карте' in price_txt:
                        continue
                    if not 'Цена' in price_txt:
                        continue
                    price = price_txt.split(' ')[1]
                    product_prices_num.append(float(price))
                price_aptek_med = product_prices_num[-1]
                meds.append({'title': title, 'id': id, 'price': price_aptek_med})
                save_file(r'stolichniki_data/parsed_med', id)
    return meds


class Stolichniki:
    HEADERS = {
        'Host': 'stolichki.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'
    }
    HEADERS_JSON = {
        'Host': 'stolichki.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
        'Referer': 'https://stolichki.ru/apteki',
        'Accept': 'application/json, text/plain, */*',
        'X-Requested-With': 'XMLHttpRequest'
    }

    def __init__(self):
        self.initial_data = self.get_initial_data()
        self.keys_for_searching = keys_for_seaching()
        self.csv_file = r'stolichniki_data/stolichniki_catalog.csv'

    def get_initial_data(self):
        resp = requests.get('https://stolichki.ru/apteki', headers=self.HEADERS)
        soup = BS(resp.text, 'lxml')
        csrf_token = soup.find('meta', attrs={'name': "csrf-token"})['content']
        self.HEADERS_JSON['X-CSRF-TOKEN'] = csrf_token
        resp = requests.get('https://stolichki.ru/stores/all?cityId=1', headers=self.HEADERS_JSON)
        json_resp = resp.json()
        stores = json_resp['stores']
        apteks = []
        for store in stores:
            apteks.append({'url': f"https://stolichki.ru/apteki/{store['id']}", 'address':store['full_address']})
        return apteks

    def create_save_files(self):
        create_save_file(r'stolichniki_data/parsed_updated_urls')
        create_save_file(r'stolichniki_data/parsed_aptek_urls')
        create_save_file(r'stolichniki_data/parsed_med')

    def update_catalog(self, begin=True):
        if begin:
            csv_writer.create_csv_file(self.csv_file)
            self.create_save_files()
        aptek_urls = [url['url'] for url in self.initial_data
                        if url['url'] not in load_file(r'stolichniki_data/parsed_aptek_urls')]
        for aptek_url in aptek_urls:
            print(aptek_url)
            updated_urls = [aptek_url + '?q=' + key for key in self.keys_for_searching if
                            aptek_url + '?q=' + key not in load_file(r'stolichniki_data/parsed_updated_urls')]
            for aptek_key_url in updated_urls:
                print(aptek_key_url)
                resp = self.request(aptek_key_url)
                meds = parsing_meds(resp)
                if meds:
                    csv_writer.add_data_in_catalog(self.csv_file, meds)
                save_file(r'stolichniki_data/parsed_updated_urls', aptek_key_url)
            save_file(r'stolichniki_data/parsed_aptek_urls', aptek_url)
        print('[INFO] Каталог обновлён')

    def update_price(self, begin=True):
        if begin:
            for aptek in self.initial_data:
                id = aptek['url'].split('/')[-1]
                file_name = r'stolichniki_data/stolichniki_' + id + '.xml'
                date = time.strftime("%Y-%m-%d %H:%M:%S")
                xml_writer.createXML(file_name, id, aptek['address'], date)
            self.create_save_files()
        aptek_urls = [url['url'] for url in self.initial_data
                      if url['url'] not in load_file(r'stolichniki_data/parsed_aptek_urls')]
        for aptek_url in aptek_urls:
            print(aptek_url)
            create_save_file(r'stolichniki_data/parsed_med')
            aptek_id = aptek_url.split('/')[-1]
            file_name = r'stolichniki_data/stolichniki_' + aptek_id + '.xml'
            updated_urls = [aptek_url + '?q=' + key for key in self.keys_for_searching if
                            aptek_url + '?q=' + key not in load_file(r'stolichniki_data/parsed_updated_urls')]
            for aptek_key_url in updated_urls:
                print(aptek_key_url)
                resp = self.request(aptek_key_url)
                meds = parsing_meds(resp)
                if meds:
                    for med in meds:
                        xml_writer.add_price(file_name, med['id'], str(med['price']))
                save_file(r'stolichniki_data/parsed_updated_urls', aptek_key_url)
            save_file(r'stolichniki_data/parsed_aptek_urls', aptek_url)
        print('[INFO] Цены обновлены')

    def request(self, url):
        r = requests.get(url, headers=self.HEADERS)
        return r.text


if __name__ == '__main__':
    parser = Stolichniki()
    parser.update_catalog(begin=True)
    parser.update_price(begin=True)
