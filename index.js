(function() {

	var lastSearch = "",
		haveAllResults = true,
		waitingForResults = false,
		scrolledAmount = 0;

	const
		searchField = document.getElementById('searchField'),
		resultsContainer = document.getElementById('resultsContainer'),
		feedback = document.getElementById('feedback'),
		viewBox = document.getElementById('viewBox'),

		Search = function(string, index, count) {
			var request = new XMLHttpRequest();
			request.onreadystatechange = function () {
				if (request.readyState === XMLHttpRequest.DONE) {
					switch (request.status) {
						case 200: // request returned successfully
							resultsContainer.innerHTML += request.response;
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
					}
				}
		    };
			//request.open('GET', '/search/' + string + '/' + index + '/' + count);
			request.open('GET', './test.html');
			request.responseType = 'text';
			request.send();
		},

// SEARCH BAR HANDLER
		onSearch = function(event) {
			if (searchField.value === "") {
				lastSearch = "";
				feedback.innerHTML = "You hungry?";
				resultsContainer.innerHTML = "";
			} else if (searchField.value !== lastSearch) {
				waitingForResults = true;
				lastSearch = searchField.value;
				feedback.innerHTML = "Waiting for results..."
				haveAllResults = false;
				Search(searchField.value, resultsContainer.children.length, 10);
			}

		},

// INFINITE SCROLLER HANDLER
		onScroll = function(event) {
		
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
				Search(lastSearch, resultsContainer.children.length, 10);
			}
		},
// NUTRITIONAL FACTS 
		getNutritionalInfo = function() {
			// TODO
		},
// EXPANDED VIEWBOX
		showViewBox = function(event) {
			// event.target should point to img
			if (event.target !== event.currentTarget) {
				document.body.className = "noscroll";
				viewBox.style.top = scrolledAmount + "px";
				viewBox.firstElementChild.src = event.target.src;
				viewBox.children[1].innerHTML = event.target.previousElementSibling.innerHTML;
				viewBox.style.display = "block";
			}
			
		},
		hideViewBox = function(event) {
			// make sure user clicked viewBox and not any of it's children
			if (event.target === event.currentTarget) {
				event.target.style.display = "none";
				document.body.className = "";
			}
		};
	
// HOOK EVERYTHING UP

	searchField.addEventListener('change', onSearch);
	viewBox.addEventListener('click', hideViewBox);
	resultsContainer.addEventListener('click', showViewBox);
	window.addEventListener('scroll', onScroll);


	window.onbeforeunload = function() {

		// cleanup all event listeners before we exit
		window.removeEventLister('scroll', onScroll);
		searchField.removeEventLister('change', onSearch);
		viewBox.removeEventLister('click', hideViewBox);
		resultsContainer.removeEventLister('click', showViewBox);
	}

})();