from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:digi@digi/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'launchcode101'

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, owner): 
        self.name = name
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship("Blog", backref='user')

    def __init__(self, name):
        self.name = name

@app.before_request
def require_login():
    allowed_routes = ['login','signup','index','blog','userpage']
    if request.endpoint not in allowed_routes and 'username' not in session:
        print request.endpoint
        return redirect('/login')

@app.route('/user', methods=['GET'])
def userpage():
    if 'id' in request.args:
        user = User.query.filter_by(id = request.args['id']).first()

        print user.blogs
        return render_template('user.html', user=user)
    return redirect('/')
@app.route('/blog', methods=['GET'])
def blog():
    if 'id' in request.args:
        post = Blog.query.filter_by(id = request.args['id']).first()

        return render_template('singleblog.html', post = post)

    posts = Blog.query.order_by(Blog.id.desc()).all()

    return render_template('blog.html', posts = posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        # add the post
        user = User.query.filter_by(id=session['userid']).first()
        post = Blog('blog', user)
        post.title = request.form['title']
        post.body = request.form['body']
        post.owner_id = session['userid']

        db.session.add(post)
        db.session.commit()

        return redirect('/blog?id=' + str(post.id), code=302)

    return render_template('newpost.html')

@app.route('/logout', methods=['POST','GET'])
def logout():
    del session['userid']
    del session['username']
    return redirect('/blog')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form['username'] == '':
            return render_template('login.html', form=request.form, errorMessage="Username is required")
        if request.form['password'] == '':
            return render_template('login.html', form=request.form, errorMessage="Password is required")

        # See if there is a user match
        user = User.query.filter_by(username=request.form['username']).first()

        if user is not None:
            # check the password
            if user.password == request.form['password']:
                session['userid'] = user.id
                session['username'] = user.username
                # since the username and password check out send them to the newpost page
                return redirect('/newpost')
            else: 
                # send them an error message that the user/pass was not correct since password was wrong
                return render_template('login.html', form=request.form, errorMessage="Username and/or Password is invalid")
        else:
            # send them an error message that the user/pass was not correct since username was wrong
            return render_template('login.html', form=request.form, errorMessage="Username and/or Password is invalid")
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        # add to the database after checking that all the fields are good
        if request.form['username'] == '':
            return render_template('signup.html', form=request.form, errorMessage="Username is required")
        if request.form['password'] == '':
            return render_template('signup.html', form=request.form, errorMessage="Password is required")
        if len(request.form['username']) < 3:
            return render_template('signup.html', form=request.form, errorMessage="Username is too short")
        if len(request.form['password']) < 3:
            return render_template('signup.html', form=request.form, errorMessage="Password is too short")

        user = User('user')
        user.username = request.form['username']
        user.password = request.form['password']

        db.session.add(user)
        db.session.commit()

        return redirect('/newpost')
    return render_template('signup.html')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    latestPosts = Blog.query.order_by(Blog.id.desc()).limit(10).all()

    return render_template('index.html', users=users, latest=latestPosts)

if __name__ == '__main__':
    app.run()
