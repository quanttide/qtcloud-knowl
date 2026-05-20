from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class NameField:
    """唯一标识名（≤100），slug 风格。

    Usage:
        >>> from pydantic import BaseModel
        >>> class M(BaseModel):
        ...     name: NameField
        >>> m = M(name="my-project")
        >>> m.name
        'my-project'
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: type, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.str_schema(max_length=100)


class LabelField:
    """显示标签（≤50）。

    Usage:
        >>> from pydantic import BaseModel
        >>> class M(BaseModel):
        ...     label: LabelField
        >>> m = M(label="Active")
        >>> m.label
        'Active'
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: type, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.str_schema(max_length=50)


class DescriptionField:
    """描述（长文本）。

    Usage:
        >>> from pydantic import BaseModel
        >>> class M(BaseModel):
        ...     desc: DescriptionField
        >>> m = M(desc="some long text")
        >>> m.desc
        'some long text'
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: type, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.str_schema()


class Domain(BaseModel):
    """知识领域。

    一个领域代表一个知识领域的建模结果，包含本体、实例、关系。

    Usage:
        >>> d = Domain(id="org-gov", name="组织管理", perspective="组织管理视角",
        ...     files=["org-charter.md"], vocabulary=["权责", "流程"])
        >>> d.id
        'org-gov'
        >>> len(d.files)
        1
        >>> "权责" in d.vocabulary
        True
    """

    id: NameField = ""
    name: NameField = ""
    perspective: DescriptionField = ""
    files: list[str] = []
    vocabulary: list[str] = []


class Ontology(BaseModel):
    """本体定义。

    Usage:
        >>> o = Ontology(id="onto-1", name="role-auth", label="角色权责",
        ...     perspective="组织管理", description="角色与权责的对应关系",
        ...     pattern="角色以职责+权限成对定义",
        ...     source_files=["org-charter.md"])
        >>> o.name
        'role-auth'
        >>> o.label
        '角色权责'
    """

    id: str = ""
    name: NameField = ""
    label: LabelField = ""
    perspective: DescriptionField = ""
    description: DescriptionField = ""
    pattern: DescriptionField = ""
    source_files: list[str] = []


class Instance(BaseModel):
    """本体实例。

    Usage:
        >>> inst = Instance(id="inst-1", ontology="role-auth", subject="项目经理",
        ...     source="org-charter.md", article="第12条",
        ...     data={"principle": "负责项目全生命周期管理"})
        >>> inst.subject
        '项目经理'
        >>> inst.data["principle"]
        '负责项目全生命周期管理'
    """

    id: str = ""
    ontology: str = ""
    subject: str = ""
    source: str = ""
    article: str = ""
    data: dict = Field(default_factory=dict)


class Relation(BaseModel):
    """域间关系。

    Usage:
        >>> r = Relation(id="rel-1", source_ontology="role-auth", target_ontology="org-gov:approval",
        ...     relation="depends", description="角色权责依赖于审批流程定义")
        >>> r.relation
        'depends'
        >>> ":" in r.target_ontology
        True
    """

    id: str = ""
    source_ontology: str = ""
    target_ontology: str = ""
    source_instance: str = ""
    target_instance: str = ""
    relation: str = ""
    description: DescriptionField = ""
    detail: DescriptionField = ""
