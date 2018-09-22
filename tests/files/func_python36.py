import time

def handler(event):
    time.sleep(10)

    print("Hello World {}".format(event[0]))
    return 42