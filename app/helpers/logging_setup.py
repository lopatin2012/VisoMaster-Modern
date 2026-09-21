"""Application logging.

Writes a rotating ``visomaster.log`` next to the app (repo root) and mirrors warnings/errors
to stderr. Also installs excepthooks so uncaught exceptions (main thread and worker threads)
are recorded instead of only printed/lost.
"""

import logging
import logging.handlers
import os
import sys
import threading

LOG_FILE = "visomaster.log"
_CONFIGURED_ATTR = "_visomaster_logging_configured"

_FORMAT = logging.Formatter(
    "%(asctime)s %(levelname)-7s [%(threadName)s] %(name)s: %(message)s"
)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure the root logger once. Safe to call multiple times."""
    root = logging.getLogger()
    if getattr(root, _CONFIGURED_ATTR, False):
        return root

    root.setLevel(level)

    # App diagnostics (model loading, enhancer tracing, VRAM, display path) are
    # DEBUG-level and can be very noisy per frame. Enable them only on request:
    #   set VISOMASTER_DEBUG=1
    if os.environ.get("VISOMASTER_DEBUG", "").strip().lower() in ("1", "true", "yes", "on"):
        logging.getLogger("app").setLevel(logging.DEBUG)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=2_000_000, backupCount=2, encoding="utf-8"
    )
    file_handler.setFormatter(_FORMAT)
    file_handler.setLevel(logging.DEBUG)
    root.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(_FORMAT)
    console_handler.setLevel(logging.WARNING)
    root.addHandler(console_handler)

    def _excepthook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        root.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

    sys.excepthook = _excepthook

    def _thread_excepthook(args):
        name = args.thread.name if args.thread else "?"
        root.critical(
            "Uncaught exception in thread %s",
            name,
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    threading.excepthook = _thread_excepthook

    setattr(root, _CONFIGURED_ATTR, True)
    root.info("Logging initialised -> %s", LOG_FILE)
    return root
