import numpy as np
import ujson  # UltraJSON for faster JSON processing
import os

class EmbeddingStorage:
    """
    Stores embeddings and metadata in memory.

    Stores embeddings and corresponding metadata (recency, importance) in memory.
    Supports loading from and saving to a JSON Lines file.

    Attributes:
        records (list): A list of all records, where each record is a dictionary
            with keys 'id', 'embedding', 'recency', and 'importance'.
        embeddings_list (list): A list of embeddings.
        recencies_list (list): A list of recencies.
        importances_list (list): A list of importances.
        id_to_index (dict): A mapping from record ID to index.
    """

    def __init__(self):
        # Initialize storage structures
        self.records = []                # List of all records
        self.embeddings_list = []        # List of embeddings
        self.recencies_list = []         # List of recencies
        self.importances_list = []       # List of importances
        self.id_to_index = {}            # Mapping from record ID to index

    def load_from_jsonl(self, file_path):
        """Load records from a JSON Lines file."""
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return

        # Clear any existing data
        self.records.clear()
        self.embeddings_list.clear()
        self.recencies_list.clear()
        self.importances_list.clear()
        self.id_to_index.clear()

        with open(file_path, 'r') as f:
            for idx, line in enumerate(f):
                record = ujson.loads(line.strip())
                record_id = record['id']
                self.records.append(record)
                self.embeddings_list.append(record['embedding'])
                self.recencies_list.append(record['recency'])
                self.importances_list.append(record['importance'])
                self.id_to_index[record_id] = idx

    def save_to_jsonl(self, file_path):
        """Save records to a JSON Lines file."""
        with open(file_path, 'w') as f:
            for record in self.records:
                line = ujson.dumps(record)
                f.write(line + '\n')

    def insert(self, record):
        """Insert a new record."""
        record_id = record['id']
        if record_id in self.id_to_index:
            raise ValueError(f"Record with ID {record_id} already exists.")
        idx = len(self.records)
        self.records.append(record)
        self.embeddings_list.append(record['embedding'])
        self.recencies_list.append(record['recency'])
        self.importances_list.append(record['importance'])
        self.id_to_index[record_id] = idx

    def remove(self, record_id):
        """Remove a record by its ID."""
        if record_id not in self.id_to_index:
            raise ValueError(f"Record with ID {record_id} not found.")
        idx = self.id_to_index.pop(record_id)

        # Remove the record
        self.records.pop(idx)
        self.embeddings_list.pop(idx)
        self.recencies_list.pop(idx)
        self.importances_list.pop(idx)

        # Update id_to_index mapping for indices after the removed record
        for rec_id in self.id_to_index:
            rec_idx = self.id_to_index[rec_id]
            if rec_idx > idx:
                self.id_to_index[rec_id] = rec_idx - 1

    def update(self, record_id, new_record):
        """Update an existing record."""
        if record_id not in self.id_to_index:
            raise ValueError(f"Record with ID {record_id} not found.")
        idx = self.id_to_index[record_id]

        # Update the record
        self.records[idx] = new_record
        self.embeddings_list[idx] = new_record['embedding']
        self.recencies_list[idx] = new_record['recency']
        self.importances_list[idx] = new_record['importance']

        # Update ID mapping if the ID has changed
        new_record_id = new_record['id']
        if new_record_id != record_id:
            del self.id_to_index[record_id]
            self.id_to_index[new_record_id] = idx

    def query(self, x, alpha, beta, gamma, top_k):
        """
        Query the top_k records based on the combined score of recency, importance, and similarity.
        Score = alpha * recency + beta * importance + gamma * similarity(vector x, embedding)
        """
        n = len(self.embeddings_list)
        if n == 0:
            print("No records to query.")
            return []

        # Convert lists to NumPy arrays for vectorized operations
        embeddings_array = np.array(self.embeddings_list)
        recencies_array = np.array(self.recencies_list)
        importances_array = np.array(self.importances_list)

        # Normalize embeddings (if not already normalized)
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        embeddings_normed = embeddings_array / norms

        # Normalize query vector
        x = np.array(x)
        x_norm = np.linalg.norm(x)
        if x_norm == 0:
            x_norm = 1e-10
        x_normed = x / x_norm

        # Compute similarities
        similarities = embeddings_normed.dot(x_normed)

        # Compute combined scores
        scores = alpha * recencies_array + beta * importances_array + gamma * similarities

        # Use argpartition to get indices of top_k scores
        if top_k < n:
            top_k_indices = np.argpartition(-scores, top_k-1)[:top_k]
            # Sort the top_k indices
            top_k_indices = top_k_indices[np.argsort(-scores[top_k_indices])]
        else:
            # If top_k >= n, return all records sorted
            top_k_indices = np.argsort(-scores)

        # Retrieve corresponding records
        top_k_records = [self.records[i] for i in top_k_indices]
        return top_k_records
