from stockscanner.persistence.dao import IndexDAO, IndexFileSystemDB


def get_index_dao(db) -> IndexDAO:
    if db == "fs":
        return IndexFileSystemDB()
