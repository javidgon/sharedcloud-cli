import os

__VERSION__ = '0.0.5'


DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'
DATA_FOLDER = '{}/.sharedcloud'.format(os.path.expanduser('~'))

SHAREDCLOUD_CLI_URL = os.environ.get('SHAREDCLOUD_CLI_URL', 'https://sharedcloud.io')
SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME = '{}/{}'.format(DATA_FOLDER, os.environ.get(
    'SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME', 'client_config'))
SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME = '{}/{}'.format(DATA_FOLDER, os.environ.get(
    'SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME', 'instance_config'))

JOB_STATUSES = {
    'CREATED': 1,
    'IN_PROGRESS': 2,
    'SUCCEEDED': 3,
    'FAILED': 4,
    'TIMEOUT': 5
}

INSTANCE_STATUSES = {
    'NOT_AVAILABLE': 1,
    'AVAILABLE': 2
}

INSTANCE_TYPES = {
    'CPU': 1,
    'GPU': 2
}

SESSION_STATUSES = {
    'CREATED': 1,
    'IN_PROGRESS': 2,
    'FINISHED': 3,
}

SHAREDCLOUD_AGENT_CONTAINER_NAME = 'sharedcloud-agent'
SHAREDCLOUD_AGENT_PAYLOAD_FILENAME = 'data.json'
SHAREDCLOUD_AGENT_PORT = 4005

SHAREDCLOUD_INSTANCE_TUNNEL_CONTAINER_NAME = 'sharedcloud-instance-tunnel-client'


SHAREDCLOUD_SESSION_CONTAINER_NAME = 'sharedcloud-session'
SHAREDCLOUD_SESSION_PORT = 8000
SHAREDCLOUD_SESSION_TUNNEL_CONTAINER_NAME = 'sharedcloud-session-tunnel-client'
