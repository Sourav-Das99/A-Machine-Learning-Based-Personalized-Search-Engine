from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

app = Flask(__name__, static_folder="static")
app.secret_key = 'your_secret_key'  


def connect_to_database():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "nbase")
        )
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None


def fetch_all_videos(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, vname, genre, tags, description, location, pdf_location FROM tables")
    videos = cursor.fetchall()
    cursor.close()
    return videos

def fetch_user_interactions(conn):
    return pd.read_sql("SELECT user_id, video_id, rating FROM user_interactions", conn)


def recommend_videos(input_video_name, user_id=None, limit=5):
    conn = connect_to_database()
    if not conn:
        return []

    videos = fetch_all_videos(conn)
    if not videos:
        conn.close()
        return []

    df = pd.DataFrame(videos)
    df['features'] = df['vname'] + " " + df['genre'] + " " + df['tags'] + " " + df['description']

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['features'])

    try:
        input_index = df[df['vname'].str.contains(input_video_name, case=False)].index[0]
    except IndexError:
        conn.close()
        return []

    # Content-based recommendation
    cosine_sim = cosine_similarity(tfidf_matrix[input_index], tfidf_matrix).flatten()
    content_indices = cosine_sim.argsort()[-limit-1:-1][::-1]

    recommended_indices = set(content_indices)

    # Collaborative 
    if user_id:
        ratings_df = fetch_user_interactions(conn)
        user_item_matrix = ratings_df.pivot_table(index='user_id', columns='video_id', values='rating').fillna(0)

        if user_id in user_item_matrix.index:
            svd = TruncatedSVD(n_components=5)
            matrix_svd = svd.fit_transform(user_item_matrix)

            sim_scores = cosine_similarity([matrix_svd[user_item_matrix.index.get_loc(user_id)]], matrix_svd)[0]
            similar_users = sim_scores.argsort()[-5:][::-1]

            for sim_user_idx in similar_users:
                sim_user_id = user_item_matrix.index[sim_user_idx]
                if sim_user_id == user_id:
                    continue
                top_rated = user_item_matrix.loc[sim_user_id].sort_values(ascending=False).head(limit).index
                recommended_indices.update(df[df['id'].isin(top_rated)].index)

    conn.close()

    
    final_videos = []
    for i in recommended_indices:
        final_videos.append({
            'id': df.iloc[i]['id'],
            'vname': df.iloc[i]['vname'],
            'tags': df.iloc[i]['tags'],
            'location': df.iloc[i]['location'],
            'pdf_location': df.iloc[i]['pdf_location'],
            'video_url': f"/static/videos/{df.iloc[i]['location'].split('/')[-1]}",
            'pdf_url': f"/static/pdfs/{df.iloc[i]['pdf_location'].split('/')[-1]}" if df.iloc[i]['pdf_location'] else None
        })

    return final_videos


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = connect_to_database()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['student_id'] = user['id']
            session['student_name'] = user['name']
            return redirect(url_for('index'))
        else:
            return render_template('login_student.html', error="Invalid credentials")
    return render_template('login_student.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = connect_to_database()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO students (name, email, password) VALUES (%s, %s, %s)",
                           (name, email, password))
            conn.commit()
            return redirect(url_for('login'))
        except mysql.connector.Error as e:
            print(f"Registration error: {e}")
            return render_template('register.html', error="Registration failed.")
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/abc', methods=['GET', 'POST'])
def index():
    conn = connect_to_database()
    if not conn:
        return render_template('vid.html', error="Database error.")

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, vname, genre, tags, description, location, pdf_location FROM tables ORDER BY id DESC LIMIT 5")
    recent_videos = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        video_name = request.form.get('video_name') or request.form.get('video_name_from_speech')
        if video_name:
            recommended_videos = recommend_videos(video_name, user_id=session.get('student_id'))
            return render_template('vid.html', videos=recommended_videos)
        else:
            return render_template('vid.html', videos=recent_videos)

    return render_template('vid.html', videos=recent_videos)

@app.route('/rate_video', methods=['POST'])
def rate_video():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    user_id = session['student_id']
    video_id = request.form.get('video_id')
    rating = request.form.get('rating')

    if not video_id or not rating:
        return redirect(url_for('index'))

    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO user_interactions (user_id, video_id, rating)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE rating = VALUES(rating)
        """, (user_id, video_id, rating))
        conn.commit()
    except Exception as e:
        print(f"Rating error: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
