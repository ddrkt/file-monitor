import requests
import os
import json


class APIClient:
    DEFAULT_API_HOST = 'http://127.0.0.1:5000/'
    CONFIG_FILE_NAME = 'config.json'

    def __init__(self):
        self._config = dict()
        self.read_config()

    def create_config_file(self):
        if not os.path.exists(self.CONFIG_FILE_NAME):
            f = open(self.CONFIG_FILE_NAME, 'w')
            f.write('{}')
            f.close()

    def get_config_val(self, key):
        return self._config.get(key)

    def read_config(self):
        self.create_config_file()

        with open(self.CONFIG_FILE_NAME, 'r') as config_file:
            try:
                data = json.load(config_file)
                self._config = data
            except json.decoder.JSONDecodeError:
                data = {}

            if 'api_host' not in data:
                data['api_host'] = self.DEFAULT_API_HOST
            # Immediately update host to request license if required
            self._config['api_host'] = data['api_host']

            if not ('license_key' in data and 'license_id' in data):
                license_id, license_key = self.request_new_license()
                data['license_key'] = license_key
                data['license_id'] = license_id
                self.load_license(license_key, license_id)

            if 'viewer_token' not in data:
                data['viewer_token'] = self.request_view_token()

            self._config = data
        self.write_config()

    def write_config(self):
        self.create_config_file()
        with open(self.CONFIG_FILE_NAME, 'w') as config_file:
            json.dump(self._config, config_file)

    def load_license(self, license_key, license_id):
        self._config['license_key'] = license_key
        self._config['license_id'] = license_id

    def get_endpoint_url(self, path, pk=None):
        endpoint = f'{self.get_config_val("api_host")}{path}'
        if pk:
            endpoint = f'{endpoint}/{pk}'
        return endpoint

    def get_license_header(self):
        return {
            'license_key': self.get_config_val('license_key'),
            'license_id': str(self.get_config_val('license_id'))
        }

    def send_request(self, request_type, endpoint, data=None):
        if data is None:
            data = dict()
        return getattr(requests, request_type)(endpoint, json=data, headers=self.get_license_header())

    def request_new_license(self):
        response = self.send_request(
            'post',
            self.get_endpoint_url('licenses')
        ).json()
        return response.get('id'), response.get('token')

    def request_view_token(self):
        response = self.send_request(
            'post',
            self.get_endpoint_url('tokens')
        ).json()
        return response.get('token')

    def get_active_files(self):
        response = self.send_request(
            'get',
            self.get_endpoint_url('files')
        )
        return response.json()

    def add_file(self, file_path):
        response = self.send_request(
            'post',
            self.get_endpoint_url('files'),
            {'file_path': file_path}
        )
        return response.json()

    def change_file_status(self, file_id, new_status):
        response = self.send_request(
            'patch',
            self.get_endpoint_url('files', file_id),
            {'status': new_status}
        )
        return response.json()

    def add_file_stats(self, file_id, stats):
        # If status == False it means file was not found
        if not stats:
            self.change_file_status(file_id, 'Unavailable')
            return False

        response = self.send_request(
            'post',
            self.get_endpoint_url('file_stats'),
            {'file_id': file_id, **stats}
        )
        return response.json()

    def get_report(self, period):
        response = self.send_request(
            'post',
            self.get_endpoint_url('reports'),
            period
        )
        return response.json()
