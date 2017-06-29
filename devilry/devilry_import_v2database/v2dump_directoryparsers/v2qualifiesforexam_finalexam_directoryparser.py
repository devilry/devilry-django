from devilry.devilry_import_v2database import v2dump_directoryparser


class V2QualifiesForFinalExamDirectoryParser(v2dump_directoryparser.V2DumpDirectoryParser):
    def get_app_label(self):
        return 'devilry_qualifiesforexam'

    def get_model_name_lowercase(self):
        return 'qualifiesforfinalexam'
