from tests.constants import InstanceType, Image, Message
from tests.test_utils import TestWrapper


# Workflow
def test_user_cleans_an_image_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3
    )
    TestWrapper.download_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.clean_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_user_wants_to_clean_an_image_without_having_an_instance():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.clean_image_unsuccessfully(
        registry_path=Image.WEB_CRAWLING_PYTHON36['path'], error_code=1, msg=Message.NO_INSTANCE_FOUND)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_gets_validation_error_when_trying_to_clean_an_image_while_being_logged_out():
    TestWrapper.clean_image_unsuccessfully(
        registry_path=Image.WEB_CRAWLING_PYTHON36['path'], error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields
def test_user_gets_validation_error_when_cleaning_an_image_without_registry_path():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.clean_image_unsuccessfully(error_code=2, msg='Missing option "--registry-path"')

    TestWrapper.delete_account_successfully()

# Invalid fields
