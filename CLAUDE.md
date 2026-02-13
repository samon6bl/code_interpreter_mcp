# Code Interpreter MCP Server

基于 **Streamable HTTP** 的 MCP 服务器，提供多语言代码执行能力。

## 环境设置

### 1. 激活虚拟环境

```bash
source .venv/bin/activate
```

### 2. 启动服务器

```bash
# 默认配置
python -m code_interpreter_mcp

# 自定义工作目录
WORKING_DIR=/tmp/my-workspace python -m code_interpreter_mcp

# 自定义端口
MCP_PORT=9000 python -m code_interpreter_mcp
```

服务器将在 `http://0.0.0.0:8000/mcp` 启动。

### 3. Claude Desktop 配置

在 `~/.config/claude/claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "code-interpreter": {
      "transport": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## 可用工具

| 工具 | 描述 |
|------|------|
| `execute_code` | 执行代码（支持 python/bash/c/cpp） |
| `list_languages` | 列出支持的语言及编译器路径 |
| `get_working_dir` | 获取工作目录和磁盘使用情况 |
| `write_file` | 在工作目录创建文件 |
| `list_files` | 列出目录内容 |

## 支持的语言

- **Python** (python3)
- **Bash/Shell** (bash/sh)
- **C** (gcc/clang)
- **C++** (g++/clang++)

## 快速测试

```bash
# 激活环境
source .venv/bin/activate

# 测试 Python 执行
python -c "
import asyncio
from code_interpreter_mcp.executors import PythonExecutor

async def test():
    exec = PythonExecutor()
    result = await exec.execute('print(\"Hello, World!\")')
    print(result)

asyncio.run(test())
"
```

## 部署

### systemd 服务

```ini
[Unit]
Description=MCP Code Interpreter Server
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/opt/mcp-code-interpreter
Environment="WORKING_DIR=/var/mcp-workspace"
Environment="MCP_HOST=0.0.0.0"
Environment="MCP_PORT=8000"
ExecStart=/opt/mcp-code-interpreter/.venv/bin/python -m code_interpreter_mcp
Restart=always

[Install]
WantedBy=multi-user.target
```

## ⚠️ 安全警告

此服务器**不实现沙箱或资源限制**，请在受控环境中运行：

- 使用 Docker 容器
- 使用 cgroups 限制资源
- 限制工作目录权限
- 定期清理工作目录
