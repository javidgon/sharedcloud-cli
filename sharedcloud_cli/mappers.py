import datetime

import timeago

from sharedcloud_cli.constants import DATETIME_FORMAT, JOB_STATUSES, INSTANCE_STATUSES, INSTANCE_TYPES


def _map_datetime_obj_to_human_representation(datetime_obj, resource, token):
    """
    Map a datetime obj into a human readable representation.

    :param datetime_obj: the datetime object that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    now = datetime.datetime.strptime(resource.get('current_server_time'), DATETIME_FORMAT)

    if datetime_obj:  # It can be None for certain dates
        return timeago.format(datetime.datetime.strptime(datetime_obj, DATETIME_FORMAT), now)


def _map_job_status_to_human_representation(status, resource, token):
    """
    Map an Job Status type code (e.g., 1, 2) to a human readable name.

    :param status: integer with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    for status_name, id in JOB_STATUSES.items():
        if id == status:
            return status_name


def _map_instance_status_to_human_representation(status, resource, token):
    """
    Map an Instance status code (e.g., 1, 2) to a human readable name.

    :param status: integer with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    for status_name, id in INSTANCE_STATUSES.items():
        if id == status:
            return status_name


def _map_instance_type_to_human_readable(type, resource, token):
    """
    Map an Instance type code (e.g., 1, 2) to a human readable name.

    :param type: integer with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    for type_name, id in INSTANCE_TYPES.items():
        if id == type:
            return type_name


def _map_non_formatted_money_to_version_with_currency(cost, resource, token):
    """
    Map a non formatted money str (e.g., 0.001) to a version with currency (e.g., $0.001).

    :param cost: float with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    return '$%.3f' % cost


def _map_duration_to_human_readable(duration, resource, token):
    """
    Map duration in seconds (e.g., 5) into a human readable representation (e.g., 1 second/s).

    :param duration: integer with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    if duration:
        return '{} second/s'.format(duration)


def _map_boolean_to_human_readable(boolean, resource, token):
    """
    Map a boolean into a human readable representation (Yes/No).

    :param boolean: boolean with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    if boolean:
        return 'Yes'
    else:
        return 'No'

