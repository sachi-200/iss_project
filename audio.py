import mysql.connector
import psycopg2
import os

def connect_to_database():
        DATABASE_URL = "postgresql://ars_project_24:nFB1gdzfCFoG3th7gxpEWw@iss-project-1-2-4150.7s5.aws-ap-south-1.cockroachlabs.cloud:26257/iss_project?sslmode=verify-full"
        return psycopg2.connect(DATABASE_URL)
    
try:
    conn = connect_to_database()
    
    # Read the MP3 file
    with open("/home/anagha/Downloads/SUCCESS/jpeg_prbm/static/S2.mp3", "rb") as audio_file:
        audio_blob = audio_file.read()

    # Insert the blob into the database
    cursor = conn.cursor()
    audio_name = "HBD.mp3"
    insert_query = "INSERT INTO audio (audio_name, audio_blob) VALUES (%s, %s)"
    cursor.execute(insert_query, (audio_name, audio_blob))  # Pass parameters as a tuple
    conn.commit()

    print("Audio inserted successfully!")

except psycopg2.Error as error:
    print("Error inserting audio:", error)

finally:
    # Close the connection
    if 'conn' in locals() and conn is not None:
        if conn.closed == 0:
            cursor.close()
            conn.close()