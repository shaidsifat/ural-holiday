# -*- coding: UTF-8 -*-
# '''=================================================
# @Project: rhizo
# @File   : utils.py
# @IDE    : PyCharm
# @Author : Muhammad Arshad
# @Email  : arshad@hexasoft.io
# @Time   : 11/12/2021 7:03 PM
# @Desc   :
# '''=================================================
import os
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
load_dotenv()


def get_secret(key, default=None):
    secret = os.getenv(key=key, default=default)
    if secret is None:
        raise ImproperlyConfigured(f'Set the {key} secret environment variable')
    return secret


def custom_user_authentication_rule(user):
    return user is not None
