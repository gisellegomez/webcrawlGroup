from flask import Flask, render_template, url_for, request
from searcher import *
import re
import requests
from lxml import etree, objectify

rgxThumb = re.compile(r"/thumb/", re.IGNORECASE)
rgxJpg = re.compile(r"\.jpg/.+$")
rgxJPG = re.compile(r"\.JPG/.+$")
resulting = []
category = []

def getRealImgURL(url):

	realURL = rgxThumb.sub('/', url)
	realURL = rgxJpg.sub('.jpg', realURL)
	realURL = rgxJPG.sub('.JPG', realURL) # wikipedia urls are case sensitive

	return realURL

def strip_ns(tree):
    for node in tree.iter():
        try:
            has_namespace = node.tag.startswith('{')
        except AttributeError:
            continue
        if has_namespace:
            node.tag = node.tag.split('}', 1)[1]

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	print ("Someone is at the home page.")
	return render_template('index.html')

@app.route('/description', methods=['POST'])
def my_link():
	index = request.form.get('n')
	# print (index)
	with open('results.txt', 'r') as f:
		data = f.read()

	data = data.splitlines()
	index2 = int(index)+1
	body = data[int(index):index2]
	body = str(body).split('^')
	# category = body[1]
	body = body[3]

	if not body:
		return '', 404
	else:
		return render_template('description.html', body=body), 200

@app.route('/nutrition', methods=['POST'])
def my_nutrition():
	search = request.form.get('n')
	index = request.form.get('i')
	search = search.split(" ")
	searchFact = []
	if len(search) > 1:
		for k in search:
			if "OR" in k or "AND" in k:
				continue
			else:
				searchFact.append(k)

	with open('results.txt', 'r') as f:
		data = f.read()

	data = data.splitlines()
	index2 = int(index)+1
	body = data[int(index):index2]
	body = str(body).split('^')

	category = body[1]

	if 'Fruits' in category or 'Desserts' in category:
		if len(searchFact) > 1:
			for k in searchFact:
				if k in body[3]:
					search = k
		rawpage = requests.get("https://api.nal.usda.gov/ndb/search/?format=xml&q="+str(search)+"&max=1&offset=0&ds=Standard%20Reference&api_key=UpWx85gGQQoabxNYrWtIf7eDJ4tQSwkzcllpAqwF")
	else:
		if len(searchFact) > 1:
			for k in searchFact:
				if k in body[0]:
					search = k
		rawpage = requests.get("https://api.nal.usda.gov/ndb/search/?format=xml&q=" +str(search)+ "&max=1&offset=0&ds=Standard%20Reference&api_key=UpWx85gGQQoabxNYrWtIf7eDJ4tQSwkzcllpAqwF")
	body = rawpage.content
	root = etree.fromstring(body)
	strip_ns(root)

	webUrl = root.xpath('//ndbno/text()')
	rawpage = requests.get("https://api.nal.usda.gov/ndb/reports/?ndbno="+webUrl[0]+"&type=b&format=xml&api_key=UpWx85gGQQoabxNYrWtIf7eDJ4tQSwkzcllpAqwF")
	body = rawpage.content
	root = etree.fromstring(body)
	strip_ns(root)

	webUrl = root.xpath('//nutrient')
	result = []
	for k in webUrl:
		name = k.get('name')
		unit = k.get('unit')
		value = k.get('value')
		nutrient = name+" "+value+" "+unit
		result.append(nutrient)

	# print(result)

	if not root:
		return '', 404
	else:
		return render_template('nutrients.html', results=result), 200

@app.route('/sources', methods=['POST'])
def my_source():
	index = request.form.get('n')
	# print (index)
	with open('results.txt', 'r') as f:
		data = f.read()

	data = data.splitlines()
	index2 = int(index)+1
	body = data[int(index):index2]
	body = str(body).split('^')
	body = body[4]
	# split string description into list of paragraphs

	# body = data[index][3].splitlines()
	if not body:
		return '', 404
	else:
		return render_template('sources.html', body=body), 200

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
			results.write("^")
		results.write('\n')
	results.close()
	# print(resulting)
	for result in resulting:
		if "None"  in result[2]:
			result[2] = "http://vignette3.wikia.nocookie.net/joke-battles/images/f/f0/Snacks-512.png/revision/latest?cb=20161115030953"
		result[2] = getRealImgURL(result[2])
		stuff = str(result[2]).split(".png")

		if len(stuff) > 1:
			result[2] = stuff[0]+".png"
		else:
			result[2] = str(stuff[0])

		stuff = str(result[2]).split(".jpeg")

		if len(stuff) > 1:
			result[2] = stuff[0] + ".jpeg"
		else:
			result[2] = str(stuff[0])

		stuff = str(result[2]).split(".jpg")

		if len(stuff) > 1:
			result[2] = stuff[0] + ".jpg"
		else:
			result[2] = str(stuff[0])

		stuff = str(result[2]).split(".JPG")

		if len(stuff) > 1:
			result[2] = stuff[0] + ".JPG"
		else:
			result[2] = str(stuff[0])

		stuff = str(result[2]).split(".svg")

		if len(stuff) > 1:
			result[2] = stuff[0] + ".svg"
		else:
			result[2] = str(stuff[0])

	if not resulting:
		# no results for search
		return '', 404
	elif len(resulting) is index:
		# client already has all results
		return '', 204
	else:
		# render results for client
		count = index + count
		return render_template('results.html', results=resulting[index:count], index=index), 200

if __name__ == '__main__':
	app.run(debug=True)