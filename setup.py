from setuptools import setup, find_packages

setup(
    name="lexical_analyzer_parser",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'mypy>=1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'lexparse=interpreter:main',
        ],
    },
)
