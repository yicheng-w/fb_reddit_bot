import fbchat
import time
import os

email = raw_input("email: ")
passwd = raw_input("passwd: ")
screenshotdir = raw_input("screenshot directory (full path): ")
if screenshotdir[-1] != "/":
    screenshotdir += "/"

images = ['png', 'jpg', 'gif']

def get_most_recent_screenshot():
    dated_files = [(os.path.getmtime(screenshotdir + fn), os.path.basename(fn)) 
                   for fn in os.listdir(screenshotdir)
                   if fn.lower()[-3:] in images]
    dated_files.sort()
    dated_files.reverse()
    newest = dated_files[0][1]
    return screenshotdir + newest

class ChatBot(fbchat.Client):
    def __init__(self, email, password, debug=True, user_agent=None):
        fbchat.Client.__init__(self, email, password, debug, user_agent)

    def on_message(self, mid, author_id, author_name, message, metadata):
        self.markAsDelivered(author_id, mid)
        self.markAsRead(author_id)

        print "%s (%s) said: %s" % (author_name, author_id, message)

        other_id = metadata['delta']['messageMetadata']['threadKey']['otherUserFbId']

        if str(author_id) == str(self.uid) and message == "send screenshot":
            self.sendLocalImage(other_id, image=get_most_recent_screenshot())

bot = ChatBot(email, passwd, debug=False)
bot.listen()
