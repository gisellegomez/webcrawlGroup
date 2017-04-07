from flask import Flask, render_template, url_for, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	print "Someone is at the home page."
	return render_template('welcome_page.html')

@app.route('/questions/')
def my_link():
	print 'I got clicked!'
	return 'Click.'

@app.route('/search/', methods=['GET', 'POST'])
@app.route('/search/<query>/<index>/<count>', methods=['GET', 'POST'])
def results():
	if request.method == 'POST':
		data = request.form
	else:
		data = request.args

	
	#query = request.form['searchterm']

	# search for query -> will get list of results
	# pass back count number of results starting at index in results list
	# render templates and combine into single string
	return render_template('results.html', query=query)

if __name__ == '__main__':
	app.run(debug=True)