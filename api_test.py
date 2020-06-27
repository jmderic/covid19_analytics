#!/usr/bin/python3

import urllib.request, urllib.parse, json, datetime


def get_ts_fm_dt(dt) :
    return dt.strftime('%Y%m%d_%H%M%S')

def get_timestamp() :
    dt_now = datetime.datetime.now()
    return get_ts_fm_dt(dt_now)

#url = 'https://data.ca.gov/api/3/action/datastore_search?resource_id=926fd08f-cc91-4828-af38-bd45de97f8c3'
url = 'https://data.ca.gov/api/3/action/datastore_search?resource_id=926fd08f-cc91-4828-af38-bd45de97f8c3&limit=32000&filters={"county": "Orange"}'
# filters=%7B%22county%22%3A%20%22Orange%22%7D
safe_url = 'https://data.ca.gov/api/3/action/datastore_search?resource_id=926fd08f-cc91-4828-af38-bd45de97f8c3&limit=32000&filters=%7B%22county%22%3A%20%22Orange%22%7D'
#url = 'https://data.ca.gov/api/3/action/help_show?name=datastore_search'

#safe_url = urllib.parse.quote(url)
#print(safe_url)

fileobj = urllib.request.urlopen(safe_url)
#print fileobj.read()

parsed = json.load(fileobj)

ts = get_timestamp()

#with open(f'/tmp/api_test_{ts}.txt', 'w') as f:
#    f.write(parsed["result"])

with open(f'/tmp/api_test_{ts}.json', 'w') as f:
    json.dump(parsed, f, indent=4, sort_keys=True)
