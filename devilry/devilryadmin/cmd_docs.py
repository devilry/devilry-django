#!/usr/bin/env python
# Completely clean and rebuild the docs. Depends on docs_clean, docs_autogenerate_restful and docs_sphinx_build.

from common import depends, Command, forwardable_args


depends(Command('docs_clean'),
        Command('docs_autogenerate_restful'),
        Command('docs_sphinx_build', *forwardable_args()))
