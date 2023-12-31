from typing import Optional

from pocketbase import PocketBase  # Client also works the same
from pocketbase.services.record_service import RecordAuthResponse
from pocketbase.utils import ClientResponseError

COL_USERS = 'users'
COL_CREDITS = 'credits'
COL_FEATURES = 'features'


def __users(pb: PocketBase):
    return pb.collection(COL_USERS)


def __features(pb: PocketBase):
    return pb.collection(COL_FEATURES)


def __credits(pb: PocketBase):
    return pb.collection(COL_CREDITS)


def verify_email(pb: PocketBase, email: str):
    __users(pb).requestVerification(email)


def reset_password(pb: PocketBase, email: str):
    __users(pb).requestPasswordReset(email)


def get_credits(pb: PocketBase) -> int:
    print(pb.auth_store.model.id)
    result = __credits(pb).get_one(
        pb.auth_store.model.id
    ).__dict__
    return result['amount_cred']


def get_active_features(pb: PocketBase) -> [str]:
    result = __users(pb).get_one(
        pb.auth_store.model.id
    ).__dict__
    feature_ids = result['active_features']
    result = []
    for fid in feature_ids:
        feat = __features(pb).get_one(fid).__dict__
        result.append(feat)
    print(result)
    return result


def login(pb: PocketBase, email: str, password: str) -> Optional[RecordAuthResponse]:
    try:
        return __users(pb).auth_with_password(email, password)
    except ClientResponseError:
        return None
