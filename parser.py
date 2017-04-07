# Giselle Gomez - giselle.gomez@wsu.edu
# Aaron Goin - aaron.goin@wsu.edu
# Ri "Richie" Zhang - ri.zhang@wsu.edu
# CS 483
# Web Scraper - Sweets, Fruits, Desserts

from lxml import etree, objectify
import requests
import sqlite3 as lite
import sys

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
#######                 End Grab Page and Format Output                   ########

#######         Start Build Database from Wiki Category                   ########
def tableFromWiki(table, category):
    image = None
    titles = []
    wiki = "https://en.wikipedia.org/w/api.php?"

    categoryURL = queryCategory(wiki, 'Category:'+category, 'max')
    root = format(categoryURL)
    webUrl = root.xpath('//cm')

    for k in webUrl:
        stuff = k.get('title')
        titles.append(stuff)

    with con: #   Let's create our table!
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " + table + "(Name STRING, Source STRING, Description STRING, Image STRING)")
        for k in titles:
            if 'template' not in k.lower() and 'category' not in k.lower():
                newVal = searchWikiURL(wiki, k, 1)
                newValForm = format(newVal)
                title = newValForm.xpath('/SearchSuggestion/Section/Item/Text/text()')  # Grab Title
                description = newValForm.xpath('/SearchSuggestion/Section/Item/Description/text()')  # Grab Description
                url = newValForm.xpath('/SearchSuggestion/Section/Item/Url/text()')
                imageTag = newValForm.xpath('//Image')  # Grab Image
                for k in imageTag:  # We have a list, and need to iter through it
                    image = k.get('source')
                if len(description) == 0:
                    cur.execute("INSERT INTO " + table + "(Name, Source, Description, Image) VALUES(?, ?, ?, ?)",
                                (title[0], url[0], 'None', str(image)))
                else:
                    cur.execute("INSERT INTO " + table + "(Name, Source, Description, Image) VALUES(?, ?, ?, ?)",
                            (title[0], url[0], description[0], str(image)))
#######         End Build Database from Wiki Category         #######

#######              START DATABASE BUILDING                  ####### 
def main():
    tableFromWiki('Sweets', 'Confectionery stubs')
    tableFromWiki('Desserts', 'Dessert stubs')
    tableFromWiki('Fruits', 'Fruit stubs')

#######                END DATABASE BUILDING                  ####### 

if __name__ == '__main__':
    main()