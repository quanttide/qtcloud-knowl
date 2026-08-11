# 命令参考

qtcloud-knowl CLI（Rust，PyPI 包名 `qtcloud-knowl-cli`）。

## extract

```
qtcloud-knowl extract --source <文档.md> [--data-dir <目录>]
```

知识库抽取：从单篇 .md 文档生成知识库 JSON（domain/ontologies/instances），全程 LLM 驱动。

### 参数

| 选项 | 说明 |
|------|------|
| `--source` `-s` | 源文档 .md 文件路径（必填） |
| `--data-dir` | 知识库输出目录（默认 `data`，可用 `QTCLOUD_KNOWL_DATA_HOME` 覆盖） |

### 输出

```
抽取完成。保存至 {data-dir}/{文档名}.json。
```

生成 JSON 结构：`{"domain": {...}, "ontologies": [...], "instances": [...]}`，
条目字段为 `id`（UUID）/`name`/`label`/`description`，实例额外含 `ontology`。

## acquire

```
qtcloud-knowl acquire [--input <文件>] [--output <目录>]
```

知识获取与可编码性评估：从文档提取规则（1-5 评分）、可编码率、模糊点与编码问题清单。

### 参数

| 选项 | 说明 |
|------|------|
| `--input` | 输入文件路径（为空时读取默认源：bylaw/handbook/tutorial/profile） |
| `--output` | 输出目录（默认 `data`），写入 `extracted.yaml` |

## extract-by-type

```
qtcloud-knowl extract-by-type --input <本体.yaml> --type <类型> [--model <模型.yaml>]
```

本体抽取：按类型（cognition/todo/motif/annotate/worldbuilding/scene-graph/policy）将本体 YAML 编译为结构化产物。

### 参数

| 选项 | 说明 |
|------|------|
| `--input` `-i` | 本体 YAML 路径（必填） |
| `--type` `-t` | 抽取类型（必填） |
| `--model` `-m` | 模型声明 YAML 路径（约束 LLM 输出） |

## summary

```
qtcloud-knowl summary --input <知识.yaml> [--output <目录>]
```

知识总结：忠实总结现有知识，不生成新产物，输出 Markdown。

## 环境变量

| 变量 | 说明 |
|------|------|
| `QTCLOUD_KNOWL_LLM_API_KEY` | LLM API Key（兼容 `DEEPSEEK_API_KEY`） |
| `QTCLOUD_KNOWL_LLM_MODEL` | 模型（默认 `deepseek-chat`） |
| `QTCLOUD_KNOWL_LLM_BASE_URL` | Base URL（默认 DeepSeek 官方） |
| `QTCLOUD_KNOWL_DATA_HOME` | 数据目录（默认 `./data`） |
| `QTCLOUD_KNOWL_STATE_HOME` | 状态目录（默认 `data/.state`） |
