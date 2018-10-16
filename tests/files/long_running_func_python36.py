import time

def handler(event):
    time.sleep(40)

    print("Hello World {}".format(event[0]))
    return 42