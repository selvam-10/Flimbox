from flask import Flask, render_template, abort, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='post@1234',   
        database='db'          
    )
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Ensure Id is selected for linking
    cursor.execute("SELECT Id, Title, Release_Year, Director, Genre, Duration, Rating, Images FROM Movies")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', movies=movies)

# Route 1: Movie Detail Page (Defines endpoint: 'movie_detail')
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all details needed for the detail page
    cursor.execute("SELECT * FROM Movies WHERE Id = %s", (movie_id,))
    movie = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if movie is None:
        abort(404)
        
    return render_template('movie_detail.html', movie=movie)

# Route 2: Admin/Editor Page (Defines endpoint: 'add_movie_details')
@app.route('/movie/add-details/<int:movie_id>', methods=['GET', 'POST'])
def add_movie_details(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT Id, Title, Plot, Cast FROM Movies WHERE Id = %s", (movie_id,))
    movie = cursor.fetchone()

    if movie is None:
        cursor.close()
        conn.close()
        abort(404)  # movie_detail_url won't be needed here

    # movie exists, safe to create the URL
    movie_detail_url = url_for('movie_detail', movie_id=movie_id)

    if request.method == 'POST':
        plot = request.form['plot']
        cast = request.form['cast']

        update_query = """
            UPDATE Movies
            SET Plot = %s, Cast = %s
            WHERE Id = %s
        """
        try:
            cursor.execute(update_query, (plot, cast, movie_id))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('movie_detail', movie_id=movie_id))
        except Exception as e:
            conn.rollback()
            print(f"Database error: {e}")

    cursor.close()
    conn.close()
    return render_template('movie.html', movie=movie, movie_detail_url=movie_detail_url)

if __name__ == '__main__':
    app.run(debug=True)