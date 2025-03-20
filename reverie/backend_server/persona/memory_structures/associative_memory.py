"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: associative_memory.py
Description: Defines the core long-term memory module for generative agents.

Note (May 1, 2023) -- this class is the Memory Stream module in the generative
agents paper.
"""

import json
import datetime
from pathlib import Path
import numpy as np
import os

from persona.memory_structures.memory import Memory


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


# memory types
EVENT = 0
THOUGHT = 1
CHAT = 2
ARCHIVE = 3


MAPPING = {
    "event": EVENT,
    "chat": CHAT,
    "thought": THOUGHT,
    "archive": ARCHIVE,
}


class AssociativeMemory(Memory):
    def __init__(self, f_saved):
        super().__init__()
        self.nodes = []
        self.kw_mappings = ({}, {}, {}, {})
        self.id_mappings = ([], [], [], [])
        self.embeddings = np.zeros((0, 1536))
        self.embedding_keys = []

        f_path = Path(f_saved)
        if not f_path.exists():
            os.mkdir(str(f_path))

        if (f_path / "embeddings.npy").exists():
            embeddings = np.load(f"{f_saved}/embeddings.npy")
        else:
            embeddings = np.zeros((0, 1536))

        if (f_path / "embedding_keys.json").exists():
            embedding_keys = json.load(open(f"{f_saved}/embedding_keys.json"))
        else:
            embedding_keys = []

        if (f_path / "nodes.json").exists():
            nodes_load = json.load(open(f"{f_saved}/nodes.json"))
        else:
            nodes_load = []

        for idx, node in enumerate(nodes_load):
            self.add_node(
                node["type"],
                datetime.datetime.strptime(node["created"], "%Y-%m-%d %H:%M:%S"),
                datetime.datetime.strptime(node["expiration"], "%Y-%m-%d %H:%M:%S") if node["expiration"] else None,
                node["subject"],
                node["predicate"],
                node["object"],
                node["description"],
                set(node["keywords"]),
                node["poignancy"],
                embedding_keys[idx],
                embeddings[idx],
                node["filling"],
            )

    def save(self, out_json):
        nodes = [
            {
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
                "filling": node.filling,
            }
            for node_type in self.nodes
            for node in node_type
        ]

        with open(f"{out_json}/nodes.json", "w") as f:
            json.dump(nodes, f)

        np.save(f"{out_json}/embeddings.npy", self.embeddings)

        with open(f"{out_json}/embedding_keys.json", "w") as f:
            json.dump(self.embedding_keys, f)

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
        node_id = len(self.nodes)
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
        self.id_mappings[idx].append(node_id)
        self.embedding_keys.append(embedding_key)
        self.nodes.append(node)
        self.embeddings = np.append(self.embeddings, [embedding_vec], axis=0)
        keywords = [i.lower() for i in keywords]
        for kw in keywords:
            if kw in self.kw_mappings[idx]:
                self.kw_mappings[idx][kw][0:0] = [node.node_id]
            else:
                self.kw_mappings[idx][kw] = [node.node_id]
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
            "event",
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
            "thought",
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
            "chat",
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
        )

    def add_simple(self, node_type, description, embedding_vec, keywords):
        tm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.add_node(node_type, tm, tm, "", "", "", description, keywords, 0, description, embedding_vec, [])

    def get_summarized_latest_events(self, retention):
        ret_set = set()
        for e_id in self.id_mappings[EVENT][:retention]:
            e_node = self.nodes[e_id]
            ret_set.add(e_node.spo_summary())
        return ret_set

    def get_str_node(self, node_type):
        ret_str = ""
        m = MAPPING[node_type]
        ids = self.id_mappings[m]
        for id in ids:
            event = self.nodes[id]
            ret_str += f"{'Event', id, ': ', event.spo_summary(), ' -- ', event.description}\n"
        return ret_str

    def get_str_seq_events(self):
        return self.get_str_node("event")

    def get_events(self):
        return [self.nodes[id] for id in self.id_mappings[EVENT]]

    def get_thoughts(self):
        return [self.nodes[id] for id in self.id_mappings[THOUGHT]]

    def get_str_seq_thoughts(self):
        return self.get_str_node("thought")

    def get_str_seq_chats(self):
        ret_str = ""
        ids = self.nodes[CHAT]
        for id in ids:
            event = self.nodes[id]
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
            if i.lower() in self.kw_mappings[t]:
                ret += self.kw_mappings[t][i.lower()]
        ret = set(self.nodes[id] for id in ret)
        return ret

    def retrieve_relevant_thoughts(self, s_content, p_content, o_content):
        return self.retrieve_relevant_nodes("thought", s_content, p_content, o_content)

    def retrieve_relevant_events(self, s_content, p_content, o_content):
        return self.retrieve_relevant_nodes("event", s_content, p_content, o_content)

    def retrieve_by_keywords(self, type, keywords):
        """
        Retrieve nodes of given type that match any of the keywords

        Args:
            type (str): Node type ("event", "thought", "chat", "archive")
            keywords (list): List of keywords to match

        Returns:
            list: Matching nodes sorted by creation date (newest first)
        """
        idx = MAPPING[type]
        matches = set()
        keywords = [k.lower() for k in keywords]

        for kw in keywords:
            if kw in self.kw_mappings[idx]:
                matches.update(self.nodes[self.kw_mappings[idx][kw]])

        return matches

    def retrieve_by_sim(self, type, sentence, count=10):
        """
        Retrieve most similar nodes using embedding similarity

        Args:
            type (str): Node type ("event", "thought", "chat", "archive")
            sentence (np.array): Query embedding vector
            count (int): Number of results to return

        Returns:
            list: Top matching nodes sorted by similarity
        """
        idx = MAPPING[type]

        embedding_vec = np.array(sentence)
        similarities = np.dot(self.embeddings, embedding_vec) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(embedding_vec)
        )
        top_indices = np.argsort(similarities)[-count:][::-1]
        return [self.nodes[i] for i in top_indices if i in self.id_mappings[idx]]

    def get_last_chat(self, target_persona_name):
        if target_persona_name.lower() in self.kw_mappings[CHAT]:
            return self.kw_mappings[CHAT][target_persona_name.lower()][0]
        else:
            return False
