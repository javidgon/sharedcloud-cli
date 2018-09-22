import time

def handler(event):
    time.sleep(10)
    raise Exception('This is a test Exception')
