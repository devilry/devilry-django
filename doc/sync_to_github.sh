#!/bin/bash


VERSION=dev
REPODIR=devilry.github.com
OUTDIR=$REPODIR/$VERSION
INDIR=build/html


make clean html
rm -rf $OUTDIR
cp -r $INDIR $OUTDIR
cd $REPODIR; git add $VERSION; cd ..
