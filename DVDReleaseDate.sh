#!/bin/bash

rm -f /tmp/all.movies
for aa in $(lynx -dump http://www.dvdsreleasedates.com/ | sed -n '/Visible links/,/Hidden links/p' | awk '/^[[:space:]][[:digit:]].*\/movies\//{print $NF}' | sort -u)
do
  #echo $aa
  if [[ $aa =~ "TV-" ]]; then
    #echo "Matched TV- : ${aa}"
    continue
  fi
  lynx -dump $aa | awk -vaa=$aa '
function bail() {name="";imdb="";genre="";date="";imdblink="";readdate="";exit}
/^[A-Za-z0-9]/ {
                 if(name==""){
                    name=$0
                    gsub(/\).*/,")",name)
                 }
                 if($0~/release date.*set for/){
                   origline=$0
                   gsub(/.*release date.*set for| and.*/,"")
                   if($0~/est/){bail()}
                   if(date=="")date=$0
                   if(date=="")getline
                   origline=origline" "$0
                   gsub(/.*release date.*set for| and.*/,"")
                   if($0~/est/){bail()}
                   if(date=="")date=$0
                 }
               }
/Rating: TV/ {bail()}
/\(TV Series\)/ {bail()}
/^[[:space:]]+imdb:/ {
                       if(imdb==""){
                         match($0,/([[:digit:]]\.[[:digit:]])/,arr)
                         imdb=arr[1]
                         match($0,/\[([[:digit:]]+)\]/,arr)
                         imdblink=arr[1]
                         #if (int(imdb)<7){bail()}
                       }
                     }
/^[[:space:]]+Genre/ {
                       gsub(/Genre\(s\): /,"")
                       gsub(/[0-9]|\[|\]/,"");
                       gsub(/^[ \t]+/,"");
                       genre=$0
                     }
/^[[:space:]]+[[:digit:]]+\./ {
                                if($1==imdblink){
                                  imdblink=$2
                                  #bail()
                                }
                              }
END{if(imdblink!="")print name";"imdb";"genre";"date";"imdblink}

' >> /tmp/all.movies
done
sort /tmp/all.movies -o /tmp/all.movies

if [ ! -f /tmp/all.movies.base ]; then
  /bin/cp /tmp/all.movies /tmp/all.movies.base
  exit
fi
rm -f /tmp/mail.html
awk -F';' 'NR==FNR && a[$1"|"$4]=1 {} NR>FNR { k=$1"|"$4;if (k in a == 0) print $0}' all.movies.base all.movies > /tmp/diff$$
#rc=$(comm -23 /tmp/all.movies /tmp/all.movies.base | wc -l)
if [[ -s /tmp/diff$$ ]]; then
  OLDIFS=$IFS
  IFS=";"
  desc=""
  cat <<EOT > /tmp/mail.html
  <!DOCTYPE html>
  <html itemscope itemtype="http://schema.org/QAPage">
  <head>
  <style type="text/css">
  table.imagetable {
        font-family: verdana,arial,sans-serif;
        font-size:11px;
        color:#333333;
        border-width: 1px;
        border-color: #999999;
        border-collapse: collapse;
  }
  table.imagetable th {
        background:#b5cfd2 url('cell-blue.jpg');
        border-width: 1px;
        padding: 8px;
        border-style: solid;
        border-color: #999999;
  }
  table.imagetable td {
        background:#dcddc0 url('cell-grey.jpg');
        border-width: 1px;
        padding: 8px;
        border-style: solid;
        border-color: #999999;
  }
  </style>
  </head>
  <h1>DVD Release Date</h1>
  <table class="imagetable">
  <tr><th>Movie</th><th>IMDB Rating</th><th>Genre</th><th>Release</th></tr>
EOT
  while read name imdb genre reldate imdblink
    do
      cat <<EOT >> /tmp/mail.html
      <tr>
      <td><a href=${imdblink}>${name}</a></td>
      <td>${imdb}</td>
      <td>${genre}</td>
      <td>${reldate}</td>
      </tr>
EOT
  done < /tmp/diff$$
  IFS=$OLDIFS
  echo " </table>" >> /tmp/mail.html

  cat <<EOF - /tmp/mail.html | /usr/sbin/sendmail -t
To: <EMAIL>
Subject: DVD Release Dates
Content-Type: text/html

EOF
  #echo "`date`: /tmp/all.movies Changed" >> /var/log/filechanges.log
  cat /tmp/diff$$ >> /tmp/all.movies.base
  sort -u /tmp/all.movies.base -o /tmp/all.movies.base
  rm /tmp/diff$$
fi
