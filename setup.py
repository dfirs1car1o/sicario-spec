"""Legacy-toolchain entry point. pyproject.toml is the source of truth.

Older pip builds through this file directly and its arguments OVERRIDE
pyproject, so the declarations below must mirror pyproject exactly. An
earlier version drifted — it excluded the `presets` package — and every
wheel it built shipped without the preset classes, so installed builds
could not generate governance docs and a fresh init failed its own gate.
CI asserts the built wheel's contents to keep this file honest.
"""

from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).resolve().parent
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

setup(
    name="sicario-spec",
    version=VERSION,
    description="Secure-by-default governance bundle for GitHub Spec Kit.",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    packages=find_packages(include=["sicario_cli*", "presets*"]),
    include_package_data=True,
    package_data={
        "sicario_cli": ["assets/**/*", "rules/schema.json"],
        "presets": ["**/rules/*.rule.json"],
    },
    entry_points={"console_scripts": ["sicario=sicario_cli.cli:main"]},
)
