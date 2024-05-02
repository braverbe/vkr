import numpy as np
from imgbeddings import imgbeddings
from PIL import Image
import psycopg2
import os

DB_NAME = "face_recognization"
DB_USER = "postgres"
DB_PASSWORD = "pass"
DB_HOST = "localhost"  # or your database host
DB_PORT = "5432"       # or your database port

conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


# loading the face image path into file_name variable
file_name = "content/uncnown_persons/zxczz.jpg"  # replace <INSERT YOUR FACE FILE NAME> with the path to your image
# opening the image
img = Image.open(file_name)
# loading the `imgbeddings`
ibed = imgbeddings()

# calculating the embeddings
embedding = ibed.to_embeddings(img)
# print(embedding[0].tolist())
# print(np.array(embedding[0].tolist()))


cur = conn.cursor()
string_representation = "["+ ", ".join(str(x) for x in embedding[0].tolist()) +"]"

cur.execute("SELECT picture, embedding FROM pictures;")
rows = cur.fetchall()

# Initialize variables for storing the nearest neighbor information
nearest_neighbor = None
min_distance = float('inf')

# Calculate the distance or similarity for each row
for row in rows:
    picture, stored_embedding = row
    stored_embedding = np.array(stored_embedding)  # Convert stored embedding to numpy array
    distance = np.linalg.norm(stored_embedding - embedding[0].tolist())  # Calculate Euclidean distance
    # Alternatively, you can use other similarity metrics such as cosine similarity
    # print(f'{picture}: {distance}')
    # Update nearest neighbor information if the current row has a smaller distance
    if distance < min_distance:
        # print(distance, min_distance, min_distance-distance)
        nearest_neighbor = picture
        min_distance = distance

if (min_distance<16):
    print(f"Nearest neighbor: {nearest_neighbor}, distance: {min_distance}")
else:
    print("No nearest persons, distance: ", min_distance)

cur.close()