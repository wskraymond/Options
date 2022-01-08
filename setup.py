import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Options",
    version="0.0.1",
    author="Raymond",
    author_email="author@example.com",
    description="Options",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    project_urls={
        "Bug Tracker": "",
    },
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    install_requires=[
        'pandas',
        'numpy',
        'datetime',
        'pandas_datareader',
        'scipy',
        'matplotlib',
        'requests',
        'py_vollib'
    ],
    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    package_dir={'': 'src'},  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=setuptools.find_packages(where='src'),  # Required
    python_requires=">=3.6"
)
