# import chromadb


# class Storage:
#     """数据库存储类"""
#     def __init__(self, event: str = None, content: str = None):
#         """
#         初始化存储

#         Args:
#             event(str): the event
#             content(str): the content of related case
#         """
#         self.chromadb = chromadb.Client()
#         self.collection = self.chromadb.create_collection(name="tizi365")
#         if content == None:
#             self.content = "Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters."
#         else:
#             self.content = content
#         self.add(self.content)

#     def add(self, text: str, embedding: list[float] = None):
#         """添加新的嵌入向量"""
#         print("Building database...")
#         texts = text.split('.')
#         self.collection.add(
#             documents=texts,
#             metadatas=[{"source": "my_source"} for _ in range(len(texts))],
#             ids=[f'id{i}' for i in range(len(texts))]
#         )
#         print("Build database successfully!")

#     def get_texts(self, query, num_result: int = 1) -> list[str]:
#         """
#         获取给定问题对应的文本
        
#         Args:
#             query(str): the query
#             num_result(int): the number of results queried
        
#         Return:
#             result(str): The results. Multiple results are concatenated into a single string.
#         """
#         tmp_results = self.collection.query(query_texts=query, n_results=num_result)
#         tmp_results = tmp_results['documents'][0]
#         result = ''
#         for single_result in tmp_results:
#             result += single_result
#         print("Query result: ", result)
#         return result

# if __name__ == '__main__':
#     storage = Storage()
#     query = "nuclear"
#     texts = storage.get_texts(query, 2)

from typing import List
import chromadb
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter


class Storage:
    """数据库存储类"""
    def __init__(self, event: str = 'default', case: str = "Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters."):
        """
        初始化存储

        Args:
            event(str): the event
            content(str): the content of related case
        """
        self.chromadb = chromadb.Client()
        self.collection = self.chromadb.create_collection(name=event)
        self.case = case
        self.get_contents()
        self.add(self.content)

    def add(self, texts: List[str], embedding: list[float] = None):
        """添加新的嵌入向量"""
        print("Building database...")
        self.collection.add(
            documents=texts,
            metadatas=[{"source": "my_source"} for _ in range(len(texts))],
            ids=[f'id{i}' for i in range(len(texts))]
        )
        print("Build database successfully!")

    def get_texts(self, query, num_result: int = 1) -> list[str]:
        """
        获取给定问题对应的文本
        
        Args:
            query(str): the query
            num_result(int): the number of results queried
        
        Return:
            result(str): The results. Multiple results are concatenated into a single string.
        """
        tmp_results = self.collection.query(query_texts=query, n_results=num_result)
        tmp_results = tmp_results['documents'][0]
        result = ''
        for single_result in tmp_results:
            result += single_result
        print("Query result: ", result)
        return result
    
    def get_contents(self):
        """
        Get related contents from internet.
        """
        loader = TextLoader("./doc-1.txt")
        docs = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(docs)
        self.content = [doc.page_content for doc in docs]

if __name__ == '__main__':
    storage = Storage()
    query = "nuclear"
    texts = storage.get_texts(query, 2)
