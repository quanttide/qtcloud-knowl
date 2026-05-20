import pytest
from pydantic import BaseModel, ValidationError

from qtcloud_knowl.models import Domain, Instance, NameField, Ontology, Relation


class TestNameField:
    def test_valid(self):
        class M(BaseModel):
            name: NameField

        m = M(name="valid-slug-name")
        assert m.name == "valid-slug-name"

    def test_default_to_empty_string(self):
        class M(BaseModel):
            name: NameField = ""

        m = M()
        assert m.name == ""

    def test_rejects_too_long(self):
        class M(BaseModel):
            name: NameField = ""

        with pytest.raises(ValidationError):
            M(name="x" * 101)


class TestDomain:
    def test_defaults(self):
        d = Domain()
        assert d.id == ""
        assert d.name == ""
        assert d.files == []

    def test_with_values(self):
        d = Domain(id="test", name="测试领域", perspective="测试", files=["a.md"], vocabulary=["v1", "v2"])
        assert d.id == "test"
        assert len(d.files) == 1
        assert len(d.vocabulary) == 2

    def test_model_dump(self):
        d = Domain(id="dump-test", name="dump")
        data = d.model_dump()
        assert data["id"] == "dump-test"
        assert data["name"] == "dump"


class TestOntology:
    def test_defaults(self):
        o = Ontology()
        assert o.id == ""
        assert o.source_files == []

    def test_with_values(self):
        o = Ontology(id="o1", name="test-onto", label="测试", pattern="pattern")
        assert o.pattern == "pattern"
        assert o.label == "测试"

    def test_label_too_long(self):
        with pytest.raises(ValidationError):
            Ontology(label="x" * 51)


class TestInstance:
    def test_defaults(self):
        inst = Instance()
        assert inst.data == {}

    def test_data_defaults_to_empty(self):
        inst = Instance(id="i1", ontology="o1", subject="subj")
        assert inst.data == {}

    def test_model_dump_excludes_data_keys_not_in_standard(self):
        inst = Instance(id="i1", ontology="o1", subject="s", source="src", article="art", data={"extra": "val"})
        dumped = inst.model_dump()
        assert dumped["id"] == "i1"
        assert dumped["data"]["extra"] == "val"


class TestRelation:
    def test_defaults(self):
        r = Relation()
        assert r.relation == ""

    def test_cross_domain_target(self):
        r = Relation(source_ontology="o1", target_ontology="other-domain:o2", relation="depends")
        assert ":" in r.target_ontology

    def test_model_dump(self):
        r = Relation(id="r1", source_ontology="o1", target_ontology="o2", relation="links")
        dumped = r.model_dump()
        assert dumped["relation"] == "links"
