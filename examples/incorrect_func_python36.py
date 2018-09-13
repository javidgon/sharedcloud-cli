import platform

def handler(event):
    # This function should FAIL due to this syntax error
    print 'Python version: {}'.format(platform.python_version())

    return 'Hello friend, you are passing {} arguments'.format(len(event))
