import os


class Config:
    def __init__(self):
        self.FLASK_APP = os.environ.get('FLASK_APP')
        self.FLASK_DEBUG = os.environ.get('FLASK_DEBUG')

