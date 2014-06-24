import json
import codecs
import sqlite3
from os.path import isfile
from os import remove
from address import Address


def main():
    save_json()
    save_sqlite()


def save_json():
    a = Address()
    with codecs.open('data/address.json', 'w', 'utf-8') as f:
        # save address datas in json format,
        # set ensure_ascii to False to write utf-8 character correctly
        f.write(json.dumps(a.datas, ensure_ascii=False, indent=4))


def save_sqlite():
    a = Address()

    filename = 'data/address.db'
    # remove exist database file
    if isfile(filename):
        remove(filename)

    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE address (_id INTEGER PRIMARY KEY AUTOINCREMENT, city TEXT, cityarea TEXT, address TEXT)')
    counter = 0
    for city in a.datas:
        for cityarea in a.datas[city]:
            for address in a.datas[city][cityarea]:
                row = (counter, city, cityarea, address)
                cursor.execute('INSERT INTO address VALUES (?,?,?,?)', row)
                counter += 1
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
