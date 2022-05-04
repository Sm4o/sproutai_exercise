import os
import json

from pytest import fixture

from api.app import app, MODERATION_API_URL
from init_db import create_database


TEST_DATABASE = "database_test.db'"


def teardown_database():
    os.remove(TEST_DATABASE)


@fixture
def client():
    os.environ['DB_CONNECTION'] = TEST_DATABASE
    create_database()
    with app.test_client() as client:
        yield client
    teardown_database()


def test_post__clean_language(client, requests_mock):
    requests_mock.post(MODERATION_API_URL, json={
        "hasFoulLanguage": False,
    })
    post_data =  {
        "title": "This is an engaging title",
        "paragraphs": [
            "This is the first paragraph. It contains two sentences.",
            "This is the second parapgraph. It contains two more sentences",
            "Third paraphraph here."
        ]
    }
    resp = client.post("/posts", json=post_data)
    data = json.loads(resp.data)
    assert data['hasFoulLanguage'] == False 
    

def test_post__foul_language(client, requests_mock):
    requests_mock.post(MODERATION_API_URL, json={
        "hasFoulLanguage": True,
    })
    post_data =  {
        "title": "This is an engaging title",
        "paragraphs": [
            "This is the first paragraph. It contains two sentences.",
            "This is the second parapgraph. It contains two more sentences",
            "Third paraphraph here."
        ]
    }
    resp = client.post("/posts", json=post_data)
    data = json.loads(resp.data)
    assert data['hasFoulLanguage'] == True 