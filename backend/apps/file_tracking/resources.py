from project import db
from flask import request
from apps.file_tracking.models import FileStats, File, STAT_ATTRIBUTES
from apps.file_tracking.schemas import file_schema, files_schema, file_stat_schema, file_stats_schema
from flask_restful import Resource, abort
from mixins import LicenseAuthMixin
from apps.reports.backends.builder import ReportBuilder


class FilesResource(LicenseAuthMixin, Resource):
    def get(self):
        license_id = self.verify_license_or_token()
        if not license_id:
            abort(403, error_message='License check failed')
        ReportBuilder().get_report_qs(license_id)

        files = File.query.filter_by(license_id=license_id).filter(File.status.in_(['Active', 'Unavailable'])).all()
        return files_schema.jsonify(files)

    def post(self):
        license_id = self.verify_license()
        if not license_id:
            abort(403, error_message='License check failed')
        file_path = request.json.get('file_path')

        file = File.query.filter_by(file_path=file_path, license_id=license_id).first()
        if file:
            file.status = 'Active'
        else:
            file = File()
            file.file_path = request.json.get('file_path')
            file.license_id = license_id
            file.status = 'Active'
            db.session.add(file)
        db.session.commit()

        return file_schema.jsonify(file)


class FileResource(LicenseAuthMixin, Resource):
    def get(self, file_id):
        if not self.verify_license_or_token():
            abort(403, error_message='License check failed')

        file = File.query.get_or_404(file_id)
        return file_schema.jsonify(file)

    def patch(self, file_id):
        if not self.verify_license():
            abort(403, error_message='License check failed')

        file = File.query.get_or_404(file_id)
        if 'status' in request.json:
            file.status = request.json.get('status')

        db.session.commit()
        return file_schema.jsonify(file)

    def delete(self, file_id):
        if not self.verify_license():
            abort(403, error_message='License check failed')

        file = File.query.get_or_404(file_id)
        db.session.delete(file)
        db.session.commit()
        return '', 204


class FileStatsResource(LicenseAuthMixin, Resource):
    def get(self):
        license_id = self.verify_license_or_token()
        if not license_id:
            abort(403, error_message='License check failed')

        query = FileStats.query.join(File).filter(File.license_id == license_id)
        if 'file_id' in request.args:
            file_id = request.args.get('file_id')
            file = File.query.get(file_id)
            if not file or file.license_id != license_id:
                abort(400, error_message='File not found')
            query.filter_by(file_id=file_id)

        return file_stats_schema.jsonify(query.all())

    def post(self):
        license_id = self.verify_license()
        if not license_id:
            abort(403, error_message='License check failed')

        new_stat_rec = FileStats()
        file_id = request.json.get('file_id')
        file = File.query.get(file_id)
        if file.license_id != int(license_id):
            abort(403, error_message='License check failed')

        new_stat_rec.file_id = file_id
        for stat_attr in STAT_ATTRIBUTES:
            stat_name = stat_attr.get('name')
            if stat_name in request.json:
                setattr(new_stat_rec, stat_name, request.json.get(stat_name))
        db.session.add(new_stat_rec)
        db.session.commit()
        return file_stat_schema.jsonify(new_stat_rec)


def register_resources(api):
    api.add_resource(FilesResource, '/files')
    api.add_resource(FileResource, '/files/<int:file_id>')
    api.add_resource(FileStatsResource, '/file_stats')
