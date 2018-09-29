import os

from tests.constants import Image
from tests.test_utils import TestWrapper


# Workflow

def test_user_sees_the_list_of_functions_successfully():
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


def test_user_sees_the_code_of_a_function_successfully():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    TestWrapper.get_function_code_successfully(uuid=function_uuid, expected_code='time.sleep(10)')

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_gets_validation_error_when_listing_functions_while_being_logged_out():
    TestWrapper.check_list_functions_output(
        expected_logout_warning=True
    )

# Missing fields


# Invalid Fields
