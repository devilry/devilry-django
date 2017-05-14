from devilry.devilry_import_v2database import v2dump_directoryparser


class V2UserDirectoryParser(v2dump_directoryparser.V2DumpDirectoryParser):
    def get_app_label(self):
        return 'auth'

    def get_model_name_lowercase(self):
        return 'user'
