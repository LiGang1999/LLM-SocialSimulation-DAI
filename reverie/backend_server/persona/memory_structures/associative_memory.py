"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: associative_memory.py
Description: Defines the core long-term memory module for generative agents.

Note (May 1, 2023) -- this class is the Memory Stream module in the generative
agents paper.
"""

import json
import datetime
from enum import Enum
import numpy as np

from utils import *

from persona.memory_structures.memory import *


class ConceptNode:
    def __init__(
        self,
        node_id,
        node_type,
        created,
        expiration,
        s,
        p,
        o,
        description,
        embedding_key,
        poignancy,
        keywords,
        filling,
    ):
        self.node_id = node_id
        self.type = node_type  # thought / event / chat

        self.created = created
        self.expiration = expiration
        self.last_accessed = self.created

        self.subject = s
        self.predicate = p
        self.object = o

        self.description = description
        self.embedding_key = embedding_key
        self.poignancy = poignancy
        self.keywords = keywords
        self.filling = filling

    def __str__(self):
        return f"ConceptNode({self.node_id}, {self.type}, {self.created}, {self.expiration}, {self.subject}, {self.predicate}, {self.object}, {self.description}, {self.embedding_key}, {self.poignancy}, {self.keywords}, {self.filling})"

    def __repr__(self):
        return self.__str__()

    def spo_summary(self):
        return (self.subject, self.predicate, self.object)


class MemoryType(Enum):
    EVENT = 0
    THOUGHT = 1
    CHAT = 2


MAPPING = {
    "event": MemoryType.EVENT,
    "chat": MemoryType.CHAT,
    "thought": MemoryType.THOUGHT,
}


class AssociativeMemory(Memory):
    def __init__(self, f_saved):
        super().__init__()
        self.count = 0
        self.nodes = ([], [], [])
        self.kw_mappings = ({}, {}, {})
        self.embeddings = []
        self.embedding_keys = []

        # Load embeddings
        embedding_dict = json.load(open(f"{f_saved}/embeddings.json"))
        self.embedding_keys = list(embedding_dict.keys())
        self.embeddings = np.array(list(embedding_dict.values()))

        # Load nodes
        nodes_load = json.load(open(f"{f_saved}/nodes.json"))
        self.count = len(nodes_load)

        for node_id, node_details in nodes_load.items():
            self.add_node(
                node_details["type"],
                datetime.datetime.strptime(node_details["created"], "%Y-%m-%d %H:%M:%S"),
                datetime.datetime.strptime(node_details["expiration"], "%Y-%m-%d %H:%M:%S") if node_details["expiration"] else None,
                node_details["subject"],
                node_details["predicate"],
                node_details["object"],
                node_details["description"],
                set(node_details["keywords"]),
                node_details["poignancy"],
                node_details["embedding_key"],
                self.embeddings[node_details["embedding_key"]],
                node_details["filling"]
            )

    def save(self, out_json):
        nodes_dict = {
            str(node.node_id): {
                "type": node.type,
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
            for node_type in self.nodes
            for node in node_type
        }

        with open(f"{out_json}/nodes.json", "w") as f:
            json.dump(nodes_dict, f)

        with open(f"{out_json}/embeddings.json", "w") as f:
            json.dump({k: v.tolist() for k, v in zip(self.embedding_keys, self.embeddings)}, f)

    def add_node(
        self,
        node_type,
        created,
        expiration,
        s,
        p,
        o,
        description,
        keywords,
        poignancy,
        embedding_key,
        embedding_vec,
        filling,
    ):
        self.count += 1
        node_id = len(self.nodes[0]) + len(self.nodes[1]) + len(self.nodes[2]) + 1
        # Node type specific clean up.
        if "(" in description:
            description = " ".join(description.split()[:3]) + " " + description.split("(")[-1][:-1]

        # Creating the <ConceptNode> object.
        node = ConceptNode(
            node_id,
            node_type,
            created,
            expiration,
            s,
            p,
            o,
            description,
            embedding_key,
            poignancy,
            keywords,
            filling,
        )

        idx = MAPPING[node_type]

        # Creating various dictionary cache for fast access.
        self.nodes[idx][0:0] = [node]
        keywords = [i.lower() for i in keywords]
        for kw in keywords:
            if kw in self.kw_mappings[idx]:
                self.kw_mappings[idx][kw][0:0] = [node]
            else:
                self.kw_mappings[idx][kw] = [node]

        self.embeddings.append(embedding_vec)
        self.embedding_keys.append(embedding_key)

        return node

    def add_event(
        self,
        created,
        expiration,
        s,
        p,
        o,
        description,
        keywords,
        poignancy,
        embedding_key,
        embedding_vec,
        filling,
    ):
        return self.add_node(
            "event", created, expiration, s, p, o, description, keywords, poignancy, embedding_key, embedding_vec,
            filling
        )

    def add_thought(
        self,
        created,
        expiration,
        s,
        p,
        o,
        description,
        keywords,
        poignancy,
        embedding_key,
        embedding_vec,
        filling,
    ):
        return self.add_node(
            "thought", created, expiration, s, p, o, description, keywords, poignancy, embedding_key, embedding_vec,
            filling
        )

    def add_chat(
        self,
        created,
        expiration, 
        s,
        p,
        o,
        description,
        keywords,
        poignancy,
        embedding_key,
        embedding_vec,
        filling,
    ):
        return self.add_node(
            "chat", created, expiration, s, p, o, description, keywords, poignancy, embedding_key, embedding_vec,
            filling
        )

    def add_simple(self, node_type, description, embedding_vec, keywords):
        tm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.add_node(node_type, tm, tm, "", "", "", description, keywords, 0, description, embedding_vec, [])

    def get_summarized_latest_events(self, retention):
        ret_set = set()
        for e_node in self.seq_event[:retention]:
            ret_set.add(e_node.spo_summary())
        return ret_set
    
    def get_str_node(self, node_type):
        ret_str = ""
        m = MAPPING[node_type]
        n = self.nodes[m]
        for count, event in enumerate(n):
            ret_str += f"{'Event', len(n) - count, ': ', event.spo_summary(), ' -- ', event.description}\n"
        return ret_str

    def get_str_seq_events(self):
        return self.get_str_node("events")

    def get_thoughts(self):
        return self.seq_thought

    def get_str_seq_thoughts(self):
        return self.get_str_node("thoughts")

    def get_str_seq_chats(self):
        ret_str = ""
        n = self.nodes[MAPPING["chat"]]
        for count, event in enumerate(n):
            ret_str += f"with {event.object.content} ({event.description})\n"
            ret_str += f"{event.created.strftime('%B %d, %Y, %H:%M:%S')}\n"
            for row in event.filling:
                ret_str += f"{row[0]}: {row[1]}\n"
        return ret_str
    
    def retrieve_relevant_nodes(self, node_type, s, p, o):
        t = MAPPING[node_type]
        contents = [s, p, o]
        ret = []
        for i in contents:
            if i in self.kw_mappings[t]:
                ret += self.kw_mappings[t][i.lower()]
        ret = set(ret)
        return ret
    
    def retrieve_relevant_thoughts(self, s_content, p_content, o_content):
        return self.retrieve_relevant_nodes("thoughts", s_content, p_content, o_content)

    def retrieve_relevant_events(self, s_content, p_content, o_content):
        return self.retrieve_relevant_nodes("events", s_content, p_content, o_content)

    def retrieve_by_keywords(self, type, keywords):
        """
        Retrieve nodes of given type that match any of the keywords
        
        Args:
            type (str): Node type ("event", "thought", "chat")
            keywords (list): List of keywords to match
            
        Returns:
            list: Matching nodes sorted by creation date (newest first)
        """
        idx = MAPPING[type]
        matches = set()
        keywords = [k.lower() for k in keywords]
        
        for kw in keywords:
            if kw in self.kw_mappings[idx]:
                matches.update(self.kw_mappings[idx][kw])
        
        return sorted(matches, key=lambda x: x.created, reverse=True)

    def retrieve_by_sim(self, type, sentence, count):
        """
        Retrieve most similar nodes using embedding similarity
        
        Args:
            type (str): Node type ("event", "thought", "chat") 
            sentence (np.array): Query embedding vector
            count (int): Number of results to return
            
        Returns:
            list: Top matching nodes sorted by similarity
        """
        idx = MAPPING[type]
        nodes = self.nodes[idx]
        
        node_embeddings = np.array([self.embeddings[node.embedding_key] for node in nodes])
        similarities = np.dot(node_embeddings, sentence) / (
            np.linalg.norm(node_embeddings, axis=1) * np.linalg.norm(sentence)
        )
        top_indices = np.argsort(similarities)[-count:][::-1]
        return [nodes[i] for i in top_indices]


    def get_last_chat(self, target_persona_name):
        if target_persona_name.lower() in self.kw_to_chat:
            return self.kw_to_chat[target_persona_name.lower()][0]
        else:
            return False
