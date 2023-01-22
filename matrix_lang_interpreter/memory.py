from typing import List, Optional, Dict
from dataclasses import dataclass


class Memory:
    def __init__(self):
        self.mem: Dict[str, any] = {}

    def has_key(self, key: str) -> bool:
        return key in self.mem

    def get(self, key: str) -> any:
        return self.mem[key]

    def put(self, key: str, value: any):
        self.mem[key] = value

class MemoryStack:
    def __init__(self, memory: Optional[Memory] = None):
        self.memories: List[Memory] = []
        if memory:
            self.memories.append(memory)

    def has_key(self, key: str) -> bool:
        for memory in reversed(self.memories):
            if memory.has_key(key):
                return True
        return False

    def get(self, key: str) -> any:
        for memory in reversed(self.memories):
            if memory.has_key(key):
                return memory.get(key)

    def insert(self, key: str, value: any):
        memory = self.memories[-1]
        memory.put(key, value)

    def set(self, key: str, value: any):
        for memory in reversed(self.memories):
            if memory.has_key(key):
                memory.put(key, value)

    def push(self, memory: Memory):
        self.memories.append(memory)

    def pop(self) -> Memory:
        return self.memories.pop()
