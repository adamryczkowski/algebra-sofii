set fallback := true

[private]
help:
    just --list

[private]
install-pipx: (install-system-dependency "pipx" "pipx")
    #!/usr/bin/env bash
    set -euo pipefail
    set -x
    pipx ensurepath
    set +x

install-poetry:
    #!/usr/bin/env bash
    set -euo pipefail

    # Check if running inside Docker as non-root user
    if [ -f /.dockerenv ] && [ "$(whoami)" != "root" ]; then
        echo "Detected Docker environment with non-root user, using pip instead of pipx"
        # Check if poetry is already installed
        if command -v poetry &> /dev/null; then
            echo "Poetry is already installed."
        else
            echo "Installing poetry using pip..."
            pip install --user poetry
            # Add ~/.local/bin to PATH if not already there
            if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
                export PATH="$HOME/.local/bin:$PATH"
                echo "Added ~/.local/bin to PATH"
            fi
        fi
    else
        # Use the original pipx-based installation
        just install-pipx-dependency "poetry"
    fi

[private]
install-system-dependency macname linuxname commandname="":
    #!/usr/bin/env bash
    set -euo pipefail
    # Check if running under the MacOS operating system
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [[ "{{ commandname }}" == "" ]]; then
            commandname="{{ macname }}"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ "{{ commandname }}" == "" ]]; then
            commandname="{{ linuxname }}"
        fi
    else
        echo "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    if command -v "$commandname" &> /dev/null; then
        echo "$commandname is already installed."
        exit 0
    fi
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install {{ macname }}
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if ! dpkg -s "{{ linuxname }}">/dev/null  2> /dev/null; then
            if [[ "$(whoami)" != "root" ]]; then
                set -x
                sudo apt-get update
                sudo apt-get install -y {{ linuxname }}
                set +x
            else
                set -x
                apt-get update
                apt-get install -y {{ linuxname }}
                set +x
            fi
        fi
    fi

[private]
install-pipx-dependency name command_name="{{name}}": install-pipx
    #!/usr/bin/env bash
    set -euo pipefail
    if command -v {{ command_name }} &> /dev/null; then
      exit 0
    fi

    pipx install {{ name }}

# installs pre-commit hooks (and pre-commit if it is not installed)
install-hooks: install-pre-commit
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -f .git/hooks/pre-commit ]; then
      pre-commit install --install-hooks
    fi

[private]
install-pre-commit: install-venv (install-pipx-dependency "pre-commit")

[private]
install: install-poetry
    #!/usr/bin/env bash
    set -euo pipefail
    # Deactivate any active Python virtual environment
    if [ -n "${VIRTUAL_ENV-}" ]; then
      deactivate || true
    fi
    poetry install

# Creates a virtual environment for each subproject. Required for pyRight pre-commit check to work correctly.
install-venv: install-poetry
    #!/usr/bin/env bash
    set -euo pipefail
    set -x
    # Deactivate any active Python virtual environment
    if [ -n "${VIRTUAL_ENV-}" ]; then
      deactivate || true
    fi
    if [ ! -d ".venv" ]; then
        poetry install
    else
        echo "Virtual environment already exists."
    fi

# Setup the project by installing pre-commit hooks and venvs. Required for pre-commit checks to work correctly.
setup: install-venv install-hooks propagate-default-setup

# Makes sure that the project is set up with _any_ configuration. If the configuration is missing, it will create a default one.
propagate-default-setup:
    #!/usr/bin/env bash
    set -euo pipefail
    # Do nothing at the moment

# Upgrades all pip dependencies for all the subprojects. Besides the obvious benefits, potentially dagnereous, because newer versions may contain bugs.
upgrade-all-dependencies:
    #!/usr/bin/env bash
    set -euo pipefail
    poetry update

# Runs pre-commit hooks on all files
validate: install-poetry install-hooks propagate-default-setup
    #!/usr/bin/env bash
    set -euo pipefail

    # Ensure virtual environment exists and all dependencies (including dev) are installed
    if [ -n "${VIRTUAL_ENV-}" ]; then
      deactivate || true
    fi
    poetry install

    if pre-commit run --all-files; then
        echo "Pre-commit validation passed successfully"
    else
        echo "Pre-commit validation failed"
        exit 1
    fi

# Cleans all virtual environments. This is useful when you want to start from scratch, or after a major upgrade or branch jump.
clean: install-poetry
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -n "${VIRTUAL_ENV-}" ]; then
      echo "Please first deactivate the existing virtual environment."
      exit 1
    fi
    poetry env remove --all

# Tests each subproject by recursively calling `just test` in each subproject directory.
test:
    #!/usr/bin/env bash
    set -euo pipefail
    poetry run coverage  run --source . --omit 'tests/*' -m pytest -W error::RuntimeWarning
    poetry run coverage report -m

# Re-writes the dependencies of each subproject to the latest versions and updates the lock files.
poetry-lock: install-poetry
    #!/usr/bin/env bash
    set -euo pipefail
    poetry lock

# Updates pre-commit hooks to the latest versions
upgrade-precommit:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v pre-commit &> /dev/null; then
      echo "pre-commit is not installed. Please run 'just install-hooks' first."
      exit 1
    fi
    pre-commit autoupdate
