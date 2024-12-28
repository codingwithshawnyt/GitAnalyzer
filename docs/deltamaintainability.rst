.. _deltamaintainability:

===================
Change Maintenance
===================

Overview
========

GitAnalyzer implements the *Open Source Change Maintenance Model* (OS-CMM) to evaluate how code changes affect maintainability. This model is derived from research presented at the 2019 TechDebt Conference [DiBiase2019]_.
For enterprise applications, a comprehensive version supporting over 100 programming languages is available through the `Software Improvement Group <https://www.softwareimprovementgroup.com/>`_ (SIG).

The open-source version in GitAnalyzer provides a simplified implementation suitable for academic research and analysis of systems written in common programming languages. While GitAnalyzer's version control functionality works with any language, the *metric calculations* (like function size and complexity) require language-specific implementations, which are handled by `Lizard <https://github.com/terryyin/lizard>`_.

The OS-CMM implementation enhances GitAnalyzer's metrics by adding three commit-level measurements focusing on size risk, complexity risk, and interface risk.

Core Concept
===========

Simply put, the change maintenance metric represents the fraction of *safe changes* in a commit. Values range from 0.0 (all changes are high-risk) to 1.0 (all changes are safe). The metric rewards improvements in code quality while penalizing degradation.

The model begins with a *risk assessment* [Heitlager2007]_. Traditionally, code units (typically methods) are classified into four categories: safe, moderate, risky, and critical. A class's risk assessment is represented as a 4-tuple (*s, m, r, c*) showing the code volume (line count) in each category.

For simplicity, OS-CMM uses just two categories: safe and unsafe (combining moderate, risky, and critical). To analyze changes, we use *change risk assessments* - pairs (*ds, du*) where *ds* represents the change in safe code volume, and *du* represents the change in unsafe code volume.

These assessments determine positive and negative changes:

- Adding safe code is positive, while adding unsafe code is negative
- Removing unsafe code is positive, and removing safe code is positive only if it's not replaced with unsafe code

The final value is calculated as: *positive changes / (positive changes + negative changes)*.
If there are no changes (denominator is zero), the result is undefined (``None``).

.. _Metrics:

Metrics
=======

The model can evaluate any property measurable at the method level. GitAnalyzer's OS-CMM implementation examines three metrics:

- **Function size**: Lines of code per method; safe threshold is 15 lines
- **Function complexity**: Cyclomatic complexity per method; safe threshold is 5
- **Function interface**: Parameter count per method; safe threshold is 2

While the original model included coupling and code duplication metrics, these aren't easily calculated per-commit using Lizard. The thresholds are intentionally language-agnostic and were established through empirical research [Alves2010]_, using industry benchmark data from SIG [SIG2019]_.

Implementation Example
====================

Here's how to collect maintenance metrics from a repository::

    from gitanalyzer import Repository

    repo = Repository("https://github.com/codingwithshawnyt/GitAnalyzer")
    for commit in repo.traverse_commits():
        print("| {} | {} | {} | {} |".format(
            commit.msg,
            commit.cmm_function_size,
            commit.cmm_function_complexity,
            commit.cmm_function_interface
            ))

The resulting values are proportions between 0.0 and 1.0.
Changes to files in unsupported languages (like ``.xml``, ``.yaml``, ``.txt``, or ``.md``) are ignored.
If no supported files are modified in a commit, the metric returns ``None``.

Technical Details
===============

The main interface consists of three properties on the ``Commit`` class: ``cmm_function_size``, ``cmm_function_complexity``, and ``cmm_function_interface``.
The implementation offers several customization points:

- Thresholds are defined as constants in the ``Method`` class
- Core functions use an enum parameter to specify which metric to evaluate
- Protected methods for calculating risk and change assessments at both ``Commit`` and ``Modification`` levels enable detailed analysis of specific commits

Comparison with SIG Implementation
================================

GitAnalyzer's OS-CMM differs from SIG's commercial version in several ways:

- OS-CMM only supports languages compatible with `Lizard <https://github.com/terryyin/lizard>`_ (approximately 15)
- OS-CMM uses Lizard's method identification, which may differ from SIG's in complex cases (lambdas, nested functions, etc.)
- OS-CMM counts all lines including whitespace, while SIG only counts statement lines
- OS-CMM uses SIG's thresholds but may categorize borderline cases differently due to measurement differences

While individual measurements may vary slightly between implementations, overall trends and statistical analyses should remain consistent. Therefore:

- For research purposes, GitAnalyzer's open implementation ensures reproducibility
- For production use and comprehensive maintainability monitoring, SIG's robust implementation is recommended

References
==========

.. [DiBiase2019] Marco di Biase, Ayushi Rastogi, Magiel Bruntink, and Arie van Deursen. **The Delta Maintainability Model: measuring maintainability of fine-grained code changes**. IEEE/ACM International Conference on Technical Debt (TechDebt) at ICSE 2019, pp 113-122 (`preprint <https://pure.tudelft.nl/portal/en/publications/the-delta-maintainability-model-measuring-maintainability-of-finegrained-code-changes(6ff67dee-2781-47d7-916f-bd36c5b61beb).html>`_, `doi <https://doi.org/10.1109/TechDebt.2019.00030>`_).

.. [Heitlager2007] Ilja Heitlager, Tobias Kuipers, and Joost Visser. **A Practical Model for Measuring Maintainability**. 6th International Conference on the Quality of Information and Communications Technology, QUATIC 2007, IEEE, pp 30-39 (`preprint <http://wiki.di.uminho.pt/twiki/pub/Personal/Joost/PublicationList/HeitlagerKuipersVisser-Quatic2007.pdf>`_, `doi <https://doi.org/10.1109/QUATIC.2007.8>`_)

.. [Alves2010] Tiaga Alves, Christiaan Ypma, and Joost Visser. **Deriving metric thresholds from benchmark data**. IEEE International Conference on Software Maintenance (ICSM), pages 1–10. IEEE, 2010 (`preprint <http://wiki.di.uminho.pt/twiki/pub/Personal/Tiago/Publications/icsm10rt-alves.pdf>`_, `doi <https://doi.org/10.1109/ICSM.2010.5609747>`_).

.. [SIG2019] Reinier Vis, Dennis Bijslma, and Haiyun Xu. SIG/TÜViT Evaluation Criteria Trusted Product  Maintainability:  Guidance for producers. Version 11.0. Software Improvement Group, 2019 (`online <https://www.softwareimprovementgroup.com/wp-content/uploads/2019/11/20190919-SIG-TUViT-Evaluation-Criteria-Trusted-Product-Maintainability-Guidance-for-producers.pdf>`_).