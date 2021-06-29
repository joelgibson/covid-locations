#!/usr/bin/env python3

import urllib.request
import json
import pathlib
import logging
import sys
import time


logging.basicConfig(
    format=r"%(asctime)s - %(levelname)s - %(message)s",
    datefmt=r"%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
    level=logging.INFO,
)


def fetch_resource_url():
    """
    Fetch the 'resource' URL from the dataset metadata file, using the resource with
    the name 'COVID-19 current case locations'. The URL returned looks something like
    https://data.nsw.gov.au/data/dataset/0a52e6c1-bc0b-48af-8b45-d791a6d8e289/resource/f3a28eed-8c2a-437b-8ac1-2dab3cf760f9/download/covid-case-locations-20210628-2313.json

    We could have also checked the 'last_modified' field in the resource, which is in UTC (as far as I can tell).
    """

    METADATA_URL = 'https://data.nsw.gov.au/data/api/3/action/package_show?id=0a52e6c1-bc0b-48af-8b45-d791a6d8e289'
    RESOURCE_NAME = 'COVID-19 current case locations'

    with urllib.request.urlopen(METADATA_URL) as f:
        object = json.load(f)
    
    return [
        resource for resource in object['result']['resources']
        if resource['name'] == RESOURCE_NAME
    ][0]['url']


def maybe_download(resource_url: str):
    """
    Take the last part of the URL, for example 'covid-case-locations-20210628-2313.json'. If this file already
    exists inside 'src/', then do nothing. Otherwise, download whatever is at the full URL to src/.
    """
    _, filename = resource_url.rsplit('/', 1)
    path = pathlib.Path('src', filename)

    if path.exists():
        logging.info("The file %s exists, doing nothing.", path)
        return
    
    with urllib.request.urlopen(resource_url) as f:
        # Remove the BOM
        content = f.read().decode('utf-8-sig').encode('utf-8')
    
    with open(path, 'wb') as f:
        f.write(content)
    
    logging.info("New file saved to %s", path)
    

while True:
    maybe_download(fetch_resource_url())
    time.sleep(60 * 20)