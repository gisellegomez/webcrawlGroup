# Giselle Gomez - giselle.gomez@wsu.edu
# Aaron Goin - aaron.goin@wsu.edu
# Ri "Richie" Zhang - ri.zhang@wsu.edu
# CS 483
# Index scraped sql db of Sweets, Fruits, Desserts and provide command-line searching

import os, os.path
import sqlite3 as lite
import whoosh
from whoosh.query import Variations
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import MultifieldParser

# input() is python 3 version of raw_input() in python 2
# this makes code work with both python 2 and 3
try:
    import __builtin__
    input = getattr(__builtin__, 'raw_input')
except (ImportError, AttributeError):
    pass

con = lite.connect('groupData.db')

#######                 Start Search                 ########
# Modified given code for indexing - just changed schema and print out
def search(indexer, searchTerm):
    with indexer.searcher() as searcher:
        query = MultifieldParser(["Name", "Image", "Description", "Source"], schema=indexer.schema, termclass=Variations).parse(searchTerm)
        results = searcher.search(query)
        print("\nLength of results: " + str(len(results)))
        print 'Here are the first 10 results:\n'
        print '{:<25}{:<60}{:<60}{:<60}'.format('Name', 'Image URL (may be shortened)', 'Description (may be shortened)', 'Source URL (may be shortened)')
        for line in results:
            #print (line['Name'] + " || " + line['Image'] + " || " + line['Description'] + " || " + line['Source'])
            print '{:<25}{:<60}{:<60}{:<60}'.format(line['Name'][0:24], line['Image'][0:59], line['Description'][0:59], line['Source'][0:59])
#######                 End Search                     ########

#######                 Start Indexing                 ########
# Modified given code for indexing - to add each table row by row to index
def index():
    print ('\nCreating new index...\n')
    c = con.cursor()
    schema = Schema(Name=TEXT(stored=True), Image=TEXT(stored=True), Description=TEXT(stored=True), Source=TEXT(stored=True))
    indexer = create_in('indexDir', schema)

    writer = indexer.writer()
    for row in c.execute('SELECT * FROM Sweets'):
        writer.add_document(Name=row[0], Image=row[3], Description=row[2], Source=row[1])
    for row in c.execute('SELECT * FROM Fruits'):
        writer.add_document(Name=row[0], Image=row[3], Description=row[2], Source=row[1])
    for row in c.execute('SELECT * FROM Desserts'):
        writer.add_document(Name=row[0], Image=row[3], Description=row[2], Source=row[1])
    writer.commit()
    return indexer
#######                 End Indexing                  ########

#######          START INTERACTIVE SEARCH             ######## 
def main():

    # remake index if told to or one does not already exist
    if not os.path.exists("indexDir"):
        os.mkdir("indexDir")
        indexer = index()
    elif len(sys.argv) > 1 and sys.argv[1] == 'redo':
        indexer = index()
    else:
        print ('\nOpening existing index...\n')
        indexer = open_dir("indexDir")


    # Keeps looping until you write exit or quit - then will 
    # stop prompting for search terms
    searchies = True
    while(searchies): 
        searchTerm = input('\nWhat would you like to search for? ("exit" to quit)\n')
        if 'exit' == searchTerm.lower():
            print("Exiting...")
            searchies = False
        else: results = search(indexer, searchTerm)
#######          END INTERACTIVE SEARCH                  ####### 

if __name__ == '__main__':
    main()