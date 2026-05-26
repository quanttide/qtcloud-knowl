# CONTRIBUTING

## 项目结构

project-root/
├── cmd/                  # 可执行程序入口（每个子目录一个 main 包）
│   ├── app/              #   → 构建出 app 二进制
│   │   └── main.go
│   └── cli/              #   → 构建出 cli 二进制
│       └── main.go
│
├── internal/             # 私有包（Go 编译器强制：外部无法导入）
│   ├── database/         #   数据库访问层
│   ├── service/          #   业务逻辑
│   └── handler/          #   HTTP 处理
│
├── pkg/                  # 公共包（可被外部项目导入）
│   └── knowledge/        #   如知识工程核心模型
│
├── api/                  # API 定义（protobuf / OpenAPI / REST）
├── configs/              # 配置文件模板
├── scripts/              # 构建/部署脚本
├── docs/                 # 文档
├── _examples/            # 用户演示示例（_ 前缀：go build 自动跳过编译）
│
├── go.mod                # module 声明
├── go.sum                # 依赖锁文件
├── Makefile              # 常用构建目标
└── README.md / CHANGELOG.md / ROADMAP.md / TODO.md
