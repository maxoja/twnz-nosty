from typing import Optional, List

from pocketbase import PocketBase  # Client also works the same
from pocketbase.services.record_service import RecordAuthResponse
from pocketbase.utils import ClientResponseError

from twnz.pb.models import FeatureModel

COL_USERS = 'users'
COL_CREDITS = 'credits'
COL_FEATURES = 'features'
COL_ANNOUNCEMENTS = 'announcements'


def __users(pb: PocketBase):
    return pb.collection(COL_USERS)


def __features(pb: PocketBase):
    return pb.collection(COL_FEATURES)


def __credits(pb: PocketBase):
    return pb.collection(COL_CREDITS)


def __announcements(pb: PocketBase):
    return pb.collection(COL_ANNOUNCEMENTS)


def verify_email(pb: PocketBase, email: str):
    __users(pb).requestVerification(email)


def reset_password(pb: PocketBase, email: str):
    __users(pb).requestPasswordReset(email)


def get_credits(pb: PocketBase) -> int:
    print(pb.auth_store.model.id)
    result = __credits(pb).get_one(
        pb.auth_store.model.id
    ).__dict__
    return int(result['amount_cred'])


def get_active_features(pb: PocketBase) -> List[FeatureModel]:
    result = __users(pb).get_one(
        pb.auth_store.model.id
    ).__dict__
    feature_ids = result['active_features']
    result = []
    for fid in feature_ids:
        feat = __features(pb).get_one(fid).__dict__
        result.append(FeatureModel.from_json(feat))
    print(result)
    return result


def get_applicable_announcements(pb: PocketBase, this_client_count: int) -> List[str]:
    lst = __announcements(pb).get_list(1, 20,{'filter': f'forCounterBelow > {this_client_count}'})
    result = [i.__dict__['message'] for i in lst.items]
    print(result)
    return result


def login(pb: PocketBase, email: str, password: str) -> Optional[RecordAuthResponse]:
    try:
        return __users(pb).auth_with_password(email, password)
    except ClientResponseError:
        return None
