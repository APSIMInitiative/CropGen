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
    def __init__(self, config):
        super().__init__(config)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #
    # Connects
    #
    def connect(self, host, port):
        try:
            self.socket.connect((host, port))
        except ConnectionRefusedError:
            logging.error("Connection refused: Failed to connect to %s:%s", host, port)
            raise

    #
    # Sets the timeout
    #
    def set_timeout(self, timeout_seconds):
        # Only apply the timeout if one has been configured and it is greater than the default of 0.
        if timeout_seconds > 0:
            try:
                self.socket.settimeout(timeout_seconds)
            except socket.error as e:
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
        except socket.error as e:
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
            # Read the message size byte array that proceeds each message.
            message_size_byte_array = self.socket.recv(self.config.socket_data_num_bytes_buffer_size)
            # Convert it to an integer and then use this to read the message itself
            # with the known size.
            message_size_bytes = int.from_bytes(message_size_byte_array, self.config.socket_data_endianness)
            logging.info("%s - Received message size: '%d' bytes", self.__class__.__name__, message_size_bytes)
            message_data = self.read_data(message_size_bytes)
            return super().create_message_wrapper(message_data)
        except socket.error as e:
            logging.error("Socket read error: %s", str(e))
            raise

    #
    # Reads the data
    #
    def read_data(self, message_size_bytes):
        # Initialise our buffer
        message_data = bytearray(message_size_bytes)
        # Now iterate calling receive each time until we've read all of the data.
        buffer_pos = 0
        while buffer_pos < message_size_bytes:
            read_data = self.socket.recv(self.config.socket_receive_buffer_size)
            read_data_length = len(read_data)
            message_data[buffer_pos: buffer_pos + read_data_length] = read_data
            buffer_pos += read_data_length

        logging.debug("%s - Finished reading message. Message Size Bytes: '%d'", __class__.__name__, message_size_bytes)

        return message_data
