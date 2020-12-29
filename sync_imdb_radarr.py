#!/usr/bin/env python3

import os
import sys
from os.path import dirname
sys.path.insert(1,dirname(__file__) + '/lib')

import pprint
import requests
import json

print("Starting PP Script")

radarr_host = '192.168.1.101'
radarr_port = "7878"
radarr_webroot = 'radarr'
radarr_ssl = 0
radarr_key = "38b9097ad5ba47de9f6e5b62b121486a"

if radarr_ssl == 1:
    proto = 'https'
else:
    proto = 'http'

radarr_url = proto + "://" + radarr_host + ":" + radarr_port + "/" + radarr_webroot
print("Radarr URL: %s" % radarr_url)

url = "https://radarrapi.servarr.com/v1/list/imdb/ls008298371"
response = json.loads(requests.get(url).text)

radarrSession = requests.Session()
radarrSession.trust_env = False
radarrMovies = radarrSession.get('{0}/api/movie?apikey={1}'.format(radarr_url, radarr_key))
if radarrMovies.status_code != 200:
    print('Radarr server error - response %s' % radarrMovies.status_code)

for movie in radarrMovies.json():
    radarr_id = None
    radarr_title = None
    #print("Processing Movie %s(%s)" % (movie['title'], movie['imdbId']))
    for imdbMovie in response:
        if imdbMovie["ImdbId"] == movie['imdbId']:
            #print('Got a match: %s[%s]' % (movie['title'],movie['id']))
            radarr_id = movie['id']
            radarr_title = movie['title']
            break
    if radarr_id is None:
        deleteSession = requests.Session()
        deleteSession.trust_env = False
        deleteMovies = deleteSession.delete('{0}/api/movie/{1}?apikey={2}&addExclusion=false&deleteFiles=false'.format(radarr_url, movie['id'], radarr_key))
        if deleteMovies.status_code != 200:
            print('Radarr delete server error - response %s' % deleteMovies.status_code)
            exit(1)
        print("Successfully deleted %s" % movie['title'] )
        
