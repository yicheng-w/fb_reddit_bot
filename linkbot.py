
import json
import fbchat
import random
import requests
import traceback
import sys
import time
import os

from urllib.parse import urlparse, urljoin, parse_qs
from argparse import ArgumentParser
from sys import argv

def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except:
        print("ERROR: '%s'" % x)
        return False

def god_dammit_cynthia(url):
    '''
    Takes in a google url, e.g.
    https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiWyNDhqbHqAhXJc98KHdhBDE0QFjAAegQIAxAB&url=https%3A%2F%2Fwhat-if.xkcd.com%2F4%2F&usg=AOvVaw08HMiEaewSk083jktRVxpn

    and goes through the get request params to find the target url
    '''

    parsed = urlparse(url)
    parsed = parse_qs(parsed.query)
    if 'url' not in parsed:
        return None
    return parsed['url'][0]

def format_url(url, get_params):
    if get_params is None:
        return url

    for i, k in enumerate(get_params):
        prefix = "?" if i == 0 else "&"
        url = url + "%s%s=%s" % (prefix, k, get_params[k])

    return url

def clean_url(url, allowed_items):
    parsed = urlparse(url)
    get_params = parse_qs(parsed.query)

    url_id = parsed.netloc + parsed.path
    cleaned_url = "%s%s" % (parsed.netloc, parsed.path)

    if parsed.scheme is not None and len(parsed.scheme) != 0:
        cleaned_url = "%s://%s" % (parsed.scheme, cleaned_url)

    filtered_get_params = {}

    if "www.google.com/url" in url_id:
        return god_dammit_cynthia(url)

    for item in allowed_items:
        k = item['domain']
        if k in url_id:
            for param in get_params:
                if param in item['allowed_params']:
                    filtered_get_params[param] = get_params[param][0]

    if len(filtered_get_params) == 0:
        filtered_get_params = None

    return format_url(cleaned_url, filtered_get_params)

class LinkClient(fbchat.Client):
    def __init__(self, username, password, target_threads, allow_list, **kwargs):
        fbchat.Client.__init__(self, username, password, **kwargs)
        self._target_threads = target_threads
        self._allow_list = allow_list

    def onMessage(self, mid, author_id, message_object, thread_id, thread_type,
            ts, metadata, msg, **kwargs):

        if len(self._target_threads) == 0 or thread_id in self._target_threads:
            text = message_object.text
            if uri_validator(text):
                print("Link detected")

                cleaned_url = clean_url(text, self._allow_list)

                if cleaned_url == text:
                    print("good link ^.^")
                else:
                    msg = fbchat.Message(text=cleaned_url,
                            reply_to_id=mid)
                    self.send(msg, thread_id, thread_type)
            print(message_object)

if __name__ == '__main__':

    email = input("email: ").strip()
    passwd = input("passwd: ").strip()

    config = json.load(open('config.json'))

    c = LinkClient(email, passwd, config['chats'], config['allow_list'])
    c.listen()

    allowed_items = json.load(open('config.json'))['allow_list']

    test_1 = "https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiWyNDhqbHqAhXJc98KHdhBDE0QFjAAegQIAxAB&url=https%3A%2F%2Fwhat-if.xkcd.com%2F4%2F&usg=AOvVaw08HMiEaewSk083jktRVxpn"
    print(clean_url(test_1, allowed_items))

    test_2 = "https://www.youtube.com/watch?v=wCHLalpQFfo&t=326"
    print(clean_url(test_2, allowed_items))

    test_3 = "www.lmgtfy.com?q=hello+world"
    print(clean_url(test_3, allowed_items))

    test_4 = "https://www.nytimes.com/2020/06/24/nyregion/ny-coronavirus-states-quarantine.amp.html?ved=2ahUKEwiqjpTB5ZrqAhVJlHIEHW87BQkQ0PADegQIBBAT&usg=AOvVaw2Pd2dEJgNEcV4oslBYAIxf"
    print(clean_url(test_4, allowed_items))



