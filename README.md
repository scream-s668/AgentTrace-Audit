# AgentTrace-Audit：AI Agent 行为审计与安全门禁系统

## 1. 项目简介
这是一个针对 LLM Agent（大语言模型智能体）的测试与拦截框架。
项目使用 Python 和 Pytest 编写，主要用于捕获 Agent 内部工具调用的轨迹（Trace），
并在违规操作发生前进行主动阻断。

## 2. 解决什么问题
传统测试只关注 Agent 的最终回复。但在实际业务中，大模型可能出现“嘴上拒绝，后台却偷偷调用退款接口”的越权行为，或者出现参数幻觉。
本项目通过记录 Agent 的结构化 Trace，并在高危动作（如执行退款）发生前增加一层确定性的代码门禁（Gatekeeper），防止资金流失。

## 3. 核心模块
- **黑匣子 (`audit/tracer.py`)**：记录 Agent 每一次工具调用的名称、参数、耗时和执行状态（尝试/拦截/成功），最终生成 JSON 证据文件。
- **策略门禁 (`audit/gatekeeper.py`)**：读取 `config/rules.yaml` 中的规则，检查高危操作的“前置条件”与“时序顺序”（例如：必须先查订单，才能退款）。
- **语义裁判 (`audit/judge.py`)**：调用真实大模型 API，对拦截时返回的客服话术进行礼貌度打分，防止语气不当。
- **被测系统 (`agent/workflow.py`)**：接入 DeepSeek API。内部设计了 `force_bad=True` 开关，用于在测试时强制绕过概率，走违规分支。

## 4. 如何运行
1. 安装依赖：
   `pip install pytest openai pyyaml`
2. 配置密钥：
   在 `agent/` 目录下新建 `secret_key.py` 文件，填入：`REAL_API_KEY = "sk-你的密钥"`（该文件已被 `.gitignore` 屏蔽，不会上传）。
3. 运行自动化测试：
   `pytest tests/test_behavior.py -s -v`

## 5. 测试用例说明
项目包含 3 个核心测试用例：
- `test_unauthorized_refund_is_blocked`：测未查订单直接退款的越权行为，断言门禁是否拦截，并检查数据库状态是否安全。
- `test_out_of_order_actions_are_blocked`：人工伪造乱序 Trace，断言门禁能否识别时序错误。
- `test_rejection_tone_is_polite`：测大模型裁判对拒绝话术的打分是否达标（>=8分）。

## 6. CI/CD 与降级机制
项目配置了 GitHub Actions 流水线，每次 Push 自动触发测试。
考虑到云端环境没有真实的 API Key，代码中加入了 `skipif` 跳过机制：本地运行结果为 `3 passed`，云端 CI 环境运行结果为 `2 passed, 1 skipped`，确保流水线稳定不报红。

## 7. 目录结构
```text
AgentTrace-Audit/
├── agent/        # 被测业务逻辑与工具
├── audit/        # 黑匣子、门禁、裁判等审计代码
├── config/       # YAML 策略配置
├── tests/        # Pytest 用例及生成的 Trace JSON
└── .github/      # CI 流水线配置
```
## 8. 局限与边界
- 目前仅覆盖单轮对话的时序与越权拦截。
- 底层业务采用 FAKE_DB 打桩，未接入真实数据库。
- 门禁规则目前仅支持简单的字段判断与索引比较。