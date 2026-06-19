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
    author="SicarioSpec Contributors",
    author_email="dfirs1car1o@users.noreply.github.com",
    url="https://github.com/dfirs1car1o/sicario-spec",
    python_requires=">=3.9",
    packages=find_packages(include=["sicario_cli", "sicario_cli.*"]),
    include_package_data=True,
    package_data={"sicario_cli": ["assets/**/*"]},
    entry_points={"console_scripts": ["sicario=sicario_cli.cli:main"]},
    keywords=["spec-kit", "appsec", "devsecops", "ai-security", "governance"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
    ],
    project_urls={
        "Homepage": "https://github.com/dfirs1car1o/sicario-spec",
        "Repository": "https://github.com/dfirs1car1o/sicario-spec",
        "Issues": "https://github.com/dfirs1car1o/sicario-spec/issues",
        "Changelog": "https://github.com/dfirs1car1o/sicario-spec/blob/main/CHANGELOG.md",
    },
)
