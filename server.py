from flask import Flask, render_template, url_for, request
from searcher import *

rgxThumb = re.compile(r"/thumb/", re.IGNORECASE)
rgxJpg = re.compile(r"\.jpg/.+$")
rgxJPG = re.compile(r"\.JPG/.+$")
resulting = []
def getRealImgURL(url):

	realURL = rgxThumb.sub('/', url)
	realURL = rgxJpg.sub('.jpg', realURL)
	realURL = rgxJPG.sub('.JPG', realURL) # wikipedia urls are case sensitive

	return realURL


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	print ("Someone is at the home page.")
	return render_template('index.html')

@app.route('/description', methods=['POST'])
def my_link():
	index = request.form.get('n')
	print (index)
	with open('results.txt', 'r') as f:
		data = f.read()
	print(data)

	data = data.split(', | \n')
	print(data)

	# split string description into list of paragraphs

	body = data[index][3].splitlines()
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
	results = open('results.txt', 'w')

	resulting = search(indexer, query)

	# Globally store
	for k in resulting:
		for j in k:
			results.write(j)
			results.write(",")
		results.write('\n')
	results.close()
	# print(resulting)
	for result in resulting:
		result[2] = getRealImgURL(result[2])

	if not resulting:
		# no results for search
		return '', 404
	elif len(resulting) is index:
		# client already has all results
		return '', 204
	else:
		# render results for client
		count = index + count
		return render_template('results.html', results=resulting[index:count]), 200

if __name__ == '__main__':
	app.run(debug=True)