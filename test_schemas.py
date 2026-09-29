import pytest
from pydantic import ValidationError

from schemas import MatchResult, PolicyExtraction, PolicyRequirement


def test_valid_requirement_select():
    req = PolicyRequirement(
        id="req_1",
        description="企业注册地是否在上海",
        type="select",
        options=["是", "否"],
        weight="must",
    )
    assert req.weight == "must"


def test_valid_requirement_number():
    req = PolicyRequirement(
        id="req_2",
        description="研发费用占比",
        type="number",
        unit="%",
        weight="must",
    )
    assert req.unit == "%"


def test_select_requires_options():
    with pytest.raises(ValidationError):
        PolicyRequirement(
            id="req_1",
            description="缺少选项",
            type="select",
        )


def test_invalid_weight_rejected():
    with pytest.raises(ValidationError):
        PolicyRequirement(
            id="req_1",
            description="权重非法",
            type="number",
            weight="critical",
        )


def test_empty_id_rejected():
    with pytest.raises(ValidationError):
        PolicyRequirement(
            id="   ",
            description="空 id",
            type="number",
        )


def test_policy_extraction_valid():
    data = {
        "policy_name": "高新技术企业认定",
        "support_target": "科技型企业",
        "benefits": "税收减免15%",
        "deadline": "2026-09-30",
        "requirements": [
            {
                "id": "req_1",
                "description": "成立一年以上",
                "type": "select",
                "options": ["是", "否"],
                "weight": "must",
            }
        ],
        "materials": ["营业执照复印件"],
    }
    model = PolicyExtraction.model_validate(data)
    assert model.policy_name == "高新技术企业认定"
    assert len(model.requirements) == 1


def test_policy_extraction_missing_name_rejected():
    with pytest.raises(ValidationError):
        PolicyExtraction.model_validate({"requirements": [], "materials": []})


def test_match_score_out_of_range_rejected():
    with pytest.raises(ValidationError):
        MatchResult(match_score=150, eligible=True)


def test_match_result_valid():
    result = MatchResult(
        match_score=85,
        summary="基本符合",
        eligible=True,
        unmet_requirements=[],
        action_plan=["准备材料", "按时提交"],
    )
    assert result.match_score == 85
    assert result.eligible is True
