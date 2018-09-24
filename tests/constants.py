class Image:
    WEB_CRAWLING_PYTHON36 = {
        'path': 'sharedcloud/web-crawling-python36:latest',
        'uuid': '24b3a0f8-c405-4928-954f-d5c93273f88a',
        'description': 'An image with web crawling libraries'
    }
    WEB_CRAWLING_PYTHON27 = {
        'path': 'sharedcloud/web-crawling-python27:latest',
        'uuid': 'a8e496b2-ab15-40ee-a1bf-3a28d7a8a2c3',
        'description': 'An image with web crawling libraries'
    }
    STANDARD_NODE8 = {
        'path': 'sharedcloud/standard-node8:latest',
        'uuid': '1a5111c1-17ee-459f-a4da-9c5272d86b1d',
        'description': 'An image with standard libraries'
    }

class Message:
    YOU_ARE_LOGOUT_WARNING = 'You seem to be logged out. Please log in first'
    NO_INSTANCE_FOUND = 'We couldn\'t find an instance in this computer'
    NO_RESOURCE_FOUND = 'Not found resource'
    JOBS_STILL_RUNNING = 'Please wait until they are finished'


class InstanceType:
    GPU = 'gpu'
    STANDARD = 'standard'