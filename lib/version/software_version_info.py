import logging
import os
from pathlib import Path

from lib.version.version_info import VersionInfo
from lib.version.git_repository_info import GitRepositoryInfo

class SoftwareVersionInfo():    
    VERSION_FILES_DIRECTORY = os.path.join(os.path.dirname(__file__), "..", "..")
    
    def __init__(self) -> None:
        self.version_info_file = os.path.join(self.VERSION_FILES_DIRECTORY, "version.txt")
        self.git_details_file = os.path.join(self.VERSION_FILES_DIRECTORY, "git_details.txt")

        self.version_info = self.parse_application_version()
        self.git_repository_info = self.parse_git_versions()


    def parse_application_version(self):
        if not os.path.exists(self.version_info_file):
            logging.error("Failed to find Version Info File: '%s'", self.version_info_file)
            return None
        
        version_file_contents = Path(self.version_info_file).read_text().strip()
        return VersionInfo.from_file_contents(version_file_contents)


    def parse_git_versions(self):
        if not os.path.exists(self.git_details_file):
            logging.error("Failed to find Git Details File: '%s'", self.git_details_file)
            return None
        
        with open(self.git_details_file, "r") as file:
            return [GitRepositoryInfo.from_csv_line(line) for line in file.readlines()[1:] if line.strip()]


    def to_string(self):
        lines = []
        lines.append("VersionInfo")
        
        if self.version_info is not None:
            lines.append(self.version_info.to_json(True))
        else:
            lines.append("VersionInfo: None")

        lines.append("GitRepositoryInformation")
        
        if self.git_repository_info:
            lines.extend(info.to_json(True) for info in self.git_repository_info if info is not None)
        else:
            lines.append("No Git repository information available.")

        return "\n".join(lines)

    
    @staticmethod
    def get_type_name():
        return __class__.__name__