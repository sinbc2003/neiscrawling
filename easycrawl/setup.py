from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="easycrawl",
    version="0.2.0",
    author="EasyCrawl Team",
    author_email="easycrawl@example.com",
    description="AI 기반 웹 크롤러 자동 생성 도구 - 코딩 없이 누구나 쉽게!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/easycrawl/easycrawl",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "anthropic>=0.39.0",
        "rich>=13.7.0",
        "pydantic>=2.0.0",
        "click>=8.1.0",
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "flask-socketio>=5.3.0",
        "sqlalchemy>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "easycrawl=easycrawl.cli:main",
            "easycrawl-web=easycrawl.web_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "easycrawl": [
            "templates/*.py",
            "web/templates/*.html",
            "web/static/css/*.css",
            "web/static/js/*.js",
        ],
    },
)
