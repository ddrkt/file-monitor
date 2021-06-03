from flask import Flask
from flask_cors import CORS
from project import db, migrate, api, serializers
from project.settings import configure_application
from apps.licenses.resources import register_resources as register_license_endpoints
from apps.file_tracking.resources import register_resources as register_file_tracking_endpoints
from apps.reports.resources import register_resources as register_reports_endpoints


def register_api_endpoints(api_app):
    register_license_endpoints(api_app)
    register_file_tracking_endpoints(api_app)
    register_reports_endpoints(api_app)


def create_app():
    application = Flask(
        __name__,
        instance_relative_config=True
    )
    configure_application(application)
    CORS(application)
    db.init_app(application)
    migrate.init_app(application, db)
    serializers.init_app(application)
    register_api_endpoints(api)
    api.init_app(application)
    return application
