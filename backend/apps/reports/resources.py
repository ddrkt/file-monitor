from flask import jsonify, request
from apps.reports.backends import ReportBuilder
from mixins import LicenseAuthMixin
from flask_restful import Resource, abort


class ReportsResource(LicenseAuthMixin, Resource):
    def post(self):
        license_id = self.verify_license_or_token()
        if not license_id:
            return abort(403, error='Invalid license')

        period = {}
        if 'days' in request.json:
            period['days'] = int(request.json.get('days'))
        if 'hours' in request.json:
            period['hours'] = int(request.json.get('hours'))

        # If period was not given, than use default period, described in class
        if len(period) == 0:
            period = None

        builder = ReportBuilder()
        report = builder.get_report_qs(license_id, period)
        return jsonify(report)

    def get(self):
        abort(405, error='Method not allowed')


def register_resources(api):
    api.add_resource(ReportsResource, '/reports')
