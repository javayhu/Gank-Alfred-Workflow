#!/usr/bin/python
# encoding: utf-8

import sys
from workflow import Workflow, web

logger = None

# Different icon image for different type of gank
ICON_DEFAULT = 'icon.png'
ICON_GANK = 'gank.png'
ICON_ANDROID = 'android.png'
ICON_IOS = 'apple.png'
ICON_HTML5 = 'html5.png'
ICON_PICTURE = 'picture.png'
ICON_VIDEO = 'video.png'
ICON_OTHER = 'other.png'

# 加载今天的干货列表
def today():
    import datetime
    now = datetime.datetime.now()
    # load today ganks from gank.io
    # url = 'http://gank.io/api/day/' + now.strftime("%Y/%m/%d")
    url = 'http://gank.io/api/day/2016/06/22'
    r = web.get(url)

    # throw an error if request failed, Workflow will catch this and show it to the user
    r.raise_for_status()

    ganks = []
    data = r.json()
    categories = data['category']
    results = data['results']
    for category in categories:
        for gank in results[category]:
            ganks.append(gank)

    return ganks

# 给定关键词搜索干货 -> 第二版本的搜索接口：由官方gank.io提供搜索接口
# http://gank.io/api/search/query/android animation/category/all/count/50/page/1 
def search(query):
    # search the ganks from gank.io
    url = 'http://gank.io/api/search/query/%s/category/all/count/50/page/1' % query 
    r = web.get(url)

    # throw an error if request failed, Workflow will catch this and show it to the user
    r.raise_for_status()

    ganks = []
    data = r.json()
    results = data['results']
    for gank in results:
        ganks.append(gank)

    return ganks

# 给定关键词搜索干货，这里使用的是干货集中营中的http://gank.io/search?q=接口，通过解析返回网页得到结果
# def search_v2(query):
#     from bs4 import BeautifulSoup
#     from bs4 import UnicodeDammit
#     # search the ganks from gank.io
#     # url = 'http://gank.io/search?%s=%s' % ('q', query)
#     url = 'http://gank.io/search'
#     params = dict(q=query)
#     r = web.get(url, params)

#     # throw an error if request failed, Workflow will catch this and show it to the user
#     r.raise_for_status()

#     ganks = []
#     soup = BeautifulSoup(r.text, 'html.parser', from_encoding = 'unicode')
#     table = soup.body.find('div', 'content').find('ol')
#     for row in table.find_all('li'):
#         gank = {}
#         gank['url'] = row.a.get('href')
#         gank['desc'] = row.a.string
#         gank['type'] = row.find_all('small')[0].string
#         gank['who'] = row.find_all('small')[1].string
#         ganks.append(gank)

#     return ganks

# 给定关键词搜索干货 -> 第一版本的搜索接口：由自己的项目Ganks-for-gank.io提供搜索接口
def search_v1(query):
    # search the ganks from gankio.herokuapp.com
    url = 'http://gankio.herokuapp.com/search'
    params = dict(keyword=query)
    r = web.post(url, params)

    # throw an error if request failed, Workflow will catch this and show it to the user
    r.raise_for_status()

    return r.json()

# determine the image
def icon(type):
    if 'Android' in type:
        return ICON_ANDROID
    elif 'iOS' in type:
        return ICON_IOS
    elif u'前端' in type:
        return ICON_HTML5
    elif u'休息视频' in type:
        return ICON_VIDEO
    elif u'福利' in type:
        return ICON_PICTURE
    elif u'拓展资源' in type:
        return ICON_OTHER
    elif u'瞎推荐' in type:
        return ICON_OTHER
    elif 'App' in type:
        return ICON_GANK
    else:
        return ICON_GANK

def main(wf):
    # The Workflow instance will be passed to the function you call from `Workflow.run`. 
    # Not so useful, as the `wf` object created in `if __name__ ...` below is global.
    
    # Get query from Workflow
    if len(wf.args):
     query = ' '.join(wf.args)
    else:
     query = None

    # If query is None, load today ganks, else search with given query string
    if query:
        # Search ganks or load from cached data, cache for 10 mins
        def wrapper():
            return search(query)
        ganks = wf.cached_data(query, wrapper, max_age=600)
        # ganks = search(query)
    else:
        # Load today ganks or load from cached data, cache for 1 min
        ganks = wf.cached_data('today', today, max_age=60)
        # add result items to workflow
    
    for gank in ganks:
        wf.add_item(title=gank['desc'],
                    subtitle=gank['who'],
                    arg=gank['url'],
                    valid=True,
                    icon=icon(gank['type']))
    
    # Send output to Alfred. You can only call this once.
    # Well, you *can* call it multiple times, but Alfred won't be listening any more...
    wf.send_feedback()
    #print(wf._items)


if __name__ == '__main__':
    # Create a global `Workflow` object
    wf = Workflow()
    logger = wf.logger
    # wf = Workflow(update_settings={
    #     'github_slug': 'hujiaweibujidao/Gank-Alfred-Workflow',
    #     'frequency': 7
    # })

    # Call your entry function via `Workflow.run()` to enable its helper
    # functions, like exception catching, ARGV normalization, magic arguments etc.
    sys.exit(wf.run(main))

    # if wf.update_available:
    #     wf.start_update()

