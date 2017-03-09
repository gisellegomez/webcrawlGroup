# Giselle Gomez - giselle.gomez@wsu.edu
# Aaron Goin - aaron.goin@wsu.edu
# Ri "Richie" Zhang - ri.zhang@wsu.edu
# CS 483
# Web Scraper - Sweets, Fruits, Desserts

from lxml import etree, objectify
import requests
import sqlite3 as lite
import sys
import whoosh
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser

con = lite.connect('groupData.db')

#######                             Start URL Builders                           #######
def setName():
    return 'includexmlnamespace=1'

def setProps(whatProp):
    return 'prop='+whatProp+'&'

def setPage(whatPage):
    return 'page='+whatPage+'&'

def setSection(whatSection):
    return 'section='+whatSection+'&'

def setAction(whatAction):
    return 'action='+whatAction+'&'

def setFormat(whatFormat):
    return 'format='+whatFormat+'&'

def searchFor(searchTerms, limit):
    return 'search='+searchTerms+'&limit='+str(limit)+'&'

def titles(whatTitles):
    listOfTitles = ''
    for title in whatTitles:
        listOfTitles += title+"|"
    return 'titles='+listOfTitles[:-1]+'&'

def getPage(url):
    page = requests.get(url)
    return page

def setCategory(category, limit):
    return 'cmtitle='+category+'&cmlimit=' + limit + '&cmdir=desc'

def searchWikiURL(wikiURL, searchTerms, limit):
    return wikiURL+setAction('opensearch')+setFormat('xml')+searchFor(searchTerms, limit)

def queryWikiURL(wikiURL, queryTerms):
    return wikiURL+setAction('query')+setFormat('xml')+titles(queryTerms)

def queryCategory(wikiURL, catTitle, limit):
    return wikiURL + setAction('query') + setFormat('xml') + 'list=categorymembers&' + setCategory(catTitle, limit)

def parseWikiURL(wikiURL, searchTerms, props, section):
    if section == None:     #   If there is no section provided, we're grabbing page sections
        return wikiURL+setAction('parse')+setFormat('xml')+setPage(searchTerms)+setProps(props)+setName()
    else:                   #   Else we're grabbing the links in the given section
        return wikiURL+setAction('parse')+setFormat('xml')+setPage(searchTerms)+setProps(props)+setSection(section)+setName()

#######                          End URL Builders                              #######

#######                        Start Create XML Tree                           #######
def strip_ns(tree):
    for node in tree.iter():
        try:
            has_namespace = node.tag.startswith('{')
        except AttributeError:
            continue
        if has_namespace:
            node.tag = node.tag.split('}', 1)[1]
#######                        End Create XML Tree                          ########

#######                 Start Grab Page and Format Output                   ########
def format(url):
    rawpage = getPage(url)
    page = rawpage.content          #   Grab content of output
    root = etree.fromstring(page)   #   Stringify the content
    strip_ns(root)                  #   Strip the root tag
    return root
#######                 Start Grab Page and Format Output                   ########

#######                 Start Search                 ########
# Modified given code for indexing - just changed schema and print out
def search(indexer, searchTerm):
    with indexer.searcher() as searcher:
        query = MultifieldParser(["Name", "Image", "Description", "Source"], schema=indexer.schema).parse(searchTerm)
        results = searcher.search(query)
        print("Length of results: " + str(len(results)))
        for line in results:
            print (line['Name'] + ": " + line['Image'] + " " + line['Description'] + " " + line['Source'])
#######                 End Search                     ########

#######                 Start Indexing                 ########
# Modified given code for indexing - to add each table row by row to index
def index(): 
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
#######                 End Indexing                 ########

def main():
    #######          START INTERACTIVE SEARCH              ####### 
    searchies = True
    indexer = index()

    searchTerm = input('What would you like to search for?\n')
    if 'quit' == searchTerm.lower() or 'exit' == searchTerm.lower():
        print("Exiting...")
        searchies = False

    # Keeps looping until you write exit or quit - then will 
    # stop prompting for search terms
    while(searchies): 
        results = search(indexer, searchTerm)
        searchTerm = input('\n What would you like to search for?\n')
        if 'quit' == searchTerm.lower() or 'exit' == searchTerm.lower():
            print("Exiting...")
            searchies = False
    #######          END INTERACTIVE SEARCH                  ####### 

    #######         START DATABASE BUILDING                  ####### 
    #
    #  Each section below is identical - due to using categories.
    #  It made it easier to just write the code for one category
    #  & then use it for each additional category
    #
    ###############################################################
    # image = None
    # titles = []
    # wiki = "https://en.wikipedia.org/w/api.php?"
    #
    # categoryURL = queryCategory(wiki, 'Category:Confectionery stubs', 'max')
    # root = format(categoryURL)
    # webUrl = root.xpath('//cm')
    #
    # for k in webUrl:
    #     stuff = k.get('title')
    #     titles.append(stuff)
    #
    # with con:                                       #   Let's create our table!
    #     cur = con.cursor()
    #     cur.execute("CREATE TABLE IF NOT EXISTS Sweets(Name STRING, Source STRING, Description STRING, Image STRING)")
    #     for k in titles:
    #         if 'template' not in k.lower() and 'category' not in k.lower():
    #             newVal = searchWikiURL(wiki, k, 1)
    #             newValForm = format(newVal)
    #             title = newValForm.xpath('/SearchSuggestion/Section/Item/Text/text()')  # Grab Title
    #             description = newValForm.xpath('/SearchSuggestion/Section/Item/Description/text()')  # Grab Description
    #             url = newValForm.xpath('/SearchSuggestion/Section/Item/Url/text()')
    #             imageTag = newValForm.xpath('//Image')  # Grab Image
    #             for k in imageTag:  # We have a list, and need to iter through it
    #                 image = k.get('source')
    #             if len(description) == 0:
    #                 cur.execute("INSERT INTO Sweets(Name, Source, Description, Image) VALUES(?, ?, ?, ?)",
    #                             (title[0], url[0], None, str(image)))
    #             else:
    #                 cur.execute("INSERT INTO Sweets(Name, Source, Description, Image) VALUES(?, ?, ?, ?)",
    #                         (title[0], url[0], description[0], str(image)))
    #
    # image = None
    # titles = []
    #
    # categoryURL = queryCategory(wiki, 'Category:Dessert stubs', 'max')
    # root = format(categoryURL)
    # webUrl = root.xpath('//cm')
    #
    # for k in webUrl:
    #     stuff = k.get('title')
    #     titles.append(stuff)
    #
    # with con:  # Let's create our table!
    #     cur = con.cursor()
    #     cur.execute("CREATE TABLE IF NOT EXISTS Desserts(Name STRING, Source STRING, Description STRING, Image STRING)")
    #     for k in titles:
    #         if 'template' not in k.lower() and 'category' not in k.lower():
    #             newVal = searchWikiURL(wiki, k, 1)
    #             newValForm = format(newVal)
    #             title = newValForm.xpath('/SearchSuggestion/Section/Item/Text/text()')  # Grab Title
    #             description = newValForm.xpath('/SearchSuggestion/Section/Item/Description/text()')  # Grab Description
    #             url = newValForm.xpath('/SearchSuggestion/Section/Item/Url/text()')
    #             imageTag = newValForm.xpath('//Image')  # Grab Image
    #             for k in imageTag:  # We have a list, and need to iter through it
    #                 image = k.get('source')
    #             if len(description) == 0:
    #                 cur.execute("INSERT INTO Desserts(Name, Source, Description, Image) VALUES(?, ?, ?, ?)",
    #                             (title[0], url[0], None, str(image)))
    #             else:
    #                 cur.execute("INSERT INTO Desserts(Name, Source, Description, Image) VALUES(?, ?, ?, ?)",
    #                         (title[0], url[0], description[0], str(image)))
    #
    # image = None
    # titles = []
    #
    # categoryURL = queryCategory(wiki, 'Category:Fruit stubs', 'max')
    # root = format(categoryURL)
    # webUrl = root.xpath('//cm')
    #
    # for k in webUrl:
    #     stuff = k.get('title')
    #     titles.append(stuff)
    #
    # with con:  # Let's create our table!
    #     cur = con.cursor()
    #     cur.execute("CREATE TABLE IF NOT EXISTS Fruits(Name STRING, Source STRING, Description STRING, Image STRING)")
    #     for k in titles:
    #         if 'template' not in k.lower() and 'category' not in k.lower():
    #             newVal = searchWikiURL(wiki, k, 1)
    #             newValForm = format(newVal)
    #             title = newValForm.xpath('/SearchSuggestion/Section/Item/Text/text()')  # Grab Title
    #             description = newValForm.xpath('/SearchSuggestion/Section/Item/Description/text()')  # Grab Description
    #             url = newValForm.xpath('/SearchSuggestion/Section/Item/Url/text()')
    #             imageTag = newValForm.xpath('//Image')  # Grab Image
    #             for k in imageTag:  # We have a list, and need to iter through it
    #                 image = k.get('source')
    #             if len(description) == 0:
    #                 cur.execute("INSERT INTO Fruits(Name, Source, Description, Image) VALUES(?, ?, ?, ?)",
    #                             (title[0], url[0], 'None', str(image)))
    #             else:
    #                 cur.execute("INSERT INTO Fruits(Name, Source, Description, Image) VALUES(?, ?, ?, ?)",
    #                         (title[0], url[0], description[0], str(image)))
    #######                END DATABASE BUILDING                ####### 

if __name__ == '__main__':
    main()