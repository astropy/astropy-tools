# This set of repositories is a mixture of affiliated packages and packages
# that use astropy_helpers and opted in receiving automated PRs to update
# the helpers version. If your package requires Python 3.5+ consider adding
# it to the list in the "helpers_3.py" file to recieve updates for the
# Python 3.5+ releases of astropy-helpers.

repositories = sorted(set([
    ('astropy', 'specutils'),
    ('astropy', 'astroquery'),
    ('astropy', 'photutils'),
    ('ejeschke', 'ginga'),
    ('astroML', 'astroML'),
    ('weaverba137', 'pydl'),
    ('aplpy', 'aplpy'),
    ('astrofrog', 'reproject'),
    ('pyvirtobs', 'pyvo'),
    ('gammapy', 'gammapy'),
    ('astropy', 'ccdproc'),
    ('sncosmo', 'sncosmo'),
    ('glue-viz', 'glue'),
    ('astropy', 'pyregion'),
    ('radio-astro-tools', 'spectral-cube'),
    ('olebole', 'python-cpl'),
    ('astropy', 'astroplan'),
    ('astropy', 'astroscrappy'),
    ('zblz', 'naima'),
    ('RiceMunk', 'omnifit'),
    ('adrn', 'gala'),
    ('jobovy', 'galpy'),
    ('StingraySoftware', 'HENDRICS'),
    ('StingraySoftware', 'stingray'),
    ('astropy', 'halotools'),
    ('jesford', 'cluster-lensing'),
    ('Chandra-MARX', 'marxs'),
    ('pyspeckit', 'pyspeckit'),
    ('linetools', 'linetools'),
    ('poliastro', 'poliastro'),
    ('astropy', 'regions'),
    ('chandra-marx', 'marxs'),
    ('hamogu', 'astrospec'),
    ('hamogu', 'arcus'),
    ('hamogu', 'marxs-lynx'),
    ('hamogu', 'psfsubtraction'),
    ('astropy', 'regions'),
    ('astropy', 'astropy-healpix'),
    ('astropy', 'saba'),
    ('astropy', 'package-template'),
    ('sunpy', 'sunpy'),
    ('chianti-atomic', 'ChiantiPy'),
    ('pyspeckit', 'pyspeckit'),
    ('spacetelescope', 'asdf'),
    ('spacetelescope', 'astroimtools'),
    ('spacetelescope', 'synphot_refactor'),
    ('spacetelescope', 'stsynphot_refactor'),
    ('spacetelescope', 'stginga'),
    ('spacetelescope', 'imexam'),
    ('spacetelescope', 'spherical_geometry'),
    ('spacetelescope', 'gwcs'),
    ('spacetelescope', 'specviz'),
    ('spacetelescope', 'cubeviz'),
    ('spacetelescope', 'mosviz'),
    ('stsci-jwst', 'wss_tools'),
    ('hipspy', 'hips'),
    ('desihub', 'specsim'),
    ('dkirkby', 'speclite'),
    ('matteobachetti', 'srt-single-dish-tools'),
    ('mhvk', 'baseband'),
    ('BEAST-Fitting', 'beast'),
    ('PAHFIT', 'pypahfit'),
    ('karllark', 'dust_extinction'),
    ('karllark', 'dust_attenuation'),
    ('karllark', 'measure_extinction')
]))
