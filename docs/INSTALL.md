# Install the method

Use `python3 scripts/capability.py doctor`, then `python3 scripts/capability.py install --dest <skills-parent>`. Keep the complete installed folder and license. Identical reinstall is idempotent; conflicts are refused unless you deliberately choose `--replace`, which retains a dated backup. Remove only that folder to uninstall. No native runtime, server, provider, or service is required to read and apply the method.

## Optional native work

The optional `scripts/local_runtime.py` materializes a local behavior with absolute checkout paths and this checkout’s canonical skill. Its generated file belongs in ignored `.capability-check/`, is local to this machine, and contains no provider keys. Compose it with your configured host/provider only when native execution is needed. It does not install or start the independent MCP server. Frozen v2.0.0 native entrypoints and policy evidence remain retained for compatibility; see the native release guide for those versioned instructions.

For a local native behavior, run `uv run --with PyYAML python scripts/local_runtime.py --output .capability-check/imagen-studio.yaml`. The materializer needs PyYAML (already present in a configured Amplifier Python environment); `uv run --with` keeps that development dependency separate. The generated behavior adds no provider/session and does not activate itself. Compose it deliberately into the existing host only when native execution is needed.
