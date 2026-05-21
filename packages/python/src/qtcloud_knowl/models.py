from pydantic import BaseModel


class Domain(BaseModel):
    id: str = ""
    name: str = ""
    label: str = ""
    description: str = ""


class Ontology(BaseModel):
    id: str = ""
    name: str = ""
    label: str = ""
    description: str = ""


class Instance(BaseModel):
    id: str = ""
    name: str = ""
    label: str = ""
    description: str = ""


class Relation(BaseModel):
    id: str = ""
    name: str = ""
    label: str = ""
    description: str = ""
