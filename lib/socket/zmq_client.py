import zmq
import logging
import google.protobuf.any_pb2 as any_pb2
from google.protobuf.message import Message

from lib.utils.constants import Constants
import lib.proto.proto_paths
import CgmMessage_pb2
import InitApsimResponse_pb2

class ZMQClient:
    
    def __init__(self, config, cgm_relay_address: str):
        self.config = config
        self.cgm_relay_address = cgm_relay_address
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self._connect()
        

    def _connect(self):
        try:
            connection_str = self._generate_connection_string()
            self.socket.connect(connection_str)
            logging.info(f"Connection to: {connection_str} successful.")
        except zmq.ZMQError as e:
            logging.exception(f"Connection to {connection_str} failed: {e}")


    def _generate_connection_string(self) -> str:
        address = self.cgm_relay_address if self.config.IS_RUNNING_IN_DOCKER else "localhost"
        return f"tcp://{address}:{Constants.CGM_RELAY_SOCKET_SERVICE_PORT}"


    def send_proto_message(self, proto, name: str):
        try:
            cgm_message = self.wrap_proto(proto, name)
            data = cgm_message.SerializeToString()
            self.socket.send(data)
            response = self.receive_proto_message()
            return response
            
        except zmq.ZMQError as e:
            print(f"Failed to send message: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


    def receive_proto_message(self):
        response_data = self.socket.recv()
        response_cgm_message = CgmMessage_pb2.CgmMsg()
        response_cgm_message.ParseFromString(response_data)
        response_proto = self.unwrap_proto(response_cgm_message, InitApsimResponse_pb2.InitApsimResponseProto)
        return response_proto


    def wrap_proto(self, proto, name: str) -> CgmMessage_pb2.CgmMsg:
        cgm_message = CgmMessage_pb2.CgmMsg()
        cgm_message.name = name
        any_message = any_pb2.Any()
        any_message.Pack(proto)
        cgm_message.body.CopyFrom(any_message)
        return cgm_message


    def unwrap_proto(
        self, 
        cgm_message: CgmMessage_pb2.CgmMsg,
        message_type: type
    ) -> Message:

        if not isinstance(cgm_message, CgmMessage_pb2.CgmMsg):
            raise TypeError("Expected a CgmMessage_pb2.CgmMsg instance.")
        
        any_message = cgm_message.body
        message = message_type()
        
        if not any_message.Unpack(message):
            raise ValueError("Failed to unpack message.")
        
        return any_message
    

    def close(self):
        if self.socket:
            self.socket.close()
        self.context.term()