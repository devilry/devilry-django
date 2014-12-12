#/bin/bash

# Resize and convert apple-touch-icon.png
convert -background transparent -resize x16 -gravity center -crop 16x16+0+0 apple-touch-icon.png -flatten favicon.ico
