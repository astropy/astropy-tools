#!/bin/env xonsh
"""
A xonsh script to run generate all the reference images for astropy core.

The idea of this script is you give it the astropy repo dir and the
astropy-data dir where the figure tests live, and then you PR the changes to
the astropy-data repo.

Usage:
    generate_reference_images.xsh <astropy_repo_dir> <base_images_output_dir> [--new-dir | --sub-dir=<subdir>] [--clean] [--sudo]

Options:
    - h --help          Show this screen.
    --version           Show version.
    --new-dir           Generate a new timestamp dir in <base_images_output_dir>.
    --sub-dir=<subdir>  Use this subdir in <base_images_output_dir> rather than creating a new one.
    --clean             Run `git clean -fxd` after every build to clean the env.
    --sudo              Run the `git clean -fxd` with sudo, and also chown the output dir at the end.
"""
from docopt import docopt
import datetime
from pathlib import Path

import yaml

args = docopt(__doc__, version="0.2")

base_path = Path(args['<astropy_repo_dir>'])
output_path = Path(args['<base_images_output_dir>'])
create_new_dir = args['--new-dir']
sub_dir = args['--sub-dir']

clean_comand = None
if args['--clean']:
    clean_command = "git clean -fxd"
    if args['--sudo']:
        clean_command = f"sudo {clean_command}"
    clean_command = clean_command.split()

if create_new_dir:
    sub_dir = datetime.datetime.now().isoformat()

with open(base_path / '.circleci' / 'config.yml') as f:
    config = yaml.load(f)

config = dict(filter(lambda x: x if x[0].startswith("image-tests") else None, config['jobs'].items()))


print("Found the following builds in the circleci config:")
builds = {}
for name, build in config.items():
    image = build['docker'][0]['image']
    commands = []
    for step in build['steps']:
        if not isinstance(step, dict):
            continue
        command = step.get('run', {}).get('command', '')

        if "--mpl" in command:
            print(name)
            if "mpldev" in name:
                version = "3.2.x"
            else:
                version = image.split(":")[0].split("mpl")[1]
                version = f"{version[0]}.{version[1]}.x"
            command = command.split("-a")[0]
            if sub_dir:
                command += f'-a "--mpl --mpl-generate-path=/images/{sub_dir}/{version}"'
            else:
                command += f'-a "--mpl --mpl-generate-path=/images/{version}"'

        if command:
            commands.append(command)

    command = ['/bin/sh', '-c', ';'.join(commands)]

    builds[name] = {'image': image,
                    'command': command}


def clean_repo():
    if clean_command:
        cwd = Path.cwd()
        cd f"{base_path}"
        print("Cleaning repo...")
        $[@(clean_command)]
        cd f"{cwd}"


# Ensure we start with a clean env
clean_repo()

for name, build in builds.items():
    print()
    print()
    print(f"Running {name} build...")
    docker pull f"{build['image']}"
    print(build['command'])
    docker run -v f"{base_path.resolve()}:/repo" -v f"{output_path.resolve()}:/images" -w /repo f"{build['image']}" @(build['command'])
    clean_repo()

if args['--sudo']:
    uid = $(id -u).strip()
    $[sudo chown -R @(uid) @(output_path.resolve())]
