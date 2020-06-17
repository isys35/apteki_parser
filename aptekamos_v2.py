from parsing_base import Parser
from bs4 import BeautifulSoup


class AptekamosParser(Parser):
    SIZE_ASYNC_REQUEST = 100

    def __init__(self):
        super().__init__()
        self.host = 'https://aptekamos.ru'
        self.data_catalog_name = 'aptekamos_data'
        self.apteks = []

    def load_initial_data(self):
        with open(f"{self.data_catalog_name}/initial_data.txt", 'r', encoding='utf8') as file:
            initial_data = file.read()
        apteks_urls = initial_data.split('\n')
        return apteks_urls

    def update_apteks(self):
        self.apteks = []
        apteks_url = self.load_initial_data()
        apteks_resp = self.requests.get(apteks_url)
        count_apteks = len(apteks_url)
        for aptek_resp_index in range(count_apteks):
            soup = BeautifulSoup(apteks_resp[aptek_resp_index], 'lxml')
            header_aptek = soup.select_one('#main-header').select_one('h1').text
            aptek_name = str()
            for name in Apteka.names:
                if name in header_aptek:
                    aptek_name = name
                    break
            aptek_address = soup.select_one('#org-addr').text
            aptek_url = apteks_url[aptek_resp_index]
            self.apteks.append(Apteka(name=aptek_name, url=aptek_url, address=aptek_address, host=self.host))

    def get_med_names(self):
        max_page_in_catalog = self.get_max_page_in_catalog()
        page_urls = [self.host + '/tovary']
        page_urls.extend([f'https://aptekamos.ru/tovary?page={i}' for i in range(2, max_page_in_catalog + 1)])
        splited_page_url = self.split_list(page_urls, self.SIZE_ASYNC_REQUEST)
        meds = []
        for url_list in splited_page_url:
            resps = self.requests.get(url_list)
            for resp in resps:
                soup = BeautifulSoup(resp, 'lxml')
                meds_in_page = soup.select('.ret-med-name')
                for med in meds_in_page:
                    a = med.select_one('a')
                    if a:
                        meds.append(a['title'])

    def get_max_page_in_catalog(self):
        url = self.host + '/tovary'
        resp = self.request.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        pager_text = soup.select_one('#d-table-pager-text').text
        meds = int(pager_text.split(' ')[-1])
        pages = (meds // 100) + 1
        return pages




class Apteka:
    names = ['НЕОФАРМ',
             'ГОРЗДРАВ',
             'Планета Здоровья',
             'ВИТА Экспресс',
             'Самсон-Фарма',
             'Будь Здоров!',
             'Калина Фарм',
             'Живика']

    def __init__(self, name, url, address, host):
        self.name = name
        self.url = url
        self.address = address
        self.host = host
        self.upd_time = None

if __name__ == '__main__':
    parser = AptekamosParser()
    parser.get_med_names()
