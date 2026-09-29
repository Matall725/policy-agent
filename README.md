# Policy Agent - 政策文本解析与匹配工具

把冗长、非结构化的政府与产业政策文件，自动解析成结构化字段，并根据用户实际情况完成申报条件匹配与评估。

输入一段政策原文，得到一份可核对的申报资格清单；输入多份政策，得到一张可导出的对比表。

---

## 解决什么问题

政策文件通常篇幅长、条件分散，申报人需要逐条比对自身资质。这个工具把这件事拆成两步：

1. **信息抽取**：把政策原文转成结构化数据（申报对象、扶持力度、截止日期、逐条申报条件、所需材料）。
2. **条件匹配**：根据用户对每条条件的回答，判断是否符合申报要求，给出差距分析与行动建议。

## 功能特性

- 政策原文一键结构化，输出固定字段的 JSON。
- 根据抽取出的条件自动生成资格自测表单（选择题 / 数值题）。
- 匹配度评分、是否符合、未满足条件分析、申报行动指南。
- 批量解析多份政策，生成对比表。
- 支持导出 Markdown 报告与 CSV 对比表。
- 兼容任意 OpenAI 格式接口（DeepSeek、OneAPI、OpenAI 等）。

## 系统架构

```text
                 ┌────────────────┐
                 │    用户输入     │
                 └───────┬────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │     Prompt 层         │
              │  extractor / matcher │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │     LLM 客户端        │
              │  结构化输出 + 降级     │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   响应解析 Parsers    │
              │ 提取 JSON / 去 Markdown│
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Schema 校验         │
              │  Pydantic 模型        │
              └──────────┬───────────┘
                         │
              ┌──────────┴───────────┐
              ▼                      ▼
      ┌──────────────┐      ┌────────────────┐
      │  单份分析 UI  │      │  批量对比 / 导出 │
      └──────────────┘      └────────────────┘
```

## 主要模块

| 文件 | 职责 |
| --- | --- |
| `app.py` | Streamlit 界面：输入、条件表单、报告展示、批量解析、导出 |
| `agent.py` | Agent 编排：调用模型、结构化输出降级、解析失败重试 |
| `parsers.py` | 从模型原始回复中提取 JSON，剥离 Markdown 包裹 |
| `schemas.py` | Pydantic 数据模型，对抽取结果与匹配结果做强校验 |
| `batch.py` | 批量政策解析与对比表生成 |
| `exporters.py` | Markdown 报告与 CSV 导出 |
| `config.py` | 配置加载：环境变量优先，本地文件兜底 |
| `prompts/` | 抽取与匹配两个阶段的系统提示词 |

## 输出结构

抽取阶段输出：

```json
{
  "policy_name": "政策名称",
  "support_target": "扶持对象",
  "benefits": "扶持力度",
  "deadline": "申报截止日期",
  "requirements": [
    {
      "id": "req_1",
      "description": "申报条件描述",
      "type": "select",
      "options": ["是", "否"],
      "weight": "must"
    }
  ],
  "materials": ["所需材料"]
}
```

匹配阶段输出：

```json
{
  "match_score": 85,
  "summary": "总体评估",
  "eligible": true,
  "unmet_requirements": [
    {
      "description": "未满足的条件",
      "gap_analysis": "差距分析",
      "suggestion": "改进建议"
    }
  ],
  "action_plan": ["第一步", "第二步"]
}
```

## 支持的模型

任何提供 OpenAI 兼容 `chat/completions` 接口的服务都可以使用。程序会优先请求结构化输出（`response_format=json_object`），当服务端不支持时自动降级为普通文本模式，再通过解析与校验兜底。

| 服务 | API Base 示例 | 模型示例 |
| --- | --- | --- |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| 自建 / OneAPI | `http://localhost:3000/v1` | 任意 |

## 快速开始

需要 Python 3.9 及以上。

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置密钥

复制环境变量模板并填入自己的配置：

```bash
cp .env.example .env
```

```text
OPENAI_API_BASE=https://api.deepseek.com/v1
OPENAI_API_KEY=你的密钥
OPENAI_MODEL_NAME=deepseek-chat
```

密钥只放在本地 `.env` 或侧边栏中，`.env` 与 `config.json` 已被 `.gitignore` 排除。

### 3. 启动应用

```bash
streamlit run app.py
```

### 4. 运行测试

```bash
pytest -q
```

## 工程设计说明

模型返回的内容并不总是合法的 JSON，也可能带 Markdown 包裹或多余说明文字。项目针对这一点做了几层处理：

- **能力不写死**：不再通过 `model_name` 判断模型是否支持结构化输出，而是"先尝试、失败则降级"。
- **解析容错**：`parsers.py` 支持纯 JSON、代码块包裹、前后带说明文字、嵌套对象等多种情况。
- **强校验**：`schemas.py` 用 Pydantic 校验字段是否缺失、类型是否正确、枚举是否合法。
- **失败重试**：首次解析或校验失败时，将原始回复回传给模型要求修正，再解析一次。
- **配置安全**：环境变量优先于本地配置文件，密钥不写入仓库。

## 项目结构

```text
policy-agent/
├── app.py                 # Streamlit 界面
├── agent.py               # Agent 编排
├── parsers.py             # LLM 响应解析
├── schemas.py             # 结构化校验
├── batch.py               # 批量解析
├── exporters.py           # 报告导出
├── config.py              # 配置加载
├── prompts/
│   ├── extractor_prompt.md
│   └── matcher_prompt.md
├── test_agent.py
├── test_parsers.py
├── test_schemas.py
├── test_batch.py
├── test_exporters.py
├── requirements.txt
└── .env.example
```

## 免责声明

本工具的输出由大语言模型生成，仅用于辅助阅读政策与初步判断，不构成申报承诺或法律意见。实际申报条件请以官方文件与主管部门答复为准。
