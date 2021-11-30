import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

logging.basicConfig(
        format='%(levelname)s %(asctime)s %(message)s',
        level=logging.DEBUG)

openConnections=0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global openConnections
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    openConnections+=1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get count of posts
def getPostsCount():
    connection = get_db_connection()
    results = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return len(results)

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.info("Article does not exist")
      return render_template('404.html'), 404
    else:
      logging.info("Article \"" + str(post["title"]) + "\" retrieved!")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info("The \"About Us\" page is retrieved")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logger.info("New article \"" + title + "\" is created.")
            return redirect(url_for('index'))

    return render_template('create.html')

#Define health check
@app.route('/healthz')
def getHealthCheck():
        message = {"result":"OK - healthy"}
        response = app.response_class(
                response=json.dumps(message),
                status=200,
                mimetype='application/json'
                )
        return response

#Define metrics
@app.route('/metrics')
def getMetrics():
    global openConnections
    message = dict()
    message["db_connection_count"] = openConnections
    message["post_count"] = getPostsCount()
    
    response = app.response_class(
            response=json.dumps(message),
            status=200,
            mimetype='application/json'
            )
    return response

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
