from ievv_opensource.utils import ievvbuildstatic
from ievv_opensource.utils.lazy_static import LazyStatic
from ievv_opensource.utils.lazy_string import LazyString

import django_cradmin


class SassBuild(ievvbuildstatic.sassbuild.Plugin):
    def __init__(
        self,
        sourcefile,
        sourcefolder="styles",
        destinationfolder=None,
        other_sourcefolders=None,
        sass_include_paths=None,
        sass_variables=None,
        **kwargs,
    ):

        super(SassBuild, self).__init__(
            sourcefile=sourcefile,
            sourcefolder=sourcefolder,
            destinationfolder=destinationfolder,
            other_sourcefolders=other_sourcefolders,
            sass_include_paths=sass_include_paths,
            sass_variables=self.build_cradmin_sass_variables(sass_variables),
            **kwargs,
        )

    def build_cradmin_sass_variables(self, extra_sass_variables):
        sass_variables = {
            "media-path": LazyString(
                "'{}'", LazyStatic("django_cradmin_styles/{}/media".format(django_cradmin.__version__))
            )
        }
        if extra_sass_variables:
            sass_variables.update(extra_sass_variables)
        return sass_variables
