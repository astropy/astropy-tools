#!/usr/bin/env python

import tqdm
import math
import json
import urllib
import argparse
import requests

def get_travis_build_info(reponame, token, fail_output_fn=None):
    headers = {'Travis-API-Version':'3', 'Authorization':'token ' + token}

    slug = urllib.parse.urlencode({'':reponame})[1:]
    base_url = 'https://api.travis-ci.org'

    start_url = '/repo/{}/builds?limit=100'.format(slug)
    res =  requests.get(base_url + start_url, headers=headers)
    if not res.ok:
        raise ValueError('first request was not 200/OK - returned "{}"',format(res.text), res, res.headers)

    j = res.json()
    builds = j['builds']

    npages = math.ceil(j['@pagination']['count']/j['@pagination']['limit'])
    try:
        with tqdm.tqdm(total=npages) as pbar:
            while j['@pagination']['next'] is not None:
                res = requests.get(base_url + j['@pagination']['next']['@href'], headers=headers)
                pbar.update(1)
                if not res.ok:
                    raise ValueError('Request was not 200/OK - returned "{}"',format(res.text), res, res.headers)
                j = res.json()
                builds.extend(j['builds'])
            pbar.update(1)  # should get to 100%
    finally:
        if fail_output_fn:
            with open(fail_output_fn, 'w') as f:
                json.dump(builds, f)


    return builds

if __name__ == '__main__':
    p = argparse.ArgumentParser()

    p.add_argument('reponame')
    p.add_argument('token')
    p.add_argument('-o', '--output-file', default='travis_build_info.json')
    p.add_argument('--no-gzip', action='store_true')

    args = p.parse_args()
    builds = get_travis_build_info(args.reponame, args.token, args.output_file + '.fail')

    if builds:
        fn = args.output_file
        if not args.no_gzip:
            import gzip
            fopen = gzip.open
            if not fn.endswith('.gz'):
                fn += '.gz'
            fobj = gzip.open(fn, 'wt')
        else:
            fobj = open(fn, 'w')
        try:
            json.dump(builds, fobj)
        finally:
            fobj.close()
