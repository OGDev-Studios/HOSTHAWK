from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="hosthawk",
    version="1.0.0",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    include_package_data=True,
    install_requires=[
        'scapy>=2.5.0,<3.0.0',
        'python-nmap>=0.7.1,<1.0.0',
        'netifaces>=0.11.0,<1.0.0',
        'python-whois>=0.8.0,<1.0.0',
        'xmltodict>=0.13.0,<1.0.0',
        'colorama>=0.4.6,<1.0.0',
        'dnspython>=2.1.0,<3.0.0',
        'Flask>=2.0.1,<3.0.0',
        'Flask-SocketIO>=5.1.1,<6.0.0',
        'requests>=2.26.0,<3.0.0',
        'beautifulsoup4>=4.9.3,<5.0.0',
        'cryptography>=3.4.7,<42.0.0',
        'Jinja2>=3.0.1,<4.0.0',
        'fpdf>=1.7.2,<2.0.0',
    ],
    extras_require={
        'dev': [
            'black>=21.7b0,<24.0.0',
            'flake8>=3.9.2,<7.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'hosthawk=scanner.cli:main',
        ],
    },
    python_requires='>=3.8',
    author="HostHawk Team",
    author_email="team@hosthawk.io",
    description="Enterprise-grade network scanner for security professionals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords=["network", "scanner", "security", "pentest", "vulnerability", "nmap"],
    url="https://github.com/yourusername/hosthawk",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/hosthawk/issues",
        "Documentation": "https://hosthawk.readthedocs.io",
        "Source Code": "https://github.com/yourusername/hosthawk",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Monitoring",
    ],
)
