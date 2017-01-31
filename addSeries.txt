#!/bin/bash

# Download IMDB RSS
wget http://rss.imdb.com//list/<LISTID> -O imdb.xml -o /dev/null
# How many Series to Process
COUNT=$(grep -c guid imdb.xml)

for aa in `seq ${COUNT}`; do
  # Get IMDB Name from the RSS
  srName=$(xmllint --xpath "//channel/item[${aa}]/*[self::title]/text()" imdb.xml | sed 's/ (.*//g')
  # Get IMDB-ID from the RSS
  imdbID=$(xmllint --xpath "//channel/item[${aa}]/*[self::guid]/text()" imdb.xml | awk -F\/ '{print $(NF-1)}')
  # Get TVDB-ID using IMDB-ID
  tvdbID=$(curl "https://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=${imdbID}&api_key=<API_KEY>" 2>/dev/null| xmllint --xpath "//Data/Series/seriesid/text()" -)
  echo "Adding => $srName | $imdbID | $tvdbID"
  # Add it to Sonarr
  curl http://localhost/sonarr/api/series -X POST -d '{"tvdbId":"'${tvdbID}'", "title": "'"${srName}"'", "qualityProfileId": "1", "monitored": false, "images": [], "seasons": [], "rootFolderPath": "/storage/TVShows/", "addOptions": {"ignoreEpisodesWithFiles": true, "ignoreEpisodesWithoutFiles": true, "searchForMissingEpisodes": false}}' --header X-Api-Key:<API_KEY> 2>/dev/null
done
rm -f imdb.xml
