import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Set

import numpy as np  # Added import for numpy


@dataclass
class ConceptNode:
    node_id: str
    node_count: int
    type_count: int
    node_type: str  # thought / event / chat
    depth: int

    created: datetime
    expiration: Optional[datetime]
    last_accessed: datetime

    subject: str
    predicate: str
    object: str

    description: str
    embedding_key: str
    embedding_index: int  # Added to link to numpy array index
    poignancy: float
    keywords: Set[str]
    filling: List[str]

    def __str__(self):
        return (f"ConceptNode({self.node_id}, {self.node_count}, {self.type_count}, "
                f"{self.node_type}, {self.depth}, {self.created}, {self.expiration}, "
                f"{self.subject}, {self.predicate}, {self.object}, {self.description}, "
                f"{self.embedding_key}, {self.poignancy}, {self.keywords}, {self.filling})")

    def spo_summary(self):
        return (self.subject, self.predicate, self.object)


class AssociativeMemory(Memory):
    def __init__(self, f_saved):
        super().__init__()
        self.id_to_node: Dict[str, ConceptNode] = {}

        # Initialize data structures for different node types
        self.seq_nodes: Dict[str, List[ConceptNode]] = {'event': [], 'thought': [], 'chat': []}
        self.kw_to_nodes: Dict[str, Dict[str, List[ConceptNode]]] = {'event': {}, 'thought': {}, 'chat': {}}
        self.kw_strength: Dict[str, Dict[str, int]] = {'event': {}, 'thought': {}}

        # Embedding handling
        self.embedding_key_to_index: Dict[str, int] = {}  # Map embedding keys to indices in the numpy array
        self.embeddings = self._load_embeddings(f_saved + "/embeddings.json")

        # Load nodes and keyword strengths from files
        nodes_load = self._load_json(f_saved + "/nodes.json")
        for node_id, node_details in nodes_load.items():
            node = self._create_node_from_details(node_id, node_details)
            self.id_to_node[node_id] = node
            self._add_node_to_structures(node)

        kw_strength_load = self._load_json(f_saved + "/kw_strength.json")
        self.kw_strength['event'] = kw_strength_load.get('kw_strength_event', {})
        self.kw_strength['thought'] = kw_strength_load.get('kw_strength_thought', {})

    @staticmethod
    def _load_json(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)

    def _load_embeddings(self, filepath):
        # Load embeddings from JSON, convert to numpy array
        with open(filepath, 'r') as f:
            embeddings_dict = json.load(f)
        # Create a consistent ordering of embeddings
        sorted_items = sorted(embeddings_dict.items())
        embeddings_list = []
        for idx, (key, embedding) in enumerate(sorted_items):
            self.embedding_key_to_index[key] = idx
            embeddings_list.append(embedding)
        return np.array(embeddings_list)

    def _save_embeddings(self, filepath):
        # Save embeddings from numpy array back to dictionary format
        embeddings_dict = {key: self.embeddings[idx].tolist()
                           for key, idx in self.embedding_key_to_index.items()}
        self._save_json(filepath, embeddings_dict)

    def _create_node_from_details(self, node_id, node_details):
        created = datetime.strptime(node_details["created"], "%Y-%m-%d %H:%M:%S")
        expiration = (datetime.strptime(node_details["expiration"], "%Y-%m-%d %H:%M:%S")
                      if node_details["expiration"] else None)

        embedding_key = node_details["embedding_key"]
        embedding_index = self.embedding_key_to_index.get(embedding_key)

        return ConceptNode(
            node_id=node_id,
            node_count=node_details["node_count"],
            type_count=node_details["type_count"],
            node_type=node_details["type"],
            depth=node_details["depth"],
            created=created,
            expiration=expiration,
            last_accessed=created,
            subject=node_details["subject"],
            predicate=node_details["predicate"],
            object=node_details["object"],
            description=node_details["description"],
            embedding_key=embedding_key,
            embedding_index=embedding_index,
            poignancy=node_details["poignancy"],
            keywords=set(node_details["keywords"]),
            filling=node_details["filling"]
        )

    def _add_node_to_structures(self, node):
        node_type = node.node_type
        self.seq_nodes[node_type].insert(0, node)  # Insert at beginning to maintain order

        # Add to keyword mapping
        keywords = {kw.lower() for kw in node.keywords}
        for kw in keywords:
            self.kw_to_nodes[node_type].setdefault(kw, []).insert(0, node)

        # Update keyword strengths for events and thoughts
        if node_type in {'event', 'thought'} and f"{node.predicate} {node.object}".strip().lower() != "is idle":
            for kw in keywords:
                self.kw_strength[node_type][kw] = self.kw_strength[node_type].get(kw, 0) + 1

    def save(self, out_json):
        # Save nodes
        nodes_data = {}
        for node_id, node in self.id_to_node.items():
            nodes_data[node_id] = {
                "node_count": node.node_count,
                "type_count": node.type_count,
                "type": node.node_type,
                "depth": node.depth,
                "created": node.created.strftime("%Y-%m-%d %H:%M:%S"),
                "expiration": node.expiration.strftime("%Y-%m-%d %H:%M:%S") if node.expiration else None,
                "subject": node.subject,
                "predicate": node.predicate,
                "object": node.object,
                "description": node.description,
                "embedding_key": node.embedding_key,
                "poignancy": node.poignancy,
                "keywords": list(node.keywords),
                "filling": node.filling
            }
        self._save_json(out_json + "/nodes.json", nodes_data)

        # Save keyword strengths
        kw_strength_data = {
            'kw_strength_event': self.kw_strength['event'],
            'kw_strength_thought': self.kw_strength['thought']
        }
        self._save_json(out_json + "/kw_strength.json", kw_strength_data)

        # Save embeddings
        self._save_embeddings(out_json + "/embeddings.json")

    @staticmethod
    def _save_json(filepath, data):
        with open(filepath, 'w') as outfile:
            json.dump(data, outfile)

    def add_node(self, *, node_type, created, expiration, s, p, o, description,
                 keywords, poignancy, embedding_pair, filling):
        # Setup node counts and IDs
        node_count = len(self.id_to_node) + 1
        type_count = len(self.seq_nodes[node_type]) + 1
        node_id = f"node_{node_count}"
        depth = 0

        if node_type == 'thought':
            depth = 1
            if filling:
                depth += max((self.id_to_node[fill_id].depth for fill_id in filling if fill_id in self.id_to_node), default=0)

        embedding_key, embedding_vector = embedding_pair

        # Update embeddings numpy array
        if embedding_key in self.embedding_key_to_index:
            embedding_index = self.embedding_key_to_index[embedding_key]
            self.embeddings[embedding_index] = embedding_vector
        else:
            embedding_index = len(self.embeddings)
            self.embedding_key_to_index[embedding_key] = embedding_index
            # Append new embedding
            self.embeddings = np.vstack([self.embeddings, embedding_vector]) if self.embeddings.size else np.array([embedding_vector])

        node = ConceptNode(
            node_id=node_id,
            node_count=node_count,
            type_count=type_count,
            node_type=node_type,
            depth=depth,
            created=created,
            expiration=expiration,
            last_accessed=created,
            subject=s,
            predicate=p,
            object=o,
            description=description,
            embedding_key=embedding_key,
            embedding_index=embedding_index,
            poignancy=poignancy,
            keywords=set(keywords),
            filling=filling
        )

        self.id_to_node[node_id] = node
        self._add_node_to_structures(node)
        return node

    def add_event(self, **kwargs):
        return self.add_node(node_type='event', **kwargs)

    def add_thought(self, **kwargs):
        return self.add_node(node_type='thought', **kwargs)

    def add_chat(self, **kwargs):
        return self.add_node(node_type='chat', **kwargs)

    def get_summarized_latest_events(self, retention):
        return {node.spo_summary() for node in self.seq_nodes['event'][:retention]}

    def get_str_seq_events(self):
        return ''.join(
            f"Event {len(self.seq_nodes['event']) - idx}: {node.spo_summary()} -- {node.description}\n"
            for idx, node in enumerate(self.seq_nodes['event'])
        )

    def get_str_seq_thoughts(self):
        return ''.join(
            f"Thought {len(self.seq_nodes['thought']) - idx}: {node.spo_summary()} -- {node.description}\n"
            for idx, node in enumerate(self.seq_nodes['thought'])
        )

    def get_str_seq_chats(self):
        ret_str = ""
        for chat in self.seq_nodes['chat']:
            ret_str += f"with {chat.object} ({chat.description})\n"
            ret_str += f"{chat.created.strftime('%B %d, %Y, %H:%M:%S')}\n"
            for speaker, message in chat.filling:
                ret_str += f"{speaker}: {message}\n"
        return ret_str

    def retrieve_relevant_nodes(self, node_type, s_content, p_content, o_content):
        contents = {s_content.lower(), p_content.lower(), o_content.lower()}
        ret = set()
        kw_to_nodes = self.kw_to_nodes[node_type]
        for content in contents:
            ret.update(kw_to_nodes.get(content, []))
        return ret

    def retrieve_relevant_thoughts(self, s_content, p_content, o_content):
        return self.retrieve_relevant_nodes('thought', s_content, p_content, o_content)

    def retrieve_relevant_events(self, s_content, p_content, o_content):
        return self.retrieve_relevant_nodes('event', s_content, p_content, o_content)

    def get_last_chat(self, target_persona_name):
        kw = target_persona_name.lower()
        return self.kw_to_nodes['chat'].get(kw, [None])[0]

    def query_by_relevance(self, query_embedding, top_k):
        """
        Returns a dictionary mapping node_ids to cosine similarity scores for the top_k most similar embeddings.
        """
        if self.embeddings.size == 0:
            return {}

        # Normalize embeddings to unit vectors
        embeddings_norm = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        query_norm = query_embedding / np.linalg.norm(query_embedding)

        # Compute cosine similarities
        cosine_similarities = embeddings_norm @ query_norm

        # Get the top_k indices
        top_indices = np.argsort(-cosine_similarities)[:top_k]

        # Map indices back to node_ids
        index_to_key = {idx: key for key, idx in self.embedding_key_to_index.items()}
        top_nodes = {}
        for idx in top_indices:
            embedding_key = index_to_key[idx]
            # Find node_id(s) with this embedding_key
            node_ids = [node_id for node_id, node in self.id_to_node.items() if node.embedding_key == embedding_key]
            for node_id in node_ids:
                top_nodes[node_id] = cosine_similarities[idx]

        return top_nodes
