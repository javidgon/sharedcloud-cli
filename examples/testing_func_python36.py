def handler(event):
    print("Hello World {}".format(event[0]))
    return 42 + int(event[0])