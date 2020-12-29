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
#TMDBAPIKEY=

# PushOver UserKey
#UserKey=

# PushOver API-Token
#APIToken=

# Radarr host.
#
# The ipaddress for your Radarr server. e.g For the Same system use localhost or 127.0.0.1
#rahost=localhost

# Radarr port.
#raport=7878

# Radarr API key.
#raapikey=38b9097ad5ba47de9f6e5b62b121486a

# Radarr uses ssl (0, 1).
#
# Set to 1 if using ssl, else set to 0.
#rassl=0

# Radarr web_root
#
# set this if using a reverse proxy.
#raweb_root=radarr

### NZBGET QUEUE SCRIPT                                          ###
##############################################################################

import os
import sys
from os.path import dirname
sys.path.insert(1,dirname(__file__) + '/lib')

#if os.environ.get('NZBNA_EVENT') not in ['NZB_ADDED']:
#    print("Not a valid NZBGET Event")
#    sys.exit(0)

import pprint
import guessit
import guessit.patterns.extension
import requests
import json
from tmdb_api import tmdb

from justwatch import JustWatch
from pushover import init, Client

# NZBGet Exit Codes
NZBGET_POSTPROCESS_PARCHECK = 92
NZBGET_POSTPROCESS_SUCCESS = 93
NZBGET_POSTPROCESS_ERROR = 94
NZBGET_POSTPROCESS_NONE = 95

radarr_host = os.environ['NZBPO_RAHOST']
radarr_port = os.environ['NZBPO_RAPORT']
radarr_webroot = os.environ['NZBPO_RAWEB_ROOT']
radarr_ssl = os.environ['NZBPO_RASSL']
radarr_key = os.environ['NZBPO_RAAPIKEY']

#from dotenv import load_dotenv
#load_dotenv(os.path.join('/opt/htpc-config/nzbget/scripts/nzbget.env'))
#env_var = os.environ
#print("User's Environment variable:")
#pprint.pprint(dict(env_var), width = 1)
#print("Starting SearchProviders PP Script")

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
required_options = ('NZBPO_TMDBAPIKEY', 'NZBPO_USERKEY', 'NZBPO_APITOKEN', 'NZBPO_RAHOST', 'NZBPO_RAPORT', 'NZBPO_RAWEB_ROOT', 'NZBPO_RASSL', 'NZBPO_RAAPIKEY')
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
radarr_id = 0
radarr_title = ''

if radarr_ssl == 1:
    proto = 'https'
else:
    proto = 'http'

radarr_url = proto + "://" + radarr_host + ":" + radarr_port + "/" + radarr_webroot
print("Radarr URL: %s" % radarr_url)

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
                    elif provider.get('provider_id') == 384:
                        jw_provider = "HBO Max"
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

print('[DETAIL] Sending to PushOver')
try:
    client = Client(os.environ['NZBPO_USERKEY'], api_token=os.environ['NZBPO_APITOKEN'])
    client.send_message(text, title="SearchProviders")
    print('Sent to PushOver')
except Exception as e:
    print("Failed to send to PushOver")


# Delete from Radarr
print("Deleting from Radarr...")
radarrSession = requests.Session()
radarrSession.trust_env = False
#print("%s/api/movie?apikey=%s" % (radarr_url, radarr_key))
radarrMovies = radarrSession.get('{0}/api/movie?apikey={1}'.format(radarr_url, radarr_key))
if radarrMovies.status_code != 200:
    print('Radarr server error - response %s' % radarrMovies.status_code)
    sys.exit(NZBGET_POSTPROCESS_NONE)
for movie in radarrMovies.json():
    tmdb_id = movie['tmdbId']
    print("Processing Movie %s(%s)" % (movie['title'], movie['tmdbId']))
    if nzb_tmdbid == movie['tmdbId']:
        print('Got a match: %s[%s]' % (movie['title'],movie['id']))
        radarr_id = movie['id']
        radarr_title = movie['title']
        break
if radarr_id is not None and radarr_id != 0:
    deleteSession = requests.Session()
    deleteSession.trust_env = False
    deleteMovies = deleteSession.delete('{0}/api/movie/{1}?apikey={2}&addExclusion=true'.format(radarr_url, radarr_id, radarr_key))
    if deleteMovies.status_code != 200:
        print('Radarr delete server error - response %s' % deleteMovies.status_code)
        sys.exit(NZBGET_POSTPROCESS_NONE)
    print("Successfully deleted %s" % radarr_title )
else:
    print("Movie not found in Radarr: [%s]" % (nzb_tmdbid))
#curl -H 'Accept: application/json' -H 'Content-Type: application/json' -H 'X-Api-Key: 38b9097ad5ba47de9f6e5b62b121486a' -X GET http://127.0.0.1:7878/radarr/api/movie | jq '.[] | select(.tmdbId == 447365) | .id'

print("[NZB] MARK=BAD")
