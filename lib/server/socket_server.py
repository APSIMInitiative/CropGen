import asyncio
import logging

from lib.socket.socket_client import SocketClient
from lib.message_processing.message_processor import MessageProcessor
from lib.models.error_message  import ErrorMessage

#
# A socket server that handles incoming requests from clients.
#
class SocketServer():

    #
    # Constructor
    #
    def __init__(self, config):
        self.config = config

    #
    # Callback which is invoked when a client is connecting to this server.
    #
    def client_connected_callback(self, client_reader, client_writer):
        asyncio.ensure_future(
            self.client_listener(client_reader, client_writer)
        )
    
    #
    # Handles listening to the connected client and processing any messages.
    #
    async def client_listener(self, reader, writer):
        socket_client = SocketClient(self.config, reader, writer)
        client_address = writer.get_extra_info('peername')
        logging.debug('Connected to client %s. Waiting for commands', client_address)

        while True:
            data = await reader.read(self.config.socket_receive_buffer_size)

            if data == b'':
                logging.debug('Client %s disconnected', client_address)
                return
            else:
                message_processor = MessageProcessor(self.config, socket_client)
                await message_processor.process_run_message(data)
