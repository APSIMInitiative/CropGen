import logging
import os

from typing import Dict, Any, Type, TypeVar

T = TypeVar('T')

class EnvironmentVariablesProvider:
    WEB_SERVER_PORT_NUMBER = "WEB_SERVER_PORT_NUMBER"
    JOBS_SERVER = "JobsServer"
    HPC_ID = "HPC_ID"
    WORKER_ID = "WORKER_ID"
    UPDATE_FREQUENCY = "UPDATE_FREQUENCY"
    PROXY_IP_FILE = "PROXY_IP_FILE"
    RELAY_IP_FILE = "RELAY_IP_FILE"
    HPC_ROOT_DIR = "HPC_ROOT_DIR"
    CGM_RELAY_SOCKET_SERVICE_PORT = "CGM_RELAY_SOCKET_SERVICE_PORT"
    CGM_RELAY_PUSH_PORT = "CGM_RELAY_PUSH_PORT"
    CGM_RELAY_PULL_PORT = "CGM_RELAY_PULL_PORT"
    TOTAL_CLIENTS = "TOTAL_CLIENTS"
    

    def __init__(self):
        self._env_variable_values: Dict[str, Any] = self.create_env_var_mapping()
        self.load_environment_variables()


    def get_web_server_port_number(self) -> int:
        return self.get_variable(int, self.WEB_SERVER_PORT_NUMBER)
    

    def get_jobs_server_address(self) -> str:
        return self.get_variable(str, self.JOBS_SERVER).strip()
    

    def get_hpc_id(self) -> str:
        return self.get_variable(str, self.HPC_ID).strip()
    

    def get_worker_id(self) -> str:
        return self.get_variable(str, self.WORKER_ID).strip()
    

    def get_update_freq(self) -> int:
        return self.get_variable(int, self.UPDATE_FREQUENCY)
    

    def get_proxy_ip_file(self) -> str:
        return self.get_variable(str, self.PROXY_IP_FILE).strip()
    

    def get_relay_ip_file(self) -> str:
        return self.get_variable(str, self.RELAY_IP_FILE).strip()
    

    def get_hpc_root_dir(self) -> str:
        return self.get_variable(str, self.HPC_ROOT_DIR).strip()
    
    
    def get_cgm_relay_socket_service_port(self) -> int:
        return self.get_variable(int, self.CGM_RELAY_SOCKET_SERVICE_PORT)
    
    
    def get_cgm_relay_push_port(self) -> int:
        return self.get_variable(int, self.CGM_RELAY_PUSH_PORT)
    
    
    def get_cgm_relay_pull_port(self) -> int:
        return self.get_variable(int, self.CGM_RELAY_PULL_PORT)
    
    
    def get_total_clients(self) -> int:
        return self.get_variable(int, self.TOTAL_CLIENTS)
    

    def get_variable(self, var_type: Type[T], name: str) -> T:
        if name not in self._env_variable_values:
            raise ValueError(f"Unknown environment variable: {name}")

        value = self._env_variable_values[name]
        try:
            return var_type(value)
        except ValueError:
            logging.error(f"Failed to convert environment variable '{name}' to type '{var_type}'")
            raise


    def load_environment_variables(self):
        for name in self._env_variable_values.keys():
            env_var_value = os.getenv(name)
            if env_var_value is not None:
                logging.info(f"Found override env var: '{name}'. Setting value to '{env_var_value}'")
                self._env_variable_values[name] = env_var_value


    @staticmethod
    def create_env_var_mapping() -> Dict[str, Any]:
        return {
            EnvironmentVariablesProvider.WEB_SERVER_PORT_NUMBER: 80,
            EnvironmentVariablesProvider.JOBS_SERVER: "",
            EnvironmentVariablesProvider.HPC_ID: "debug",
            EnvironmentVariablesProvider.WORKER_ID: 0,
            EnvironmentVariablesProvider.UPDATE_FREQUENCY: 1,
            EnvironmentVariablesProvider.PROXY_IP_FILE: "",
            EnvironmentVariablesProvider.RELAY_IP_FILE: "",
            EnvironmentVariablesProvider.HPC_ROOT_DIR: "",
            EnvironmentVariablesProvider.CGM_RELAY_SOCKET_SERVICE_PORT: 5555,
            EnvironmentVariablesProvider.CGM_RELAY_PUSH_PORT: 5557,
            EnvironmentVariablesProvider.CGM_RELAY_PULL_PORT: 5558,
            EnvironmentVariablesProvider.TOTAL_CLIENTS: 0,
        }
