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

# PushOver UserKey
#UserKey=

# PushOver API-Token
#APIToken=

### NZBGET QUEUE SCRIPT                                          ###
##############################################################################

import os
import sys
from os.path import dirname
sys.path.insert(1,dirname(__file__) + '/lib')

if os.environ.get('NZBNA_EVENT') not in ['NZB_ADDED']:
    print("Not a valid NZBGET Event")
    sys.exit(0)

import pprint
import guessit
import guessit.patterns.extension
import requests
import json
from tmdb_api import tmdb

from justwatch import JustWatch
from pushover import init, Client

#from dotenv import load_dotenv
#load_dotenv(os.path.join('/opt/htpc-config/nzbget/scripts/nzbget.env'))
env_var = os.environ
print("User's Environment variable:")
pprint.pprint(dict(env_var), width = 1)
print("Starting SearchProviders PP Script")

def tmdbInfo(guessData):
    tmdb.configure(os.environ['NZBPO_TMDBAPIKEY'])
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

try:
    movies = just_watch.search_for_item(query=nzb_tmdbtitle)
except Exception as e:
    print("Could not determine Streaming Services")
    sys.exit(NZBGET_POSTPROCESS_NONE)

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
try:
    client = Client(os.environ['NZBPO_USERKEY'], api_token=os.environ['NZBPO_APITOKEN'])
    client.send_message(text, title="SearchProviders")
    print('Sent to PushOver')
except Exception as e:
    print("Failed to send to PushOver")

print("[NZB] MARK=BAD")
