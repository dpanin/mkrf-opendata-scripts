import configparser
from os import path, makedirs
from queue import Queue
from shutil import copyfileobj
from sys import argv
from threading import Thread
import requests

word = 'живопись'
limit = 1000

links = []


'''word = argv[1]
try:
    limit = argv[2]
except IndexError:
    exit("Error: please, enter image download limit.") '''

config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['google_image_downloader']['CustomSearchAPI_key']
cx_key = config['google_image_downloader']['cx_key']
print (api_key)

def get_data():
    url = 'https://www.googleapis.com/customsearch/v1?key={0}&cx={1}&q={2}&num={3}&searchType=image'.format(api_key, cx_key, word, limit)
    print (url)
    r = requests.get(url)
    jsn = r.json()
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
            print('Processing: ' + title)
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
    data = get_data()
    for i in data:
        queue.put((str(count), i['mime'], i['link']))
        count += 1
    queue.join()
    print('Done')


if __name__ == '__main__':
    main()
