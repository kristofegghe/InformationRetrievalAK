import lucene
import re

from java.nio.file import Path, Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer, StandardTokenizer
from org.apache.lucene.document import Document,Field,StoredField,StringField,TextField
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.index import DirectoryReader,IndexReader,IndexOptions,IndexWriterConfig,IndexWriter
from org.apache.lucene.store import FSDirectory,SimpleFSDirectory,MMapDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from lxml import etree



# https://code.activestate.com/recipes/410469-xml-as-dictionary/
lucene.initVM(vmargs=['-Djava.awt.headless=true'])


infile="../../../andy/Desktop/InformationRetrieval/pom.xml"

counter=0

def openStore():
    return SimpleFSDirectory(Paths.get("index/"))
def getWriter(store, analyzer=None, create=False):
    if analyzer is None:
        analyzer =StandardAnalyzer()
    analyzer = LimitTokenCountAnalyzer(analyzer, 10000)
    config = IndexWriterConfig(analyzer)
    # config.setInfoStream(PrintStreamInfoStream(System.out))
    if create:
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    return writer
def indexiets(infile,TitlemagNoneZijn, limit = 10000):
    try:
        context = etree.iterparse(infile)
    except:
        print("cannot open file: {}".format(infile))
        return
    store=openStore()
    writer=None
    p=re.compile(r'<.*?>')
    try:
        analyzer =StandardAnalyzer()
        writer = getWriter(store, analyzer, True)
        counter=0
        countwithtitle=0
        for event,elem in context:
            if(counter>150000):
                break
            print(counter)
            print(countwithtitle)
            counter+=1
            doc = Document()
            hasTitle=False
            for key in elem.attrib:
                # print(key)
                if key in ["CreationDate","Score","Body","CommentCount","LastActivityDate","Id","Tags","Title","AnswerCount","FavoriteCount"]:
                    if key =="Title":
                        # print(elem.attrib[key])
                        countwithtitle+=1
                        hasTitle=True

                    doc.add(Field(key, p.sub('',elem.attrib[key]),
                                      TextField.TYPE_STORED))
            if(hasTitle or TitlemagNoneZijn):
                writer.addDocument(doc)
            elem.clear()
            for ancestor in elem.xpath('ancestor-or-self::*'):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]

    finally:
        del context
        writer.close()

def preProcessSearchTerm(searchTerm):
    fuzzySearchTerm = ""
    listOfWords=searchTerm.split()
    for word in listOfWords:

        if len(word) < 5:
            percent = (len(word)-1)/len(word)
        elif len(word) < 10:
            percent = (len(word)-2)/len(word)
        else:
            percent = (len(word) - 3) / len(word)
        fuzzySearchTerm += "{}~{} ".format(word, percent-0.05)

    return fuzzySearchTerm

def query(searchTerm, limit = 50):
    store = openStore()
    reader=DirectoryReader.open(store)
    try:

        searcher = IndexSearcher(reader)
        spellCorrectionSearchTerm = preProcessSearchTerm(searchTerm)
        string= "(Title:{})^3 OR Body:{} OR (Tags:{})^2".format(spellCorrectionSearchTerm,spellCorrectionSearchTerm,spellCorrectionSearchTerm)
        query = QueryParser("Title", StandardAnalyzer()).parse(string)

        topDocs = searcher.search(query, limit)
        print(topDocs.scoreDocs)
        rank=1
        for i in topDocs.scoreDocs:
            print(i)

            print("rank {} : Title=".format(rank),searcher.doc(i.doc).get("Title"), ", with score {}".format(i.score))
            rank+=1
    finally:
        reader.close()

print("write '\q' to exit the program")
while True:
    ans1 = input("Do you want to 'index' data or ask a query answer with ('query' or 'index')?")
    while ans1 != "query" and ans1 != "index" and ans1 != "\q":
        ans1 = input("Answer with ('query' or 'index')")
    if ans1 == "query":
        ans2 = input("how many results do you want to receive?")
        if ans2 == "\q":
            break
        try:
            limit = int(ans2)
        except ValueError:
            print("you did not give a number so you will receive the top 50 results")
            limit = 50
        ans3 = input("give your search query")
        if ans3 == "\q":
            break
        query(ans3, limit)
    elif ans1 == "index":
        ans2 = input("give the relative path to the xml file with the data")
        if ans2 == "\q":
            break
        infile = ans2
        ans3 = input("Do you want to index results without a title answer with ('yes' or 'no')?")
        while ans3 != "yes" and ans3 != "no" and ans3 != "\q":
            ans3 = input("Answer with ('yes' or 'no')")
        if ans3 == "yes":
            removeEmptyTitle = False
        elif ans3 == "no":
            removeEmptyTitle = True
        else:
            break
        ans4 = input("how many documents do you want to index?")
        if ans4 == "\q":
            break
        try:
            limit = int(ans4)
        except ValueError:
            print("you did not give a number so you we will index the first 10 000 documents")
            limit = 10000
        indexiets(infile,removeEmptyTitle, limit)

    else:
        break