
def create_save_file(file_name):
    with open(file_name, 'w') as load_file:
        load_file.write('')


def save_file(file_name, url):
    with open(file_name, 'a') as load_file:
        load_file.write(url + '\n')


def save_html_file(name, r):
    with open(f'{name}.html', 'wb') as html_file:
        html_file.write(r.encode('utf-8'))


def load_file(file_name):
    with open(file_name, 'r') as load_file:
        data = load_file.read()
    return data.split('\n')