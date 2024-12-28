# Base configuration for Sphinx documentation builder
#

# Command line configurable parameters
OPTS          =
BUILD_CMD     = sphinx-build
PROJECT_NAME  = GitAnalyzer
SRC_DIR       = .
OUT_DIR       = _build

# Default target shows help information
help:
	@$(BUILD_CMD) -M help "$(SRC_DIR)" "$(OUT_DIR)" $(OPTS) $(O)

.PHONY: help Makefile

# Generic rule: forwards all targets to Sphinx builder
# O parameter serves as an alias for OPTS
%: Makefile
	@$(BUILD_CMD) -M $@ "$(SRC_DIR)" "$(OUT_DIR)" $(OPTS) $(O)