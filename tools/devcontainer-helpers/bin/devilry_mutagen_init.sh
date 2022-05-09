#!/bin/sh

if [ -f "tools/devcontainer-helpers/bin/devilry_mutagen_init.sh" ]; then
    docker volume create devilry_dockerdev_mutagensync_volume
    docker container create --name devilry_dockerdev_mutagensync_container -v devilry_dockerdev_repo:/volumes/sync mutagenio/sidecar:0.13.1
    docker container start devilry_dockerdev_mutagensync_container
    docker exec devilry_dockerdev_mutagensync_container chown 1000:1000 /volumes/sync
    docker exec devilry_dockerdev_mutagensync_container chmod go+w /volumes/sync
    mutagen sync create \
        --name="devilry-dockerdev-sync" \
        --sync-mode=two-way-resolved \
        --default-owner-beta="id:1000" \
        --default-group-beta="id:1000" \
        --ignore 'node_modules/,.pytest_cache/,.vscode-atest-temp/,dbdev_tempdata/,.venv/' \
        . docker://devilry_dockerdev_mutagensync_container/volumes/sync

else
    echo "ERROR: You must be in the root directory of the devilry repo to run this script.";
fi
