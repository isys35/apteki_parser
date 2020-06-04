import csv


def add_data_in_catalog(file_name, data):
    meds_ids = get_meds_ids(file_name)
    with open(file_name, "a", newline="") as file:
        data = [[el['id'], el['title']] for el in data if el['id'] not in meds_ids]
        writer = csv.writer(file, delimiter = ';')
        writer.writerows(data)


def get_meds_names(file_name):
    with open(file_name, "r", encoding='cp1251') as f_obj:
        return [row[1] for row in csv.reader(f_obj, delimiter=';')]


def get_meds_ids(file_name):
    with open(file_name, "r", encoding='cp1251') as f_obj:
        return [row[0] for row in csv.reader(f_obj, delimiter=';')]


def create_csv_file(file_name):
    with open(file_name, "w", newline="") as file:
        csv.writer(file)