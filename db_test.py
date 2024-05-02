import numpy as np
from imgbeddings import imgbeddings
from PIL import Image
import psycopg2
import os
# Replace these values with your actual database connection details
DB_NAME = "face_recognization"
DB_USER = "postgres"
DB_PASSWORD = "pass"
DB_HOST = "localhost"  # or your database host
DB_PORT = "5432"       # or your database port

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
        img = Image.open("stored-faces/" + filename)
        # loading the `imgbeddings`
        ibed = imgbeddings()
        # calculating the embeddings
        embedding = ibed.to_embeddings(img)
        cur = conn.cursor()
        print(embedding[0].tolist())
        cur.execute("INSERT INTO pictures values (%s,%s)", (filename, embedding[0].tolist()))
        print(filename)
    conn.commit()
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL:", error)

finally:
    # Close the cursor and connection
    if conn:
        conn.close()
        print("PostgreSQL connection is closed")
