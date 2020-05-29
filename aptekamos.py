from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
import requests
from bs4 import BeautifulSoup as BS
import csv_writer
from history_writer import *
import time
import xml_writer
# from xml_writer import createXML, add_price, get_meds_id
import aiohttp
import asyncio
from requests.exceptions import ProxyError
import sys
from json.decoder import JSONDecodeError
import grequests
from threading import Thread


def get_initial_data():
    with open('aptekamos_data/initial_data.txt', 'r', encoding='utf8') as txt:
        rows = txt.read().split('\n')
        apteks = []
        print(rows)
        for row in rows:
            splited_row = row.split(';')
            aptek = {'url': splited_row[0], 'address': splited_row[1]}
            apteks.append(aptek)
        return apteks


def parsing_meds_data(resp):
    soup = BS(resp, 'lxml')
    apteks = soup.select('.org-data')
    data = {}
    for aptek in apteks:
        aptek_url = aptek.select_one('.ret-org')['href']
        try:
            aptek_price = float(
                aptek.select_one('.ret-drug-price').text.replace('\n', '').replace(',', '.').strip())
        except ValueError:
            continue
        data[aptek_url] = aptek_price
    return data


def parsing_pages_apteks(resp):
    soup = BS(resp, 'lxml')
    check_pages = soup.select_one('#d-table-page-num')
    if check_pages:
        pages = 1 + int(soup.select_one('#d-table-pager-text').text.split(' ')[-1]) // 250
        return pages


def parsing_meds(resp):
    soup = BS(resp, 'lxml')
    meds_in_page = soup.select('.ret-med-name')
    meds = []
    for med in meds_in_page:
        a = med.select_one('a')
        if a:
            meds.append({'title': a['title'].replace(' цена', ''),
                                  'href': a['href'], 'id': a['href'].split('-')[-1].replace('/ceni', '')})
    return meds





async def fetch_content_post(url, session, headers, init_data):
    async with session.get(url, headers=headers, json=init_data) as response:
        resp = await response.text()
        return resp


async def req_post(urls, headers, init_data):
    async with aiohttp.ClientSession as session:
        tasks = []
        for i in range(0, len(urls)):
            task = asyncio.create_task(fetch_content_post(urls[i], session, headers[i], init_data[i]))
            tasks.append(task)
        resps = await asyncio.gather(*tasks, return_exceptions=True)
        return resps



def splited_list(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]


class AptekaMos:
    def __init__(self):
        self.headers = {'Host': 'aptekamos.ru',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'}
        self.initial_data = get_initial_data()
        self.url = 'https://aptekamos.ru/tovary'
        self.proxies_list = []
        self.with_proxy = False
        self.proxies_list = None
        self.proxie = None

    def update_catalog(self, begin=True):
        csv_file = r'aptekamos_data\catalog_aptekamos.csv'
        if begin:
            csv_writer.create_csv_file(csv_file)
            create_save_file(r'aptekamos_data\parsed_pages_url_catalog')
        pages = self.get_max_page()
        pages_url = [self.url]
        pages_url.extend([f'https://aptekamos.ru/tovary?page={i}' for i in range(2, pages + 1)])
        pages_url = [url for url in pages_url if url not in load_file(r'aptekamos_data\parsed_pages_url_catalog')]
        for page_url in pages_url:
            print(page_url)
            resp_page = self.sync_request(page_url, self.headers)
            save_html_file('ape', resp_page)
            meds = parsing_meds(resp_page)
            csv_writer.add_data_in_catalog(csv_file, meds)
            save_file(r'aptekamos_data\parsed_pages_url_catalog', page_url)
        print('[INFO] Каталог csv собран')

    def update_prices(self, begin=True):
        apteks_url = [aptek['url'] for aptek in self.initial_data]
        if begin:
            for aptek in self.initial_data:
                id = aptek['url'].replace('/ob-apteke','').split('-')[-1]
                file_name = r'aptekamos_data\aptekamos_' + id + '.xml'
                date = time.strftime("%Y-%m-%d %H:%M:%S")
                createXML(file_name, id, aptek['address'], date)
                create_save_file(r'aptekamos_data\parsed_pages_url')
                create_save_file(r'aptekamos_data\parsed_med')
        pages = self.get_max_page()
        pages_url = [self.url]
        pages_url.extend([f'https://aptekamos.ru/tovary?page={i}' for i in range(2, pages + 1)])
        pages_url = [url for url in pages_url if url not in load_file(r'aptekamos_data\parsed_pages_url')]
        for page_url in pages_url:
            t_start = time.time()
            print(page_url)
            resp_page = self.sync_request(page_url, self.headers)
            meds = parsing_meds(resp_page)
            meds = [med for med in meds if med['href'] not in load_file(r'aptekamos_data\parsed_med')]
            for med in meds:
                print(med['href'])
                print(med)
                resp_med = self.sync_request(med['href'], self.headers)
                meds_data = parsing_meds_data(resp_med)
                pages_apteks = parsing_pages_apteks(resp_med)
                if pages_apteks:
                    pages_apteks_urls = [med[
                                             'href'] + f'?llat=0.0&llng=0.0&on=&so=0&p=&f=&c=&page={i + 1}&min=0&max=0&ord=0&sale=0&e=0&st=0&r' \
                                             f'=&me=0&duty=0&mn=0' for i in range(1, pages_apteks+1)]
                    for page_aptek_url in pages_apteks_urls:
                        print(page_aptek_url)
                        resp_med = self.sync_request(page_aptek_url, self.headers)
                        meds_data_page = parsing_meds_data(resp_med)
                        meds_data.update(meds_data_page)
                for apt in meds_data:
                    if apt in apteks_url:
                        id_aptek = apt.replace('/ob-apteke', '').split('-')[-1]
                        file_name = r'aptekamos_data\aptekamos_' + id_aptek + '.xml'
                        add_price(file_name, med['id'], str(meds_data[apt]))
                        print(file_name + ' upd')
                save_file(r'aptekamos_data\parsed_med', med['href'])
            print('Время на cтраницу ' + str(time.time() - t_start))
            save_file(r'aptekamos_data\parsed_pages_url', page_url)

    def get_max_page(self):
        r = self.sync_request(self.url, self.headers)
        soup = BS(r, 'html.parser')
        pager_text = soup.select_one('#d-table-pager-text').text
        meds = int(pager_text.split(' ')[-1])
        pages = (meds // 100) + 1
        return pages

    def sync_request(self, url, headers):
        while True:
            try:
                r = requests.get(url, headers=headers, proxies=self.proxie)
                if 'Доступ к странице запрещен.' in r.text:
                    print('Доступ к странице запрещен.')
                    if not self.proxies_list:
                        self.proxies_list = proxy.get_proxies()
                    proxie = self.proxies_list.pop()
                    self.proxie = {'http': proxie, 'https': proxie}
                else:
                    break
            except ProxyError:
                print(str(self.proxie) + ' не работает')
                if not self.proxies_list:
                    self.proxies_list = proxy.get_proxies()
                proxie = self.proxies_list.pop()
                self.proxie = {'http': proxie, 'https': proxie}
        return r.text


class AptekaMosAsync(AptekaMos):
    def __init__(self):
        super().__init__()

    def async_request(self, urls, headers):
        responses = asyncio.run(req(urls, headers))
        for response in responses:
            if 'Доступ к странице запрещен.' in response:
                print('Доступ к странице запрещен.')
                sys.exit()
        return responses

    def update_prices(self, begin=True):
        apteks_url = [aptek['url'] for aptek in self.initial_data]
        if begin:
            for aptek in self.initial_data:
                id = aptek['url'].replace('/ob-apteke','').split('-')[-1]
                file_name = r'aptekamos_data\aptekamos_' + id + '.xml'
                date = time.strftime("%Y-%m-%d %H:%M:%S")
                createXML(file_name, id, aptek['address'], date)
                create_save_file(r'aptekamos_data\parsed_pages_url')
                create_save_file(r'aptekamos_data\parsed_med')
        pages = self.get_max_page()
        pages_url = [self.url]
        pages_url.extend([f'https://aptekamos.ru/tovary?page={i}' for i in range(2, pages + 1)])
        pages_url = [url for url in pages_url if url not in load_file(r'aptekamos_data\parsed_pages_url')]
        for page_url in pages_url:
            t_start = time.time()
            print(page_url)
            resp_page = self.sync_request(page_url, self.headers)
            meds = parsing_meds(resp_page)
            meds = [med for med in meds if med['href'] not in load_file(r'aptekamos_data\parsed_med')]
            resps_med_main = self.async_request([med['href'] for med in meds], [self.headers for _ in range(len(meds))])
            for resp_med_main in resps_med_main:
                print(meds[resps_med_main.index(resp_med_main)]['href'])
                meds_data = parsing_meds_data(resp_med_main)
                pages_apteks = parsing_pages_apteks(resp_med_main)
                if pages_apteks:
                    pages_apteks_urls = [meds[
                                             resps_med_main.index(resp_med_main)]['href'] + f'?llat=0.0&llng=0.0&on=&so=0&p=&f=&c=&page={i + 1}&min=0&max=0&ord=0&sale=0&e=0&st=0&r' \
                                             f'=&me=0&duty=0&mn=0' for i in range(1, pages_apteks+1)]
                    print(pages_apteks_urls)
                    resps_med = self.async_request(pages_apteks_urls, [self.headers for _ in range(len(pages_apteks_urls))])
                    for r_med in resps_med:
                        meds_data_page = parsing_meds_data(r_med)
                        meds_data.update(meds_data_page)
                for apt in meds_data:
                    if apt in apteks_url:
                        id_aptek = apt.replace('/ob-apteke', '').split('-')[-1]
                        file_name = r'aptekamos_data\aptekamos_' + id_aptek + '.xml'
                        add_price(file_name, meds[resps_med_main.index(resp_med_main)]['id'], str(meds_data[apt]))
                        print(file_name + ' upd')
                save_file(r'aptekamos_data\parsed_med', meds[resps_med_main.index(resp_med_main)]['href'])
            print('Время на cтраницу ' + str(time.time() - t_start))
            save_file(r'aptekamos_data\parsed_pages_url', page_url)


class AptekaMosAPI(AptekaMosAsync):
    def api_request(self, aptek_url, aptek_id, med):
        headers = {'Host': 'aptekamos.ru',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Referer': aptek_url,
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Length': '79',
                    'Origin': 'https://aptekamos.ru'}
        data = '{"orgId": %s, "wuserId": 0,"searchPhrase": "%s"}' % (aptek_id, med)
        url = 'https://aptekamos.ru/Services/WOrgs/getOrgPrice4?compressOutput=1'
        r = requests.post(url, headers=headers, data=data.encode('utf8'))
        if 'Доступ запрещен' in r.text:
            print('Доступ запрещен')
            sys.exit()
        try:
            return r.json()
        except JSONDecodeError:
            print('JSONDecodeError')
            print(r.text)
            return None

    def update_prices(self, begin=True):
        apteks = [[aptek['url'].replace('/ob-apteke','').split('-')[-1], aptek['url'], aptek['address']] for aptek in self.initial_data]
        meds = csv_writer.read_meds_names('aptekamos_data/catalog_aptekamos.csv')
        if begin:
            for aptek in apteks:
                file_name = r'aptekamos_data\aptekamos_' + aptek[0] + '.xml'
                date = time.strftime("%Y-%m-%d %H:%M:%S")
                createXML(file_name, aptek[0], aptek[2], date)
                create_save_file(r'aptekamos_data\parsed_med')
                create_save_file(r'aptekamos_data\parsed_apteks')
        parsing_apteks = [aptek for aptek in apteks if str(aptek) not in load_file(r'aptekamos_data\parsed_apteks')]
        for aptek in parsing_apteks:
            file_name = r'aptekamos_data\aptekamos_' + aptek[0] + '.xml'
            parsing_meds = [med for med in meds if med not in load_file(r'aptekamos_data\parsed_med')]
            for med in parsing_meds:
                print(aptek, med)
                t0 = time.time()
                resp = self.api_request(aptek[1], aptek[0], med)
                print(time.time()-t0)
                if not resp:
                    save_file(r'aptekamos_data\parsed_med', med)
                    continue
                if resp['price']:
                    med_id = str(resp['price'][0]['medId'])
                    price = str(resp['price'][0]['price'])
                    add_price(file_name, med_id, price)
                    print(med_id, price)
                    print(file_name + ' upd')
                save_file(r'aptekamos_data\parsed_med', med)
            create_save_file(r'aptekamos_data\parsed_med')
            save_file(r'aptekamos_data\parsed_apteks', str(aptek))


class AptekaMosAsyncAPI(AptekaMosAPI):
    def update_prices(self, begin=True):
        threads = [PriceUpdater(aptek, begin) for aptek in self.initial_data]
        for thread in threads:
            thread.start()


def api_request(aptek_url, aptek_id, med_lst):
    headers = [{'Host': 'aptekamos.ru',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Referer': aptek_url,
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Length': '79',
                    'Origin': 'https://aptekamos.ru'} for _ in range(len(med_lst))]
    data = [{"orgId": int(aptek_id), "wuserId": 0, "searchPhrase": med} for med in med_lst]
    urls = ['https://aptekamos.ru/Services/WOrgs/getOrgPrice4?compressOutput=1' for _ in range(len(med_lst))]
    responses = [grequests.post(urls[i], headers=headers[i], json=data[i]) for i in range(len(med_lst))]
    resp_list = []
    for r in grequests.imap(responses):
        if r.status_code == 200:
            resp_list.append(r.json())
        elif r.status_code == 500:
            print('Сервер обнаружил внутреннюю ошибку, которая не позволила ему выполнить этот запрос.')
            resp_list.append(None)
            sys.exit()
        else:
            print(r.status_code)
            print(r.text)
            sys.exit()
    return resp_list


class PriceUpdater(Thread):
    def __init__(self, aptek, begin):
        super().__init__()
        self.aptek = aptek
        self.begin = begin

    def update_prices(self):
        csv_dragid_file_name = r'aptekamos_data/catalog_aptekamos_dragid.csv'
        meds = csv_writer.get_meds_names('aptekamos_data/catalog_aptekamos.csv')
        aptek_id = self.aptek['url'].replace('/ob-apteke', '').split('-')[-1]
        file_name = r'aptekamos_data/aptekamos_' + aptek_id + '.xml'
        date = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.begin:
            xml_writer.createXML(file_name, aptek_id, self.aptek['address'], date)
            create_save_file(r'aptekamos_data/parsed_med_{}'.format(aptek_id))
            csv_writer.create_csv_file(csv_dragid_file_name)
        parsing_meds = [med for med in meds if med not in load_file(r'aptekamos_data/parsed_med_{}'.format(aptek_id))]
        splited_meds = splited_list(parsing_meds, 20)
        for med_lst in splited_meds:
            # print(self.aptek['url'], aptek_id, med_lst)
            resps = api_request(self.aptek['url'], aptek_id, med_lst)
            for i in range(len(resps)):
                if not resps[i]:
                    save_file(r'aptekamos_data/parsed_med_{}'.format(aptek_id), med_lst[i])
                    continue
                if resps[i]['price']:
                    for price_json in resps[i]['price']:
                        drug_id = str(price_json['drugId'])
                        if drug_id not in csv_writer.get_meds_ids(csv_dragid_file_name):
                            if len(resps[i]['price']) == 1:
                                med_name = price_json['medName']
                            else:
                                med_name = price_json['medName'] + f" № {price_json['pack']}"
                                if not price_json['pack']:
                                    med_name = price_json['medName']
                            if not med_name:
                                med_name = price_json['itemName']
                            data_meds = [{'title': med_name, 'id': drug_id}]
                            csv_writer.add_data_in_catalog(csv_dragid_file_name, data_meds)
                        # print(price_json['itemId'])
                        if drug_id == '0':
                            drug_id = str(price_json['itemId'].split('\t')[0])
                            if drug_id not in csv_writer.get_meds_ids(csv_dragid_file_name):
                                if len(resps[i]['price']) == 1:
                                    med_name = price_json['medName']
                                else:
                                    med_name = price_json['medName'] + f" № {price_json['pack']}"
                                    if not price_json['pack']:
                                        med_name = price_json['medName']
                                if not med_name:
                                    med_name = price_json['itemName']
                                data_meds = [{'title': med_name, 'id': drug_id}]
                                csv_writer.add_data_in_catalog(csv_dragid_file_name, data_meds)
                        price = str(price_json['price']).replace('.', ',')
                        if drug_id not in xml_writer.get_meds_id(file_name):
                            xml_writer.add_price(file_name, drug_id, price)
                            print(drug_id, price)
                            print(file_name + ' upd')
                save_file(r'aptekamos_data/parsed_med_{}'.format(aptek_id), med_lst[i])


    def run(self):
        self.update_prices()
        print('[FINISH] ' + str(self.aptek))


if __name__ == '__main__':
    parser = AptekaMosAsyncAPI()
    # parser.update_catalog(begin=True)
    parser.update_prices(begin=True)
