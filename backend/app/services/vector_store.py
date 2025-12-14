import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings
import os

class ProductVectorDB:
    def __init__(self):
        # Use persistent storage
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use Google's embedding model if available, otherwise default
        if settings.GOOGLE_API_KEY:
            self.ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=settings.GOOGLE_API_KEY)
        else:
            # Fallback to default (all-MiniLM-L6-v2)
            self.ef = embedding_functions.DefaultEmbeddingFunction()
            
        self.collection = self.client.get_or_create_collection(
            name="product_catalog",
            embedding_function=self.ef
        )

    def add_products(self, products: list[dict]):
        """
        Products should be a list of dicts with keys: id, name, details, price, etc.
        """
        ids = [str(p["sku"]) for p in products]
        documents = [f"{p['name']} - {p.get('details', '')}" for p in products]
        metadatas = []
        import json
        for p in products:
            meta = p.copy()
            # Flatten or stringify 'specs' because Chroma metadata must be primitives
            if "specs" in meta and isinstance(meta["specs"], dict):
                meta["specs"] = json.dumps(meta["specs"])
            metadatas.append(meta)
        
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query: str, k: int = 3) -> list[dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        if not results['documents'][0]:
            return []
            
        matches = []
        # Chromadb results are lists of lists (one list per query)
        for i in range(len(results['metadatas'][0])):
            item = results['metadatas'][0][i]
            # Chroma returns distance (smaller is better). 
            # We can convert to a similarity score if needed, but for now we keep distance.
            item['distance'] = results['distances'][0][i] 
            matches.append(item)
            
        return matches
