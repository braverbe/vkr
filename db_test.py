import random

import numpy as np
from dotenv import load_dotenv
from imgbeddings import imgbeddings
from PIL import Image
import psycopg2
import os
load_dotenv()
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    for filename in os.listdir("stored-faces"):
        # opening the image
        doctypes = ['passport', 'studID']
        doctype = random.choice(doctypes)
        docid = random.randint(100000, 999999)
        img = Image.open("stored-faces/" + filename)
        # loading the `imgbeddings`
        ibed = imgbeddings()
        # calculating the embeddings
        embedding = ibed.to_embeddings(img)
        cur = conn.cursor()
        print(embedding[0].tolist())
        cur.execute("INSERT INTO users (docid, doctype, embedding) VALUES (%s, %s::doc_type, %s)",
                    (docid, doctype, embedding[0].tolist()))
        # print("INSERT INTO users values (%s,%s,%s)", (docid, doctype, embedding[0].tolist()))
        print(filename)
    conn.commit()
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL:", error)

finally:
    # Close the cursor and connection
    if conn:
        conn.close()
        print("PostgreSQL connection is closed")
