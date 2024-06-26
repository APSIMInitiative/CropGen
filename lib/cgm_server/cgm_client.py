import logging

from lib.utils.constants import Constants
from lib.socket.socket_client import SocketClient
from lib.socket.socket_client_singleton import SocketClientSingleton
from lib.socket.socket_client_base import ReadMessageData
from lib.utils.date_time_helper import DateTimeHelper

#
# The real CGM Client
#
class CGMClient:
    #
    # Constructor
    #
    def __init__(self, host, port, config):
        self.host = host
        self.port = port
        self.config = config
        SocketClientSingleton(SocketClient(config))

    #
    # Tests whether we can connect to the CGM server over our socket.
    #
    def test_cgm_connection(self):
        try:
            logging.info("Testing CGM Connection")
            SocketClientSingleton.get_instance().connect(self.host, self.port)
            logging.info("CGM Connection OK")
            return True
        except Exception:
            logging.exception("CGM Connection NOT OK")
            return False

    #
    # Handles constructing a new socket connection to the CGM, sending the
    # message and returning the raw response.
    #
    def call_cgm(self, message):
        errors = []

        try:
            logging.info("Calling CGM with message: '%s'.", message.get_type_name())
            logging.debug("Message data: %s", message.to_json(self.config.PrettyPrintJsonInLogs))
            return self.perform_call_cgm(message)
        
        except Exception as exception:
            error = f"{Constants.CGM_SERVER_EXCEPTION} ({self.host}:{self.port}) - {exception}"
            logging.error(error)
            errors.append(error)

        return ReadMessageData(errors, None)
    
    #
    # Handles constructing a new socket connection to the CGM, sending the
    # message and returning the raw response.
    #
    def perform_call_cgm(self, message):
        request_start_time = DateTimeHelper.get_date_time()

        SocketClientSingleton.get_instance().write_text(message)
        data = SocketClientSingleton.get_instance().read_text()

        if data.is_disconnect_message:
            logging.warning("Received disconnected response from: %s request. Time taken: %s",
                message.get_type_name(),
                DateTimeHelper.get_elapsed_time_since(request_start_time),
            )
        else:
            logging.info("Received response from: %s request. Time taken: %s",
                message.get_type_name(),
                DateTimeHelper.get_elapsed_time_since(request_start_time),
            )

        return data

    #
    # Validates the read message data and captures all of the errors.
    # If this returns true, the object is safe to use.
    #
    def validate_cgm_call(self, read_message_data, request, response_name):
        if not read_message_data:
            return [Constants.CGM_SERVER_NO_DATA_READ]

        # This is to handle any exceptions thrown from the Python code.
        if read_message_data.errors:
            return read_message_data.errors
        
        # Has the socket been disconnected whilst we were waiting for a response.
        if read_message_data.is_disconnect_message:
            return [
                f'{Constants.CGM_SERVER_DISCONNECTED_WHILE_WAITING_FOR_RESPONSE}: {response_name}'
            ]

        # If any of the message data is null.
        if (
            not read_message_data.message_wrapper
            or not read_message_data.message_wrapper.TypeName
            or not read_message_data.message_wrapper.TypeBody
        ):
            return [Constants.CGM_SERVER_INVALID_RESPONSE]

        # This is to handle an error response.
        if read_message_data.message_wrapper.TypeName == Constants.CGM_SERVER_TYPE_NAME_EXCEPTION_RESPONSE:
            # If there is an exception thrown in CGM, it is useful to log out the request that may have caused it.
            # Log request name and body first, followed by the exception.
            return [
                f'{request.get_type_name()}: {request.to_json()}',
                f'{Constants.CGM_SERVER_ERROR_RESPONSE}: {read_message_data.message_wrapper.TypeBody}'
            ]

        return []
