from batch import split_policy_texts, to_comparison_rows


def test_split_policy_texts():
    raw = "政策一内容\n---\n政策二内容\n---\n\n---\n政策三内容"
    assert split_policy_texts(raw) == ["政策一内容", "政策二内容", "政策三内容"]


def test_split_ignores_blank_parts():
    assert split_policy_texts("   \n---\n   ") == []


def test_to_comparison_rows_skips_failures():
    results = [
        {
            "index": 1,
            "ok": True,
            "data": {
                "policy_name": "政策A",
                "support_target": "企业",
                "benefits": "补贴",
                "deadline": "2026-01-01",
                "requirements": [{"id": "req_1"}, {"id": "req_2"}],
                "materials": ["营业执照"],
            },
            "error": None,
        },
        {"index": 2, "ok": False, "data": None, "error": "解析失败"},
    ]
    rows = to_comparison_rows(results)
    assert len(rows) == 1
    assert rows[0]["policy_name"] == "政策A"
    assert rows[0]["requirement_count"] == 2
    assert rows[0]["material_count"] == 1
