#!/usr/bin/python

# encoding: utf-8

import sys

from workflow import Workflow, ICON_WEB, web

ICON_DEFAULT = 'icon.png'

def search(query):
    # search the ganks from gank.io
    url = 'http://ganks-for-gankio.herokuapp.com//search'
    params = dict(keyword=query)
    r = web.post(url, params)

    # throw an error if request failed, Workflow will catch this and show it to the user
    r.raise_for_status()

    return r.json()


def main(wf):
    # The Workflow instance will be passed to the function
    # you call from `Workflow.run`. Not so useful, as
    # the `wf` object created in `if __name__ ...` below is global.
    #
    # Get query from Alfred
    query = wf.args[0]

    # Search ganks or load from cached data, 10 mins
    def wrapper():
        return search(query)
    ganks = wf.cached_data(query, wrapper, max_age=600)
     
    # Parse the JSON returned by pinboard and extract the ganks
    for gank in ganks:
        wf.add_item(title=gank['title'],
                     subtitle=gank['source'],
                     arg=gank['url'], 
                     valid=True,
                     icon=ICON_DEFAULT)
    
    # Send output to Alfred. You can only call this once.
    # Well, you *can* call it multiple times, but Alfred won't be listening
    # any more...
    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow` object
    wf = Workflow()
    # Call your entry function via `Workflow.run()` to enable its helper
    # functions, like exception catching, ARGV normalization, magic
    # arguments etc.
    sys.exit(wf.run(main))
