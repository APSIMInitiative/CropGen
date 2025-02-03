from typing import Optional

from lib.utils.date_time_helper import DateTimeHelper
from lib.models.common.model import Model

class GitRepositoryInfo(Model):
    def __init__(
        self,
        repository = "",
        branch = "",
        commit_sha = "",
        last_commit_date = None,
        last_commit_message = "",
        tags = "",
        repository_url = ""
    ):
        self.repository = repository
        self.branch = branch
        self.commit_sha = commit_sha
        self.last_commit_date = last_commit_date
        self.last_commit_message = last_commit_message
        self.tags = tags
        self.repository_url = repository_url


    @classmethod
    def from_csv_line(cls, line: str) -> Optional["GitRepositoryInfo"]:
        expected_fields = 7
        parts = [p.strip() for p in line.split(",", expected_fields)]

        if len(parts) < expected_fields:
            return None

        try:
            last_commit_date = DateTimeHelper.str_to_date(parts[3])
        except ValueError:
            return None

        return cls(
            repository=parts[0],
            branch=parts[1],
            commit_sha=parts[2],
            last_commit_date=last_commit_date,
            last_commit_message=parts[4].strip('"').strip(),
            tags=parts[5].strip('"').strip(),
            repository_url=parts[6].strip('"').strip()
        )
