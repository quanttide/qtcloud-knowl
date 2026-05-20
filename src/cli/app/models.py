from pydantic import BaseModel
from quanttide import NameField, LabelField, DescriptionField


class Domain(BaseModel):
    id: str = ""
    name: NameField = ""
    perspective: DescriptionField = ""
    files: list[str] = []
    vocabulary: list[str] = []


class Ontology(BaseModel):
    id: str = ""
    name: NameField = ""
    label: LabelField = ""
    perspective: DescriptionField = ""
    description: DescriptionField = ""
    pattern: str = ""
    source_files: list[str] = []


class Instance(BaseModel):
    id: str = ""
    ontology: str = ""
    subject: str = ""
    source: str = ""
    article: str = ""
    data: dict = {}


class Relation(BaseModel):
    id: str = ""
    source_ontology: str = ""
    target_ontology: str = ""
    source_instance: str = ""
    target_instance: str = ""
    relation: str = ""
    description: DescriptionField = ""
    detail: str = ""
