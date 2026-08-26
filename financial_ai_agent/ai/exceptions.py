class FinancialAIError(RuntimeError):
    """Safe base exception for application-level failures."""


class AIProviderError(FinancialAIError):
    pass


class AIProviderAuthenticationError(AIProviderError):
    pass


class AIProviderRateLimitError(AIProviderError):
    pass


class AIProviderTimeoutError(AIProviderError):
    pass


class AIProviderUnavailableError(AIProviderError):
    pass


class AIModelNotFoundError(AIProviderError):
    pass


class AIContextLimitError(AIProviderError):
    pass


class AIInvalidResponseError(AIProviderError):
    pass


class AICapabilityNotSupportedError(AIProviderError):
    pass


class ToolPermissionError(FinancialAIError):
    pass


class ApprovalRequiredError(FinancialAIError):
    pass

