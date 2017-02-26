import fbchat
import random
import requests
from bs4 import BeautifulSoup
import traceback
import sys
import time

email = raw_input("email: ")
passwd = raw_input("passwd: ")

reddit_timeout = 15 # technically 2, but just to be safe
last_reddit_request = 0

reddit_base = "http://reddit.com/"

def get_reddit_thread(subreddit):
    global last_reddit_request

    ct = time.time()
    if ct - last_reddit_request < reddit_timeout:
        return None

    last_reddit_request = ct

    url = reddit_base + subreddit

    #print "accessing reddit"
    reddit_page = BeautifulSoup(requests.get(url).text, 'html.parser')
    #print "Bsdone"

    reddit_links = []

    #print reddit_page.prettify()

    for link in reddit_page.find_all('a'):
        if (link.get('data-href-url')):
            if (link.get('data-href-url')[:2] == "/r"):
                reddit_links.append(reddit_base + link.get('data-href-url'))
            else:
                reddit_links.append(link.get('data-href-url'))

    #print reddit_links

    if len(reddit_links) > 0:
        return random.choice(reddit_links)

    return None

class ChatBot(fbchat.Client):
    def __init__(self, email, password, debug=True, user_agent=None):
        fbchat.Client.__init__(self, email, password, debug, user_agent)

    def on_message(self, mid, author_id, author_name, message, metadata):
        global last_result
        self.markAsDelivered(author_id, mid)
        self.markAsRead(author_id)

        print "%s (%s) said: %s" % (author_name, author_id, message)

        if metadata['delta']['messageMetadata']['threadKey']['otherUserFbId'] == str(self.uid):
            if (message != last_result):
                last_result = ">>> " + str(eval(message))
                self.send(author_id, last_result)

        #if (str(author_id) == saujas_fb_id):
            #    self.send(author_id, random.choice(motivational_quotes))

        elif (str(author_id) == mlb_fb_id):
            if (random.randrange(0, 20) == 0):
                imageurl = get_random_wholesome_meme()
                if (imageurl):
                    self.sendRemoteImage(author_id, message="oh also this:",
                            image=imageurl)

                    #elif (str(author_id) != str(self.uid)):
        #    self.send(author_id, "Message received")

bot = ChatBot(email, passwd, debug=False)
bot.listen()
