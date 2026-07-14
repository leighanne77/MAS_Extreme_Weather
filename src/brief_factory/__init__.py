"""brief_factory — deterministic core for briefing standards and briefs.

Compiles machine-readable blocks into a Brief and renders it as an
branded document. No LLM anywhere in this package: agents may *draft*
narrative fields upstream, but every number entering a Brief flows through
typed, cited, linted blocks (see models.blocks).

Dependency direction: imports loaders/enums read-only; never imports agents.
"""

__version__ = "0.1.0"
