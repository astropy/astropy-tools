# This set of repositories is a mixture of affiliated packages and packages
# that use astropy_helpers and opted in receiving automated PRs to update
# the helpers version. If your package requires Python 3.5+ consider adding
# it to the list in the "helpers_3.py" file to recieve updates for the
# Python 3.5+ releases of astropy-helpers.

repositories = sorted(set([
    ('astropy', 'astroquery'),
    ('astropy', 'pyregion'),
    ('radio-astro-tools', 'spectral-cube'),
    ('astropy', 'astroplan'),
    ('astropy', 'astroscrappy'),
    ('RiceMunk', 'omnifit'),
    ('astropy', 'halotools'),
    ('pyspeckit', 'pyspeckit'),
    ('linetools', 'linetools'),
    ('astropy', 'astropy-healpix'),
    ('desihub', 'specsim'),
    ('dkirkby', 'speclite'),
    ('matiscke', 'lcps')
]))
