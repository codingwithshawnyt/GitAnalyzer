"""
Analyzes and computes the number of change blocks (hunks) within commit modifications.
"""
from statistics import median

from gitanalyzer import ModificationType
from gitanalyzer.metrics.process.process_metric import ProcessMetric


class ChangeBlockCounter(ProcessMetric):
    """
    Analyzes the fragmentation of changes in commit files by counting distinct
    blocks of modifications (hunks). This metric helps understand if changes
    are concentrated (few hunks) or scattered (many hunks) throughout a file.
    
    For multiple commits, the metric returns the median number of change blocks
    across the commit range.
    """

    def calculate_blocks(self):
        """
        Computes the number of change blocks per modified file.

        :return: dict mapping file paths to their change block counts
        """
        path_mapping = {}
        file_blocks = {}

        for commit in self.repository.iterate_commits():
            for changed_file in commit.changed_files:
                current_path = path_mapping.get(
                    changed_file.new_location, 
                    changed_file.new_location
                )

                if changed_file.modification_type == ModificationType.RENAME:
                    path_mapping[changed_file.previous_location] = current_path

                changes = changed_file.diff_content
                block_started = False
                block_count = 0

                for change_line in changes.splitlines():
                    if change_line[0] in {'+', '-'}:
                        if not block_started:
                            block_started = True
                            block_count += 1
                    else:
                        block_started = False

                if current_path in file_blocks:
                    file_blocks[current_path].append(block_count)
                else:
                    file_blocks[current_path] = [block_count]

        # Calculate median for files with multiple commits
        result = {
            path: median(blocks) 
            for path, blocks in file_blocks.items()
        }

        return result
