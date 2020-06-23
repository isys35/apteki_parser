import sqlite3
import time

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
            'rub' REAL,
            'upd_time' INTEGER,
            'med_id' INTEGER NOT NULL,
            'aptek_id' INTEGER NOT NULL,
            FOREIGN KEY ('med_id') REFERENCES 'med'('id'),
            FOREIGN KEY ('aptek_id') REFERENCES 'apteka'('id'))""")


def get_aptek_id(price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    apteka_url = price.apteka.url
    query = f"""SELECT id FROM apteka WHERE url='{apteka_url}'"""
    cursor.execute(query)
    data_aptek = cursor.fetchone()
    if not data_aptek:
        aptek_id = add_apteka(price.apteka)
    else:
        aptek_id = data_aptek[0]
    cursor.close()
    conn.close()
    return aptek_id


def get_med_id(price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    med_name = price.med.name
    query = f"""SELECT id FROM med WHERE name='{med_name}'"""
    cursor.execute(query)
    data_meds = cursor.fetchone()
    if not data_meds:
        med_id = add_med(price.med)
    else:
        med_id = data_meds[0]
    cursor.close()
    conn.close()
    return med_id


def add_price(price):
    aptek_id = get_aptek_id(price)
    med_id = get_med_id(price)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = f"""SELECT id from price WHERE aptek_id={aptek_id} AND med_id={med_id}"""
    cursor.execute(query)
    data_price = cursor.fetchone()
    if not data_price:
        upd_data = [price.rub, aptek_id, med_id, int(time.time())]
        cursor.execute(f"""INSERT INTO price (rub, aptek_id, med_id, upd_time)
                            VALUES (?, ?, ?, ?)""", upd_data)
    else:
        upd_data = [price.rub, int(time.time()), aptek_id, med_id]
        query = f"""UPDATE price
                    SET rub=?, upd_time=?
                    WHERE aptek_id=? AND med_id=?"""
        cursor.execute(query, upd_data)
    conn.commit()
    cursor.close()
    conn.close()


def add_apteka(apteka):
    """Добавляем аптеку в базу и возращаем её id """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data = [apteka.url, apteka.name, apteka.address, apteka.host, int(apteka.host_id)]
    query = f"""INSERT INTO apteka (url, name, address, host, host_id) 
                VALUES (?,?,?,?,?)"""
    cursor.execute(query, data)
    conn.commit()
    query = f"""SELECT id FROM apteka WHERE url='{apteka.url}'"""
    cursor.execute(query)
    id = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return id


def add_med(med):
    """Добавляем лекарство в базу и возращаем её id """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = f"""INSERT INTO med (name) 
                VALUES ('{med.name}')"""
    cursor.execute(query)
    conn.commit()
    query = f"""SELECT id FROM med WHERE name='{med.name}'"""
    cursor.execute(query)
    id = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return id


if __name__ == '__main__':
    create_db()
    create_tables()
