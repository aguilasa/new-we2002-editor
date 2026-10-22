"""duckmcp: drive any PlayStation game in the DuckStation fork over MCP.

Game-agnostic by design (PLAN-DUCKMCP-PY.md section 2.1): hardware, the
emulator's files, processes and dialogs, and the MCP protocol -- never a
serial, a title, a menu route or a game's RAM address. Callers put `tools/`
(the parent of this folder) on `sys.path` and `import duckmcp`.
"""

from .errors import (SKIP, Fail, NotRunning, SessionLost, Skip,  # noqa: F401
                     ToolError)
from .client import Client  # noqa: F401
from .session import Session  # noqa: F401

__version__ = "0.2.0"
"""The package version; bumped when the public surface changes."""

__all__ = ["Session", "Client", "SKIP", "Fail", "Skip", "NotRunning", "ToolError",
           "SessionLost", "__version__"]
