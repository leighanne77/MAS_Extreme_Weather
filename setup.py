from setuptools import setup, find_packages

setup(
    name="multi-agent-climate-risk",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "aiohttp",
        "google-cloud-aiplatform",
        "vertexai",
        "google-adk",
        "python-dotenv",
        "pytest",
        "pytest-asyncio"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A multi-agent system for climate risk analysis using function-based tools.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/multi-agent-climate-risk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 