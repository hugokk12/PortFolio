from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd


class VectorRetriever:
    def __init__(self):
        pass

    def read_csv(self, csv_path, embeddings_model, db_location):
        df = pd.read_csv(csv_path)
        self.db_location = db_location
        self.embeddings = OllamaEmbeddings(model=embeddings_model)
        self.add_documents = not os.path.exists(self.db_location)

        if self.add_documents:
            documents = []
            ids = []
            
            for i, row in df.iterrows():
                document = Document(
                    page_content=row["Title"] + " " + row["Review"],
                    metadata={"rating": row["Rating"], "date": row["Date"]},
                    id=str(i)
                )
                ids.append(str(i))
                documents.append(document)
            self.documents = documents
            self.ids = ids
    
    def create_vector_store(self):
                
        vector_store = Chroma(
            collection_name="restaurant_reviews",
            persist_directory=self.db_location,
            embedding_function=self.embeddings
        )

        if self.add_documents:
            vector_store.add_documents(documents=self.documents, ids=self.ids)
            
        self.retriever = vector_store.as_retriever(
            search_kwargs={"k": 5}
        )
