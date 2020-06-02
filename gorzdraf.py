from parsing_base import Parser
from bs4 import BeautifulSoup


class GorZdrafParser(Parser):
    MAIN_PAGE = 'https://gorzdrav.org'

    def __init__(self):
        super().__init__()
        self.folder_data = 'gorzdraf_data'
        self.csv_catalog = f'{self.folder_data}/catalog_gorzdraf.csv'

    def update_catalog(self):
        resp = self.request.get(self.MAIN_PAGE)
        soup = BeautifulSoup(resp.text, 'lxml')
        soup.select('.c-catalog-body__item')


if __name__ == '__main__':
    parser = GorZdrafParser()
    parser.update_catalog()




