from typing import Any
from pydantic import BaseModel


class Domain(BaseModel):
    id: str = ""
    name: str = ""
    label: str = ""
    description: str = ""
    perspective: str = ""
    files: list[str] = []
    vocabulary: list[str] = []


class Ontology(BaseModel):
    id: str = ""
    name: str = ""
    label: str = ""
    description: str = ""
    perspective: str = ""
    pattern: str = ""
    source_files: list[str] = []


class Instance(BaseModel):
    id: str = ""
    name: str = ""
    label: str = ""
    description: str = ""
    ontology: str = ""
    subject: str = ""
    source: str = ""
    article: str = ""
    data: dict[str, Any] = {}


class Relation(BaseModel):
    id: str = ""
    name: str = ""
    label: str = ""
    description: str = ""
    source_ontology: str = ""
    target_ontology: str = ""
    source_instance: str = ""
    target_instance: str = ""
    relation: str = ""
    detail: str = ""
