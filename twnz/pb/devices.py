import subprocess

from pocketbase import PocketBase  # Client also works the same

COL_USERS = 'users'
COL_CREDITS = 'credits'
COL_DEVICES = 'devices'

K_REGISTERED = 'registered'
K_AUTHORIZED = 'authorized'
K_ALREADY_REGISTERED = 'alreadyRegistered'
K_SUCCESS = 'success'


def __get_uuid() -> str:
    return subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()


def __check_device(pb: PocketBase, user_id: str, device_id: str) -> dict:
    # {'authorized': True, 'registered': True}
    return pb.send(f"/checkDevice/{user_id}/{device_id}", {
        'method': 'GET'
    })


def __register_device(pb: PocketBase, user_id: str, device_id: str) -> dict:
    # {'alreadyRegistered': True, 'success': False}
    return pb.send(f"/registerDevice/{user_id}/{device_id}", {
        'method': 'GET'
    })


def check_already_has_a_registered_device(pb: PocketBase, user_id: str) -> bool:
    return __check_device(pb, user_id, __get_uuid())[K_REGISTERED]


def check_device_authorized(pb: PocketBase, user_id: str) -> bool:
    return __check_device(pb, user_id, __get_uuid())[K_AUTHORIZED]


def register_new_device(pb: PocketBase, user_id: str) -> bool:
    return __register_device(pb, user_id, __get_uuid())[K_SUCCESS]


def get_user_id_after_logged_in(pb: PocketBase) -> str:
    return pb.auth_store.model.id