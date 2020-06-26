import db
import csv_writer


def create_full_catalog_csv():
    data = db.get_data_meds()
    csv_writer.create_csv_file('Полный каталог.csv')
    csv_writer.add_data_in_catalog('Полный каталог.csv', data)



if __name__ == '__main__':
    db.get_data_meds('https://gorzdrav.org')