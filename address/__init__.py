# -*- encoding: utf-8 -*-

import logging
import re
from multiprocessing import Pool
import requests
from bs4 import BeautifulSoup

city_url = 'http://www.post.gov.tw/post/internet/Postal/index.jsp?ID=207'
address_url = 'http://www.post.gov.tw/post/internet/Postal/streetNameData.jsp'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/ (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'

requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.WARNING)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class Address():
    def __init__(self):
        # first get the content of the search page
        res = requests.get(city_url, headers={'User-Agent': USER_AGENT})

        # initiate a BeautifulSoup instance with page content
        soup = BeautifulSoup(res.content)

        # all the data we parsed are saved in datas
        self.datas = {}

        cities = self.__get_cities(soup)
        self.__get_cityareas(soup, cities)
        self.__get_all_address()

    def cityarea(self, city_name=None):
        """
            Return all the cityareas of the city you gave.
        """
        # if no city_name given, return every city
        if not city_name:
            return self.datas.keys()

        # if city_name given, return every cityarea of this city
        city = self.datas.get(city_name)
        if city:
            return city.keys()

    def address(self, city_name, cityarea_name):
        """
            Return all the addresses of the city and cityarea you gave.
        """
        # if city_name or cityarea_name are not given,
        # use the result of cityarea()
        if not any([city_name, cityarea_name]):
            return self.cityarea(city_name)

        # if both city_name and cityarea_name are given,
        # return every address of this cityarea
        city = self.datas[city_name]
        if city:
            return city.get(cityarea_name)

    def __get_cities(self, soup):
        # get all the city names within <select> tag,
        select = soup.find('select', attrs={'name': 'city'})

        cities = []

        # start from one because first one is a placeholder text
        for city in select.findAll('option')[1:]:
            # get city name from the <option> tag
            city_text = city.get_text()
            cities.append(city_text)
            logger.debug('city: %s' % (city_text))
        return cities

    def __get_cityareas(self, soup, cities):
        city_counter = 0

        for script in soup.findAll('script'):
            # get the <script> tag content
            content = script.get_text()

            # there are lots of <script> tags,
            # we just want the one contains 'cityarea'
            if 'cityarea' in content:
                is_cityarea = False
                cityareas = {}

                # iterate each line through content
                for line in content.splitlines():
                    # if line contains 'cityarea_account' text,
                    # then next line should be cityarea name
                    if re.search(r'cityarea_account\[\d+\] = \d+;', line):
                        # set is_cityarea to true,
                        # so we can scrape out cityarea name
                        is_cityarea = True

                        # only record cityarea when array is not empty,
                        # also check cityarea always correspond with a city
                        if cityareas and len(cities) > city_counter:
                            # save city and cityarea into a dictionary item
                            city = cities[city_counter]
                            self.datas[city] = {}
                            for cityarea in cityareas:
                                self.datas[city][cityarea] = []

                            # go to next city
                            city_counter += 1

                        # after saving city and cityarea,
                        # clean array to record next city's cityarea
                        cityareas = []

                    # if previous line contains 'cityarea_account',
                    # then this line contains cityarea name we want
                    if is_cityarea:
                        m = re.search(r'cityarea\[\d+\] = \'(.*?)\';', line)
                        if m:
                            cityareas.append(m.group(1))
                            logger.debug('cityarea: %s' % m.group(1))

                break

    def __get_all_address(self):
        # create a process pool that can start task
        pool = Pool(processes=10)

        # record async result of each task,
        # after finish we can get results from them
        results = []

        # iterate through each city and cityarea
        for city in self.datas:
            for cityarea in self.datas[city]:
                # start a task finding addresses of this city and cityarea
                results.append(pool.apply_async(get_address, (city, cityarea)))

        # block until all tasks finished
        pool.close()
        pool.join()

        # iterate each result to get addresses
        for result in results:
            city, cityarea, address = result.get()
            self.datas[city][cityarea] = address


def get_address(city, cityarea):
    """
        Use city and cityarea as post data to get addresses
    """

    logger.debug('process %s %s' % (city, cityarea))
    data = {
        'city': city,
        'cityarea': cityarea
    }

    res = requests.post(
        address_url,
        data=data,
        headers={'User-Agent': USER_AGENT})

    # each address is between <array0> and </array0>
    address = re.findall('<array0>(.*?)</array0>', res.content)

    # convert each address to unicode
    address = [item.decode('utf-8') for item in address]
    return city, cityarea, address
