#!/usr/bin/env python3
"""
SEB Harness PyRIT Initializer
=============================
Registers an HTTPTarget pointing at the SEB LocalTestHarness (OpenAI-compatible
/v1/chat/completions endpoint) so PyRIT scenarios can run against it.
"""

import os
from pyrit.prompt_target.http_target.http_target import HTTPTarget
from pyrit.registry import TargetRegistry
from pyrit.setup.initializers.pyrit_initializer import PyRITInitializer
from pyrit.common.parameter import Parameter


class SEBHarnessInitializer(PyRITInitializer):
    """Initialize a target that hits the SEB LocalTestHarness."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def supported_parameters(self) -> list[Parameter]:
        return [
            Parameter(
                name="endpoint",
                description="SEB LocalTestHarness OpenAI-compatible endpoint URL",
                default="http://127.0.0.1:8765/v1/chat/completions",
            ),
            Parameter(
                name="model",
                description="Model name to report (for registry metadata)",
                default="defended",
            ),
        ]

    @property
    def required_env_vars(self) -> list[str]:
        return []

    async def initialize_async(self) -> None:
        endpoint = self.params.get("endpoint", "http://127.0.0.1:8765/v1/chat/completions")
        model = self.params.get("model", "defended")

        # HTTPTarget needs the raw HTTP request template with {PROMPT} placeholder
        host = endpoint.replace("http://", "").replace("https://", "").split("/")[0]
        path = "/" + "/".join(endpoint.replace("http://", "").replace("https://", "").split("/")[1:])
        http_request = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "Content-Type: application/json\r\n"
            "\r\n"
            "{\"model\":\"" + model + "\",\"messages\":[{\"role\":\"user\",\"content\":\"{PROMPT}\"}]}"
        )

        target = HTTPTarget(
            http_request=http_request,
            prompt_regex_string="{PROMPT}",
            use_tls=False,
            model_name=model,
        )

        registry = TargetRegistry.get_registry_singleton()
        registry.register_instance(target, name="seb_harness")
        registry.add_tags(name="seb_harness", tags=["target", "seb", "dogfood"])
        print(f"Registered SEB harness target at {endpoint}")


if __name__ == "__main__":
    # Allow direct execution for testing
    import asyncio
    init = SEBHarnessInitializer()
    asyncio.run(init.initialize_async())