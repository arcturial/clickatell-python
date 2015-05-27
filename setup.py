from setuptools import setup, find_packages

setup(
    name="clickatell",
    version="0.1.1",
    author="Chris Brand",
    author_email="webmaster@cainsvault.com",
    keywords=["clickatell","sms"],
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/arcturial/clickatell-python",
    license="LICENSE",
    description="Library for interacting with the Clickatell SMS Gateway",
    long_description=open("README.md").read(),
    install_requires=[
        "requests",
        "mock"
    ]
)
