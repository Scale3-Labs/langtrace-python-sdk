from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class OpenAISpanAttributes(BaseModel):
    url_full: str = Field(..., alias='url.full')
    llm_api: str = Field(..., alias='llm.api')
    llm_model: str = Field(..., alias='llm.model')
    # llm_temperature: Optional[float] = Field(None, alias='llm.temperature')
    # llm_top_p: Optional[float] = Field(None, alias='llm.top_p')
    # llm_user: Optional[str] = Field(None, alias='llm.user')
    # llm_system_fingerprint: Optional[str] = Field(None, alias='llm.system.fingerprint')
    # http_max_retries: Optional[int] = Field(None, alias='http.max.retries')
    # http_timeout: Optional[int] = Field(None, alias='http.timeout')
    llm_prompts: str = Field(..., alias='llm_prompts')
    llm_responses: str = Field(..., alias='llm_responses')
    # llm_token_counts: Optional[str] = Field(None, alias='llm.token.counts')
    # llm_stream: Optional[bool] = Field(None, alias='llm.stream')
    # llm_encoding_format: Optional[str] = Field(None, alias='llm.encoding.format')
    # llm_dimensions: Optional[str] = Field(None, alias='llm.dimensions')





