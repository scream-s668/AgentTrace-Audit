# AgentTrace-Audit: AI Agent 行为审计与安全门禁系统

## 📖 项目背景与痛点
在 LLM Agent（智能体）的实际业务落地中，传统测试面临巨大挑战：
1. **黑盒不可见**：大模型的思考和工具调用是黑盒，只看最终回复无法发现“口头拒绝、后台乱扣钱”的越权行为。
2. **结果非确定**：大模型具有随机性，传统的断言（Assert）极易失效，导致 CI/CD 中出现大量的 Flaky Test（不稳定测试）。
3. **语义难校验**：拦截或拒绝时的语气是否礼貌，传统代码无法判断。

项目在构建一套轻量级的 **Agent 行为审计框架**，通过结构化 Trace 记录、YAML 策略门禁拦截、以及大模型语义裁判，实现对 Agent 执行过程的全链路质量保障。

## 🛠️ 技术栈
- **语言与环境**：Python 3.12, Conda
- **测试框架**：Pytest
- **大模型交互**：OpenAI SDK (接入 DeepSeek-V3 API)
- **数据驱动**：PyYAML (策略配置分离)
- **架构模式**：依赖注入、Mock 打桩、LLM-as-a-Judge

## ✨ 核心架构与亮点
- `agent/`: **被测业务系统**。包含真实大模型调用逻辑，并保留了 `force_bad` 开关，用于消除大模型随机性，实现稳定的回归测试。
- `audit/tracer.py`: **黑匣子组件**。无侵入式记录 Agent 每一步的工具调用（包含工具名、参数、耗时、执行状态），沉淀为 JSON 证据链。
- `audit/gatekeeper.py`: **安全门禁引擎**。读取 YAML 规则，在业务副作用（如修改数据库）发生前进行前置校验，不仅能拦截“越权调用”，还能拦截“时序错误（先退款后查单）”。
- `audit/judge.py`: **大模型语义裁判**。调用大模型对 Agent 拒答话术的礼貌度进行 0-10 分打分评估。
- `.github/workflows/`: **CI/CD 流水线**。配置了 GitHub Actions，每次 push 代码自动触发 Pytest 回归测试，确保代码质量。

## 🚀 快速开始

## 🔄 CI/CD 自动化集成
本项目已接入 **GitHub Actions**。每次代码 Push 或提交 Pull Request，都会自动触发流水线：
1. 自动搭建 Ubuntu + Python 3.12 环境。
2. 安装 `requirements.txt` 依赖。
3. 自动执行 `pytest` 全量回归测试。
*(注：考虑到 CI 环境的数据安全，语义裁判测试用例在无大模型 API 的环境下会自动 Skip，确保流水线 100% 稳定绿通。)*

### 1. 环境准备
```bash
# 创建并激活虚拟环境
conda create -n ai_test python=3.12 -y
conda activate ai_test

# 安装依赖
pip install pytest openai pyyaml