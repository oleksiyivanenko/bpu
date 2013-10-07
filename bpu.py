#!/usr/bin/env python

# BPU (Blog Photos Uploader)

import os
import sys
import xml.etree.ElementTree as et
import requests
from time import gmtime, strftime
from key import ACCESS_TOKEN, USERNAME

class PhotosAPI:
    MP = "http://api-fotki.yandex.ru/api/users/%s/" % USERNAME
    SPEC = "{http://www.w3.org/2005/Atom}"
    def __init__(self, key):
        self.key = "OAuth " + key

    def getAlbums(self):
        url = self.MP + "albums/"
        rq = requests.get(url)
        res = {}
        xml = et.fromstring(rq.text.encode('utf-8'))
        for line in xml.findall(self.SPEC + 'entry'):
            id_string = line.find(self.SPEC + 'id').text
            real_id = id_string.split(":")[-1]
            res[real_id] = line.find(self.SPEC + 'title').text
        return res
        

    def createAlbum(self, album_name):
        url = self.MP + "albums/"
        data = """<entry xmlns="http://www.w3.org/2005/Atom" xmlns:f="yandex:fotki">
        <title>%s</title>
        </entry>""" % album_name
        rq = requests.post(url, headers={'Authorization' : self.key,
            'content-type':'application/atom+xml; charset=utf-8; type=entry'}, data=data)
        xml = et.fromstring(rq.text.encode('utf-8'))
        id_string = xml.find(self.SPEC + 'id').text
        real_id = id_string.split(":")[-1]
        return real_id

    def uploadPhoto(self, album_id, photo):
        url = "%salbum/%s/photos/" % (self.MP, album_id)
        headers = {'Authorization' : self.key,
            'content-type':'image/jpeg'}
        rq = requests.post(url, headers=headers, data=photo)
        xml = et.fromstring(rq.text.encode('utf-8'))
        content_element = xml.find(self.SPEC + 'content')
        link = content_element.get('src')
        return link

def uploadPhotos(path):
    dir_name = os.path.abspath(path).split("/")[-1]
    api = PhotosAPI(ACCESS_TOKEN)
    album_id = api.createAlbum(dir_name)
    print "Album %s created. Id %s" % (dir_name, album_id)
    filename = "%s_%s.md" % (strftime("%Y-%m-%d", gmtime()),dir_name)
    md_file = open(filename, 'a')
    for files in os.listdir(path):
        if files.endswith(".jpg"):
            f = open(os.path.join(path, files), "rb")
            ima = f.read()
            f.close()
            link = api.uploadPhoto(album_id,ima)
            print "Photo %s \t [Done]" % files
            md_file.write("![%s](%s)\n" % (files, link))
    md_file.close()
    print "%s created." % filename

if __name__ == "__main__":
    uploadPhotos(sys.argv[1])