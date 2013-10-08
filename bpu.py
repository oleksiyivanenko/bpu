#!/usr/bin/env python

# BPU (Blog Photos Uploader)

import os
import sys
import json
import requests
from time import gmtime, strftime
from key import ACCESS_TOKEN, USERNAME

class PhotosAPI:
    MP = "http://api-fotki.yandex.ru/api/users/%s/" % USERNAME
    def __init__(self, key):
        self.key = "OAuth " + key

    def getAlbums(self):
        url = self.MP + "albums/"
        rq = requests.get(url, headers={'Accept' : 'application/json'})
        js =  json.loads(rq.text)
        res = {}
        for entry in js['entries']:
            real_id = entry['id'].split(":")[-1]
            res[real_id] = entry['title']
        return res
        

    def createAlbum(self, album_name):
        url = self.MP + "albums/"
        data_dict = {'title': album_name}
        data_js = json.dumps(data_dict)
        rq = requests.post(url, headers={'Authorization' : self.key,
            'Accept' : 'application/json',
            'content-type':'application/json; charset=utf-8; type=entry'}, data=data_js)
        js = json.loads(rq.text)
        real_id = js['id'].split(":")[-1]
        return real_id

    def uploadPhoto(self, album_id, photo):
        url = "%salbum/%s/photos/" % (self.MP, album_id)
        headers = {'Authorization' : self.key,
            'Accept' : 'application/json',
            'content-type':'image/jpeg'}
        rq = requests.post(url, headers=headers, data=photo)
        js = json.loads(rq.text)
        return js['img']['orig']['href']

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