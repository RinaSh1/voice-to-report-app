"""Domain errors. They are mapped to HTTP responses in app.main."""


class LLMError(Exception):
    """The language model could not answer (network, auth, refusal, cut-off output, ...)."""


class ReportGenerationError(Exception):
    """The model did not produce a valid report, even after a retry."""


class RateLimitExceeded(Exception):
    """A usage limit of the public demo was reached."""
