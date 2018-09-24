import time

def handler(event):
    time.sleep(60)

    print("Hello World {}".format(event[0]))
    return 42