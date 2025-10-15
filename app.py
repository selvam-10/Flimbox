from flask import Flask, render_template, abort, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'Say Hello To My Little Friend!'  # Needed for sessions

# ---------------------- DATABASE CONNECTION ----------------------
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='post@1234',   
        database='db'          
    )
    return conn


# ---------------------- HOME PAGE ----------------------
@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT Id, Title, Release_Year, Director, Genre, Duration, Rating, Images FROM Movies")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()

    # Determine if admin is logged in
    is_admin = session.get('is_admin', False)

    return render_template('index.html', movies=movies, is_admin=is_admin)


# ---------------------- MOVIE DETAIL PAGE ----------------------
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Movies WHERE Id = %s", (movie_id,))
    movie = cursor.fetchone()
    cursor.close()
    conn.close()

    if movie is None:
        abort(404)

    # Pass admin status to template
    is_admin = session.get('is_admin', False)
    return render_template('movie_detail.html', movie=movie, is_admin=is_admin)


# ---------------------- ADD OR EDIT MOVIE DETAILS (ADMIN ONLY) ----------------------
@app.route('/movie/add-details/<int:movie_id>', methods=['GET', 'POST'])
def add_movie_details(movie_id):
    # Only admin can access
    if not session.get('is_admin'):
        flash("You don't have permission to access this page.", "warning")
        return redirect(url_for('movie_detail', movie_id=movie_id))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT Id, Title, Plot, Cast FROM Movies WHERE Id = %s", (movie_id,))
    movie = cursor.fetchone()

    if movie is None:
        cursor.close()
        conn.close()
        abort(404)

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
            flash("Movie details updated successfully!", "success")
            return redirect(url_for('movie_detail', movie_id=movie_id))
        except Exception as e:
            conn.rollback()
            flash(f"Database error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    cursor.close()
    conn.close()
    return render_template('movie.html', movie=movie, movie_detail_url=movie_detail_url)


# ---------------------- LOGIN ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        # Only admin can log in
        if username == 'admin' and password == 'CR7Reunited':
            session['logged_in'] = True
            session['is_admin'] = True
            return redirect(url_for('home'))
        else:
            flash("You entered wrong password.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# ---------------------- LOGOUT ----------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


# ---------------------- MAIN ----------------------
if __name__ == '__main__':
    app.run(debug=True)
