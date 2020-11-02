import lucene
import os

from java.io import StringReader,File
from java.nio.file import Path, Paths
from org.apache.lucene.analysis.ja import JapaneseAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer, StandardTokenizer
from org.apache.lucene.document import Document,Field,StoredField,StringField,TextField
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.index import DirectoryReader,IndexReader,IndexOptions,IndexWriterConfig,IndexWriter
from org.apache.lucene.store import FSDirectory,SimpleFSDirectory,MMapDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.queryparser.classic import QueryParser
from xml.etree import cElementTree as ElementTree
from lxml import etree



# https://code.activestate.com/recipes/410469-xml-as-dictionary/
lucene.initVM(vmargs=['-Djava.awt.headless=true'])


infile="../stackoverflow.com-Posts/Posts.xml"
context = etree.iterparse(infile)
counter=0








#
# infile="smallTest.xml"
# context = etree.iterparse(infile, events=('end',), tag='title')
#
# # for event, elem in context:
# #     print('%s\n' % elem.text.encode('utf-8'))
# # doc = etree.parse('smallTest.xml')
# # # obj = untangle.parse('smallTest.xml')
# # print(etree.tostring(doc))
# # print("ok")
# #
# # for i in doc.getroot():
# #     j =  etree.tostring(i)
# #     dict_str = j.decode("UTF-8")
#
# # print("ok")
# lucene.initVM(vmargs=['-Djava.awt.headless=true'])
# # Basic tokenizer example.
# test = "This is euh how we do it."
# dir= "directori/"
#

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
def indexiets(context):
    store=openStore()
    writer=None
    try:
        analyzer =StandardAnalyzer()
        writer = getWriter(store, analyzer, True)
        counter=0
        for event,elem in context:
            if(counter>1500000):
                break
            print(counter)
            counter+=1
            doc = Document()
            for key in elem.attrib:
                doc.add(Field(key, elem.attrib[key],
                                  TextField.TYPE_STORED))
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
        query = QueryParser("Title", StandardAnalyzer()).parse(searchTerm)

        topDocs = searcher.search(query, 50)

        print(topDocs.scoreDocs)
        rank=1
        for i in topDocs.scoreDocs:

            print("rank {} : Title=".format(rank),searcher.doc(i.doc).get("Title"), ", with score {}".format(i.score))
            rank+=1
    finally:
        reader.close()
indexiets(context)
# query("Javascript")
