from __future__ import annotations

from typing import Type

from financial_ai_agent.providers.crm.base import BaseCRMProvider

_PROVIDERS: dict[str, Type[BaseCRMProvider]] = {}


def register_crm_provider(provider_type: str, provider_class: Type[BaseCRMProvider]) -> None:
    _PROVIDERS[provider_type] = provider_class


def get_crm_provider(connector) -> BaseCRMProvider:
    if connector.crm_type in {"ERPNext CRM", "Frappe CRM"}:
        from financial_ai_agent.providers.crm.frappe_crm import FrappeCRMProvider
        return FrappeCRMProvider(connector)
    try:
        return _PROVIDERS[connector.crm_type](connector)
    except KeyError as exc:
        raise ValueError(f"CRM provider is not installed: {connector.crm_type}") from exc
