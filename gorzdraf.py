from parsing_base import Parser
from bs4 import BeautifulSoup
import csv_writer


class GorZdrafParser(Parser):
    MAIN_PAGE = 'https://gorzdrav.org'

    def __init__(self):
        super().__init__()
        self.folder_data = 'gorzdraf_data'
        self.csv_catalog = f'{self.folder_data}/catalog_gorzdraf.csv'

    def update_catalog(self):
        print('[INFO] Обновление каталога...')
        csv_writer.create_csv_file(self.csv_catalog)
        resp = self.request.get(self.MAIN_PAGE)
        soup = BeautifulSoup(resp.text, 'lxml')
        url_categories = [self.MAIN_PAGE + item.select_one('a')['href'] for item in soup.select('.c-catalog-body__item')]
        max_pages = self.get_max_pages(url_categories)
        count_categories = len(url_categories)
        url_categories_with_pages = []
        for category_index in range(count_categories):
            category_with_page = [url_categories[category_index]]
            for page in range(1, max_pages[category_index]+1):
                url_page = url_categories[category_index] + f'?q=%3AavailableInStoresOrStock%3Atrue&page={page}'
                category_with_page.append(url_page)
            url_categories_with_pages.append(category_with_page)
        for category_with_page in url_categories_with_pages:
            meds = self.get_meds(category_with_page)
            csv_writer.add_data_in_catalog(self.csv_catalog, meds)
        print('[INFO] Обновление каталога завершено')

    def update_prices(self):
        print('[INFO] Обновление цен...')
        apteks = self.get_apteks()

    def get_apteks(self):
        print('[INFO] Получение аптек...')
        resp = self.request.get(self.MAIN_PAGE + '/apteki/list/')
        max_page = self.get_max_page(resp.text)
        urls = [self.MAIN_PAGE + '/apteki/list/']
        extend_list = [self.MAIN_PAGE + f'/apteki/list/?page={page}' for page in range(1, max_page)]
        urls.extend(extend_list)
        print(urls)

    def get_max_page(self, resp_text):
        soup = BeautifulSoup(resp_text, 'lxml')
        return int(soup.select('.b-pagination__item')[-2].text)

    def get_meds(self, urls):
        resps = self.requests.get(urls)
        meds = []
        for resp in resps:
            soup = BeautifulSoup(resp, 'lxml')
            product_blocks = soup.select('.c-prod-item.c-prod-item--grid')
            for product_block in product_blocks:
                index = product_block.select_one('a')['data-gtm-id']
                title = product_block.select_one('a')['data-gtm-name']
                med = {'id': index, 'title': title}
                meds.append(med)
        return meds

    def get_max_pages(self, urls):
        resps = self.requests.get(urls)
        max_pages = []
        for resp in resps:
            max_pages.append(self.get_max_page(resp))
        return max_pages


if __name__ == '__main__':
    parser = GorZdrafParser()
    parser.update_prices()





