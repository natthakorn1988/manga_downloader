
from __future__ import with_statement
import glob
import img2pdf
import os
import sys
import urllib.request
from bs4 import BeautifulSoup

class Manga:

    URL_REQUEST_HEADERS = {
        'User-Agent': 'Mozilla'
    }

    def __init__(self, website, comic):
        self.website = website
        self.comic = comic
        self.baseurl = website + '/' + comic

    def read_url_request(self, request_url):
        res_bytes = None
        try:
            req = urllib.request.Request(request_url, headers=self.URL_REQUEST_HEADERS)
            res = urllib.request.urlopen(req)
            res_bytes = res.read()
        except:
            print(sys.exc_info()[0])
        return res_bytes

    def make_dirs(self, dirname):
        if isinstance(dirname, str) and not os.path.exists(dirname):
            os.makedirs(dirname)

    def get_soup_object(self, url):
        soup = None
        res_bytes = self.read_url_request(url)
        if res_bytes != None:
            res_str = str(res_bytes)
            soup = BeautifulSoup(res_str, 'html.parser')
        return soup

    def get_pages_url_from_chapter(self, chapter_url):
        pages = []
        soup = self.get_soup_object(chapter_url)
        if soup == None:
            raise Exception('[ERROR] soup pages cannot be None')
        else:
            for option_tags in soup.find_all('option'):
                option = option_tags.get('value')
                if (option.find(self.comic) > -1):
                    pages.append(self.website + option)
        return pages

    def get_image_url_from_page(self, page_url):
        image_url = None
        soup = self.get_soup_object(page_url)
        for img_src in soup.find_all('img'):
            img = img_src.get('src')
            if (img.find(self.comic[:4]) > -1):
            # if (img.find(self.comic[:6]) > -1):
                image_url = img
                break
        return image_url

    def download_image_from_url(self, image_url, image_name):
        dirname = os.path.dirname(image_name)
        self.make_dirs(dirname)

        image_bytes = self.read_url_request(image_url)
        with open(image_name, 'wb') as im:
            im.write(image_bytes)

    def download_chapters(self, from_chapter, to_chapter):
        for chapter_number in range(from_chapter, to_chapter + 1):
            chapter_url = self.baseurl + '/' + str(chapter_number)
            pages_url = self.get_pages_url_from_chapter(chapter_url)
            for page_number, page_url in enumerate(pages_url):
                # Retrieve image source
                image_url = self.get_image_url_from_page(page_url)
                # Construct image name
                image_folder = self.comic + '_' + str(chapter_number).zfill(3)
                image_ext = os.path.splitext(image_url)[1]
                image_name = str(page_number + 1).zfill(3) + image_ext
                image_path = os.path.join(os.getcwd(), image_folder, image_name)
                # Save image source to local file
                self.download_image_from_url(image_url, image_path)
                print('Downloaded - ' + image_path)

    def chapters2pdf(self, from_chapter, merge=20, image_ext='jpg'):
        to_chapter = from_chapter + merge - 1
        pdf_name = self.comic + '_' + str(from_chapter).zfill(3) + '_' + str(to_chapter).zfill(3) + '.pdf'
        pdf_file = os.path.join(os.getcwd(), pdf_name)

        image_list = []
        for index in range(merge):
            image_folder = self.comic + '_' + str(from_chapter + index).zfill(3)
            image_path = os.path.join(os.getcwd(), image_folder, '*.' + image_ext)
            image_list += glob.glob(image_path)

        pdf_bytes = img2pdf.convert(image_list)
        with open(pdf_file, 'wb') as pdf:
            pdf.write(pdf_bytes)
            print('PDF Completed - ' + pdf_file)

    def __str__(self):
        return self.baseurl

if __name__ == '__main__':

    manga = Manga('http://mangareader.net', 'vinland-saga')
    # from_chapter = 83
    # to_chapter = 100
    # manga.download_chapters(from_chapter, to_chapter)

    from_chapter = 101
    to_chapter = 120
    merge = 20

    for x in range(from_chapter, to_chapter, merge):
       manga.chapters2pdf(x, merge)
