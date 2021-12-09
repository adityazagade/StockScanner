from stockscanner.utils import FileUtils


class Config:
    @classmethod
    def load_config(cls):
        return FileUtils.read_json_file("config.json")
