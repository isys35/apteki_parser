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
    host_id: int
    name: str
    url: str
    address: str
    host: str


class Med(NamedTuple):
    name: str
    url: str


class Price(NamedTuple):
    apteka: Apteka
    med: Med
    rub: float