.. _modifiedfile_toplevel:

=============
ModifiedFile
=============

You can get a list of modified files as well as their diffs and current source code from each commit. All *Modifications* can be obtained by iterating over the ModifiedFile object. Each modification object references a modified file and has the following fields:

* **old_path**: old path of the file (can be ``None`` if the file is added)
* **new_path**: new path of the file (can be ``None`` if the file is deleted)
* **filename**: return only the filename (e.g., given a path-like-string such as "/Users/dspadini/pydriller/myfile.py" returns “myfile.py”)
* **change_type**: type of the change: can be Added, Deleted, Modified, or Renamed. If you use `change_type.name` you get `ADD`, `DELETE`, `MODIFY`, `RENAME`.
* **diff**: diff of the file as Git presents it (e.g., starting with @@ xx,xx @@).
* **diff_parsed**: diff parsed in a dictionary containing the added and deleted lines. The dictionary has 2 keys: “added” and “deleted”, each containing a list of Tuple (int, str) corresponding to (number of line in the file, actual line).
* **added_lines**: number of lines added
* **deleted_lines**: number of lines removed
* **source_code**: source code of the file (can be ``None`` if the file is deleted or only renamed)
* **source_code_before**: source code of the file before the change (can be ``None`` if the file is added or only renamed)
* **methods**: list of methods of the file. The list might be empty if the programming language is not supported or if the file is not a source code file. These are the methods **after** the change.
* **methods_before**: list of methods of the file **before** the change (e.g., before the commit.)
* **changed_methods**: subset of *methods* containing **only** the changed methods. 
* **nloc**: Lines Of Code (LOC) of the file
* **complexity**: Cyclomatic Complexity of the file
* **token_count**: Number of Tokens of the file

**NOTE**: the list of modifications might be empty if the commit is a merge commit. For more info on this, check out `this post <https://haacked
.com/archive/2014/02/21/reviewing-merge-commits/>`_.

For example::

    for commit in Repository('path/to/the/repo').traverse_commits():
        for m in commit.modified_files:
            print(
                "Author {}".format(commit.author.name),
                " modified {}".format(m.filename),
                " with a change type of {}".format(m.change_type.name),
                " and the complexity is {}".format(m.complexity)
            )

