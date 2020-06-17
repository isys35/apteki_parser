from parsing_base import Parser
from bs4 import BeautifulSoup


class AptekamosParser(Parser):
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
        apteks_url = self.load_initial_data()
        apteks_resp = self.requests.get(apteks_url)
        for aptek_resp in apteks_resp:
            soup = BeautifulSoup(aptek_resp, 'lxml')
            header_aptek = soup.select_one('#main-header').select_one('h1').text
            aptek_name = str()
            for name in Apteka.names:
                if name in header_aptek:
                    aptek_name = name
                    break

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
    parser.update_apteks()
