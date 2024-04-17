import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    "beartype==0.14.1",
    "cryptography==2.8",
    "requests==2.31.0",
    "pyzmq==26.0.0",
    "pydantic[email]==2.5.2"
]


setuptools.setup(
    name="movai-core-shared",
    version="2.5.0-12",
    author="Backend team",
    author_email="backend@mov.ai",
    description="Shared objects for various Mov.AI projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MOV-AI/movai-core-shared",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=requirements,
    entry_points={},
)
