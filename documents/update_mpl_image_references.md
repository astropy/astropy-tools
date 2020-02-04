This is a quick reference for the procedure of udpating the matplotlib reference images.
The example is for the core package, but the procedure can be the same for any packages
testing against baseline images.


For small changes, anyone can update the reference images as CicleCI serves up the images
as artifacts. Here's what to do::

* Go to a recent mpldev build on CircleCI on master (e.g. https://circleci.com/gh/astropy/astropy/59263)
* Go to the artifacts tab and expand the results directory shown
* Download ``test_latex_labels.png``
* Clone the https://github.com/astropy/astropy-data repo locally
* Go inside ``testing/astropy/2019-08-02T11:38:58.288466/3.3.x`` (latest date and MPL version)
* Copy the ``test_latex_labels.png`` file into this directory
* Commit and open a PR: https://github.com/astropy/astropy-data/pull/84 - and check the differences in the diff to make sure they make sense
