import os

from setuptools import find_packages, setup


def rel(*xs: str) -> str:
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *xs)


with open(rel("README.md")) as f:
    long_description = f.read()


with open(rel("src", "pytranslate", "__init__.py")) as f:
    version_marker = "__version__ = "
    for line in f:
        if line.startswith(version_marker):
            _, version = line.split(version_marker)
            version = version.strip().strip('"')
            break
    else:
        raise RuntimeError("Version marker not found.")


dependencies = [
    "click",
    "deepl-cli",
    "googletrans",
    "requests",
]

extra_dependencies: dict[str, list[str]] = {}

extra_dependencies["all"] = list(set(sum(extra_dependencies.values(), [])))
extra_dependencies["dev"] = extra_dependencies["all"] + [
    "ruff",
    "pyright",
    "safety",
    "pytest",
]

setup(
    name="pytranslate",
    version=version,
    author="maxime1907",
    author_email="19607336+maxime1907@users.noreply.github.com",
    description="Advanced SubStation Alpha translation service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages("src", exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=True,
    python_requires=">=3.12",
    install_requires=dependencies,
    extras_require=extra_dependencies,
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
    ],
    entry_points={"console_scripts": ["pytranslate=pytranslate.cli:cli"]},
)
