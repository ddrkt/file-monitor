import string
import random
from flask_restful import Resource
from apps.licenses.models import License, ViewToken
from flask import request


class LicenseAuthMixin(object):
    def verify_license(self):
        license_id = request.headers.get('license_id')
        license_key = request.headers.get('license_key')
        if not license_id or not license_key:
            return False
        license_obj = License.query.get(license_id)
        if not license_obj:
            return False
        if not license_obj.verify_token(license_key):
            return False
        return license_id

    def verify_token(self):
        token_key = request.headers.get('token_key')
        if not token_key:
            return False
        for token in ViewToken.query.all():
            if token.verify_token(token_key):
                return token.license_id
        return False

    def verify_license_or_token(self):
        license_id = self.verify_license()
        if license_id:
            return license_id
        token_id = self.verify_token()
        if token_id:
            return token_id
        return False


class TokenResourceMixin(Resource):
    def get(self):
        return dict()

    def post(self):
        return dict()

    @staticmethod
    def generate_token(size=6, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
