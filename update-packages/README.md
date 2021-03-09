### Auto-updates for packages using astropy-helpers

**NOTE: The scripts here are primarily for archival records only.
No further update of astropy-helpers is planned.**

The scripts in this folder are used to update packages making use of
astropy-helpers by automatically opening pull requests to those packages.

If you are a package maintainer and would like your package to receive automated
pull requests to update astropy-helpers, then add your package either to
[helpers_2.py](https://github.com/astropy/astropy-procedures/blob/main/update-packages/helpers_2.py)
(if your package supports Python 2) or
[helpers_3.py](https://github.com/astropy/astropy-procedures/blob/main/update-packages/helpers_3.py)
(if your package only supports Python 3).
