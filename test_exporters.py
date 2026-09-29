from exporters import (
    comparison_to_csv,
    match_result_to_markdown,
    records_to_csv,
)


POLICY = {
    "policy_name": "高新技术企业认定",
    "support_target": "科技型企业",
    "benefits": "税收减免15%",
    "deadline": "2026-09-30",
    "materials": ["营业执照复印件", "研发费用专项审计报告"],
}

MATCH = {
    "match_score": 85,
    "eligible": True,
    "summary": "基本符合",
    "unmet_requirements": [
        {
            "description": "研发费用占比不低于5%",
            "gap_analysis": "当前为4%",
            "suggestion": "提高研发投入",
        }
    ],
    "action_plan": ["准备材料", "按时提交"],
}


def test_markdown_contains_key_sections():
    md = match_result_to_markdown(POLICY, MATCH)
    assert "# 政策匹配评估报告：高新技术企业认定" in md
    assert "匹配度得分：85 分" in md
    assert "研发费用占比不低于5%" in md
    assert "1. 准备材料" in md
    assert "- [ ] 营业执照复印件" in md


def test_markdown_handles_empty_unmet():
    md = match_result_to_markdown(
        POLICY, {**MATCH, "unmet_requirements": [], "match_score": 100}
    )
    assert "所有硬性条件均已满足。" in md


def test_csv_header_and_rows():
    csv_text = records_to_csv(
        [
            {
                "policy_name": "政策A",
                "support_target": "企业",
                "benefits": "补贴10万",
                "deadline": "2026-01-01",
                "match_score": 90,
                "eligible": True,
                "summary": "符合",
            }
        ]
    )
    lines = csv_text.strip().splitlines()
    assert lines[0].startswith("policy_name,support_target")
    assert "政策A" in lines[1]
    assert "是" in lines[1]


def test_csv_empty_records():
    csv_text = records_to_csv([])
    assert csv_text.strip() == "policy_name,support_target,benefits,deadline,match_score,eligible,summary"


def test_comparison_csv_header_and_row():
    csv_text = comparison_to_csv(
        [
            {
                "policy_name": "政策A",
                "support_target": "企业",
                "benefits": "补贴",
                "deadline": "2026-01-01",
                "requirement_count": 3,
                "material_count": 2,
            }
        ]
    )
    lines = csv_text.strip().splitlines()
    assert lines[0] == (
        "policy_name,support_target,benefits,deadline,"
        "requirement_count,material_count"
    )
    assert "政策A,企业,补贴,2026-01-01,3,2" in lines[1]
