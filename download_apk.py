import urllib
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
from settings import APK_FOLDER

def get_download_links():
    link_list = []
    next_available = True
    page = 1
    while next_available:
        try:
            url = "https://cubapk.com/store/?page={}".format(page)
            text = urlopen(url).read()
            soup = BeautifulSoup(text, features="lxml")
            page += 1
        except urllib.error.HTTPError:
            break

        data = soup.findAll('div',attrs={'class':'app-meta'})
        for div in data:
            links = div.findAll('a')
            for a in links:
                link_list.append("https://cubapk.com" + a['href'])
    return link_list

def download_apk(link):
    apath = os.path.join(APK_FOLDER, link.split('/')[-3]+'.apk')
    urllib.request.urlretrieve(link, apath )

if __name__ == '__main__':
    link_list = get_download_links()
    print('Found {}\n\n'.format(len(link_list)))
    for link in link_list:
        print("Downloading {}".format(link))
        download_apk(link)
    print('Download Complete')

