import logging
import os
import platform
import sys
import psutil
from git import Repo
from gitanalyzer import Repository as GitAnalyzerRepo
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.WARNING)
WORKSPACE_PATH = os.getenv('GITHUB_WORKSPACE')

def clone_repository(temp_directory) -> str:
    repository_path = temp_directory.join("GitAnalyzer")
    Repo.clone_from(url="https://github.com/codingwithshawnyt/GitAnalyzer", to_path=repository_path)
    return str(repository_path)

def test_memory_usage(caplog, temp_directory):
    if not WORKSPACE_PATH:
        # Ensure the environment is GitHub Actions
        return

    caplog.set_level(logging.WARNING)

    repository_path = clone_repository(temp_directory)

    logging.warning("Initiating test with base case...")
    diff_base, commits_base = analyze_commits(repository_path, 0)

    logging.warning("Initiating test with full analysis...")
    diff_full, commits_full = analyze_commits(repository_path, 1)

    logging.warning("Initiating test with metrics analysis...")
    diff_metrics, commits_metrics = analyze_commits(repository_path, 2)

    peak_memory_usage = [max(commits_base),
                         max(commits_full),
                         max(commits_metrics)]
    logging.warning("Peak memory usage: {}".format(peak_memory_usage))

    duration_full = (diff_full.seconds % 3600) // 60
    duration_metrics = (diff_metrics.seconds % 3600) // 60

    logging.warning(
        "DURATION: Base case: {}:{}:{} ({} commits/sec), "
        "Full analysis: {}:{}:{}  ({} commits/sec), "
        "Metrics analysis: {}:{}:{}  ({} commits/sec)".format(
            diff_base.seconds // 3600,
            (diff_base.seconds % 3600) // 60,
            diff_base.seconds % 60,
            704 // diff_base.seconds if diff_base.seconds != 0 else 0,
            diff_full.seconds // 3600,
            (diff_full.seconds % 3600) // 60,
            diff_full.seconds % 60,
            704 // diff_full.seconds,
            diff_metrics.seconds // 3600,
            (diff_metrics.seconds % 3600) // 60,
            diff_metrics.seconds % 60,
            704 // diff_metrics.seconds
        )
    )

    if any(memory > 250 for memory in peak_memory_usage) or \
            duration_full >= 1 or \
            duration_metrics >= 2:
        log_memory_and_time(diff_base, commits_base,
                            diff_full, commits_full,
                            diff_metrics, commits_metrics)
        raise Exception("Excessive memory usage or analysis time!")

    assert 704 == len(commits_base) == len(commits_full) == len(commits_metrics)

def log_memory_and_time(diff_base, commits_base,
                        diff_full, commits_full,
                        diff_metrics, commits_metrics):
    report = "*PYTHON V{}.{} - OS: {}*\n" \
             "*Maximum memory usage (MB)*\n" \
             "Base case: {}, Full analysis: {}, Metrics analysis: {}\n" \
             "*Minimum memory usage (MB)*\n" \
             "Base case: {}, Full analysis: {}, Metrics analysis: {} \n" \
             "*Processing Time*\n" \
             "Base case: {}:{}:{}, Full analysis: {}:{}:{}, Metrics analysis: {}:{}:{} \n" \
             "*Total commits processed*: {}\n" \
             "*Processing speed (commits/sec):*\n" \
             "Base case: {}, Full analysis: {}, Metrics analysis: {}"

    print(report.format(
        sys.version_info[0], sys.version_info[1], platform.system(),
        max(commits_base), max(commits_full), max(commits_metrics),
        min(commits_base), min(commits_full), min(commits_metrics),
        diff_base.seconds // 3600, (diff_base.seconds % 3600) // 60, diff_base.seconds % 60,
        diff_full.seconds // 3600, (diff_full.seconds % 3600) // 60,
        diff_full.seconds % 60,
        diff_metrics.seconds // 3600, (diff_metrics.seconds % 3600) // 60, diff_metrics.seconds % 60,
        len(commits_base),
        len(commits_base) / diff_base.seconds if diff_base.seconds > 0 else len(commits_base),
        len(commits_full) / diff_full.seconds,
        len(commits_metrics) / diff_metrics.seconds
    ))

def analyze_commits(repository, analysis_type):
    process = psutil.Process(os.getpid())
    cutoff_date = datetime(2021, 12, 1)
    memory_usage_records = []

    start_time = datetime.now()
    for commit in GitAnalyzerRepo(repository, to=cutoff_date).traverse_commits():
        current_memory = process.memory_info()[0] / (2 ** 20)
        memory_usage_records.append(current_memory)

        author = commit.author.name  # noqa

        if analysis_type == 0:
            continue

        for modification in commit.modified_files:
            diff_data = modification.diff  # noqa

            if analysis_type == 1:
                continue

            if modification.filename.endswith('.py'):
                complexity = modification.complexity  # noqa

    end_time = datetime.now()

    duration = end_time - start_time

    return duration, memory_usage_records