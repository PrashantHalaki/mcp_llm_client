import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="mcp-llm-client-proxy",
    version="0.1.0",
    author="Prashant Halaki",
    author_email="prashanthalaki143@gmail.com",
    description="A Multi-Client Proxy (MCP) for various LLMs with failover and flexible response formats.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PrashantHalaki/mcp_llm_client",
    project_urls={
        "Bug Tracker": "https://github.com/PrashantHalaki/mcp_llm_client/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=install_requires,
)
