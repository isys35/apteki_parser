from parsing_base import Parser
import csv_writer


class ZhivikaParser(Parser):
    MAIN_PAGE = 'https://www.aptekazhivika.ru/'
    QUERY = "query categoryProducts($pageSize: Int!, $currentPage: Int!) {\n  products: productsElastic(pageSize: $pageSize, sort: {is_in_stock:DESC,search_weight:ASC,product_qty:DESC}, currentPage: $currentPage, filter: {category_id: {eq: \"%s\"}}, applyFilter: {}) {\n    total_count\n    page_info {\n      page_size\n      current_page\n    }\n    filters {\n      request_var\n      additional_data\n      name\n      filter_items_count\n      filter_items {\n        items_count\n        value_string\n        label\n      }\n    }\n    apply_filters {\n      attribute_label\n      request_var\n      value_label\n      value_string\n    }\n    items {\n      id\n      sku\n      name\n      rec_need\n      delivery\n      delivery_status\n      thermolabile\n      termolabil_preparat\n      url_key\n      promo_label\n      orig_preparat {\n        label\n      }\n      thumbnail {\n        url\n        label\n      }\n      price {\n        oldPrice {\n            amount {\n              value\n            }\n          }\n        regularPrice {\n          amount {\n            value\n          }\n        }\n      }\n      manufacturer_id {\n        label\n      }\n      is_in_stock\n      is_isg\n      manufactures_url\n      brands_url\n      manufactures_url\n    }\n  }\n}"
    IDS_CATEGORY = [1755, 1756, 1020, 1027, 1033, 1617, 1035, 1036, 1780]
    PAGE_SIZE = 80

    def __init__(self):
        super().__init__()
        self.folder_data = 'zhivika_data'
        self.csv_file = f'{self.folder_data}/catalog_zhivika.csv'

    def update_catalog(self):
        print('[INFO] Обновление каталога...')
        csv_writer.create_csv_file(self.csv_file)
        for id_category in self.IDS_CATEGORY:
            query = self.QUERY % id_category
            current_page = 1
            max_page = None
            meds = []
            while True:
                variables = {"pageSize": self.PAGE_SIZE, "currentPage": current_page}
                json_post_data = {"query": query, "variables": variables}
                resp = self.request.post(self.MAIN_PAGE + 'graphql', json_data=json_post_data)
                resp_json = resp.json()
                for med in resp_json['data']['products']['items']:
                    print(med['id'], med['name'])
                    meds.append({'id': med['id'], 'title': med['name']})
                if not max_page:
                    max_page = 1 + resp_json['data']['products']['total_count']//self.PAGE_SIZE
                current_page += 1
                if current_page > max_page:
                    break
            csv_writer.add_data_in_catalog(self.csv_file, meds)
        print('[INFO] Каталог обновлён.')


if __name__ == '__main__':
    parser = ZhivikaParser()
    parser.update_catalog()
