from stockscanner.persistence.dao import DAO, FileSystemDAO


def get_index_dao(db) -> DAO:
    if db == "fs":
        return FileSystemDAO()
