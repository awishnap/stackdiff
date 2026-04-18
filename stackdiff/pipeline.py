"""High-level pipeline: load → resolve → mask → diff → report."""

from typing import Dict, Optional

from stackdiff.config_loader import load_config
from stackdiff.env_resolver import resolve_config
from stackdiff.masker import mask_config
from stackdiff.differ import diff_configs, DiffResult
from stackdiff.reporter import format_report


def run_pipeline(
    local_path: str,
    remote_path: str,
    resolve_env: bool = False,
    mask_secrets: bool = True,
    extra_mask_patterns: Optional[list] = None,
    env_override: Optional[Dict[str, str]] = None,
    strict_resolve: bool = True,
) -> str:
    """Load two configs, optionally resolve env vars and mask secrets, then diff.

    Args:
        local_path: Path to local config file.
        remote_path: Path to remote/staging config file.
        resolve_env: Substitute ${VAR} references before diffing.
        mask_secrets: Replace sensitive values with *** before diffing.
        extra_mask_patterns: Additional regex patterns for masking.
        env_override: Custom env table for resolution (defaults to os.environ).
        strict_resolve: Raise on unresolvable vars when resolve_env is True.

    Returns:
        Formatted diff report string.
    """
    local_cfg = load_config(local_path)
    remote_cfg = load_config(remote_path)

    if resolve_env:
        local_cfg = resolve_config(local_cfg, env=env_override, strict=strict_resolve)
        remote_cfg = resolve_config(remote_cfg, env=env_override, strict=strict_resolve)

    if mask_secrets:
        local_cfg = mask_config(local_cfg, extra_patterns=extra_mask_patterns)
        remote_cfg = mask_config(remote_cfg, extra_patterns=extra_mask_patterns)

    result: DiffResult = diff_configs(local_cfg, remote_cfg)
    return format_report(result)
