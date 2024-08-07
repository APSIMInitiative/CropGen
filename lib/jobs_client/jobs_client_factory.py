import requests

from lib.jobs_client.jobs_client_local import JobsClientLocal
from lib.jobs_client.jobs_client_server import JobsClientServer

class JobsClientFactory():
    @staticmethod
    def create(config, environment_variables_provider):
        if environment_variables_provider.get_jobs_server_address():
            return JobsClientServer(requests.Session(), environment_variables_provider)
        else:
            return JobsClientLocal(config, environment_variables_provider)
