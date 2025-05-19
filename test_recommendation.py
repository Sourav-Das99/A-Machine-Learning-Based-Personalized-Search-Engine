from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Sample video data
videos = [
    {'vname': 'Introduction to Java program', 'genre': 'program', 'tags': 'intro to java', 'description': 'Java programming', 'location': 'static/videos/67e0f15fb1174_Introduction to Java P...', 'pdf_location': 'static/pdfs/67e0f15fb1178_AeroPendulum.pdf'},
    {'vname': 'Introduction to the Machine learning', 'genre': 'ML', 'tags': 'Introduction to machine learning, Basic definition', 'description': 'Machine Learning (ML) is a subfield of artificial intelligence.', 'location': 'static/videos/67e0f675b1ce7_ML 1 _ Introduction to...', 'pdf_location': 'static/pdfs/67e0f675b1cf6_THE INDIAN EXPRESS DELHI...'},
    {'vname': 'Training and testing dataset in Machine learning', 'genre': 'ML', 'tags': 'training and testing dataset, difference between', 'description': 'In machine learning, the concepts of train and test datasets are crucial for model evaluation.', 'location': 'static/videos/67e0f8da9bf3b_ML 2 _ Training VS Tes...', 'pdf_location': None},
    {'vname': 'Supervised learning in the Machine learning', 'genre': 'ML', 'tags': 'Supervised learning with example, types of supervised learning', 'description': 'Supervised Machine Learning (Supervised ML) is one of the most popular machine learning techniques.', 'location': 'static/videos/67e0f94d61002_ML 3_ Supervised Learn...', 'pdf_location': None},
    {'vname': 'support Vector machine (SVM)', 'genre': 'ML', 'tags': 'introduction of support vector machine (svm)', 'description': 'Support Vector Machine (SVM) is a powerful and versatile machine learning algorithm.', 'location': 'static/videos/67e0fa33ef735_How Support Vector Mac...', 'pdf_location': None},
    {'vname': 'Java basic program', 'genre': 'program', 'tags': 'Displaying A Messages in Java Program', 'description': 'This video explains how to display messages in Java programming.', 'location': 'static/videos/67e1096ab292f_Displaying Messages in...', 'pdf_location': None},
    {'vname': 'Our First Java program', 'genre': 'program', 'tags': 'first java program', 'description': 'Learn how to write and execute your first Java program.', 'location': 'static/videos/67e109bf7d5cb_Our First Java Project...', 'pdf_location': None},
    {'vname': 'Programming error Java program', 'genre': 'program', 'tags': 'programming error in java', 'description': 'This video discusses common programming errors in Java.', 'location': 'static/videos/67e109ee16559_Programming Errors.mp4', 'pdf_location': None},
    {'vname': 'Introduction to Operating system', 'genre': 'operating system', 'tags': 'introduction to operating system', 'description': 'An Operating System (OS) is system software that manages computer hardware and software resources.', 'location': 'static/videos/67e10a77d3248_L-1.1_ Introduction to...', 'pdf_location': None},
    {'vname': 'Batch processing in Operating system', 'genre': 'operating system', 'tags': 'Batch processing in Operating system', 'description': 'Batch processing is the execution of a series of jobs in a program without manual intervention.', 'location': 'static/videos/67e10ab9f2748_L-1.2_ Batch Operating...', 'pdf_location': None},
    {'vname': 'Process state Operating system', 'genre': 'operating system', 'tags': 'Process state in operating system', 'description': 'The process state in an operating system refers to the current state or condition of a process.', 'location': 'static/videos/67e10adfdded7_L-1.5_ Process States ...', 'pdf_location': None},
    {'vname': 'What is Operating system', 'genre': 'operating system', 'tags': 'Introduction to operating system', 'description': 'An Operating System (OS) is a software program that manages computer hardware and software.', 'location': 'static/videos/67e10b3293346_What is Operating Syst...', 'pdf_location': None},
    {'vname': 'Rank of matrix', 'genre': 'math', 'tags': 'Rank of matrix, Simple and easy trick', 'description': 'This video explains how to find the rank of a matrix in a simple and easy manner.', 'location': 'static/videos/67e275e3e5e38_Rank of Matrix Explain...', 'pdf_location': 'static/pdfs/67e275e3e5e46_AeroPendulum.pdf'},
    {'vname': 'Inverse of matrices of 3 by 3 and 2 by 2', 'genre': 'math', 'tags': 'Inverse of a matrix, Engineering mathematics', 'description': 'Learn how to find the inverse of a matrix, both 3x3 and 2x2 matrices.', 'location': 'static/videos/67e27763cf313_Inverse & Adj(A) of 3x...', 'pdf_location': None},
    {'vname': 'Echelon form of matrix', 'genre': 'math', 'tags': 'Echelon form of a matrix, Engineering mathematics', 'description': 'In this video, we will learn how to convert a matrix into echelon form.', 'location': 'static/videos/67e277e0918a1_Echelon form of matrix...', 'pdf_location': 'static/pdfs/67e277e091751_THE INDIAN EXPRESS DELHI...'}
]

    # Add more video data here...


def recommend_videos(input_video_name, limit=6):
    # Convert input to lowercase for matching
    input_video_name = input_video_name.strip().lower()

    df = pd.DataFrame(videos)

    # Ensure the 'features' include video name, tags, and description more prominently
    df['features'] = (
        df['vname'].str.lower() * 2 + " " +  # Double weight for video name
        df['genre'].str.lower() + " " + 
        df['tags'].str.lower() * 2 + " " +  # Use integer multiplication
        df['description'].str.lower() * 2   # Use integer multiplication
    )

    # Vectorize the features using TF-IDF
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['features'])

    # First, check for exact match in video name
    try:
        input_index = df[df['vname'].str.contains(input_video_name, case=False)].index[0]
        # If an exact match is found, prioritize this video and add it to the recommendations
        recommendations = [{
            'vname': df.iloc[input_index]['vname'],
            'tags': df.iloc[input_index]['tags'],
            'location': df.iloc[input_index]['location'],
            'pdf_location': df.iloc[input_index]['pdf_location']
        }]
    except IndexError:
        # If no exact match is found, proceed with cosine similarity
        recommendations = []

    # Now find the most similar videos if no exact match or additional recommendations needed
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix).flatten()

    # Ensure that there are valid recommendations to add
    similar_indices = cosine_sim.argsort()[-limit-1:-1][::-1]  # Sort and exclude the first one (which is the video itself)

    for i in similar_indices:
        if i < len(df):  # Ensure the index is valid
            if df.iloc[i]['vname'].lower() != input_video_name:  # Don't add the exact match again
                recommendations.append({
                    'vname': df.iloc[i]['vname'],
                    'tags': df.iloc[i]['tags'],
                    'location': df.iloc[i]['location'],
                    'pdf_location': df.iloc[i]['pdf_location']
                })

    # Return the recommended videos
    return recommendations

def test_recommendation():
    video_name = input("enter somthing whta would you like")  # You can change this to test other videos
    recommendations = recommend_videos(video_name)
    
    if recommendations:
        print(f"Recommendations for '{video_name}':")
        for video in recommendations:
            print(f"Recommended Video: {video['vname']} - Tags: {video['tags']}")
    else:
        print("No recommendations found.")

if __name__ == "__main__":
    test_recommendation()
