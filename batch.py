"""Batch policy extraction and comparison helpers."""

from typing import Dict, List

from agent import PolicyAgent


def batch_extract(agent: PolicyAgent, policy_texts: List[str]) -> List[Dict]:
    """
    Extract structured data from several policy documents.

    Returns one entry per input document. A failure in one document does
    not abort the rest of the batch.
    """
    results: List[Dict] = []
    for idx, text in enumerate(policy_texts, start=1):
        try:
            data = agent.extract_policy(text)
            results.append(
                {"index": idx, "ok": True, "data": data, "error": None}
            )
        except Exception as exc:  # noqa: BLE001 - surface per-item failure
            results.append(
                {"index": idx, "ok": False, "data": None, "error": str(exc)}
            )
    return results


def to_comparison_rows(results: List[Dict]) -> List[Dict]:
    """Flatten successful extraction results into table-friendly rows."""
    rows: List[Dict] = []
    for entry in results:
        if not entry.get("ok"):
            continue
        data = entry["data"]
        rows.append(
            {
                "policy_name": data.get("policy_name", ""),
                "support_target": data.get("support_target", ""),
                "benefits": data.get("benefits", ""),
                "deadline": data.get("deadline", ""),
                "requirement_count": len(data.get("requirements", [])),
                "material_count": len(data.get("materials", [])),
            }
        )
    return rows


def split_policy_texts(raw: str, delimiter: str = "---") -> List[str]:
    """Split a block of text into individual policy documents."""
    parts = [p.strip() for p in raw.split(delimiter)]
    return [p for p in parts if p]
