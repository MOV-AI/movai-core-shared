import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    "beartype==0.14.1",
    "cryptography==2.8",
    "requests==2.28.2",
    "pyzmq==24.0.1",
    "pydantic==1.10.4",
]


setuptools.setup(
    name="movai-core-shared",
    version="2.4.1-13",
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
