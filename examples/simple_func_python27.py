import platform

def handler(event):
    print('Python version: {}'.format(platform.python_version()))

    return 'Hello friend, you are passing {} arguments'.format(len(event))
