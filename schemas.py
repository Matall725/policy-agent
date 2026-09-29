"""Pydantic schemas for LLM structured outputs."""

from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class PolicyRequirement(BaseModel):
    """A single eligibility requirement extracted from a policy document."""

    id: str
    description: str
    type: Literal["select", "number"]
    options: Optional[List[str]] = None
    unit: Optional[str] = None
    placeholder: Optional[str] = None
    weight: Literal["must", "bonus"] = "must"

    @field_validator("id")
    @classmethod
    def id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("requirement id cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("requirement description cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def options_required_for_select(self) -> "PolicyRequirement":
        if self.type == "select" and not self.options:
            raise ValueError("select-type requirement must provide options")
        return self


class PolicyExtraction(BaseModel):
    """Structured extraction result from a raw policy document."""

    policy_name: str
    support_target: str = ""
    benefits: str = ""
    deadline: str = "未知"
    requirements: List[PolicyRequirement] = Field(default_factory=list)
    materials: List[str] = Field(default_factory=list)

    @field_validator("policy_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("policy_name cannot be empty")
        return v.strip()


class UnmetRequirement(BaseModel):
    """A requirement the user does not currently satisfy."""

    description: str
    gap_analysis: str = ""
    suggestion: str = ""


class MatchResult(BaseModel):
    """Policy eligibility assessment for a specific user profile."""

    match_score: int = Field(ge=0, le=100)
    summary: str = ""
    eligible: bool
    unmet_requirements: List[UnmetRequirement] = Field(default_factory=list)
    action_plan: List[str] = Field(default_factory=list)

    @field_validator("summary")
    @classmethod
    def summary_not_empty(cls, v: str) -> str:
        return v.strip()
