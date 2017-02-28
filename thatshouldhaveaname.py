# all the imports
import os
import sqlite3
import time
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'thatshouldhaveaname.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

users = {
    "mitchell": "mitchell",
    "sebastien": "sebastien",
    "dave": "dave"
}

activate_hacker_news_sort = False

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_definitions():
    db = get_db()
    q = ""
    if activate_hacker_news_sort:
        q = "select d.id, d.definition, d.created_by, d.submission_date,  (count(n.id) + count(u.id)/(((SELECT strftime('%s', 'now')) - d.submission_date) / 86400)) as sortby_metric from definitions d, neologisms n left outer join upvotes u on u.parent_neologism = n.id where n.parent_definition = d.id group by d.id, d.definition, d.created_by, d.submission_date order by sortby_metric desc"
    else:
        q = 'select id, definition, created_by, submission_date from definitions order by id desc'
    cur = db.execute(q)
    entries = cur.fetchall()
    return render_template('show_definitions.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_definition():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into definitions (definition, created_by, submission_date) values (?, ?, ?)', 
        [request.form['definition'], session.get('username'), str(time.time()).split('.')[0]])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_definitions'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/definition/<int:definition_id>/')
def get_definition(definition_id):
    db = get_db()
    cur = db.execute('select definition, created_by, submission_date from definitions where id = ?', str(definition_id))
    d = cur.fetchone()
    d_dict = {"definition": d[0], "created_by": d[1], "submission_date": d[2], "definition_id": definition_id}
    # cur = db.execute('select id, neologism, created_by, submission_date from neologisms where parent_definition = ?', str(definition_id))
    cur = db.execute('select n.id as id, n.neologism as neologism, n.created_by as created_by, n.submission_date as submission_date, count(u.id) as upvotes from neologisms n left outer join upvotes u on u.parent_neologism = n.id where n.parent_definition = ? group by n.id, n.neologism, n.created_by, n.submission_date order by upvotes desc', str(definition_id))
    neologisms = cur.fetchall()
    cur = db.execute('select count(u.id) from upvotes u, neologisms n where u.parent_neologism = n.id and n.parent_definition = ? and u.created_by = ?', [str(definition_id), session.get('username')])
    upvote_status = cur.fetchone()
    return render_template('show_neologisms.html', d=d_dict, neologisms=neologisms, upvote_status=upvote_status[0])

@app.route('/upvote/<int:neologism_id>/')
def upvote(neologism_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into upvotes (parent_neologism, created_by, submission_date) values (?, ?, ?)',
        [neologism_id, session.get('username'), str(time.time()).split('.')[0]])
    db.commit()
    flash('New entry was successfully posted')
    cur = db.execute('select parent_definition from neologisms where id = ?', [str(neologism_id)])
    def_id = cur.fetchone()
    return redirect(url_for('get_definition', definition_id=def_id[0]))

@app.route('/add_neologism', methods=['POST'])
def add_neologism():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    def_id = request.form['definition_id']
    db.execute('insert into neologisms (neologism, created_by, parent_definition, submission_date) values (?, ?, ?, ?)', 
        [request.form['neologism'], session.get('username'), def_id, str(time.time()).split('.')[0]])
    db.commit()
    flash('New neologism was successfully posted')
    return redirect(url_for('get_definition', definition_id=def_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] not in users.keys():
            error = 'Invalid username'
        elif request.form['password'] != users[request.form['username']]:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash(request.form['username'] + ' is logged in')
            return redirect(url_for('show_definitions'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_definitions'))

if __name__ == "__main__":
    app.run()
