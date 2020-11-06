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


infile="../stackoverflow.com-Posts/Posts.xml"
context = etree.iterparse(infile)
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
def indexiets(context,TitlemagNoneZijn):
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

def query(searchTerm):
    store = openStore()
    searcher = None
    try:
        reader=DirectoryReader.open(store)
        searcher = IndexSearcher(reader)
        string= "(Title:{})^3 OR Body:{} OR (Tags:{})^2".format(searchTerm,searchTerm,searchTerm)
        query = QueryParser("Title", StandardAnalyzer()).parse(string)

        topDocs = searcher.search(query, 50)
        print(topDocs.scoreDocs)
        rank=1
        for i in topDocs.scoreDocs:
            print(i)

            print("rank {} : Title=".format(rank),searcher.doc(i.doc).get("Title"), ", with score {}".format(i.score))
            rank+=1
    finally:
        reader.close()
indexiets(context,False)
# query('Statik Java')
