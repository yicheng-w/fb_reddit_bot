import fbchat
import random
import requests
from bs4 import BeautifulSoup
import traceback
import sys
import time
import os

email = raw_input("email: ")
passwd = raw_input("passwd: ")
screenshotdir = raw_input("screenshot directory (full path): ")
if screenshotdir[-1] != "/":
    screenshotdir += "/"

reddit_timeout = 15 # technically 2, but just to be safe
last_reddit_request = 0

reddit_base = "http://www.reddit.com/"

images = ['png', 'jpg', 'jpeg', 'PNG', 'gif']

activated_list = {}

def get_most_recent_screenshot():
    dated_files = [(os.path.getmtime(screenshotdir + fn), os.path.basename(fn)) 
                   for fn in os.listdir(screenshotdir)
                   if fn.lower()[-3:] in images]
    dated_files.sort()
    dated_files.reverse()
    newest = dated_files[0][1]
    return screenshotdir + newest

def get_reddit_thread(subreddit):
    global last_reddit_request

    ct = time.time()
    if ct - last_reddit_request < reddit_timeout:
        return None

    last_reddit_request = ct

    url = reddit_base + "r/" + subreddit

    print url

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

    print reddit_links

    if len(reddit_links) > 0:
        to_ret = random.choice(reddit_links)
        while (len(to_ret) < 3):
            to_ret = random.choice(reddit_links)
        return to_ret

    return None

class ChatBot(fbchat.Client):
    def __init__(self, email, password, debug=True, user_agent=None):
        fbchat.Client.__init__(self, email, password, debug, user_agent)

    def on_message(self, mid, author_id, author_name, message, metadata):
        global last_result
        self.markAsDelivered(author_id, mid)
        self.markAsRead(author_id)

        print "%s (%s) said: %s" % (author_name, author_id, message)

        other_id = str(metadata['delta']['messageMetadata']['threadKey']['otherUserFbId'])

        if other_id == str(self.uid):
            if (message != last_result):
                last_result = ">>> " + str(eval(message))
                self.send(author_id, last_result)

        #if (str(author_id) == saujas_fb_id):
            #    self.send(author_id, random.choice(motivational_quotes))
        elif (str(author_id) in activated_list.keys()):
            if (random.randrange(0, 20) == 0):
                print "REQUESTING REDDIT"
                url = get_reddit_thread(activated_list[str(author_id)])
                if url and url[-3:] in images:
                    self.sendRemoteImage(author_id, message="oh also this:",
                            image=url)
                else:
                    self.send(author_id, url)

        elif (str(author_id) == str(self.uid)):
            if message[:8] == "activate":
                subreddit = message[9:]
                activated_list[other_id] = subreddit
                print activated_list
            elif message[:10] == "deactivate":
                del activated_list[other_id]
                print activated_list
            elif message == "send screenshot":
                self.sendLocalImage(other_id, image=get_most_recent_screenshot())
            elif str(other_id) in activated_list.keys():
                if (random.randrange(0, 20) == 0):
                    print "REQUESTING REDDIT"
                    url = get_reddit_thread(activated_list[str(other_id)])
                    if url and url[-3:] in images:
                        self.sendRemoteImage(other_id, message="oh also this:",
                                image=url)
                    else:
                        self.send(other_id, url)

                    #elif (str(author_id) != str(self.uid)):
        #    self.send(author_id, "Message received")

bot = ChatBot(email, passwd, debug=True)
bot.listen()
