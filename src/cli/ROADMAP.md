# ROADMAP

## v0.2.0（进行中）— extract 重设计：信息→知识

当前 `extract` 是一条**文档→JSON** 的流水线：读入 `.md` 文件，发给 LLM，解析 JSON 落盘。
v0.2.0 将重新设计其语义模型——**输入抽象为信息，输出建模为知识**。

### 方向

| 方面 | 现状 | 目标 |
|------|------|------|
| 输入 | `.md` 文件目录 | 统一 **InformationSource** 接口（文档/结构化数据/对话等） |
| 处理 | 逐文件 LLM 调用，单阶段 | **多阶段管道**：语境理解→概念抽取→结构建模→验证→入库 |
| 输出 | 原始 LLM JSON，UUID 无溯源 | **KnowledgeItem** 模型，可溯源、已校验、可复用 |

### 设计

#### InformationSource — 统一信息接入

```python
class InformationSource(ABC):
    @abstractmethod
    def read(self) -> list[InformationChunk]: ...
```

内置实现：

| 实现 | 输入 | 说明 |
|------|------|------|
| `DocumentSource` | `.md` 文件目录 | 当前模式，保持不变 |
| `StructuredSource` | JSON / CSV / YAML | 直接解析为信息块 |
| `ConversationSource` | 对话记录 | 从问答中提取知识 |

#### 多阶段抽取管道

```
信息 → [语境理解] → [概念抽取] → [结构建模] → [验证] → [入库] → 知识
```

| 阶段 | 职责 |
|------|------|
| 语境理解 | 识别领域/视角，注入上下文 |
| 概念抽取 | 从信息中抽候选概念与关系（复用当前 LLM 能力） |
| 结构建模 | 将候选概念归入本体结构，建立 cross-reference |
| 验证 | 校验一致性、完整性、可复用标准 |
| 入库 | 去重、融合、持久化 |

#### 知识模型

```python
class KnowledgeItem(BaseModel):
    source_ref: list[str]   # 溯源：来自哪些信息块
    domain: Domain
    ontologies: list[Ontology]
    instances: list[Instance]
    context: str            # 抽取时的语境/视角说明
```

### 任务

- [ ] 定义 `InformationSource` 接口与 `InformationChunk` 模型
- [ ] `DocumentSource` 实现（封装当前文件读取逻辑）
- [ ] 拆分 `_extract_dir` 为多阶段子函数
- [ ] 新增语境理解阶段：自动识别领域视角
- [ ] 新增结构建模阶段：概念→本体归位
- [ ] 新增验证阶段：一致性检查
- [ ] 新增 `KnowledgeItem` 模型（含 `source_ref` 溯源）
- [ ] 写入时保留 `context.json` 语境记录
- [ ] 更新 `knowl_loader.py` 适配新模型
- [ ] 更新测试套件

## v0.3.0（规划）

- 支持多信息源联合抽取（如文档 + 结构化数据交叉建模）
- 增量抽取：基于已有知识库，只处理新增/变更的信息源
- 多格式导出：`--format yaml / markdown`
- 审计功能回归：基于新知识模型的审计
