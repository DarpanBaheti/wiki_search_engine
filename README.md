# wiki_search_engine

Wiki Search Engine --
- A search engine, given a query output the most relevant pages.
- wiki dump 42GB data. XML format
- Requirements
	- query time < 1 sec
	- Indexing size 1/4th the size of original data
- Two phases
- phase 1:
	- XML SAX parser was used to read the documents.
	- Processing of documents:
	- Division of page into logical blocks: title, infobox, category, body, references etc
	- preprocessing the text
		- root, port stemming
		- stop words removal
		- tokenization
		//- NO syantax words (LOL)
	- regex for 
		- URLS
		- addresses
		- bold lines
		- quotes
	- word -> total_count;; doc1: count; doc2: count... (count sorted)
	- around 1000 files created, each file sorted on words
	- merge sort
		- delete previous files and create new 1000 files such that words are globally sorted
		- with secondary indexing that stores starting and ending word for each files
	- 7.2GB
- phase 2:
	- query preprocessing
	- tf-idf score (term frequency * inverse document frequency)
	// https://www.quora.com/How-does-TF-IDF-work
		score for a document, given a particular word:  		
		- tf: if doc contains M words, particular word occurs X times then tf = X/M
			- More occurence, more important the word in document 
		- idf: suppose total N documents, and this words occurs in K documents idf = log(N/K)
			- if occurs in all documents, the less important
			- therefore if K is high, N/K reaches 1 and idf = log(~1) reaches 0;
	- heuristics: different weights assigned to score on basis of in which block words is present: title, infobox, references.
	- 0.45 sec
- Pros and Cons
	- Particular song titles
	- Quotes
	- Syntactically corrent, but sematically ...
	- Supported fielded and non fielded queries
		- song titles: yesterday, ... 
