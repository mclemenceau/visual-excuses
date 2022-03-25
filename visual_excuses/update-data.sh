#!/usr/bin/bash

rm -f update_excuses.yaml

wget https://people.canonical.com/~ubuntu-archive/proposed-migration/update_excuses.yaml.xz

if [ -f update_excuses.yaml.xz ] ; then
    xz -dk update_excuses.yaml.xz
    rm -f update_excuses.yaml.xz
fi


PKG=$(curl http://reqorts.qa.ubuntu.com/reports/m-r-package-team-mapping.html | grep "var jd" | cut -d "=" -f2 | sed 's/;//')

echo "packages_by_team = $PKG" > packages_by_team.py