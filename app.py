import streamlit as st
import json
from config import load_config, save_config
from agent import PolicyAgent

# 页面配置
st.set_page_config(
    page_title="Policy Agent - 政策解读与匹配助手",
    page_icon="🎯",
    layout="wide"
)

# 初始化 Session State
if "config" not in st.session_state:
    st.session_state.config = load_config()

if "policy_data" not in st.session_state:
    st.session_state.policy_data = None

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

if "match_result" not in st.session_state:
    st.session_state.match_result = None

# 侧边栏：API 配置
with st.sidebar:
    st.title("⚙️ API 配置")
    st.markdown("配置您的大模型 API 密钥，支持 OpenAI 兼容格式（如 DeepSeek、OneAPI 等）。")

    api_base = st.text_input("API Base URL", value=st.session_state.config.get("api_base", ""))
    api_key = st.text_input("API Key", value=st.session_state.config.get("api_key", ""), type="password")
    model_name = st.text_input("Model Name", value=st.session_state.config.get("model_name", ""))

    if st.button("💾 保存配置", use_container_width=True):
        if not api_base or not api_key or not model_name:
            st.error("请填写完整配置！")
        else:
            st.session_state.config = save_config(api_base, api_key, model_name)
            st.success("配置保存成功！")

# 主界面标题
st.title("🎯 Policy Agent - 政策解读与匹配助手")
st.markdown("---")

# 检查 API 配置
if not st.session_state.config.get("api_key"):
    st.warning("👈 请先在左侧侧边栏配置您的 API Key 和 Model Name！")
    st.stop()

# 实例化 Agent
agent = PolicyAgent(
    api_base=st.session_state.config["api_base"],
    api_key=st.session_state.config["api_key"],
    model_name=st.session_state.config["model_name"]
)

# 布局：左侧输入政策，右侧展示匹配与问答
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 步骤 1：输入政策文本")
    policy_input = st.text_area(
        "请粘贴政策原文（支持政府补贴、人才引进、税收减免等政策）：",
        height=400,
        placeholder="例如：\n关于开展2026年度高新技术企业认定工作的通知...\n申报条件：\n1. 企业申请认定时须注册成立一年以上...\n2. 企业上年度研发费用占营业收入比例不低于5%..."
    )

    # 预设示例按钮
    st.markdown("**💡 快速体验示例政策：**")
    example_col1, example_col2 = st.columns(2)
    with example_col1:
        if st.button("📋 示例：高新技术企业认定"):
            policy_input = """关于开展2026年度高新技术企业认定工作的通知
各有关单位：
根据《高新技术企业认定管理办法》规定，现将2026年度认定申报条件通知如下：
一、申报条件：
1. 企业申请认定时须注册成立一年以上。
2. 企业通过自主研发、受让等方式，获得对其主要产品在技术上发挥核心支持作用的知识产权的所有权。
3. 企业从事研发和相关技术创新活动的科技人员占企业当年职工总数的比例不低于10%。
4. 企业近三个会计年度的研究开发费用总额占同期销售收入总额的比例符合如下要求：
   - 最近一年销售收入小于5,000万元的企业，比例不低于5%；
   - 最近一年销售收入在5,000万元至2亿元的企业，比例不低于4%；
   - 最近一年销售收入在2亿元以上的企业，比例不低于3%。
5. 近一年高新技术产品收入占企业同期总收入的比例不低于60%。
二、扶持力度：
通过认定的高新技术企业，减按15%的税率征收企业所得税。同时，首次认定给予一次性20万元资金补贴。
三、申报截止时间：
本批次申报截止时间为2026年9月30日。
"""
            st.rerun()

    with col2:
        st.header("⚡ 步骤 2：条件确认与匹配评估")

        if not policy_input:
            st.info("请在左侧输入政策文本，或点击示例按钮快速体验。")
        else:
            if st.button("🔍 开始解析政策", type="primary", use_container_width=True):
                with st.spinner("Agent 正在深度拆解政策条件，请稍候..."):
                    try:
                        st.session_state.policy_data = agent.extract_policy(policy_input)
                        st.session_state.user_answers = {}
                        st.session_state.match_result = None
                        st.success("政策解析成功！请在下方回答匹配问题。")
                    except Exception as e:
                        st.error(f"解析失败：{str(e)}")

            # 展示解析出来的政策基本信息
            if st.session_state.policy_data:
                p_data = st.session_state.policy_data
                st.markdown(f"### 📋 {p_data.get('policy_name', '未命名政策')}")

                # 基本信息卡片
                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.metric("🎯 扶持对象", p_data.get("support_target", "未明确"))
                with info_col2:
                    st.metric("💰 扶持力度/补贴", p_data.get("benefits", "未明确"))

                st.markdown(f"📅 **申报截止日期**：`{p_data.get('deadline', '未明确')}`")

                st.markdown("---")
                st.markdown("### ❓ 资格自测表单")
                st.markdown("请根据您企业的实际情况回答以下问题：")

                # 动态生成表单
                form_answers = {}
                for req in p_data.get("requirements", []):
                    req_id = req["id"]
                    desc = req["description"]
                    req_type = req["type"]
                    weight_tag = "【一票否决】" if req.get("weight") == "must" else "【加分项】"

                    st.markdown(f"**{weight_tag}** {desc}")

                    if req_type == "select":
                        options = req.get("options", ["是", "否"])
                        # 默认选择第一个
                        val = st.radio(
                            label=desc,
                            options=options,
                            key=f"input_{req_id}",
                            label_visibility="collapsed"
                        )
                        form_answers[req_id] = {
                            "description": desc,
                            "answer": val,
                            "weight": req.get("weight", "must")
                        }
                    elif req_type == "number":
                        unit = req.get("unit", "")
                        placeholder = req.get("placeholder", "")
                        val = st.number_input(
                            label=desc,
                            min_value=0.0,
                            step=1.0,
                            format="%f",
                            key=f"input_{req_id}",
                            placeholder=placeholder,
                            label_visibility="collapsed"
                        )
                        form_answers[req_id] = {
                            "description": desc,
                            "answer": f"{val} {unit}".strip(),
                            "weight": req.get("weight", "must")
                        }
                    st.markdown("")

                st.session_state.user_answers = form_answers

                if st.button("📊 开始匹配度评估", type="primary", use_container_width=True):
                    with st.spinner("Agent 正在计算匹配度并生成报告..."):
                        try:
                            st.session_state.match_result = agent.match_policy(
                                st.session_state.policy_data,
                                st.session_state.user_answers
                            )
                        except Exception as e:
                            st.error(f"评估失败：{str(e)}")

# 步骤 3：展示匹配报告
if st.session_state.match_result:
    st.markdown("---")
    st.header("📊 步骤 3：匹配评估报告")

    res = st.session_state.match_result
    score = res.get("match_score", 0)
    eligible = res.get("eligible", False)

    # 报告头部卡片
    rep_col1, rep_col2 = st.columns([1, 3])
    with rep_col1:
        st.metric("匹配度得分", f"{score} 分")
        if eligible:
            st.success("✅ 推荐申报")
        else:
            st.error("❌ 暂不推荐申报")

    with rep_col2:
        st.markdown("### 💡 评估总结")
        st.info(res.get("summary", "无总结"))

    # 未满足条件分析
    unmet = res.get("unmet_requirements", [])
    if unmet:
        st.markdown("### ⚠️ 不符项深度分析")
        for idx, item in enumerate(unmet):
            with st.expander(f"不符项 {idx+1}：{item.get('description')}", expanded=True):
                st.markdown(f"**差距分析**：{item.get('gap_analysis')}")
                st.markdown(f"**改进建议**：{item.get('suggestion')}")
    else:
        st.success("🎉 恭喜！您完全符合该政策的所有硬性申报条件！")

    # 申报行动指南
    st.markdown("### 🗺️ 保姆级申报行动指南")
    action_plan = res.get("action_plan", [])
    for idx, step in enumerate(action_plan):
        st.markdown(f"{idx+1}. {step}")

    # 所需材料清单
    st.markdown("### 📁 建议准备材料清单")
    materials = st.session_state.policy_data.get("materials", [])
    if materials:
        for mat in materials:
            st.markdown(f"- [ ] {mat}")
    else:
        st.markdown("*政策中未明确提及具体材料，建议联系主管部门咨询。*")
