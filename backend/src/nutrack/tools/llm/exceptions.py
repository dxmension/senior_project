class LLMError(Exception):
    pass


class LLMConfigurationError(LLMError):
    pass


class LLMResponseError(LLMError):
    pass


class LLMRefusalError(LLMError):
    pass


class LLMIncompleteResponseError(LLMError):
    pass

