import os

from tests.constants import Image, Message
from tests.test_utils import TestWrapper, TestUtils


# Workflow
def test_user_creates_a_function_with_code_successfully():
    code = 'def handler(event): print("Hello World {}".format(event[0])); return 42 + int(event[0])'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], code=code)

    TestWrapper.check_list_functions_output(
        expected_uuid=[function_uuid],
        expected_name=[function_name],
        expected_image=[Image.WEB_CRAWLING_PYTHON36['path']],
        expected_num_runs=['0'],
        expected_num_functions=1
    )

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


def test_user_creates_a_function_with_file_successfully():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

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
def test_user_get_validation_error_when_creating_a_function_while_being_logged_out():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    TestWrapper.create_function_unsuccessfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file, error_code=1,
        msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields
def test_user_get_validation_error_when_creating_a_function_with_missing_name():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_function_unsuccessfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file, error_code=2,
        msg='Missing option "--name"')

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_creating_a_function_with_missing_image_uuid():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_function_unsuccessfully(
        name=TestUtils.generate_random_seed(), file=file, error_code=2,
        msg='Missing option "--image-uuid"')

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_creating_a_function_with_missing_both_code_and_file():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_function_unsuccessfully(
        name=TestUtils.generate_random_seed(), image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], error_code=2,
        msg='Either "file" or "code" parameters need to be provided')

    TestWrapper.delete_account_successfully()


# Invalid Fields
def test_user_get_validation_error_when_creating_a_function_with_invalid_code():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_function_unsuccessfully(
        name=TestUtils.generate_random_seed(), image_uuid=Image.STANDARD_NODE8['uuid'], file=file, error_code=1,
        msg='needs to have the following signature')

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_creating_a_function_with_invalid_image_uuid():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_function_unsuccessfully(
        name=TestUtils.generate_random_seed(), image_uuid='blabla', file=file, error_code=2,
        msg='Invalid value for "--image-uuid"')

    TestWrapper.delete_account_successfully()
