#!/bin/sh

mutagen sync terminate devilry-dockerdev-sync
docker container stop devilry_dockerdev_mutagensync_container
docker container rm devilry_dockerdev_mutagensync_container
docker volume rm devilry_dockerdev_mutagensync_volume
