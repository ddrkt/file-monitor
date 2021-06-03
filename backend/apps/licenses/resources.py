from mixins import TokenResourceMixin, LicenseAuthMixin
from apps.licenses.models import License, ViewToken
from project import db
from flask_restful import Resource, abort
from flask import jsonify


class LicensesResource(TokenResourceMixin):
    def post(self):
        new_license = License()
        token = self.generate_token(15)
        new_license.token = token
        db.session.add(new_license)
        db.session.commit()
        return {'id': new_license.id, 'token': token}


class TokensResource(LicenseAuthMixin, TokenResourceMixin):
    def post(self):
        license_id = self.verify_license()
        if not license_id:
            abort(403, error_message='License check failed')

        new_token = ViewToken()
        token = self.generate_token(7)
        new_token.token = token
        new_token.license_id = license_id
        db.session.add(new_token)
        db.session.commit()
        return jsonify({'id': new_token.id, 'token': token, 'license_id': new_token.license_id})


class TokenLicenseCheckResource(LicenseAuthMixin, Resource):
    def post(self):
        license_id = self.verify_license_or_token()
        if not license_id:
            return {'token_valid': False, 'license_id': None}
        return {'token_valid': True, 'license_id': license_id}

    def get(self):
        abort(405, error='Method not allowed')


def register_resources(api):
    api.add_resource(LicensesResource, '/licenses')
    api.add_resource(TokensResource, '/tokens')
    api.add_resource(TokenLicenseCheckResource, '/verify_token')
