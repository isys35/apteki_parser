from parsing_base import Parser
import csv_writer
from bs4 import BeautifulSoup


class ZdorovruParser(Parser):
    MAIN_PAGE = 'https://zdorov.ru'

    def __init__(self):
        super().__init__()
        self.name = 'zdorovru'
        self.folder_data = f'{self.name}_data'
        self.csv_file = f'{self.folder_data}/{self.name}_catalog.csv'

    def update_catalog(self):
        print('[INFO] Обновление каталога...')
        csv_writer.create_csv_file(self.csv_file)
        resp = self.request.get(self.MAIN_PAGE)
        soup = BeautifulSoup(resp.text, 'lxml')
        catalog_blocks = soup.select('.catalogUl')
        category_urls = []
        for catalog_block in catalog_blocks:
            a_tags = catalog_block.select('a')
            for a_tag in a_tags:
                category_urls.append(self.MAIN_PAGE + a_tag['href'] + '?size=30')
        for category_url in category_urls:
            max_page = self.get_max_page(category_url)

    def get_max_page(self, url):
        resp = self.request.get(url)



if __name__ == '__main__':
    parser = ZdorovruParser()
    parser.update_catalog()