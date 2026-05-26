# CONTRIBUTING

## 项目结构

每条目的标注含义：
- **[标准]** — Go 工具链强制约定
- **[社区]** — 社区广泛采用，多数项目遵守
- **[惯例]** — 不成文但实用的惯例

```
project-root/
├── cmd/                  # 可执行程序入口（每个子目录一个 main 包）
│   ├── app/              #   → 构建出 app 二进制
│   │   └── main.go
│   └── cli/              #   → 构建出 cli 二进制
│       └── main.go
│
├── internal/             # 私有包（[标准] 编译器强制外部无法导入）
│   ├── database/         #   数据库访问层
│   ├── service/          #   业务逻辑
│   └── handler/          #   HTTP 处理
│
├── pkg/                  # 公共包（[社区] 可供外部项目导入的稳定 API）
│   └── knowledge/
│
├── testdata/             # 测试 fixture 数据（[标准] go test 自动识别，编译跳过）
│
├── api/                  # API 定义文件（[社区] protobuf / OpenAPI / REST）
├── configs/              # 配置文件模板（[社区]）
├── scripts/              # 本地构建/部署脚本（[社区]）
├── docs/                 # 文档（[社区]）
├── _examples/            # 用户演示示例（[惯例] _ 前缀让 go build 跳过编译）
├── hack/                 # 代码生成/lint/准入脚本（[惯例] k8s 社区起源，现广泛使用）
├── third_party/          # 第三方依赖 fork 或原始副本（[惯例] Google 系项目起源）
├── tools/                # 项目依赖的工具链（[惯例] tools.go 锁定版工具版本）
│
├── go.mod                # [标准] module 声明
├── go.sum                # [标准] 依赖锁文件
├── Makefile              # [惯例] 常用构建目标
└── README.md / CHANGELOG.md / ROADMAP.md / TODO.md
```

### 标注来源说明

| 标注 | 依据 |
|------|------|
| **[标准]** | Go 语言规范或 `go` 工具链行为决定。如 `internal/` 的导入限制由 `go build` 强制，`testdata/` 的编译跳过由 `go test` 实现，`go.mod`/`go.sum` 由 `go mod` 管理 |
| **[社区]** | 多数 Go 项目遵守但没有编译器强制。如 `cmd/`、`pkg/` 来自《Standard Go Project Layout》；`api/`、`configs/`、`scripts/`、`docs/` 被 k8s、grpc-go、prometheus 等项目一致采用 |
| **[惯例]** | 有明确源头但并非主流共识。`_examples/` 的 `_` 前缀技巧源自标准库，`hack/` 源自 Kubernetes，`third_party/` 源自 Google 内部布局，`tools/` 源自 Go 1.11 的 toolchain 管理提案 |
