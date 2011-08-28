Styles for Pygments.

Generate using something like:

    pygmentize -S tango -f html | sed -e 's/^/.codehilite /' > tango.scss

List all available styles:

    pygmentize -L
