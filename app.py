from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Welcome12#',
    'database': 'social'
}

# Database connection function
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Route for the home page to input user ID
@app.route('/')
def index():
    return render_template('index.html')

# Route to show analytics for a specific user
@app.route('/analytics/<int:user_id>', methods=['GET'])
def analytics(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get the post count for the user
    cursor.execute("""
    SELECT COUNT(id) AS post_count
    FROM photos
    WHERE user_id = %s
    """, (user_id,))
    post_count = cursor.fetchone()['post_count']

    # Get likes and comments for each photo the user has uploaded
    cursor.execute("""
    SELECT p.id AS photo_id, 
           COUNT(c.id) AS comment_count,
           COUNT(l.photo_id) AS like_count
    FROM photos p
    LEFT JOIN comments c ON p.id = c.photo_id
    LEFT JOIN likes l ON p.id = l.photo_id
    WHERE p.user_id = %s
    GROUP BY p.id
    """, (user_id,))
    
    photo_data = cursor.fetchall()

    # Get the top-liked photo for the user
    cursor.execute("""
    SELECT p.id AS photo_id, p.image_url, COUNT(l.photo_id) AS like_count
    FROM photos p
    LEFT JOIN likes l ON p.id = l.photo_id
    WHERE p.user_id = %s
    GROUP BY p.id
    ORDER BY like_count DESC
    LIMIT 1
    """, (user_id,))
    top_liked_photo = cursor.fetchone()

    # Get the five most recent comments for the user's photos
    cursor.execute("""
    SELECT c.comment_text, p.id AS photo_id, c.created_at
    FROM comments c
    JOIN photos p ON c.photo_id = p.id
    WHERE p.user_id = %s
    ORDER BY c.created_at DESC
    LIMIT 5
    """, (user_id,))
    recent_comments = cursor.fetchall()

    # Get the follower count for the user
    cursor.execute("""
    SELECT COUNT(f.follower_id) AS follower_count
    FROM follows f
    WHERE f.followee_id = %s
    """, (user_id,))
    follower_count = cursor.fetchone()['follower_count']

    cursor.close()
    connection.close()

    # Prepare data for the chart
    photo_ids = [f"Photo {photo['photo_id']}" for photo in photo_data]
    comment_counts = [photo['comment_count'] for photo in photo_data]
    like_counts = [photo['like_count'] for photo in photo_data]
    # Inside the `analytics` route function in app.py
    total_likes = sum(like_counts)
    total_comments = sum(comment_counts)

    #return render_template('analytics.html', user_id=user_id, post_count=post_count,
                        #photo_ids=photo_ids, comment_counts=comment_counts, like_counts=like_counts,
                        #total_likes=total_likes, total_comments=total_comments)


    return render_template('analytics.html', user_id=user_id, post_count=post_count,
                           photo_ids=photo_ids, comment_counts=comment_counts, 
                           like_counts=like_counts, top_liked_photo=top_liked_photo,likes_counts=like_counts,total_likes=total_likes,total_comments=total_comments,
                           recent_comments=recent_comments, follower_count=follower_count)

if __name__ == '__main__':
    app.run(debug=True)
