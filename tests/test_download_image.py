from tests.constants import InstanceType, Image, Message
from tests.test_utils import TestWrapper


# Workflows

def test_user_downloads_an_image_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.STANDARD,
        price_per_hour=1.5,
        max_num_parallel_jobs=3
    )

    TestWrapper.download_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.clean_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)

def test_user_wants_to_download_an_image_without_having_an_instance():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.download_image_unsuccessfully(
        registry_path=Image.WEB_CRAWLING_PYTHON36['path'], error_code=1, msg=Message.NO_INSTANCE_FOUND)

    TestWrapper.delete_account_successfully(uuid=account_uuid)

def test_user_gets_validation_error_trying_to_download_a_gpu_image_in_a_non_gpu_instance():
    pass

# Logged out
def test_user_gets_validation_error_when_trying_to_download_an_image_while_being_logged_out():
    TestWrapper.download_image_unsuccessfully(
        registry_path=Image.WEB_CRAWLING_PYTHON36['path'], error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)

# Missing fields
def test_user_gets_validation_error_when_downloading_an_image_without_registry_path():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.download_image_unsuccessfully(error_code=2, msg='Missing option "--registry_path"')

    TestWrapper.delete_account_successfully(uuid=account_uuid)


# Invalid fields
