import time
import fbchat

import numpy as np

camel = fbchat.Message(text="🐫")
dexit = "2151364391633711"

mean_time = 17280

if __name__ == '__main__':

    email = input("email: ").strip()
    passwd = input("passwd: ").strip()

    client = fbchat.Client(email, passwd)

    while True:
        t = np.random.exponential(mean_time)
        time.sleep(t)
        client.send(camel, dexit, fbchat.models.ThreadType.GROUP)
