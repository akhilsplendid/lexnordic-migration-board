from enum import StrEnum

from app.settings import Settings


class ModelProvider(StrEnum):
    AIML = "aiml"
    FEATHERLESS = "featherless"


class ModelTask(StrEnum):
    EXTRACT_FIELDS = "extract_fields"
    CLASSIFY_SOURCE = "classify_source"
    TAG_CASE = "tag_case"
    RISK_PRECHECK = "risk_precheck"
    LEGAL_SYNTHESIS = "legal_synthesis"
    DRAFT_PACKET = "draft_packet"
    PARTNER_REVIEW = "partner_review"


def choose_provider(task: ModelTask, settings: Settings) -> ModelProvider:
    preferred = {
        ModelTask.EXTRACT_FIELDS: ModelProvider.FEATHERLESS,
        ModelTask.CLASSIFY_SOURCE: ModelProvider.FEATHERLESS,
        ModelTask.TAG_CASE: ModelProvider.FEATHERLESS,
        ModelTask.RISK_PRECHECK: ModelProvider.FEATHERLESS,
        ModelTask.LEGAL_SYNTHESIS: ModelProvider.AIML,
        ModelTask.DRAFT_PACKET: ModelProvider.AIML,
        ModelTask.PARTNER_REVIEW: ModelProvider.AIML,
    }[task]

    if preferred == ModelProvider.FEATHERLESS and settings.featherless_api_key:
        return ModelProvider.FEATHERLESS
    if settings.aiml_api_key:
        return ModelProvider.AIML
    if settings.featherless_api_key:
        return ModelProvider.FEATHERLESS
    raise RuntimeError("No model provider API key is configured")
