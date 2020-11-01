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



# https://code.activestate.com/recipes/410469-xml-as-dictionary/

class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):

    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})


tree = ElementTree.parse('../../../andy/Desktop/InformationRetrieval/pom.xml')
root = tree.getroot()
lijst = []
for i in root:
    lijst.append(XmlDictConfig(i))
print("ok")









# infile="smallTest.xml"
# context = etree.iterparse(infile, events=('end',), tag='title')
#
# for event, elem in context:
#     print('%s\n' % elem.text.encode('utf-8'))
# doc = etree.parse('smallTest.xml')
# # obj = untangle.parse('smallTest.xml')
# print(etree.tostring(doc))
# print("ok")
#
# for i in doc.getroot():
#     j =  etree.tostring(i)
#     dict_str = j.decode("UTF-8")

# print("ok")
lucene.initVM(vmargs=['-Djava.awt.headless=true'])
# Basic tokenizer example.
test = "This is euh how we do it."
dir= "directori/"


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
def indexiets(docList):
    store=openStore()
    writer=None
    try:
        analyzer =StandardAnalyzer()
        writer = getWriter(store, analyzer, True)
        for document in docList:
            doc = Document()
            for key in document:
                doc.add(Field(key, document[key],
                              TextField.TYPE_STORED))

            writer.addDocument(doc)

    finally:
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

indexiets(lijst)
query("decimal")
