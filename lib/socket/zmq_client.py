import zmq
import logging

class ZMQClient:
    
    def __init__(self, config, host_address, port):
        self.config = config
        self.host_address = host_address
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.connect()
        

    def connect(self):
        try:
            connection_str = self._generate_connection_string()
            self.socket.connect(connection_str)
            logging.info(f"Connection to: {connection_str} successful.")
        except zmq.ZMQError as e:
            logging.exception(f"Connection to {connection_str} failed: {e}")


    def _generate_connection_string(self) -> str:
        address = self.host_address if self.config.IS_RUNNING_IN_CONTAINER else "localhost"
        return f"tcp://{address}:{self.port}"


    def send(self, data):
        try:
            self.socket.send(data)
            response = self.socket.recv()
            return response
            
        except zmq.ZMQError as e:
            logging.exception(f"Failed to send message: {e}")
        except Exception as e:
            logging.exception(f"An error occurred: {e}")


    def close(self):
        if self.socket: self.socket.close()
        self.context.term()