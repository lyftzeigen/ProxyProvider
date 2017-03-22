import random
import time
import requests
import threading
from bs4 import BeautifulSoup as bs


class ProxyWorker(threading.Thread):
    def __init__(self, method, tasks, proxy):
        threading.Thread.__init__(self)
        self.tasks = tasks
        self.method = method
        self.proxy = proxy

    def run(self):
        while len(self.tasks) > 0:
            task = self.tasks.pop()
            try:
                self.method((task, self.proxy))
            except:
                self.tasks.append(task)
                self.proxy.rating += 1
                time.sleep(1)
            finally:
                if self.proxy.rating >= 3:
                    # print('> Terminate proxy %s' % self.proxy.address)
                    break


class RatedProxy:
    def __init__(self, address):
        self.rating = 0
        self.address = address


class ProxyProvider:
    def __init__(self):
        self.proxy_list = []
        self.proxy_workers = []
        self.tasks = []

        print('> Запрос прокси серверов')

        # Запрос количества страниц
        query = 'https://hidemy.name/ru/proxy-list/?maxtime=1500&type=hs#list'
        req = requests.get(query, headers={'User-Agent': 'Chrome/43.0.2357.134'})
        page = bs(req.content, 'lxml')
        pagination = page.find('div', {'class': 'proxy__pagination'})
        last_page = pagination.findAll('li')[-1:][0]
        last_page_number = int(last_page.find('a').text)

        print('> Страниц найдено: %s' % last_page_number)

        for i in range(0, 64 * last_page_number, 64):
            # Запрос списка серверов
            query = 'https://hidemy.name/ru/proxy-list/?maxtime=1500&type=hs&start=%s#list' % str(i)
            req = requests.get(query, headers={'User-Agent': 'Chrome/43.0.2357.134'})
            page = bs(req.content, 'lxml')
            proxy_table = page.find('table', {'class': 'proxy__t'})
            proxy_table_body = proxy_table.find('tbody')
            proxy_table_rows = proxy_table_body.findAll('tr')
            for row in proxy_table_rows:
                ip = row.find('td')
                port = ip.findNext('td')
                ip = ip.text
                port = port.text
                proxy = 'http://%s:%s' % (ip, port)
                self.proxy_list.append(RatedProxy(proxy))

        random.shuffle(self.proxy_list)
        print('> Получены прокси сервера: %s' % len(self.proxy_list))

    def add_proxy_workers(self, method):
        for address in self.proxy_list:
            worker = ProxyWorker(method, self.tasks, address)
            self.proxy_workers.append(worker)

    def start_all_workers(self):
        print('> Запускаем все потоки')
        for worker in self.proxy_workers:
            if len(self.tasks) > 0:
                worker.start()
                # Плавный старт
                time.sleep(0.5)

    def add_task(self, task):
        self.tasks.append(task)

    def join_all(self):
        for worker in self.proxy_workers:
            if worker.isAlive():
                worker.join()

    def delete_all_workers(self):
        del self.proxy_workers[:]
