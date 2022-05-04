import json
import sqlite3
import os

from dotenv import load_dotenv


load_dotenv()


def create_database():
    connection = sqlite3.connect(os.environ.get('DB_CONNECTION'))

    with open('schema.sql') as f:
        connection.executescript(f.read())

    cur = connection.cursor()

    paragraphs = json.dumps({"paragraphs": ["Paragraph1", "Paragraph2"]})

    cur.execute("INSERT INTO posts (title, content, hasFoulLanguage) VALUES (?, ?, ?)",
                ('Title', paragraphs, True)
                )

    cur.execute("INSERT INTO posts (title, content, hasFoulLanguage) VALUES (?, ?, ?)",
                ('Title2', paragraphs, False)
                )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()