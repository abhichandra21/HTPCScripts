OptimusPrime:/opt/htpc-config/nzbget/scripts/deleteRadarr # cat deleteRadarr.py
#!/usr/bin/env python

#
##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###

# Delete a movie from Radarr
#
# NOTE: This script requires Python to be installed on your system.
##############################################################################
### OPTIONS                                                                ###

## Radarr
# Radarr host.
#
# The ipaddress for your Radarr server. e.g For the Same system use localhost or 127.0.0.1
#rahost=localhost

# Radarr port.
#raport=7878

# Radarr API key.
#raapikey=

# Radarr uses ssl (0, 1).
#
# Set to 1 if using ssl, else set to 0.
#rassl=0

# Radarr web_root
#
# set this if using a reverse proxy.
#raweb_root=

## TMDB
#tmdbapikey=

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################
import os
import sys
from os.path import dirname
sys.path.insert(1,dirname(__file__) + '/lib')

import pprint
import guessit
import guessit.patterns.extension
import requests
import json
from tmdb_api import tmdb

from dotenv import load_dotenv
load_dotenv(os.path.join('/opt/htpc-config/nzbget/scripts/nzbget.env'))

radarr_host = os.environ['NZBPP_RAHOST']
radarr_port = os.environ['NZBPP_RAPORT']
radarr_webroot = os.environ['NZBPP_RAWEB_ROOT']
radarr_ssl = os.environ['NZBPP_RASSL']
radarr_key = os.environ['NZBPP_RAAPIKEY']
tmdb_api_key = os.environ['NZBPP_TMDBAPIKEY']

# Check if all required script config options are present in config file
required_options = ('NZBPP_RAHOST', 'NZBPP_RAPORT', 'NZBPP_RAWEB_ROOT', 'NZBPP_RASSL', 'NZBPP_RAAPIKEY', 'NZBPP_TMDBAPIKEY')
for optname in required_options:
    if (not optname.upper() in os.environ):
        print('[ERROR] Option %s is missing in configuration file. Please check script settings' % optname[6:])
        sys.exit(POSTPROCESS_ERROR)

if radarr_ssl == 1:
    proto = 'https'
else:
    proto = 'http'

radarr_url = proto + "://" + radarr_host + ":" + radarr_port + "/" + radarr_webroot
print("Radarr URL: %s" % radarr_url)

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
            print("Matched movie title as: %s %s" % (movie["title"].encode(sys.stdout.encoding, errors='ignore'), movie["release_date"].encode(sys.stdout.encoding, errors='ignore')))
            movie = tmdb.Movie(movie["id"])
            if isinstance(movie, dict):
                tmdbid = movie["id"]
                tmdb_title = movie["title"]
            else:
                tmdbid = movie.get_id()
                tmdb_title = movie.get_title()
            return tmdbid, tmdb_title
    return None

# NZBGet Exit Codes
NZBGET_POSTPROCESS_PARCHECK = 92
NZBGET_POSTPROCESS_SUCCESS = 93
NZBGET_POSTPROCESS_ERROR = 94
NZBGET_POSTPROCESS_NONE = 95

if 'NZBOP_SCRIPTDIR' not in os.environ:
    print("This script can only be called from NZBGet (11.0 or later).")
    sys.exit(0)

if os.environ['NZBOP_VERSION'][0:5] < '11.0':
    print("NZBGet Version %s is not supported. Please update NZBGet." % (str(os.environ['NZBOP_VERSION'])))
    sys.exit(0)

print("Script triggered from NZBGet Version %s." % (str(os.environ['NZBOP_VERSION'])))
status = 0
if 'NZBPP_TOTALSTATUS' in os.environ:
    if not os.environ['NZBPP_TOTALSTATUS'] == 'SUCCESS':
        print("Download failed with status %s." % (os.environ['NZBPP_STATUS']))
        status = 1

else:
    # Check par status
    if os.environ['NZBPP_PARSTATUS'] == '1' or os.environ['NZBPP_PARSTATUS'] == '4':
        print("Par-repair failed, setting status \"failed\".")
        status = 1

    # Check unpack status
    if os.environ['NZBPP_UNPACKSTATUS'] == '1':
        print("Unpack failed, setting status \"failed\".")
        status = 1

    if os.environ['NZBPP_UNPACKSTATUS'] == '0' and os.environ['NZBPP_PARSTATUS'] == '0':
        # Unpack was skipped due to nzb-file properties or due to errors during par-check

        if os.environ['NZBPP_HEALTH'] < 1000:
            print("Download health is compromised and Par-check/repair disabled or no .par2 files found. Setting status \"failed\".")
            print("Please check your Par-check/repair settings for future downloads.")
            status = 1

        else:
            print("Par-check/repair disabled or no .par2 files found, and Unpack not required. Health is ok so handle as though download successful.")
            print("Please check your Par-check/repair settings for future downloads.")

if os.environ['NZBPP_CATEGORY'] != 'Movies':
    print("This is only valid for Movies.")
    status = 1

print("NZBPP_DIRECTORY: %s | NZBPP_FINALDIR: %s | NZBPP_NZBNAME: %s | NZBPP_NZBFILENAME: %s | NZBPP_CATEGORY: %s" % (os.environ['NZBPP_DIRECTORY'], os.environ['NZBPP_FINALDIR'],os.environ['NZBPP_NZBNAME'],os.environ['NZBPP_NZBFILENAME'],os.environ['NZBPP_CATEGORY'], ))
# All checks done, now launching the script.
if status == 1:
    sys.exit(NZBGET_POSTPROCESS_NONE)

nzb_tmdbid = 0
nzb_title = ''
radarr_id = 0
radarr_title = ''
# Get the TMDBID of the movie
guess = guessit.guess_movie_info(os.environ['NZBPP_NZBFILENAME'])
print guess.nice_string()
try:
    if guess['type'] == 'movie':
        nzb_tmdbid, nzb_tmdbtitle = tmdbInfo(guess)
        print("TMDB id from NZB: %s" % nzb_tmdbid)
except Exception as e:
    print(e)

radarrSession = requests.Session()
radarrSession.trust_env = False
#print("%s/api/movie?apikey=%s" % (radarr_url, radarr_key))
radarrMovies = radarrSession.get('{0}/api/movie?apikey={1}'.format(radarr_url, radarr_key))
if radarrMovies.status_code != 200:
    print('Radarr server error - response %s' % radarrMovies.status_code)
    sys.exit(NZBGET_POSTPROCESS_NONE)
for movie in radarrMovies.json():
    tmdb_id = movie['tmdbId']
    #print("Processing Movie %s(%s)" % (movie['title'], movie['tmdbId']))
    if nzb_tmdbid == movie['tmdbId']:
        print('Got a match: %s[%s]' % (movie['title'],movie['id']))
        radarr_id = movie['id']
        radarr_title = movie['title']
        break
if radarr_id is not None and radarr_id != 0:
    deleteSession = requests.Session()
    deleteSession.trust_env = False
    deleteMovies = deleteSession.delete('{0}/api/movie/{1}?apikey={2}'.format(radarr_url, radarr_id, radarr_key))
    if deleteMovies.status_code != 200:
        print('Radarr delete server error - response %s' % deleteMovies.status_code)
        sys.exit(NZBGET_POSTPROCESS_NONE)
    print("Successfully deleted %s" % radarr_title )
else:
    print("Movie not found in Radarr: %s[%s]" % (nzb_tmdbtitle, nzb_tmdbid))
#curl -H 'Accept: application/json' -H 'Content-Type: application/json' -H 'X-Api-Key: 38b9097ad5ba47de9f6e5b62b121486a' -X GET http://127.0.0.1:7878/radarr/api/movie | jq '.[] | select(.tmdbId == 447365) | .id'
sys.exit(NZBGET_POSTPROCESS_SUCCESS)
OptimusPrime:/opt/htpc-config/nzbget/scripts/deleteRadarr #
