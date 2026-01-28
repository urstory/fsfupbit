#
# fsfupbit - Enhanced Python wrapper for Upbit API
# Based on pyupbit (https://github.com/sharebook-kr/pyupbit)
# Modified by Full Stack Research Lab (풀스택연구소)
#
# Licensed under the Apache License, Version 2.0
# Original Copyright (c) 2021 sharebook-kr
# Modifications Copyright (c) 2025 Full Stack Research Lab
#

import setuptools

install_requires = [
   'pyjwt>=2.0.0',
   'pandas>=1.0.0',
   'requests>=2.25.0',
   'websockets>=10.0'
]

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='fsfupbit',
    version='1.0.0',
    author='Full Stack Research Lab (풀스택연구소)',
    author_email='contact@fullstack.re.kr',
    description='Enhanced Python wrapper for Upbit API with additional features (Based on pyupbit)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/fullstack-research-lab/fsfupbit',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.8',
    keywords="upbit api cryptocurrency trading bitcoin ethereum korea exchange fsfupbit",
    project_urls={
        "Bug Reports": "https://github.com/fullstack-research-lab/fsfupbit/issues",
        "Source": "https://github.com/fullstack-research-lab/fsfupbit",
        "Documentation": "https://github.com/fullstack-research-lab/fsfupbit/blob/main/docs/api.md",
        "Original Source": "https://github.com/sharebook-kr/pyupbit",
    },
)
