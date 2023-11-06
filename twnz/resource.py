import pickle
from os import path
from twnz import config


cred_path = path.join(config.RESOURCE_FOLDER, config.CRED_FILE)


def save_cred(email: str, password: str, remember: bool):
    obj = {'email': email, 'password': password, 'remember': remember}
    with open(cred_path, 'wb') as file:
        pickle.dump(obj, file)


def __load_cred() -> dict:
    if not path.isfile(cred_path):
        return {}

    with open(cred_path, 'rb') as file:
        loaded_dict = pickle.load(file)
        print(loaded_dict)
        return loaded_dict


def load_email():
    cred = __load_cred()
    return '' if 'email' not in cred else cred['email']


def load_password():
    cred = __load_cred()
    return '' if 'password' not in cred else cred['password']


def load_remember():
    cred = __load_cred()
    return False if 'remember' not in cred else cred['remember']