import sqlite3

DB_NAME = 'apteki.db'


def create_db():
    file = open(DB_NAME, 'wb')
    file.close()


# noinspection SqlNoDataSourceInspection
def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE apteka 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
        url TEXT UNIQUE, 
        name TEXT,
        address TEXT,
        host TEXT,
        upd_data INTEGER,
        host_id INTEGER)""")
    cursor.execute("""CREATE TABLE med 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT)""")
    cursor.execute("""CREATE TABLE price 
            ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 
            'rub' TEXT,
            'upd_time' INTEGER,
            'med_id' INTEGER NOT NULL,
            'aptek_id' INTEGER NOT NULL,
            FOREIGN KEY ('med_id') REFERENCES 'med'('id'),
            FOREIGN KEY ('aptek_id') REFERENCES 'apteka'('id'))""")


def add_price(price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    apteka_url = price.apteka.url
    query = f"""SELECT id FROM apteka WHERE url={apteka_url}"""
    cursor.execute(query)
    cursor.close()
    conn.close()
    data_aptek = cursor.fetchall()
    if not data_aptek:
        print(add_apteka(price.apteka))


def add_apteka(apteka):
    """Добавляем аптеку в базу и возращаем её id """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = f"""INSERT INTO apteka (url, name, address, host, host_id) 
                VALUES ({apteka.url},{apteka.name},{apteka.address},{apteka.host},{apteka.host_id})"""
    cursor.execute(query)
    conn.commit()
    query = f"""SELECT id FROM apteka WHERE url={apteka.url}"""
    cursor.execute(query)
    return cursor.fetchone()
