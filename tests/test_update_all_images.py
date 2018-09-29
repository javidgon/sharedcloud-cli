from tests.constants import InstanceType, Image, Message
from tests.test_utils import TestWrapper


# Workflow
def test_user_updates_all_images_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3
    )

    TestWrapper.download_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.update_all_images_successfully()

    TestWrapper.clean_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_user_wants_to_update_all_images_without_having_an_instance():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)
    TestWrapper.update_all_images_unsuccessfully(error_code=1, msg=Message.NO_INSTANCE_FOUND)

    TestWrapper.delete_account_successfully()


def test_user_wants_to_update_all_images_without_having_a_downloaded_image():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3
    )

    TestWrapper.update_all_images_unsuccessfully(error_code=0, msg='')

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_gets_validation_error_when_trying_to_update_all_images_while_being_logged_out():
    TestWrapper.update_all_images_unsuccessfully(error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)

# Missing fields


# Invalid fields
