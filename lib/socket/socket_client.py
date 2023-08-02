import logging
import socket

from lib.socket.socket_client_base import SocketClientBase
from lib.models.run.error_message import ErrorMessage

#
# A socket client.
#
class SocketClient (SocketClientBase):
    #
    # Constructor
    #
    def __init__(
        self, 
        config, 
        family=socket.AF_INET, 
        type=socket.SOCK_STREAM, 
        protocol=0
    ):
        super().__init__(config)
        self.socket = socket.socket(family, type, protocol)

        if self.config.max_socket_receive_size:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.config.max_socket_receive_size)

    #
    # Connects
    #
    def connect(self, host, port):
        try:
            self.socket.connect((host, port))
            self.set_timeout(self.config.socket_timeout_seconds)
        except ConnectionRefusedError:
            logging.error("Connection refused: Failed to connect to %s:%s", host, port)
            raise
        except socket.error as e:
            logging.error("Socket connection error: %s", str(e))
            raise

    #
    # Closes the socket connection.
    #
    def close(self):
        self.socket.close()

    #
    # Sets the timeout
    #
    def set_timeout(self, timeout_seconds):
        try:
            if timeout_seconds > 0:
                self.socket.settimeout(timeout_seconds)
            else:
                # Set the socket timeout to never expire
                self.socket.settimeout(None)
        except Exception as e:
            logging.error("Socket timeout error: %s", str(e))
            raise

    #
    # Writes data
    #
    def write_text(self, message):
        prepare_data = super().prepare_data_for_write(message)
        try:
            self.socket.sendall(prepare_data.message_size_byte_array)
            self.socket.sendall(prepare_data.encoded_data)
        except Exception as e:
            logging.error("Socket write error: %s", str(e))
            raise

    #
    # Writes a serialised error message.
    #
    def write_error(self, errors):
        error_message = ErrorMessage(errors) 
        self.write_text(error_message)

    #
    # Reads data
    #
    def read_text(self):
        try:
            message_size_bytes = self.read_message_size_int()
            logging.debug("%s - Received message size: '%d' bytes", self.__class__.__name__, message_size_bytes)
            message_data = self.read_data(message_size_bytes)
            return super().create_message_wrapper(message_data)
        except Exception as e:
            logging.error("Socket read error: %s", str(e))


    #
    # Read the message size which is sent before the message itself.
    #    
    def read_message_size_int(self):
        # Read the message size
        data = self.read_data(self.config.socket_data_num_bytes_buffer_size)

        # Convert to an integer
        try:
            received_int = int.from_bytes(data, byteorder=self.config.socket_data_endianness)
        except Exception as e:
            logging.error("Error converting message size to integer: %s", str(e))
            return None

        return received_int

    #
    # Reads the data for the specified byte size.
    #    
    def read_data(self, bytes_to_receive):
        data = b''

        while len(data) < bytes_to_receive:
            try:
                chunk = self.socket.recv(bytes_to_receive - len(data))
            except socket.timeout:
                # Handle timeout (data not available)
                logging.warning(
                    "%s - Read timeout. Expected %d bytes, received %d bytes. Retrying...",
                    __class__.__name__, bytes_to_receive, len(data)
                )
                # Retry.
                continue

            if not chunk:
                # Connection closed prematurely
                logging.error(
                    "%s - Connection closed prematurely. Expected %d bytes, received %d bytes.",
                    __class__.__name__, bytes_to_receive, len(data)
                )
                return b''

            data += chunk

        logging.debug("%s - Finished reading message '%d' Bytes", __class__.__name__, bytes_to_receive)

        return data