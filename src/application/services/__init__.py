"""services package (intentionally no eager re-exports).

Import concrete service modules directly to avoid pulling heavy dependencies
like OpenAI at package import time.
"""
