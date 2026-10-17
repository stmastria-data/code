from __future__ import annotations


def check_window(window: int, name: str = "window") -> int:
    if not isinstance(window, int) or isinstance(window, bool) or window < 1:
        raise ValueError(f"{name} must be a positive integer, got {window!r}")
    return window
