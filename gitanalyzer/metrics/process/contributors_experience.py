"""
Analyzes and computes the contribution distribution among file authors.
"""
from gitanalyzer import ModificationType
from gitanalyzer.metrics.process.process_metric import ProcessMetric


class FileAuthorshipDistribution(ProcessMetric):
    """
    Analyzes the distribution of code ownership by calculating the
    percentage of lines written by the most active contributor for
    each file within the specified commit range [from_commit, to_commit].
    """

    def calculate_distribution(self):
        """
        Computes the percentage of code contributed by the most active author
        for each file modified during the analyzed commit range [from_commit, to_commit].

        Returns:
            dict: Mapping of {file_path: percentage} where percentage represents
                  the portion of lines written by the top contributor.
        """
        path_mapping = {}  # Tracks file renames
        authorship_data = {}  # Stores contribution data per file

        # Analyze each commit in the repository
        for commit in self.repo_miner.traverse_commits():
            for file_change in commit.modified_files:
                current_path = path_mapping.get(file_change.new_path, 
                                             file_change.new_path)

                # Update path mapping if file was renamed
                if file_change.change_type == ModificationType.RENAME:
                    path_mapping[file_change.old_path] = current_path

                # Calculate contribution metrics
                contributor = commit.author.email.strip()
                contribution_size = file_change.added_lines + file_change.deleted_lines

                # Update contribution tracking
                if current_path not in authorship_data:
                    authorship_data[current_path] = {}
                
                if contributor not in authorship_data[current_path]:
                    authorship_data[current_path][contributor] = 0
                
                authorship_data[current_path][contributor] += contribution_size

        # Calculate percentages for top contributors
        result = {}
        for filepath, contributions in authorship_data.items():
            total_changes = sum(contributions.values())
            if total_changes > 0:  # Only include files with actual changes
                max_contribution = max(contributions.values())
                result[filepath] = round((max_contribution * 100) / total_changes, 2)

        return result
