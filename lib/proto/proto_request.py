from abc import ABC, abstractmethod

class ProtoRequest(ABC):

    @abstractmethod
    def to_proto(self):
        """Converts the request object to a protobuf message."""
        pass

    @staticmethod
    @abstractmethod
    def get_response_type() -> type:
        """Returns the response type associated with this request."""
        pass

    @abstractmethod
    def get_type_name(self):
        """Returns the type name of the implementing class."""
        pass