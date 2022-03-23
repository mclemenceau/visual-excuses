#!/usr/bin/bash

rm -f update_excuses.yaml

wget https://people.canonical.com/~ubuntu-archive/proposed-migration/update_excuses.yaml.xz

if [ -f update_excuses.yaml.xz ] ; then
    xz -dk update_excuses.yaml.xz
    rm -f update_excuses.yaml.xz
fi
