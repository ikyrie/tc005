from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ComponentKind(str, Enum):
    """Normalized kinds of architecture components detected in the diagram."""

    GATEWAY = "gateway"
    DATABASE = "database"
    MICROSERVICE = "microservice"
    QUEUE = "queue"
    CACHE = "cache"
    FRONTEND = "frontend"
    UNKNOWN = "unknown"


class RiskSeverity(str, Enum):
    """Risk severity levels used by the analysis output."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendationPriority(str, Enum):
    """Prioritization levels for recommendations produced by the model."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Component(BaseModel):
    """Represents one architecture component identified in the diagram."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(description="Human-readable name of the component as shown or inferred from the diagram.")
    kind: ComponentKind = Field(description="Normalized category of the component to avoid free-text conditionals in application logic.")
    description: str = Field(description="Short explanation of the component role, responsibilities, or context in the architecture.")


class Risk(BaseModel):
    """Represents a security or architecture risk identified in the diagram."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    code: str = Field(description="Stable risk identifier in snake_case format, for example exposed_admin_endpoint or missing_encryption_at_rest.")
    title: str = Field(description="Concise risk title suitable for report headings.")
    severity: RiskSeverity = Field(description="Impact and urgency level of the risk using the predefined severity enum.")
    description: str = Field(description="Detailed explanation of why this is a risk, where it appears, and potential consequences.")


class Recommendation(BaseModel):
    """Represents an actionable recommendation to mitigate identified risks."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(description="Concise recommendation title suitable for report sections.")
    priority: RecommendationPriority = Field(description="Implementation priority level based on risk reduction and urgency.")
    description: str = Field(description="Actionable recommendation details describing what should be changed and why.")


class ModelMetadata(BaseModel):
    """Metadata about the model that generated the analysis output."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    provider: str = Field(description="Name of the model provider, for example OpenAI, Anthropic, or Azure OpenAI.")
    model_name: str = Field(description="Exact model identifier used to generate the analysis.")


class AnalysisResult(BaseModel):
    """Structured output contract for architecture diagram analysis."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: UUID = Field(description="Unique identifier for this analysis run.")
    components: list[Component] = Field(description="List of architecture components identified in the diagram.")
    risks: list[Risk] = Field(description="List of detected risks derived from the architecture analysis.")
    recommendations: list[Recommendation] = Field(description="List of recommended mitigation actions related to detected risks.")
    limitations: list[str] = Field(description="List of analysis limitations describing what the model could not see or assess in the image.")
    model: ModelMetadata = Field(description="Metadata about the model and provider that generated this structured output.")
