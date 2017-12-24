import http.client, urllib.parse, json
import requests
import os
import time
from datetime import datetime

images_per_page = 150 # Max: 150
term = 'Tokyo' # The word to search with
max_images = 1000 # It stops when the number of searched images reaches to this number
first_page = 0 # Set a number if you want to start from the middle
save_dir = 'data'

# Set your API key in 'key.txt'
with open('key.txt', 'r') as f:
    subscription_key = f.read().strip()

def call_api(key, term, count=150, offset=0):
    if not len(key) == 32:
        print ('Subscription key is invalid.')
        return

    host = "api.cognitive.microsoft.com"
    path = "/bing/v7.0/images/search"
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}

    params = {}
    params['q'] = urllib.parse.quote(term)
    params['count'] = count
    params['offset'] = offset
    params['responseFilter'] = 'Images'
    query = '&'.join(["{}={}".format(k,v) for k, v in params.items()])

    conn = http.client.HTTPSConnection(host)

    conn.request("GET", path + "?" + query, headers=headers)
    response = conn.getresponse()
    headers = [k + ": " + v for (k, v) in response.getheaders()
                if k.startswith("BingAPIs-") or k.startswith("X-MSEdge-")]
    result = response.read().decode("utf8")
    parsed_result = json.loads(result)

    return [headers, parsed_result]

def generate_image_list(result):
    parsed_result = result
    return list(map(lambda x: x['contentUrl'], parsed_result['value']))

def add_current_time_to_filename(filename):
    return "{}_{}".format(datetime.now().strftime("%Y%m%d_%H%M%S"), filename)

def download_images(image_url_list, save_dir):
    for url in image_url_list:
        try:
            time.sleep(3)
            res = requests.get(url)
            filename_raw = os.path.basename(url)
            filename = add_current_time_to_filename(filename_raw)
            path = os.path.join(save_dir, filename)
            with open(path, 'wb') as f:
                f.write(res.content)
            print("{} saved".format(path))
        except Exception as e:
            print(e)

current_page = first_page
while True:
    offset = images_per_page * current_page
    print ("Current Page: {}, Offset: {}, Images per page: {}".format(current_page, offset, images_per_page))

    headers, result = call_api(subscription_key, term, count=images_per_page, offset=offset)
    total_estimated_matches = result['totalEstimatedMatches']

    image_url_list = generate_image_list(result)
    download_images(image_url_list, save_dir)

    current_page += 1

    if min(total_estimated_matches, max_images) < current_page * images_per_page:
        break
