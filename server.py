from flask import Flask, render_template, url_for, request
from flask.ext.api import status
from searcher import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	print "Someone is at the home page."
	return render_template('index.html')

@app.route('/description/', methods=['POST'])
def my_link():
	index = request.form.get('n')
	print index

	# split string description into list of paragraphs
	body = PLEASE_REPLACE_ME[index][3].splitlines()
	if not body:
		return '', status.HTTP_404_NOT_FOUND
	else:
		return render_template('description.html', body=body), status.HTTP_200_OK

@app.route('/results/', methods=['POST'])
def results():
	# params:
	# query (search terms)
	query = request.form.get('query')
	# index (how many results the client already has)
	index = request.form.get('index')
	# count (how many results the client wants back)
	count = request.form.get('count')

	indexer = open_dir("indexDir")
	
	results = search(indexer, query)
	print(results)
	if not results:
		# no results for search
		return '', status.HTTP_404_NOT_FOUND
	else if len(results) is count:
		# client already has all results
		return '', status.HTTP_204_NO_CONTENT
	else:
		# render results for client
		return render_template('results.html', results=results[index:count]), status.HTTP_200_OK

if __name__ == '__main__':
	app.run(debug=True)