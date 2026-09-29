"""Render policy analysis results into shareable report formats."""

import csv
import io
from typing import Dict, Iterable, List


def _fmt(value, default: str = "未明确") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def match_result_to_markdown(
    policy_data: Dict,
    match_result: Dict,
) -> str:
    """Render a single policy analysis into a Markdown report."""
    lines: List[str] = []
    name = _fmt(policy_data.get("policy_name"), "未命名政策")
    lines.append(f"# 政策匹配评估报告：{name}")
    lines.append("")

    lines.append("## 政策基本信息")
    lines.append("")
    lines.append(f"- 扶持对象：{_fmt(policy_data.get('support_target'))}")
    lines.append(f"- 扶持力度：{_fmt(policy_data.get('benefits'))}")
    lines.append(f"- 申报截止日期：{_fmt(policy_data.get('deadline'))}")
    lines.append("")

    lines.append("## 匹配结论")
    lines.append("")
    score = match_result.get("match_score", 0)
    eligible = match_result.get("eligible", False)
    lines.append(f"- 匹配度得分：{score} 分")
    lines.append(f"- 是否推荐申报：{'推荐' if eligible else '暂不推荐'}")
    lines.append(f"- 评估总结：{_fmt(match_result.get('summary'), '无')}")
    lines.append("")

    unmet = match_result.get("unmet_requirements", [])
    lines.append("## 不符项分析")
    lines.append("")
    if unmet:
        for idx, item in enumerate(unmet, start=1):
            lines.append(f"### {idx}. {_fmt(item.get('description'))}")
            lines.append("")
            lines.append(f"- 差距分析：{_fmt(item.get('gap_analysis'), '无')}")
            lines.append(f"- 改进建议：{_fmt(item.get('suggestion'), '无')}")
            lines.append("")
    else:
        lines.append("所有硬性条件均已满足。")
        lines.append("")

    lines.append("## 申报行动指南")
    lines.append("")
    action_plan = match_result.get("action_plan", [])
    if action_plan:
        for idx, step in enumerate(action_plan, start=1):
            lines.append(f"{idx}. {step}")
    else:
        lines.append("暂无建议步骤。")
    lines.append("")

    lines.append("## 建议准备材料")
    lines.append("")
    materials = policy_data.get("materials", [])
    if materials:
        for mat in materials:
            lines.append(f"- [ ] {mat}")
    else:
        lines.append("政策中未明确提及具体材料。")
    lines.append("")

    return "\n".join(lines)


def records_to_csv(records: Iterable[Dict]) -> str:
    """
    Render a batch of policy analyses into CSV text.

    Each record is expected to contain the flattened keys produced by
    batch_analyze: policy_name, support_target, benefits, deadline,
    match_score, eligible, summary.
    """
    fieldnames = [
        "policy_name",
        "support_target",
        "benefits",
        "deadline",
        "match_score",
        "eligible",
        "summary",
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for record in records:
        row = dict(record)
        if "eligible" in row:
            row["eligible"] = "是" if row["eligible"] else "否"
        writer.writerow(row)
    return buffer.getvalue()


def comparison_to_csv(rows: Iterable[Dict]) -> str:
    """Render batch extraction comparison rows into CSV text."""
    fieldnames = [
        "policy_name",
        "support_target",
        "benefits",
        "deadline",
        "requirement_count",
        "material_count",
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()
