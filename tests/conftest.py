"""Shared test setup for the whole suite.

``src/`` is added to ``sys.path`` by pytest's ``pythonpath`` ini option (the
project has no installable package because it declares no ``[build-system]``).

``utils.settings`` validates its settings at import time, so any module that
transitively imports it -- ``chains.documentary_chain``, ``tools.video`` and
therefore ``agents.documentary_agent`` -- refuses to import unless
``OPENAI_API_KEY`` is set.  Seed a dummy value before test modules are imported.
No test ever contacts OpenAI; every network client is mocked.
"""

import os

os.environ.setdefault("OPENAI_API_KEY", "sk-test-not-a-real-key")
