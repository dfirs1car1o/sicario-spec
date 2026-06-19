from setuptools import find_packages, setup


setup(
    name="sicario-spec",
    version="0.1.0",
    description="Secure-by-default governance bundle for GitHub Spec Kit.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SicarioSpec Contributors",
    license="MIT",
    python_requires=">=3.9",
    packages=find_packages(include=["sicario_cli", "sicario_cli.*"]),
    include_package_data=True,
    package_data={"sicario_cli": ["assets/**/*"]},
    entry_points={"console_scripts": ["sicario=sicario_cli.cli:main"]},
    keywords=["spec-kit", "appsec", "devsecops", "ai-security", "governance"],
)
