<p align="center"><h1 align="center">GITANALYZER</h1></p>
<p align="center">
	<em>A powerful Python library for mining and analyzing Git repositories</em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/codingwithshawnyt/GitAnalyzer?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/codingwithshawnyt/GitAnalyzer?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/codingwithshawnyt/GitAnalyzer?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/codingwithshawnyt/GitAnalyzer?style=default&color=0080ff" alt="repo-language-count">
</p>
<br>

## 🔗 Table of Contents

- [📍 Overview](#-overview)
- [👾 Features](#-features)
- [📁 Project Structure](#-project-structure)
  - [📂 Project Index](#-project-index)
- [🚀 Getting Started](#-getting-started)
  - [☑️ Prerequisites](#-prerequisites)
  - [⚙️ Installation](#-installation)
  - [🤖 Usage](#🤖-usage)
  - [🧪 Testing](#🧪-testing)
- [📌 Project Roadmap](#-project-roadmap)
- [🔰 Contributing](#-contributing)
- [🎗 License](#-license)
- [🙌 Acknowledgments](#-acknowledgments)

---

## 📍 Overview

GitAnalyzer is a Python library for mining and analyzing Git repositories. It provides a powerful interface for extracting detailed information about commits, developers, and code changes. The tool supports both local and remote repositories, with features including:

- Commit history traversal and filtering
- Code change analysis
- Developer contribution tracking
- Process metrics calculation
- Support for multiple repository analysis

---

## 👾 Features

- **Flexible Repository Access**: Analyze both local and remote Git repositories
- **Comprehensive Commit Analysis**: Extract detailed information about commits, including:
  - Author and committer details
  - Modified files and their changes
  - Code churn metrics
  - Commit relationships
- **Developer Analytics**: Track developer contributions and experience
- **Process Metrics**: Calculate various software process metrics
- **Multiple Repository Support**: Analyze multiple repositories in sequence
- **Mailmap Support**: Proper handling of author mappings via .mailmap files
- **Configurable Filters**: Filter commits by:
  - Date ranges
  - Commit hashes
  - Tags
  - File types
  - Authors

---

## 📁 Project Structure

```sh
└── GitAnalyzer/
    ├── LICENSE
    ├── Makefile                  # Build automation configuration
    ├── dev-requirements.txt      # Development dependencies
    ├── docs                      # Documentation directory
    │   ├── Makefile             # Documentation build configuration
    │   ├── commit.rst           # Commit analysis documentation
    │   ├── conf.py              # Sphinx configuration
    │   ├── deltamaintainability.rst  # Maintainability metrics docs
    │   ├── git.rst              # Git interface documentation
    │   ├── index.rst            # Documentation index
    │   ├── intro.rst            # Introduction guide
    │   ├── modifiedfile.rst     # File modification docs
    │   ├── processmetrics.rst   # Process metrics documentation
    │   ├── reference.rst        # API reference
    │   ├── repository.rst       # Repository handling docs
    │   ├── requirements.txt     # Documentation dependencies
    │   └── tutorial.rst         # Usage tutorial
    ├── gitanalyzer              # Main package directory
    │   ├── domain               # Core domain models
    │   ├── git.py              # Git interface implementation
    │   ├── metrics             # Analysis metrics implementations
    │   ├── repository.py       # Repository management
    │   └── utils               # Utility functions and helpers
    ├── pytest.ini              # PyTest configuration
    ├── requirements.txt        # Core dependencies
    ├── setup.py               # Package installation setup
    ├── test-requirements.txt  # Testing dependencies
    └── tests                  # Test suite directory
        ├── integration        # Integration tests
        ├── metrics           # Metrics tests
        ├── test_*.py         # Unit test files
```

### 📂 Project Index
<details open>
	<summary><b><code>GITANALYZER/</code></b></summary>
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/dev-requirements.txt'>dev-requirements.txt</a></b></td>
				<td><code>Development dependencies including mypy, flake8, and pytest-cov</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/pytest.ini'>pytest.ini</a></b></td>
				<td><code>PyTest configuration for test suite</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/test-requirements.txt'>test-requirements.txt</a></b></td>
				<td><code>Testing-specific dependencies</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/requirements.txt'>requirements.txt</a></b></td>
				<td><code>Core package dependencies including GitPython and pytz</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/Makefile'>Makefile</a></b></td>
				<td><code>Build and development automation tasks</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/setup.py'>setup.py</a></b></td>
				<td><code>Package installation and distribution configuration</code></td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details>
		<summary><b>gitanalyzer</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/git.py'>git.py</a></b></td>
				<td><code>Core Git interaction and repository management</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/repository.py'>repository.py</a></b></td>
				<td><code>High-level repository analysis interface</code></td>
			</tr>
			</table>
			<details>
				<summary><b>metrics</b></summary>
				<blockquote>
					<details>
						<summary><b>process</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/metrics/process/commits_count.py'>commits_count.py</a></b></td>
								<td><code>Commit frequency analysis</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/metrics/process/change_set.py'>change_set.py</a></b></td>
								<td><code>Change set size metrics</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/metrics/process/contributors_count.py'>contributors_count.py</a></b></td>
								<td><code>Contributor participation metrics</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/metrics/process/contributors_experience.py'>contributors_experience.py</a></b></td>
								<td><code>Developer experience analysis</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/metrics/process/lines_count.py'>lines_count.py</a></b></td>
								<td><code>Code line modification metrics</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/metrics/process/hunks_count.py'>hunks_count.py</a></b></td>
								<td><code>Code change block analysis</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/metrics/process/process_metric.py'>process_metric.py</a></b></td>
								<td><code>Base process metric implementation</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/metrics/process/history_complexity.py'>history_complexity.py</a></b></td>
								<td><code>Repository history complexity metrics</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/metrics/process/code_churn.py'>code_churn.py</a></b></td>
								<td><code>Code churn and volatility metrics</code></td>
							</tr>
							</table>
						</blockquote>
					</details>
				</blockquote>
			</details>
			<details>
				<summary><b>utils</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/utils/mailmap.py'>mailmap.py</a></b></td>
						<td><code>Git mailmap handling utilities</code></td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/utils/check_git_version.py'>check_git_version.py</a></b></td>
						<td><code>Git version compatibility checker</code></td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/utils/conf.py'>conf.py</a></b></td>
						<td><code>Configuration management utilities</code></td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>domain</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/domain/commit.py'>commit.py</a></b></td>
						<td><code>Commit entity model and analysis</code></td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/codingwithshawnyt/GitAnalyzer/blob/master/gitanalyzer/domain/developer.py'>developer.py</a></b></td>
						<td><code>Developer entity model and tracking</code></td>
					</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---
## 🚀 Getting Started

### ☑️ Prerequisites

Before getting started with GitAnalyzer, ensure your runtime environment meets the following requirements:

- **Python:** Version 3.8 or higher
- **Git:** Any recent version
- **Operating System:** Linux, macOS, or Windows
- **Package Manager:** pip


### ⚙️ Installation

Install GitAnalyzer using one of the following methods:

**Build from source:**

1. Clone the GitAnalyzer repository:
```sh
❯ git clone https://github.com/codingwithshawnyt/GitAnalyzer
```

2. Navigate to the project directory:
```sh
❯ cd GitAnalyzer
```

3. Install the project dependencies:

**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style=default&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ pip install -r requirements.txt -r dev-requirements.txt -r test-requirements.txt
```

### 🤖 Usage

Here's a basic example of using GitAnalyzer:

```python
from gitanalyzer import Repository

# Initialize repository (local or remote)
repo = Repository('path/to/repository')

# Traverse commits
for commit in repo.traverse_commits():
    print(f'Commit: {commit.hash}')
    print(f'Author: {commit.author.name}')
    print(f'Date: {commit.author_date}')
    
    # Access modified files
    for modification in commit.modified_files:
        print(f'Modified file: {modification.filename}')
        print(f'Changes: +{modification.added_lines}, -{modification.deleted_lines}')
```

### 🧪 Testing

Run the test suite using the following command:

```sh
❯ pytest
```

For coverage report:

```sh
❯ pytest --cov=gitanalyzer
```

---
## 📌 Project Roadmap

- [X] **Core Functionality**: Basic commit traversal and analysis
- [X] **Process Metrics**: Implementation of various process metrics
- [X] **Multiple Repository Support**: Ability to analyze multiple repositories
- [X] **Documentation**: Comprehensive documentation with Sphinx
- [ ] **Additional Metrics**: Implementation of more advanced metrics
- [ ] **Performance Optimization**: Improve analysis speed for large repositories

---

## 🔰 Contributing

- **💬 [Join the Discussions](https://github.com/codingwithshawnyt/GitAnalyzer/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/codingwithshawnyt/GitAnalyzer/issues)**: Submit bugs found or log feature requests for the `GitAnalyzer` project.
- **💡 [Submit Pull Requests](https://github.com/codingwithshawnyt/GitAnalyzer/pulls)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/codingwithshawnyt/GitAnalyzer
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com/codingwithshawnyt/GitAnalyzer/graphs/contributors">
      <img src="https://contrib.rocks/image?repo=codingwithshawnyt/GitAnalyzer">
   </a>
</p>
</details>

---

## 🎗 License

This project is protected under the [Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/) License. For more details, refer to the [LICENSE](LICENSE) file.

---

## 🙌 Acknowledgments

- **GitPython**: Core Git interaction functionality
- **Sphinx**: Documentation generation
- **pytest**: Testing framework
- All contributors who have helped improve GitAnalyzer

---