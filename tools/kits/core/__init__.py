"""The kits core: reads kit containers and returns data, never prints.

Rules of this package (PLAN-KITS-PY.md section 3.1): no printing, no process exit,
no Qt import, no mutable global state.  Errors are typed exceptions whose
message is the sentence a user interface would show.
"""
