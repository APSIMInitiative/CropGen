from websocket import create_connection
from lib.socket.socket_client_base import SocketClientBase
from lib.models.error_message import ErrorMessage

#
# A websocket client.
#
class WebSocketClient(SocketClientBase):
    #
    # Constructor
    #
    def __init__(self, url, timeout_seconds):
        self.url = url
        self.timeout_seconds = timeout_seconds
        super().__init__(None)

    #
    # Connect method
    #
    def connect(self):
        self.raw_socket = create_connection(self.url, self.timeout_seconds)
    
    #
    # Connect method
    #
    async def connect_async(self):
        raise NotImplementedError("connect_async not implemented")

    #
    # Send data method
    #
    def send_text(self, data):
        self.raw_socket.send(data)

    #
    # Send data method
    #
    async def send_text_async(self, data):
        raise NotImplementedError("send_text_async not implemented")

    #
    # Send data method
    #
    def send_error(self, errors):
        self.send_text(ErrorMessage(errors).to_json())

    #
    # Send data method
    #
    async def send_error_async(self, errors):
        raise NotImplementedError("send_error_async not implemented")

    #
    # Receive data method
    #
    def receive_text(self):
        return self.raw_socket.recv()

    #
    # Receive data method
    #
    async def receive_text_async(self):
        raise NotImplementedError("receive_text_async not implemented")
