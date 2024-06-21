from abc import ABC, abstractmethod
import InitApsimResponse_pb2

class ProtoResponse(ABC):

    @staticmethod
    @abstractmethod
    def from_proto(proto):
        """Converts from a protobuf message to the implementing class."""
        pass

    @staticmethod
    @abstractmethod
    def get_proto_type() -> type:
        """Returns the type of the protobuf message associated with the implementing class."""
        pass

    @abstractmethod
    def get_type_name(self):
        """Returns the type name of the implementing class."""
        pass