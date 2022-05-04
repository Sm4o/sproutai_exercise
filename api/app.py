from dataclasses import dataclass
import os
import json
from typing import Dict, List
import sqlite3

from flask import Flask, request
from flask_restful import Api, Resource
import requests 
from dotenv import load_dotenv

from .config import Config

load_dotenv()


app = Flask("blogposts-api")
app.config.from_object(Config())
api = Api(app)


MODERATION_API_URL = os.environ.get('MODERATION_API_URL') 


class DatabaseInterface:
    def __init__(self):
        self.conn = self.get_db_connection() 

    def get_db_connection(self):
        conn = sqlite3.connect(os.environ.get('DB_CONNECTION'))
        conn.row_factory = sqlite3.Row
        return conn
    
    def save_post(self, data: Dict[str, str]) -> None: 
        with self.conn as cursor:
            cursor.execute(
                "INSERT INTO posts (title, content, hasFoulLanguage) VALUES (?, ?, ?)",
                (data['title'], json.dumps(data['paragraphs']), data['hasFoulLanguage'])
            )
            cursor.commit()


class ModerationAPIUnavailable(Exception):
    def __init__(self):
        super().__init__("Moderation API Unavailable")


def split_into_sentences(paragraphs: List[str]) -> List[str]:
    return list(
        filter(
            None, 
            [paragraph.strip() 
            for paragraph in ' '. join(paragraphs).split('.')]
        )
    )


@dataclass
class ModerationInterface:
    data: List[str]

    def has_foul_language(self) -> bool:
        foul_language = False
        fragments = split_into_sentences(self.data['paragraphs']) 
        for sentence in fragments:
            try:
                resp = requests.post(
                    MODERATION_API_URL, 
                    data={"fragment": sentence},
                )
            except:
                raise ModerationAPIUnavailable()
            moderation = resp.json() 
            if moderation['hasFoulLanguage']:
                foul_language = True 
        return foul_language


class BlogPost(Resource):
    def post(self):
        data = request.get_json()
        moderation = ModerationInterface(data)
        try:
            data['hasFoulLanguage'] = moderation.has_foul_language() 
        except ModerationAPIUnavailable:
            data['hasFoulLanguage'] = None 
            app.logger.error("Moderation API Error", exc_info=True)
        
        DatabaseInterface().save_post(data)
        return data 


api.add_resource(BlogPost, "/posts")


if __name__ == "__main__":
    app.run()
