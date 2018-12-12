# This set of repositories is a mixture of affiliated packages and packages
# that use astropy_helpers and opted in receiving automated PRs to update
# the helpers version. If your package requires Python 3.5+ consider adding
# it to the list in the "helpers_3.py" file to recieve updates for the
# Python 3.5+ releases of astropy-helpers.

repositories = sorted(set([
    ('astropy', 'astroquery'),
    ('weaverba137', 'pydl'),
    ('astropy', 'reproject'),
    ('pyvirtobs', 'pyvo'),
    ('gammapy', 'gammapy'),
    ('sncosmo', 'sncosmo'),
    ('astropy', 'pyregion'),
    ('radio-astro-tools', 'spectral-cube'),
    ('astropy', 'astroplan'),
    ('astropy', 'astroscrappy'),
    ('zblz', 'naima'),
    ('RiceMunk', 'omnifit'),
    ('StingraySoftware', 'HENDRICS'),
    ('StingraySoftware', 'stingray'),
    ('astropy', 'halotools'),
    ('Chandra-MARX', 'marxs'),
    ('pyspeckit', 'pyspeckit'),
    ('linetools', 'linetools'),
    ('astropy', 'regions'),
    ('hamogu', 'astrospec'),
    ('hamogu', 'arcus'),
    ('hamogu', 'marxs-lynx'),
    ('hamogu', 'psfsubtraction'),
    ('astropy', 'astropy-healpix'),
    ('astropy', 'saba'),
    ('astropy', 'package-template'),
    ('spacetelescope', 'astroimtools'),
    ('spacetelescope', 'synphot_refactor'),
    ('spacetelescope', 'stsynphot_refactor'),
    ('spacetelescope', 'imexam'),
    ('desihub', 'specsim'),
    ('dkirkby', 'speclite'),
    ('discos', 'srt-single-dish-tools'),
    ('mhvk', 'baseband'),
    ('BEAST-Fitting', 'beast'),
    ('PAHFIT', 'pahfit'),
    ('karllark', 'dust_extinction'),
    ('karllark', 'dust_attenuation'),
    ('karllark', 'measure_extinction'),
    ('matiscke', 'lcps'),
    ('BEAST-Fitting', 'megabeast')
]))
