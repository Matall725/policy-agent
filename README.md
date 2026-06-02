# 政务政策解读 Agent (Policy Agent)

> 这是一个基于先进的大型语言模型 (LLM Agent) 打造的政务与产业政策智能解析引擎。通过体系化的 Prompt Engineering、信息抽取 (IE)、政策诊断 (Diagnostic) 形成了协同的 Agentic Workflow (智能体工作流)，帮助用户实现对冗长复杂的政府政策文件的自动化阅读、关键信息挖掘及精准解读。

---

## 🤖 智能体工作流 (Agentic Workflow)

核心服务基于 LLM，不依赖复杂的外部 LangChain 框架抽象，而是以原生 Pipeline 脚本驱动。在 `prompts/` 目录下清晰地维护着所有 System Prompt。系统主要编排了以下两个核心智能体链路：

### 1. 政策信息抽取 Agent (Information Extraction)
负责对原始政策公文进行结构化拆解，采用 Zero/Few-shot 设计提示词，强制大模型以结构化的 JSON schema 格式输出：
- 识别项目申报的截止日期 (Deadline)。
- **核心功能**：精准提取 **申报限制条件** 与 **扶持政策额度**，极大减轻 C 端企业/用户的政策阅读负担。

### 2. 政策诊断与适配 Agent (Policy Diagnostic)
- 结合给定的企业资质画像，该 Agent 将负责进行条件比对，输出该企业是否符合当前政策申请标准的逻辑推演结果。

---

## 💻 项目目录说明

*   `app.py`：主程序的后端服务或展示接口（可能是 Streamlit / Gradio 或者轻量级 API）。
*   `agent.py`：定义了整个 Agent Workflow，封装了 LLM 的调用与多次编排交互逻辑。
*   `config.py`：管理大模型的 API 密钥、并发数、超时以及系统基础配置设定的加载模块。
*   `prompts/`：管理和存放了各个 AI Agent 使用的模板化提示词 (Prompts)。
*   `requirements.txt`：项目的 Python 依赖包清单。

---

## 🚀 快速启动

你需要拥有基础的 Python (3.8+) 运行环境。

### 1. 安装依赖环境
```bash
# 进入项目目录并安装必须组件
pip install -r requirements.txt
```

### 2. 补全配置
在项目根目录设定环境变量，或在 `config.py` (及对应的 `.env` 文件) 中补充你的大模型 API 金钥 (API Keys)。

### 3. 拉起应用
通过终端启动核心主程序：
```bash
python app.py
```
*(如果是 Streamlit 应用，请使用 `streamlit run app.py` 作为启动命令。)*
