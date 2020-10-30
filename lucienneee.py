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
def indexiets():
    store=openStore()
    writer=None
    try:
        analyzer =StandardAnalyzer()
        writer = getWriter(store, analyzer, True)
        for filename in os.listdir(dir):
            f=open(dir+filename)
            lines=f.read()

            doc = Document()

            doc.add(Field("title", filename,
                          TextField.TYPE_STORED))
            doc.add(Field("zontent", str(lines),
                          TextField.TYPE_STORED))
            doc.add(Field("meta_words", "rabbits kanker 2are beautiful",
                          TextField.TYPE_NOT_STORED))
            writer.addDocument(doc)

    finally:
        writer.close()
        searcher = None
        try:
            reader=DirectoryReader.open(store)
            searcher = IndexSearcher(reader)
            query = QueryParser("zontent", StandardAnalyzer()).parse("panda")

            topDocs = searcher.search(query, 50)

            print(topDocs.scoreDocs)
            rank=1
            for i in topDocs.scoreDocs:

                print("rank {} : Title=".format(rank),searcher.doc(i.doc).get("title"), "with score {}".format(i.score))
                rank+=1
        finally:
            reader.close()

indexiets()
