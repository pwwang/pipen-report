from pathlib import Path
from simpleconf import Config

LOCAL_CONFIG = Path.cwd().joinpath(".pipen-report.toml")
GLOBAL_CONFIG = Path.home().joinpath(".pipen-report.toml")

# Path to npm
NPM = "npm"

# Where should the frontend dependencies installed?\n
# By default, the frontend dependencies will be installed in
# frontend/ of the python package directory. However, this
# directory may not be writable. In this case, the frontend
# dependencies will be installed in the directory specified.
NMDIR = str(Path(__file__).parent.joinpath("frontend").resolve())

# Don't build the final report.
# If True only preprare the environment
# Say if you want to do the building manually
NOBUILD = False

# External components to be used in the report
EXTLIBS = None

CONFIG = Config.load(GLOBAL_CONFIG, LOCAL_CONFIG, ignore_nonexist=True)

CONFIG_KEYS = ('extlibs', 'npm', 'nmdir', 'nobuild')
