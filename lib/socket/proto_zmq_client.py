import logging
import google.protobuf.any_pb2 as any_pb2

from lib.socket.zmq_client import ZMQClient
import lib.proto.proto_paths
import CgmMessage_pb2

class ProtoZMQClient():
    
    def __init__(self, config, host_address, port):
        self.config = config
        self.zmq_client = ZMQClient(config, host_address, port)


    def send_proto_message(
        self, 
        proto_request
    ):          
        cgm_message = self.wrap_proto(proto_request)
        data = cgm_message.SerializeToString()
        raw_response = self.zmq_client.send(data)
        response = self.process_response_message(raw_response, proto_request.get_response_type())
        return response


    def process_response_message(self, raw_response, response_type):
        response_cgm_message = CgmMessage_pb2.CgmMsg()
        response_cgm_message.ParseFromString(raw_response)
        response = self.unwrap_proto(response_cgm_message, response_type.get_proto_type())
        converted_response = response_type.from_proto(response)
        return converted_response


    def wrap_proto(self, proto_request):
        proto = proto_request.to_proto()
        name = proto_request.get_type_name()
        cgm_message = CgmMessage_pb2.CgmMsg()
        cgm_message.name = name
        any_message = any_pb2.Any()
        any_message.Pack(proto)
        cgm_message.body.CopyFrom(any_message)
        return cgm_message


    def unwrap_proto(self, cgm_message: CgmMessage_pb2.CgmMsg, response_type: type):
        if not isinstance(cgm_message, CgmMessage_pb2.CgmMsg):
            raise TypeError("Expected a CgmMessage_pb2.CgmMsg instance.")
        
        any_message = cgm_message.body
        message = response_type()
        
        if not any_message.Unpack(message):
            raise ValueError("Failed to unpack message.")

        return message
    

    def close(self):
        self.zmq_client.close()