import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from collections import deque

import numpy as np

from persona.memory_structures.memory import *
from persona.memory_structures.vector_store import VectorStore

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
    embedding_index: int  # Now maps to Faiss index ID
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
        self.seq_nodes: Dict[str, deque] = {'event': deque(), 'thought': deque(), 'chat': deque()}
        self.kw_to_nodes: Dict[str, Dict[str, deque]] = {'event': {}, 'thought': {}, 'chat': {}}
        self.kw_strength: Dict[str, Dict[str, int]] = {'event': {}, 'thought': {}}

        # Initialize vector store
        self.vector_store = VectorStore()
        self.vector_store.load(f_saved)

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

    def _save_json(self, filepath, data):
        with open(filepath, 'w') as outfile:
            json.dump(data, outfile)

    def _create_node_from_details(self, node_id, node_details):
        created = datetime.strptime(node_details["created"], "%Y-%m-%d %H:%M:%S")
        expiration = (datetime.strptime(node_details["expiration"], "%Y-%m-%d %H:%M:%S")
                     if node_details["expiration"] else None)

        # Use embedding key directly since we no longer need to map to index ID
        embedding_key = node_details["embedding_key"]

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
            embedding_index=-1,  # No longer used with new VectorStore
            poignancy=node_details["poignancy"],
            keywords=set(node_details["keywords"]),
            filling=node_details["filling"]
        )

    def _add_node_to_structures(self, node):
        node_type = node.node_type
        self.seq_nodes[node_type].appendleft(node)  # O(1)

        # Add to keyword mapping
        keywords = {kw.lower() for kw in node.keywords}
        for kw in keywords:
            self.kw_to_nodes[node_type].setdefault(kw, deque()).appendleft(node)  # O(1)

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

        # Save embeddings via vector store
        self.vector_store.save(out_json)

    def add_node(self, *, node_type, created, expiration, s, p, o, description,
                 keywords, poignancy, embedding_pair, filling):
        node_count = len(self.id_to_node) + 1
        type_count = len(self.seq_nodes[node_type]) + 1
        node_id = f"node_{node_count}"
        depth = 0

        if node_type == 'thought':
            depth = 1
            if filling:
                depth += max((self.id_to_node[fill_id].depth for fill_id in filling if fill_id in self.id_to_node), default=0)

        embedding_key, embedding_vector = embedding_pair
        
        # Add vector to vector store - no need to store index ID
        self.vector_store.add_vector(embedding_key, embedding_vector)

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
            embedding_index=-1,  # No longer used with new VectorStore
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
        return {node.spo_summary() for node in list(self.seq_nodes['event'])[:retention]}

    def get_seq_events(self):
        return list(self.seq_nodes['event'])

    def get_seq_chats(self):
        return list(self.seq_nodes['chat'])

    def get_seq_thoughts(self):
        return list(self.seq_nodes['thought'])

    def get_str_seq_events(self):
        lines = [
            f"Event {len(self.seq_nodes['event']) - idx}: {node.spo_summary()} -- {node.description}\n"
            for idx, node in enumerate(self.seq_nodes['event'])
        ]
        return ''.join(lines)

    def get_str_seq_thoughts(self):
        lines = [
            f"Thought {len(self.seq_nodes['thought']) - idx}: {node.spo_summary()} -- {node.description}\n"
            for idx, node in enumerate(self.seq_nodes['thought'])
        ]
        return ''.join(lines)

    def get_str_seq_chats(self):
        lines = []
        for chat in self.seq_nodes['chat']:
            lines.append(f"with {chat.object} ({chat.description})\n")
            lines.append(f"{chat.created.strftime('%B %d, %Y, %H:%M:%S')}\n")
            for speaker, message in chat.filling:
                lines.append(f"{speaker}: {message}\n")
        return ''.join(lines)

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
        return self.kw_to_nodes['chat'].get(kw, deque([None]))[0]

    def query_by_relevance(self, query_embedding, top_k):
        """
        Returns a dictionary mapping node_ids to similarity scores for the top_k most similar embeddings.
        """
        results = self.vector_store.query_vector(query_embedding, top_k)
        top_nodes = {}
        for embedding_key, score in results:
            # Find node_id(s) with this embedding_key
            node_ids = [node_id for node_id, node in self.id_to_node.items() 
                       if node.embedding_key == embedding_key]
            for node_id in node_ids:
                top_nodes[node_id] = score
        return top_nodes
