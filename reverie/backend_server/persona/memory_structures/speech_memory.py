from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
import json
from persona.memory_structures.vector_store import VectorStore

@dataclass
class SpeechRecord:
    speech_id: int
    speech: str
    keywords: List[str]
    date: datetime
    token_count: int
    speaker_name: str
    embedding: List[float]

class SpeechMemory:
    def __init__(self, json_path: str):
        self.vector_store = VectorStore(dim=3072)
        self.speeches: Dict[int, SpeechRecord] = {}
        self.text_to_id: Dict[str, int] = {}
        if json_path:
            self._load_speeches(json_path)
    
    def _load_speeches(self, json_path: str):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for idx, item in enumerate(data):
            speech_record = SpeechRecord(
                speech_id=idx,
                speech=item['speech'],
                keywords=item['keywords'],
                date=datetime.fromisoformat(item['date']),
                token_count=item['token_count'],
                speaker_name=item['speaker_name'],
                embedding=item['embedding']
            )
            
            self.speeches[idx] = speech_record
            self.text_to_id[item['speech']] = idx
            self.vector_store.add_vector(str(idx), item['embedding'])
    
    def get_by_id(self, speech_id: int) -> Optional[SpeechRecord]:
        return self.speeches.get(speech_id)
    
    def get_by_text(self, speech_text: str) -> Optional[SpeechRecord]:
        speech_id = self.text_to_id.get(speech_text)
        return self.speeches.get(speech_id) if speech_id is not None else None
    
    def query_similar(self, query_embedding: List[float], top_k: int) -> List[tuple[SpeechRecord, float]]:
        results = self.vector_store.query_vector(query_embedding, top_k)
        return [self.speeches[int(key)] for key, score in results]

    def get_str_summary(self):
        # print first 1 embeddings and length of all speech
        return f"First 1 embedding: {str(self.speeches[0].embedding)[:20]}... Length: {len(self.speeches)}"