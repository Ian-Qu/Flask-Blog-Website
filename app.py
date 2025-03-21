import sqlite3
import uuid
from datetime import datetime, timezone
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'WYSI'

class Post:
    def __init__(self):
        self.conn = None

    def get_db_connection(self):
        self.conn = sqlite3.connect('database.db')
        self.conn.row_factory = sqlite3.Row # Returns results with column names
    
    def execute(self, query, tuple, fetch_type):
        self.get_db_connection()
        if tuple:
            temp_result = self.conn.execute(query,tuple)
        else:
            temp_result = self.conn.execute(query)

        result = None
        if fetch_type == "one":
            result = temp_result.fetchone()
        elif fetch_type == "all":
            result = temp_result.fetchall()
        else:
            self.conn.commit()
        self.conn.close()
        return result
    
    def record_changes(self, change):
        fetch_type = None
        query = 'INSERT INTO changes (id, title, content, change_made) VALUES (?, ?, ?, ?)'
        self.execute(query, change, fetch_type)

    def get_post(self, post_id):
        query = 'SELECT * FROM posts WHERE id = ?'
        tuple = (post_id,)
        fetch_type = "one"
        post = self.execute(query, tuple, fetch_type)
        if post is None:
            abort(404)
        return post
    
    def get_all_posts(self):
        query = 'SELECT * FROM posts'
        tuple = None
        fetch_type = "all"
        posts = self.execute(query, tuple, fetch_type)
        return posts
    
    def get_all_changes(self):
        query = 'SELECT * FROM changes'
        tuple = None
        fetch_type = "all"
        changes = self.execute(query, tuple, fetch_type)
        return changes
    
    def create_post(self, title, content):
        query = 'INSERT INTO posts (id, title, content) VALUES (?, ?, ?)'
        id = str(uuid.uuid4())
        tuple = (id, title, content)
        fetch_type = None
        self.execute(query, tuple, fetch_type)  
        change_type = "Post Created: "
        change = (id, title, content, change_type)
        self.record_changes(change)
    
    def edit_post(self, title, original_title, content, original_content, id):
        query = 'UPDATE posts SET title = ?, updated_on = ?, content = ? WHERE id = ?'
        current_time = datetime.now(timezone.utc)
        updated_on = current_time.strftime('%Y-%m-%d %H:%M:%S')
        tuple = (title, updated_on, content, id)
        fetch_type = None
        self.execute(query, tuple, fetch_type)

        # Determine type based on whether the title and or content was changed
        if title != original_title and original_content != content:
            change_type = f"Post Title and Content Edited: {original_title} to "
        elif title != original_title and original_content == content:
            change_type = f"Post Title Edited: {original_title} to "
        elif title == original_title and original_content != content:
            change_type = "Post Content Edited: "
        else:
            change_type = "Post Edited, No Change: "
        change = (id, title, content, change_type)
        self.record_changes(change)

    def del_post(self, title, content, id):
        query = 'DELETE FROM posts WHERE id = ?'
        tuple = (id, )
        fetch_type = None
        self.execute(query, tuple, fetch_type)
        change_type = "Post Deleted: "
        change = (id, title, content, change_type)
        self.record_changes(change)



p = Post()
@app.route('/')
def index():
    posts = p.get_all_posts()
    #print(len(posts))
    #print(posts[0])
    return render_template('index.html', posts=posts)
#index()

@app.route('/<string:post_id>')
def post(post_id):
    post = p.get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        # Title required
        if not title:
            flash('Title is required!')
        else:
            p.create_post(title, content)
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/<string:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post =p.get_post(id)
    original_title = post[2]
    original_content = post[3]

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            p.edit_post(title, original_title, content, original_content, id,)
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<string:id>/delete', methods=('POST',))
def delete(id):
    post = p.get_post(id)
    title = post['title']
    content = post['content']
    p.del_post(title, content, id)
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

@app.route('/audit')
def audit():
    changes = p.get_all_changes()
    return render_template('audit.html', changes=changes)