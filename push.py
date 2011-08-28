from flask import Flask, render_template, g, jsonify
import sqlite3
import time

DATABASE = 'push.sqlite'
app = Flask(__name__)

def connect_db():
	return sqlite3.connect(DATABASE)
	
def query_db(query, args=(), one=False):
	cur = g.db.execute(query, args)
	rv = [dict((cur.description[idx][0], value)
		for idx, value in enumerate(row)) for row in cur.fetchall()]
	return (rv[0] if rv else None) if one else rv	
	
@app.before_request
def before_request():
    g.db = connect_db()
    
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def hello_world():
	return render_template('index.html')

@app.route('/push/', methods=['POST'])
def push():
	while(1):
		push = query_db('select * from push where read = 0 limit 1');
		if len(push) is not 0:
			g.db.execute('update push set read = 1 where id = %d' % push[0]['id'])
			g.db.commit()
			return jsonify(key=push[0]['key'], value=push[0]['value'])
		time.sleep(0.1)
		pass

if __name__ == '__main__':
	app.debug = True
	app.run()