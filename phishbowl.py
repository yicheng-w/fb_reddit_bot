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

out_file = raw_input("output_file: ")

CATCH_EM_ALL = "2356521841137542"

class ChatBot(fbchat.Client):
    def __init__(self, email, password, debug=True, user_agent=None):
        fbchat.Client.__init__(self, email, password, debug, user_agent)
        self._last_msg = None
        self._ongoing_game = False
        self._participants = []
        self._team1 = []
        self._team2 = []

    def on_message(self, mid, author_id, author_name, message, metadata):
        self.markAsDelivered(author_id, mid)
        self.markAsRead(author_id)

        print("%s (%s) said: %s" % (author_name, author_id, message))

        other_id = str(metadata['delta']['messageMetadata']['threadKey']['otherUserFbId'])

        if other_id == CATCH_EM_ALL:
            print("Catch 'em all")

        if message.startswith("@phishbowl"):
            cmd_args = message.split()[1:]

            if cmd_args[0] == "add":
                out_file.write(self._last_msg.replace("\n", " ") + '\n')

            if cmd_args[0] == "join":
                if not self._ongoing_game:
                    self._participants.append((author_name, author_id))
                    self.send(author_id, "%s joined, current participants: %s" %
                            (author_name, ",".join(self._participants)))

            if cmd_args[0] == "start":
                self._team1 = random.sample(self._participants,
                        len(self._participants) / 2)
                self._team2 = [elt for elt in self._participants if elt not in
                        self._team1]

                self.send(author_id, "The game has started!")
                self.send(author_id, "Team 1: %s" % (",".join(self._team1)))
                self.send

        else:
            self._last_msg = message
