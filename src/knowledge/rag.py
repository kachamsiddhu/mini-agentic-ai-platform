import os
import glob
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from rank_bm25 import BM25Okapi

class KnowledgeBase:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.documents = []
        self.vectorstore = None
        self.bm25 = None
        self.load_documents()

    def load_documents(self):
        docs = []
        runbook_dir = os.path.join(self.data_dir, "runbooks")
        if os.path.exists(runbook_dir):
            for file_path in glob.glob(f"{runbook_dir}/*.md"):
                loader = UnstructuredMarkdownLoader(file_path)
                docs.extend(loader.load())
        logs_dir = os.path.join(self.data_dir, "logs")
        if os.path.exists(logs_dir):
            for file_path in glob.glob(f"{logs_dir}/*.log"):
                loader = TextLoader(file_path)
                docs.extend(loader.load())
        if not docs:
            return
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.documents = text_splitter.split_documents(docs)
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key and api_key != "your_gemini_api_key_here":
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            self.vectorstore = FAISS.from_documents(self.documents, embeddings)
        tokenized_corpus = [doc.page_content.lower().split(" ") for doc in self.documents]
        if tokenized_corpus:
            self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, top_k: int = 3, filters: dict = None):
        results = []
        def matches_filters(metadata: dict) -> bool:
            if not filters:
                return True
            for k, v in filters.items():
                meta_val = metadata.get(k, "")
                src = metadata.get("source", "")
                if v.replace("-", "_") not in str(meta_val).replace("-", "_") and \
                   v.replace("-", "_") not in src.replace("-", "_"):
                    return False
            return True
        if self.vectorstore:
            v_results = self.vectorstore.similarity_search(query, k=top_k * 2)
            for doc in v_results:
                if matches_filters(doc.metadata):
                    results.append({"source": "faiss", "content": doc.page_content, "metadata": doc.metadata})
                    if len(results) >= top_k:
                        break
        if self.bm25:
            tokenized_query = query.lower().split(" ")
            bm25_docs = self.bm25.get_top_n(tokenized_query, self.documents, n=top_k * 2)
            for doc in bm25_docs:
                if matches_filters(doc.metadata):
                    results.append({"source": "bm25", "content": doc.page_content, "metadata": doc.metadata})
                    if len(results) >= top_k * 2:
                        break
        return results
