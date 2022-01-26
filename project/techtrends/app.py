import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

logger = logging.getLogger('stinout')
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    #filename='app.log',
    datefmt='%Y-%m-%d %H:%M:%S')
handler1 = logging.StreamHandler(sys.stdout)
handler1.setLevel(logging.DEBUG)
handler2 = logging.StreamHandler(sys.stderr)
handler2.setLevel(logging.ERROR)
logger.addHandler(handler1)
logger.addHandler(handler2)

db_conn_count = 0
# Function to get a database connection.
#This function connects to database with the name `database.db`
def get_db_connection():
    global db_conn_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_conn_count +=1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

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

@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('select * from posts')
    post_count = len(post_count.fetchall())
    connection.commit()
    connection.close()
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count":db_conn_count,"post_count":post_count}}),
            status=200,
            mimetype='application/json'
    )

    return response

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info("Article not retrieved and 404 generated.")
      return render_template('404.html'), 404
    else:
      connection = get_db_connection()
      title_value = connection.execute('SELECT title FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
      connection.close()
      for row in title_value:
        app.logger.info('Article {} retrieved!'.format(row))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("About page retrieved.")
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
            app.logger.info('New article created named {}.' .format(title))
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')



