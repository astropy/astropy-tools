#!/bin/env xonsh
"""
A xonsh script to run generate all the reference images for astropy core.

./generate_reference_images.xsh astropy_repo_dir images_output_dir [--new-dir]

if `--new-dir` is specifed a new timestamped dir will be created,
otherwise it is assumed that `images_output_dir` is already a timestamp dir.
"""

import datetime
from pathlib import Path

import yaml

base_path = Path($ARGS[1])
output_path = Path($ARGS[2])
create_new_dir = "--new-dir" in $ARGS
now = datetime.datetime.now().isoformat()

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
            if create_new_dir:
                command += f'-a "--mpl --mpl-generate-path=/images/{now}/{version}"'
            else:
                command += f'-a "--mpl --mpl-generate-path=/images/{version}"'

        if command:
            commands.append(command)

    command = ['/bin/sh', '-c', ';'.join(commands)]

    builds[name] = {'image': image,
                    'command': command}


for name, build in builds.items():
    print()
    print()
    print(f"Running {name} build...")
    docker pull f"{build['image']}"
    print(build['command'])
    docker run -v f"{base_path.absolute()}:/repo" -v f"{output_path.absolute()}:/images" -w /repo f"{build['image']}" @(build['command'])
