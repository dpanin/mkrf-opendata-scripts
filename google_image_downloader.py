import configparser
from math import ceil
from os import path, makedirs
from queue import Queue
from shutil import copyfileobj
from sys import argv
from threading import Thread
import requests


links = []
word = argv[1]
try:
    limit = int(argv[2])/10
    limit = ceil(limit)
except IndexError:
    exit('Ошибка: не указан лимит изображений.')

config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['google_image_downloader']['CustomSearchAPI_key']
cx_key = config['google_image_downloader']['cx_key']


def get_data(offset):
    url = 'https://www.googleapis.com/customsearch/v1?key={0}&cx={1}&q={2}&searchType=image&start={3}'.format(api_key, cx_key, word, offset)
    r = requests.get(url)
    jsn = r.json()
    if r.status_code == 400:
        exit('Response 400: проверьте правильность введенных ключей.')
    else:
        return jsn['items']


def download(title, mime, link):
    response = requests.get(link, stream=True)
    if response.status_code == 200:
        if mime == 'image/png':
            filename = 'img/' + title + '.png'
        else:
            filename = 'img/' + title + '.jpg'
        with open(filename, 'wb') as out_file:
            response.raw.decode_content = True
            copyfileobj(response.raw, out_file)


class DownloadWorker(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            title, mime, link = self.queue.get()
            print('Обрабатываю изображение: ' + title)
            download(title, mime, link)
            self.queue.task_done()


def main():
    count = 1
    if not path.exists('img'):
        makedirs('img')
    queue = Queue()
    for _ in range(8):
        worker = DownloadWorker(queue)
        worker.daemon = True
        worker.start()
    print('Получаю список изображений...')
    data = [get_data(i*10+1) for i in range(limit)]
    for items in data:
        for i in items:
            queue.put((str(count), i['mime'], i['link']))
            count += 1
    queue.join()
    print('Выполнено')


if __name__ == '__main__':
    main()
