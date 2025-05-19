import mysql.connector
import os

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "dbase")
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def fetch_all_videos():
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT vname, genre, tags, description, location, pdf_location FROM tables")
        videos = cursor.fetchall()
        cursor.close()
        return videos
    else:
        return []

def test_video_query():
    videos = fetch_all_videos()
    if videos:
        for video in videos:
            print(video)  # This will print the video details retrieved from the database
    else:
        print("No videos found or unable to connect to the database.")

if __name__ == "__main__":
    test_video_query()
