from abc import ABC, abstractmethod

from stockscanner.utils import FileUtils


class DAO(ABC):
    @abstractmethod
    def schema_exists(self):
        pass

    @abstractmethod
    def save(self, entry):
        pass


class FileSystemDAO(DAO):
    # overriding abstract method
    def __init__(self):
        self.file_name = "data.csv"

    def schema_exists(self):
        return FileUtils.file_exists(self.file_name)

    def save(self, entry):
        FileUtils.append_to_file(self.file_name, entry);
        # TODO
