#!/usr/bin/python3
#
##############################################################################
### NZBGET QUEUE SCRIPT                                          ###

# Checck if a movie exists on one of the Streaming sites
#
# NOTE: This script requires Python to be installed on your system.
##############################################################################
### OPTIONS                                                                ###

## TMDB
#tmdbapikey=

# Pushbullet API URL.
#URL=https://api.pushbullet.com/api/pushes

# Find your Access Token at <a href="https://www.pushbullet.com/account">https://www.pushbullet.com/account</a>
#AccessToken=


### NZBGET QUEUE SCRIPT                                          ###
##############################################################################

import os
import sys
from os.path import dirname
sys.path.insert(1,dirname(__file__) + '/lib')

if os.environ.get('NZBNA_EVENT') not in ['NZB_ADDED']:
        sys.exit(0)

import pprint
import guessit
import guessit.patterns.extension
import requests
import json
from tmdb_api import tmdb

from justwatch import JustWatch

#from dotenv import load_dotenv
#load_dotenv(os.path.join('/opt/htpc-config/nzbget/scripts/nzbget.env'))
#env_var = os.environ
#print("User's Environment variable:")
#pprint.pprint(dict(env_var), width = 1)

import urllib
try:
        from xmlrpclib import ServerProxy # python 2
except ImportError:
        from xmlrpc.client import ServerProxy # python 3

print("Starting SearchProviders PP Script")

def tmdbInfo(guessData):
    tmdb.configure(tmdb_api_key)
    #print("Title from guess: %s" % guessData["title"])
    movies = tmdb.Movies(guessData["title"].encode('ascii', errors='ignore'), limit=4)
    #print(movies.get_total_results())
    for movie in movies.iter_results():
        # Identify the first movie in the collection that matches exactly the movie title
        foundname = ''.join(e for e in movie["title"] if e.isalnum())
        origname = ''.join(e for e in guessData["title"] if e.isalnum())
        # origname = origname.replace('&', 'and')
        #print("Info: %s - %s\n" % (foundname, origname))
        if foundname.lower() == origname.lower():
            tmdb_title = ''
            tmdbid = 0
            print("Matched movie title as: %s %s" % (movie["title"], movie["release_date"]))
            movie = tmdb.Movie(movie["id"])
            if isinstance(movie, dict):
                tmdbid = movie["id"]
                tmdb_title = movie["title"]
            else:
                tmdbid = movie.get_id()
                tmdb_title = movie.get_title()
            return tmdbid, tmdb_title
    return None

tmdb_api_key = "45e408d2851e968e6e4d0353ce621c66"
# Check if all required script config options are present in config file
required_options = ('NZBPO_TMDBAPIKEY', 'NZBPO_ACCESSTOKEN', 'NZBPO_URL')
status = 0

if os.environ['NZBNA_CATEGORY'] != 'Movies':
    print("This is only valid for Movies.")
    status = 1

for optname in required_options:
    if (not optname.upper() in os.environ):
        print('[ERROR] Option %s is missing in configuration file. Please check script settings' % optname[6:])
        sys.exit(POSTPROCESS_ERROR)

if status == 1:
    sys.exit(NZBGET_POSTPROCESS_NONE)

nzb_tmdbid = 0
nzb_tmdbtitle = ''

#os.environ['NZBPP_NZBFILENAME'] = "Captain.Marvel.2019.720p.BluRay.x264.IMAX-WHALES.nzb"
guess = guessit.guess_movie_info(os.environ['NZBNA_FILENAME'])
print(guess.nice_string())
try:
    if guess['type'] == 'movie':
        nzb_tmdbid, nzb_tmdbtitle = tmdbInfo(guess)
        print("TMDB id from NZB: %s" % nzb_tmdbid)
except Exception as e:
    print("Could not find a TMDB match")
    sys.exit(NZBGET_POSTPROCESS_NONE)

just_watch = JustWatch(country='US')
movies = just_watch.search_for_item(query=nzb_tmdbtitle)
jw_tmdbid = 0
jw_provider = None

for movie in movies['items']:
    for score in movie.get('scoring'):
        if score.get('provider_type') == 'tmdb:id' and score.get('value') == nzb_tmdbid:
            print("Match Found on JustWatch")
            #print(movie.get('offers'))
            jw_tmdbid = score.get('value')
            if movie.get('offers') != None:
                for provider in movie.get('offers'):
                    #print(json.dumps(provider, indent=4, sort_keys=True))
                    if provider.get('provider_id') == 8:
                        jw_provider = "Netflix"
                        #print("ProviderID: %s | Provider: %s | URL: %s" % (provider.get('provider_id'), jw_provider, provider.get('urls')['standard_web']))
                        break
                    elif provider.get('provider_id') == 9:
                        jw_provider = "Amazon Prime"
                        #print("ProviderID: %s | Provider: %s | URL: %s" % (provider.get('provider_id'), jw_provider, provider.get('urls')['standard_web']))
                        break
                    elif provider.get('provider_id') == 337:
                        jw_provider = "Disney Plus"
                        #print("ProviderID: %s | Provider: %s | URL: %s" % (provider.get('provider_id'), jw_provider, provider.get('urls')['standard_web']))
                        break
                if jw_provider == None:
                    print("Could not determine Streaming Services")
                    sys.exit(NZBGET_POSTPROCESS_NONE)
if jw_tmdbid == 0:
    print("Could not find a match")
    sys.exit(NZBGET_POSTPROCESS_NONE)

print("Movie Title: %s | TMDB_ID: %s | Provider: %s" % (nzb_tmdbtitle, jw_tmdbid, jw_provider))
text = "Movie Title: " + nzb_tmdbtitle + " | TMDB_ID: " + str(jw_tmdbid) + " | Provider: " + jw_provider

print('[DETAIL] Sending to Pushbullet')
sys.stdout.flush()
#os.environ['NZBPO_URL']="https://api.pushbullet.com/api/pushes"
#os.environ['NZBPO_ACCESSTOKEN']="o.6mXC3GpZ33AgWCkgpwLdHIt750btnlNO"

password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, os.environ['NZBPO_URL'], os.environ['NZBPO_ACCESSTOKEN'], '')
handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
opener = urllib.request.build_opener(handler)
opener.open(os.environ['NZBPO_URL'])
urllib.request.install_opener(opener)
values = {'title' : 'NZBGet - SearchProviders',
           'body' : text,
           'type' : 'note' }
data = urllib.parse.urlencode(values).encode("utf-8")
print(data)
req = urllib.request.Request(os.environ['NZBPO_URL'], data)
urllib.request.urlopen(req)
print('Sent to Pushbullet')
print("[NZB] MARK=BAD")
