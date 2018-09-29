import os

from tests.constants import Image, Message
from tests.test_utils import TestUtils, TestWrapper


# Workflow

def test_delete_function_successfully():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    function_uuid, function_name = TestWrapper.create_function_successfully(Image.WEB_CRAWLING_PYTHON36['uuid'],
                                                                            file=file)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_get_validation_error_when_deleting_a_function_while_being_logged_out():
    TestWrapper.delete_function_unsuccessfully(
        uuid=TestUtils.generate_random_seed(), error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields
def test_user_get_validation_error_when_deleting_a_function_with_missing_uuid():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_function_unsuccessfully(error_code=2, msg='Missing option "--uuid"')

    TestWrapper.delete_account_successfully()


# Invalid Fields
def test_user_get_validation_error_when_deleting_a_function_with_invalid_uuid():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_function_unsuccessfully(
        uuid=TestUtils.generate_random_seed(), error_code=2, msg='Invalid value for "--uuid"')

    TestWrapper.delete_account_successfully()
