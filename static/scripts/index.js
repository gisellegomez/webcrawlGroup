(function() {

	var MAX_RESULTS = 20,
		MIN_RESULTS = 6,
		NETWORK = {
			avg: 250, // network latency in milliseconds
			n: 1 // number of requests sent (starts at 1 so we don't divide by 0)
		},
		lastSearch = "",
		haveAllResults = true,
		waitingForResults = false,
		scrolledAmount = 0;

	const
		searchField = document.getElementById('searchField'),
		resultsContainer = document.getElementById('resultsContainer'),
		feedback = document.getElementById('feedback'),
		viewBox = document.getElementById('viewBox'),
		viewBoxBtn = document.getElementById('viewBoxBtn'),
		boxTitle = document.getElementById('boxTitle'),
		boxImg = document.getElementById('boxImg'),
		boxNutrition = document.getElementById('boxNutrition'),
		boxDetails = document.getElementById('boxDetails'),

		speedTest = function(delta) {
			// get time passed 
			delta = window.performance.now() - delta;
			// calculate cumulative average
			NETWORK.avg = (delta + NETWORK.avg * NETWORK.n) / ++(NETWORK.n);
			// MAX_RESULTS is larger of:
			// square root of average latency truncated into an integer
			// or 6
			MAX_RESULTS = Math.max( Math.sqrt(NETWORK.avg)|0, MIN_RESULTS);

			//console.log("Network avg latency: " + NETWORK.avg + "\nResults max: " + MAX_RESULTS);
		},

		appendResults = function(results) {
		// using documentFragments and appending avoids resetting the entire DOM and preserves scroll position
		// but data retrieved from server as html string and needs to be parsed before appending
			
			var temp = document.createElement('div'),
				fragment = document.createDocumentFragment();
			
			// parse results into DOM Nodes using temp div
			temp.innerHTML = results;
			
			// move now parsed results from the div into the fragment
			while (temp.firstElementChild) fragment.appendChild(temp.removeChild(temp.firstElementChild));

			// appending a documentFragment into the DOM replaces itself with it's children
			// leaving no trace of the fragment in the live DOM
			resultsContainer.appendChild(fragment);
		}

		requestSearch = function(string, index, count) {

			var request = new XMLHttpRequest(),
				delta;

			request.onreadystatechange = function () {
				if (request.readyState === XMLHttpRequest.DONE) {
					speedTest(delta);
					switch (request.status) {
						case 200: // request returned successfully
							appendResults(request.response);
							waitingForResults = false;
							break;
						case 204: // no additional results for search
							feedback.innerHTML = "No more results.";
							haveAllResults = true;
							break;
						case 404: // no results at all for search string
							feedback.innerHTML = "No results.";
							haveAllResults = true;
							break;
						default:
							feedback.innerHTML = "Cannot complete search.";
							break;
					}
				}
		    };
			request.open('POST', '/results', true);
			request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
			request.responseType = 'text';
			request.send('query=' + string + '&index=' + index + '&count=' + count);

			// time our request
			// performance.now() is a DOMHighResTimeStamp, measured in milliseconds, accurate to five thousandths of a millisecond
			delta = window.performance.now();
		},

		requestDescription = function(index) {
			var request = new XMLHttpRequest(),
				delta;

			request.onreadystatechange = function () {
				if (request.readyState === XMLHttpRequest.DONE) {
					speedTest(delta);
					switch (request.status) {
						case 200: // request returned successfully
							boxDetails.innerHTML = request.response;
							break;
						default:
							boxDetails.innerHTML = 'Cannot retrieve description.';
							break;
					}
				}
		    };
			request.open('POST', '/description', true);
			request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
			request.responseType = 'text';
			request.send('n=' + index);

			delta = window.performance.now();
		}

		requestSources = function(index) {
			var request = new XMLHttpRequest(),
				delta;

			request.onreadystatechange = function () {
				if (request.readyState === XMLHttpRequest.DONE) {
					speedTest(delta);
					switch (request.status) {
						case 200: // request returned successfully
							boxSources.innerHTML = request.response;
							break;
						default:
							boxSources.innerHTML = 'Cannot retrieve Sources.';
							break;
					}
				}
		    };
			request.open('POST', '/sources', true);
			request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
			request.responseType = 'text';
			request.send('n=' + index);

			delta = window.performance.now();
		}

		handleSearch = function(event) {

			// empty search resets page
			if (searchField.value === "") {

				lastSearch = "";
				feedback.innerHTML = "You hungry?";
				resultsContainer.innerHTML = "";

			} else if (searchField.value !== lastSearch) {
			    lastSearch = "";
			    resultsContainer.innerHTML = "";
				waitingForResults = true;
				lastSearch = searchField.value;
				feedback.innerHTML = "Waiting for results..."
				haveAllResults = false;
                requestSearch(searchField.value, resultsContainer.children.length, MAX_RESULTS);
			}

		},

		getMoreResults = function(event) {
		
			var totalHeight,
				visibleHeight;

			// get amount user has scrolled down (in pixels)
			if (window.pageYOffset !== undefined) scrolledAmount = window.pageYOffset;
			else if (document.documentElement) scrolledAmount = document.documentElement.scrollTop;
			else scrolledAmount = document.body.scrollTop;

			if (waitingForResults || haveAllResults || searchField.value === "") return;

			totalHeight = document.body.clientHeight;
			visibleHeight = window.innerHeight;

			// if user close enough to bottom: get more results
			if ((totalHeight - scrolledAmount) < (visibleHeight + 200)) {
				waitingForResults = true;
				requestSearch(lastSearch, resultsContainer.children.length, MAX_RESULTS);
			}

			return false;
		},

		getNutritionalInfo = function(value, index) {
			var request = new XMLHttpRequest(),
				delta;

			request.onreadystatechange = function () {
				if (request.readyState === XMLHttpRequest.DONE) {
					speedTest(delta);
					switch (request.status) {
						case 200: // request returned successfully
							boxNutrition.innerHTML = request.response;
							break;
						default:
							boxNutrition.innerHTML = 'No nutritional info found.';
							break;
					}
				}
		    };
			request.open('POST', '/nutrition', true);
			request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
			request.responseType = 'text';
			request.send('n=' + value +'&i=' + index);
            console.log(value)
			delta = window.performance.now();
		},

		showViewBox = function(event) {
			// event.target should point to img
			if (event.target !== event.currentTarget) {
				document.body.className = "noscroll";
				viewBox.style.top = scrolledAmount + "px";
				boxImg.src = event.target.src; // set image source
				boxTitle.innerHTML = event.target.previousElementSibling.innerHTML;

				getNutritionalInfo(searchField.value, event.target.parentElement.dataset.index);
				boxDetails.innerHTML = "Retrieving details...";

				// request full text from server
				requestDescription(event.target.parentElement.dataset.index);

				boxSources.innerHTML = "Retrieving details...";
				requestSources(event.target.parentElement.dataset.index);

				// this keeps our image scaled the right way
				if (window.innerWidth > window.innerHeight) viewBox.firstElementChild.className = 'widescreen';
				else viewBox.firstElementChild.className = 'portrait';

				viewBox.style.display = "block";
			}
			
		},

		hideViewBox = function(event) {
			// make sure user clicked viewBox and not any of it's children
			if (event.target === event.currentTarget || event.target === viewBoxBtn) {
				viewBox.style.display = "none";
				document.body.className = "";
			}
		};
	

	// hook up our event listeners
	window.addEventListener('scroll', getMoreResults);
	searchField.addEventListener('change', handleSearch);
	resultsContainer.addEventListener('click', showViewBox);
	viewBox.addEventListener('click', hideViewBox);
	viewBoxBtn.addEventListener('click', hideViewBox);


	window.onbeforeunload = function() {
		// cleanup all event listeners before we exit
		window.removeEventListener('scroll', getMoreResults);
		searchField.removeEventListener('change', handleSearch);
		resultsContainer.removeEventListener('click', showViewBox);
		viewBox.removeEventListener('click', hideViewBox);
		viewBoxBtn.removeEventListener('click', hideViewBox);
	}

})();