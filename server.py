from flask import Flask, render_template, url_for, request
from searcher import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	print "Someone is at the home page."
	return render_template('welcome_page.html')

@app.route('/questions/')
def my_link():
	print 'I got clicked!'
	return 'Click.'

@app.route('/results/', methods=['GET', 'POST'])
def results():
	# if request.method == 'POST':
	# 	data = request.form
	# else:
	# 	data = request.args
	indexer = open_dir("indexDir")
	searcher = request.form.get('searchterm')
	results = search(indexer, searcher)
	print(results)
	return render_template('results.html', query=searcher, results=results)

if __name__ == '__main__':
	app.run(debug=True)