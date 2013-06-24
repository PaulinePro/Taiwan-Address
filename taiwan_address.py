#!/usr/bin/python
# -*- coding:utf-8 -*-

import urllib2
import re
import codecs
import threading
import commands
import sqlite3


# Request headers
user_agent = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36'

# URL
city_url = 'http://www.post.gov.tw/post/internet/f_searchzone/index.jsp'
cityarea_url = 'http://www.post.gov.tw/post/internet/_city_v2.js'
address_url = 'http://www.post.gov.tw/post/internet/f_searchzone/streetNameData.jsp?city={0}&cityarea={1}'

# Global variables
thread_amounts = 0
max_thread = 15


class Address:
    def __init__(self):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', user_agent)]
        urllib2.install_opener(opener)
        self.city = []
        self.city_area = []
        self.counter = 0

    def __decodebig5(self, input):
        return input.decode('big5').encode('utf-8')

    def __get_city(self):
        self.city = []
        is_in_city = False
        ufile = urllib2.urlopen(city_url)
        for line in ufile:
            if not is_in_city:
                is_in_city = re.search('<select name=\"city\" ID=\"city\" onChange', line)
            else:
                if re.search('</select>', line):
                    break
                else:
                    city = re.search('<option value=\"(.*?)\" >', line)
                    if city:
                        self.city.append(self.__decodebig5(city.group(1)))

    def __get_cityarea(self):
        self.city_area = []
        data = []
        ufile = urllib2.urlopen(cityarea_url)
        for line in ufile:
            catch = re.search('cityarea_account\[\d+\] = \d+;', line)
            if catch:
                if data:
                    self.city_area.append(data)
                    data = []
            else:
                city_area = re.search('cityarea\[\d+\] = \'(.*?)\'', line)
                if city_area:
                    data.append(self.__decodebig5(city_area.group(1)))

    def __get_address(self):
        self.thread_pool = []
        for (counter, city) in enumerate(self.city):
            thread = AddressThread(city, self.city_area[counter])
            self.thread_pool.append(thread)
        global thread_amounts
        thread_counter = 0
        while True:
            if thread_counter >= len(self.city):
                break
            else:
                if thread_amounts < max_thread:
                    self.thread_pool[thread_counter].start()
                    thread_counter += 1
                    thread_amounts += 1
        for thread in self.thread_pool:
            thread.join()

    def __write_address(self):
        commands.getstatusoutput('rm taiwan_address.csv')
        with codecs.open('taiwan_address.csv', 'a') as f:
            f.write('counter,city,cityarea,address\n')
        for thread in self.thread_pool:
            for result in thread.results:
                result = (self.counter, result['city'],
                          result['city_area'], result['address'])
                with codecs.open('taiwan_address.csv', 'a') as f:
                    f.write('{0},{1},{2},{3}\n'.format(*result))
                self.counter += 1

    def __insert_database(self):
        commands.getstatusoutput('rm taiwan_address.db')
        conn = sqlite3.connect('taiwan_address.db')
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE address (_id INTEGER PRIMARY KEY AUTOINCREMENT, city TEXT, cityarea TEXT, address TEXT)')
        for thread in self.thread_pool:
            for result in thread.results:
                row = (self.counter,result['city'],
                       result['city_area'], result['address'], )
                self.counter += 1
                cursor.execute('INSERT INTO address VALUES (?,?,?,?)', row)
        conn.commit()
        conn.close()

    def save_address(self):
        self.__get_city()
        self.__get_cityarea()
        self.__get_address()
        self.__write_address()
        self.__insert_database()


class AddressThread(threading.Thread):
    def __init__(self, city, cityareas):
        threading.Thread.__init__(self)
        self.city = city
        self.cityareas = cityareas
        self.results = []

    def run(self):
        print 'Processing', self.city
        for city_area in self.cityareas:
            url = address_url.format(self.city, city_area)
            content = urllib2.urlopen(url).read()
            list_address = re.findall('<array0>(.*?)</array0>', content)
            for address in list_address:
                self.results.append({'city': self.city, 'city_area': city_area, 'address': address})
        global thread_amounts
        thread_amounts -= 1


def main():
    address = Address()
    address.save_address()

if __name__ == '__main__':
    main()
