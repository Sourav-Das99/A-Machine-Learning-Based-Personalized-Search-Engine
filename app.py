from flask import Flask, render_template, request
import mysql.connector
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import voice 
import webbrowser
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Your DB connection and route handlers come next...


app = Flask(__name__, static_folder="static")

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "nbase")
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


def fetch_all_videos(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT vname, genre, tags, description, location, pdf_location FROM tables")
        videos = cursor.fetchall()
        cursor.close()
        return videos
    except mysql.connector.Error as e:

        print(f"Error fetching video data: {e}")
        return []

def recommend_videos(input_video_name, limit=3):
    connection = connect_to_database()
    if not connection:
        return []

    videos = fetch_all_videos(connection)
    connection.close()

    if not videos:
        return []

    df = pd.DataFrame(videos)
    df['features'] = df['vname'] + " " + df['genre'] + " " + df['tags'] + " " + df['description']

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['features'])

    try:
        # Find the index of the video that matches the input
        input_index = df[df['vname'].str.contains(input_video_name, case=False)].index[0]
    except IndexError:
        return []

    recommended_videos = [
        {
            'vname': df.iloc[input_index]['vname'],
            'tags': df.iloc[input_index]['tags'],
            'location': df.iloc[input_index]['location'],
            'pdf_location': df.iloc[input_index]['pdf_location'], 
            'video_url': f"/static/videos/{df.iloc[input_index]['location'].split('/')[-1]}",
            'pdf_url': f"/static/pdfs/{df.iloc[input_index]['pdf_location'].split('/')[-1]}" if df.iloc[input_index]['pdf_location'] else None  
        }
    ]

    
    cosine_sim = cosine_similarity(tfidf_matrix[input_index], tfidf_matrix).flatten()
    similar_indices = cosine_sim.argsort()[-limit-1:-1][::-1]

    for i in similar_indices:
        if i != input_index:  
            recommended_videos.append({
                'vname': df.iloc[i]['vname'],
                'tags': df.iloc[i]['tags'],
                'location': df.iloc[i]['location'],
                'pdf_location': df.iloc[i]['pdf_location'], 
                'video_url': f"/static/videos/{df.iloc[i]['location'].split('/')[-1]}",
                'pdf_url': f"/static/pdfs/{df.iloc[i]['pdf_location'].split('/')[-1]}" if df.iloc[i]['pdf_location'] else None  
            })
    
    return recommended_videos

"""com"""

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        connection = connect_to_database()
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO students (name, email, password) VALUES (%s, %s, %s)",
                           (name, email, password))
            connection.commit()
            return redirect(url_for('login_student'))
        except mysql.connector.IntegrityError:
            return render_template('register.html', error="Email already registered.")
        finally:
            cursor.close()
            connection.close()

    return render_template('register.html')


@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = connect_to_database()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user and check_password_hash(user['password'], password):
            session['student_id'] = user['id']
            session['student_name'] = user['name']
            return redirect(url_for('student_profile'))
        else:
            return render_template('login_student.html', error="Invalid credentials")

    return render_template('login_student.html')


@app.route('/profile')
def student_profile():
    if 'student_id' not in session:
        return redirect(url_for('login_student'))

    return render_template('profile.html', name=session['student_name'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_student'))





"""com"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login')
def login():
    return render_template('admin.html')

@app.route('/aaa')
def conf():
    return render_template('config.html')

@app.route('/abc', methods=['GET', 'POST'])
def index():
    connection = connect_to_database()
    if not connection:
        return render_template('vid.html', error="Error connecting to the database.")
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT vname, genre, tags, description, location, pdf_location FROM tables ORDER BY id DESC LIMIT 5")
    videos = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        video_name = request.form.get('video_name')
        
        if not video_name:
            video_name = request.form.get('video_name_from_speech') 
        
        if video_name:
            recommended_videos = recommend_videos(video_name)
            if recommended_videos:
                return render_template('vid.html', videos=recommended_videos)
            else:
                return render_template('vid.html', videos=videos, error="No recommendations found for your input.")
        else:
            return render_template('vid.html', videos=videos)

    return render_template('vid.html', videos=videos)



if __name__ == '__main__':
    app.run(debug=True)
    
"""

if __name__ == "__main__":
    port = 9888
    url = f"http:// 172.16.0.191:{port}"
    print(f"Starting server at {url}")
    webbrowser.open_new(url)  
    app.run(host='0.0.0.0', port=port, debug=True)

"""
