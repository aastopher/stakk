import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stack",
    version="0.0.1",
    author="Aaron Stopher",
    packages=setuptools.find_packages(include=["stack"]),
    description="Stack is designed to stack functions into a register, this registered stack is designed to be consumed by a stack of modular utilities.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aastopher/stack",
    project_urls={
        "Documentation": "https://stack.readthedocs.io",
        "Bug Tracker": "https://github.com/aastopher/stack/issues",
    },
    keywords=['agent', 'worker', 'threading', 'cli', 'utils','performance counter', 'benchmark'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
