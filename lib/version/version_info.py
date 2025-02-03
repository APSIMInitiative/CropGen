

from lib.models.common.model import Model

class VersionInfo(Model):
    def __init__(self, version):
        self.version = version

    @staticmethod
    def from_file_contents(file_contents):
        return VersionInfo(file_contents)
