#!/usr/bin/env python3
"""Check an explicitly named independent MCP executable without a provider call."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import tempfile
from pathlib import Path

import amplifier_module_tool_imagen as adapter
from jsonschema import Draft202012Validator


class Coordinator:
    def __init__(self):
        self.tools = {}

    async def mount(self, namespace, tool, name):
        self.tools[name] = tool


async def check(server: Path):
    # The child allowlist is supplied by the adapter. This invocation deliberately
    # carries no image-provider credential and calls no discovered tool.
    for name in ("OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        os.environ.pop(name, None)
    with tempfile.TemporaryDirectory(prefix="imagen-studio-contract-") as directory:
        os.environ["IMAGEN_MCP_LOG_DIR"] = directory
        coordinator = Coordinator()
        cleanup = await adapter.mount(
            coordinator,
            {
                "imagen_mcp_path": str(server),
                "output_dir": directory,
                "startup_timeout_seconds": 30,
            },
        )
        try:
            assert set(coordinator.tools) == adapter._SUPPORTED_TOOL_NAMES
            for tool in coordinator.tools.values():
                Draft202012Validator.check_schema(tool.input_schema)
                secret_fields = {"openai_api_key", "gemini_api_key"}
                assert secret_fields.isdisjoint(tool.input_schema.get("properties", {}))
            return {
                "result": "passed",
                "scope": (
                    "independent executable MCP initialize, reviewed tool discovery, "
                    "schema checks and owned cleanup"
                ),
                "tool_count": len(coordinator.tools),
                "client_tool_calls": 0,
                "provider_keys_supplied": False,
                "provider_package_imported": False,
                "effectiveness": "not measured",
            }
        finally:
            await cleanup()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    server = args.server.expanduser().resolve(strict=True)
    if not server.is_file():
        parser.error("--server must be an explicitly named executable file")
    result = asyncio.run(check(server))
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
