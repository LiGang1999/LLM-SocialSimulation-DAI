import faiss
import numpy as np
import json
import os

class VectorStore:
    def __init__(self, dim=None, hnsw_m=32):
        self.dim = dim
        self.index = None
        self.id_to_key = {}
        self.next_id = 0
        self.hnsw_m = hnsw_m  # HNSW parameter for the number of neighbors in graph

    def add_vector(self, key, vector):
        vector = np.asarray(vector, dtype='float32').reshape(1, -1)

        if self.dim is None:
            self.dim = vector.shape[1]
            # Initialize HNSW index for inner product similarity
        elif vector.shape[1] != self.dim:
            raise ValueError(f"Expected vector of dimension {self.dim}, got {vector.shape[1]}")

        if self.index is None:
            self.index = faiss.IndexHNSWFlat(self.dim, self.hnsw_m)
            
        # Normalize the vector for cosine similarity if needed
        faiss.normalize_L2(vector)
        self.index.add(vector)

        idx = self.next_id
        self.id_to_key[idx] = key
        self.next_id += 1
        return idx

    def query_vector(self, query_vector, top_k):
        if self.index is None or self.index.ntotal == 0:
            return []

        query_vector = np.asarray(query_vector, dtype='float32').reshape(1, -1)
        # Normalize the query vector if using cosine similarity
        faiss.normalize_L2(query_vector)

        D, I = self.index.search(query_vector, top_k)
        results = []
        for idx, dist in zip(I[0], D[0]):
            key = self.id_to_key.get(idx)
            if key is not None:
                results.append((key, dist))
        return results

    def save(self, filepath):
        os.makedirs(filepath, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, os.path.join(filepath, "faiss.index"))
        with open(os.path.join(filepath, "id_to_key.json"), 'w') as f:
            json.dump(self.id_to_key, f)

    def load(self, filepath):
        index_path = os.path.join(filepath, "faiss.index")
        id_to_key_path = os.path.join(filepath, "id_to_key.json")

        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            self.dim = self.index.d
            self.next_id = self.index.ntotal
        else:
            self.index = None
            self.dim = None
            self.next_id = 0

        if os.path.exists(id_to_key_path):
            with open(id_to_key_path, 'r') as f:
                self.id_to_key = {int(k): v for k, v in json.load(f).items()}
        else:
            self.id_to_key = {}
