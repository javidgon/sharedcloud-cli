import os

from tests.constants import Image, Message
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_updates_a_function_with_code_successfully():
    code = 'def handler(event): print("Hello World {}".format(event[0])); return 42 + int(event[0])'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], code=code)

    TestWrapper.update_function_successfully(
        uuid=function_uuid, image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], code=code)

    TestWrapper.check_list_functions_output(
        expected_uuid=[function_uuid],
        expected_name=[function_name],
        expected_image=[Image.WEB_CRAWLING_PYTHON36['path']],
        expected_num_runs=['0'],
        expected_num_functions=1
    )

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


def test_user_updates_a_function_with_file_successfully():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    TestWrapper.update_function_successfully(
        uuid=function_uuid, image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    TestWrapper.check_list_functions_output(
        expected_uuid=[function_uuid],
        expected_name=[function_name],
        expected_image=[Image.WEB_CRAWLING_PYTHON36['path']],
        expected_num_runs=['0'],
        expected_num_functions=1
    )

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_get_validation_error_when_updating_a_function_while_being_logged_out():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    TestWrapper.update_function_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file, error_code=1,
        msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields
def test_user_get_validation_error_when_updating_a_function_with_missing_uuid():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_function_unsuccessfully(
        name=TestUtils.generate_random_seed(), file=file, error_code=2,
        msg='Missing option "--uuid"')

    TestWrapper.delete_account_successfully()

def test_user_doesnt_get_validation_error_when_updating_a_function_with_missing_image_uuid_because_it_was_already_set():
    pass

# Invalid Fields

def test_user_gets_validation_error_when_updating_a_function_with_code_because_the_previous_set_image_doesnt_support_it():
    pass

def test_user_get_validation_error_when_updating_an_unknown_function():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_function_unsuccessfully(
        uuid=TestUtils.generate_uuid(), name=TestUtils.generate_random_seed(),
        image_uuid=Image.STANDARD_NODE8['uuid'], file=file, error_code=1,
        msg=Message.NO_RESOURCE_FOUND)

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_updating_a_function_with_invalid_code():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    TestWrapper.update_function_unsuccessfully(
        uuid=function_uuid, name=TestUtils.generate_random_seed(), image_uuid=Image.STANDARD_NODE8['uuid'], file=file,
        error_code=1,
        msg='needs to have the following signature')

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_updating_a_function_with_invalid_image_uuid():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_function_unsuccessfully(
        uuid=account_uuid, name=TestUtils.generate_random_seed(), image_uuid='blabla', file=file, error_code=2,
        msg='Invalid value for "--image-uuid"')

    TestWrapper.delete_account_successfully()
