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
    def schema_exists(self):
        return FileUtils.file_exists("data.csv")

    def save(self, entry):
        pass
        # TODO
