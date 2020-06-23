from parsing_base import Parser
from bs4 import BeautifulSoup
import apteka
import json
import time
import db


class AptekamosParser(Parser):
    SIZE_ASYNC_REQUEST = 100

    def __init__(self):
        super().__init__()
        self.host = 'https://aptekamos.ru'
        self.data_catalog_name = 'aptekamos_data'
        self.apteks = []
        self.meds = []
        self.prices = []

    def load_initial_data(self):
        with open(f"{self.data_catalog_name}/initial_data.txt", 'r', encoding='utf8') as file:
            initial_data = file.read()
        apteks_urls = initial_data.split('\n')
        return apteks_urls

    def update_apteks(self):
        print('UPDATE APTEKS')
        self.apteks = []
        apteks_url = self.load_initial_data()
        apteks_resp = self.requests.get(apteks_url)
        count_apteks = len(apteks_url)
        for aptek_resp_index in range(count_apteks):
            soup = BeautifulSoup(apteks_resp[aptek_resp_index], 'lxml')
            print(apteks_url[aptek_resp_index])
            header_aptek = soup.select_one('#main-header').select_one('h1').text
            aptek_name = str()
            for name in Apteka.names:
                if name in header_aptek:
                    aptek_name = name
                    break
            aptek_address = soup.select_one('#org-addr').text
            aptek_url = apteks_url[aptek_resp_index]
            aptek_id = aptek_url.replace('/ob-apteke', '').split('-')[-1]
            self.apteks.append(apteka.Apteka(name=aptek_name,
                                             url=aptek_url,
                                             address=aptek_address,
                                             host=self.host,
                                             host_id=int(aptek_id)))

    def update_meds(self):
        print('UPDATE MEDS')
        max_page_in_catalog = self.get_max_page_in_catalog()
        print(f"{max_page_in_catalog} максимальное кол-во страниц в каталоге")
        page_urls = [self.host + '/tovary']
        page_urls.extend([f'https://aptekamos.ru/tovary?page={i}' for i in range(2, max_page_in_catalog + 1)])
        for url in page_urls:
            print(url)
            response = self.request.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            meds_in_page = soup.select('.ret-med-name')
            for med in meds_in_page:
                a = med.select_one('a')
                if a:
                    name = a['title'].replace('цена', '').strip()
                    self.meds.append(apteka.Med(name=name,
                                                url=a['href']))

    def get_max_page_in_catalog(self):
        url = self.host + '/tovary'
        resp = self.request.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        pager_text = soup.select_one('#d-table-pager-text').text
        meds = int(pager_text.split(' ')[-1])
        pages = (meds // 100) + 1
        return pages

    def update_prices(self):
        if not self.apteks:
            self.update_apteks()
        if not self.meds:
            self.update_meds()
        print('UPDATE PRICES')
        self.prices = []
        post_url = self.host + '/Services/WOrgs/getOrgPrice4?compressOutput=1'
        for aptek in self.apteks:
            for med in self.meds:
                print(aptek.name, med.name)
                post_data = {"orgId": int(aptek.host_id), "wuserId": 0, "searchPhrase": med.name}
                response = self.request.post(url=post_url, json_data=post_data)
                download_meds = self.pars_med(response.text)
                for med_data in download_meds:
                    med = apteka.Med(name=med_data['title'],
                                     url=med.url)
                    med.host_id = med_data['id']
                    price = apteka.Price(med=med,
                                         apteka=aptek,
                                         rub=float(med_data['price']))
                    print(price.rub)
                    self.prices.append(price)
                    db.add_price(price)


    def pars_med(self, response_txt):
        print(response_txt)
        resp_json = json.loads(response_txt)
        data_meds = []
        for price_json in resp_json['price']:
            drug_id = str(price_json['drugId'])
            if drug_id == '0':
                drug_id = str(price_json['itemId'].split('\t')[0])
            if len(resp_json['price']) == 1:
                med_name = price_json['medName']
            else:
                med_name = price_json['medName'] + f" № {price_json['pack']}"
                if not price_json['pack']:
                    med_name = price_json['medName']
            if not med_name:
                med_name = price_json['itemName']
            price = str(price_json['price']).replace('.', ',')
            data_meds.append({'title': med_name, 'id': drug_id, 'price': price})
        return data_meds


if __name__ == '__main__':
    parser = AptekamosParser()
    parser = parser.load_object('aptekamos_parser')
    try:
        parser.update_prices()
    except Exception as ex:
        print(ex)
        parser.save_object(parser, 'aptekamos_parser')
