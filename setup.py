from os import path
from setuptools import setup, find_packages

# Reading requirements from files
def load_requirements(file_name):
    with open(file_name) as file:
        return file.read().strip().split('\n')

requirements_main = load_requirements('requirements.txt')
requirements_test = load_requirements('test-requirements.txt')

# Detailed description of the project
detailed_description = (
    'GitAnalyzer is a versatile Python toolkit for analyzing Git repositories. '
    'It simplifies the process of extracting data such as commits, contributors, '
    'file changes, diffs, and source code, and supports exporting data to CSV format.'
)

# Fetching the version from the package's __init__.py
def fetch_version():
    init_path = path.join(path.dirname(__file__), 'gitanalyzer', '__init__.py')
    with open(init_path) as file:
        for line in file:
            if line.startswith('__version__'):
                version_delimiter = '"' if '"' in line else "'"
                return line.split(version_delimiter)[1]
    raise RuntimeError("Version string not found.")

setup(
    name='GitAnalyzer',
    description='A toolkit for Mining Software Repositories (MSR)',
    long_description=detailed_description,
    author='Shawn Ray',
    author_email='shawnray5699@gmail.com',
    version=fetch_version(),
    packages=find_packages('.', exclude=['tests*']),
    url='https://github.com/codingwithshawnyt/GitAnalyzer',  # Assuming the URL remains unchanged
    license='Apache License',
    package_dir={'gitanalyzer': 'gitanalyzer'},
    python_requires='>=3.5',
    install_requires=requirements_main,
    tests_require=requirements_main + requirements_test,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
    ]
)
