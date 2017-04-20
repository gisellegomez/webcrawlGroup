from flask import Flask, render_template, url_for, request
from searcher import *
import re

rgxThumb = re.compile(r"/thumb/", re.IGNORECASE)
rgxJpg = re.compile(r"\.jpg/.+$")
rgxJPG = re.compile(r"\.JPG/.+$")

def getRealImgURL(url):

	print url
	realURL = rgxThumb.sub('/', url)
	realURL = rgxJpg.sub('.jpg', realURL)
	realURL = rgxJPG.sub('.JPG', realURL)

	print realURL
	return realURL


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	print "Someone is at the home page."
	return render_template('index.html')

@app.route('/description', methods=['POST'])
def my_link():
	index = request.form.get('n')
	print index

	# split string description into list of paragraphs
	body = PLEASE_REPLACE_ME[index][3].splitlines()
	if not body:
		return '', 404
	else:
		return render_template('description.html', body=body), 200

@app.route('/results', methods=['POST'])
def results():
	# params:
	# query (search terms)
	query = request.form.get('query')
	# index (how many results the client already has)
	index = int(request.form.get('index'))
	# count (how many results the client wants back)
	count = int(request.form.get('count'))

	indexer = open_dir("indexDir")
	
	results = search(indexer, query)

	for result in results:
		result[2] = getRealImgURL(result[2])

	if not results:
		# no results for search
		return '', 404
	elif len(results) is count:
		# client already has all results
		return '', 204
	else:
		# render results for client
		return render_template('results.html', results=results[index:count]), 200

if __name__ == '__main__':
	app.run(debug=True)