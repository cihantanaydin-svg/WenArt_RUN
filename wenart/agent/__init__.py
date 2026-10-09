"""The AI orchestrator of Milestone 11 (docs/milestone11.md §2, §3, §8, §9).

What: an agent loop that checks the pipeline's result (code critic + vision critic), fixes what it finds through
typed, validated edits (tools) and sends the result back to the stage that caused it.

Modules:

- ``model``: the OpenAI-compatible client of the vLLM server (``AgentModel``) and ``MockModel`` for the CPU tests;
- ``tools``: the tool registry of §3 (read tools and edit tools, JSON schemas, handlers);
- ``topdown``: the CPU top-down image of a room (pieces, fronts, door swings, window bands, failed checks);
- ``overrides``: ``orchestrator/overrides.json`` and ``python -m wenart.agent apply`` (``building_agent.json``);
- ``geometry_fix``: the clear-error checks of ``correct_geometry`` (§3.2);
- ``critic_code`` / ``critic_vision`` / ``prompts``: the checklists of §4 as code and as model questions;
- ``loop``: ``AgentLoop`` (rounds, router, stop rules, §8);
- ``log``: ``orchestrator/log.json`` (schema ``log.schema.json``), ``log.md`` and ``images/`` (§9).

Rule: the agent never edits the building JSON or a ``.blend`` directly; every accepted edit is one entry of
``overrides.json``, replayed by ``apply`` (M11 §2). Nothing here imports ``bpy``.
"""
