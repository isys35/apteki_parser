from typing import NamedTuple
NAMES = ['НЕОФАРМ',
        'ГОРЗДРАВ',
             'Планета Здоровья',
             'ВИТА Экспресс',
             'Самсон-Фарма',
             'Будь Здоров!',
             'Калина Фарм',
             'Живика']

class Apteka(NamedTuple):


    def __init__(self, name, url, address, host, host_id):
        self.host_id = int(host_id)
        self.name = name
        self.url = url
        self.address = address
        self.host = host
        self.upd_time = None

    def refresh_upd_time(self):
        self.upd_time = time.time()


class Med:
    def __init__(self, name, url):
        self.host_id = None
        self.name = name
        self.url = url


class Price:
    def __init__(self, med, apteka, rub):
        self.apteka = apteka
        self.med = med
        self.rub = rub
        self.upd_time = None
        self.refresh_upd_time()

    def refresh_upd_time(self):
        self.upd_time = time.time()