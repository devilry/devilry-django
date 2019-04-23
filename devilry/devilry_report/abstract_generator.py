import xlsxwriter
from django.utils import timezone


class AbstractReportGenerator(object):
    """
    Abstract generator class that generators must inherit from. Provides an interface for
    generators used by :class:`devilry.devilry_report.models.DevilryReport`.
    """
    def __init__(self, devilry_report):
        self.devilry_report = devilry_report

    @classmethod
    def get_generator_type(cls):
        """
        Get the generator type as string.

        Returns:
            str: Generator type.
        """
        raise NotImplementedError()

    def get_output_filename_prefix(self):
        """
        Get the output filename prefix. Returns ``report`` by default.

        Returns:
            str: Output filename prefix.
        """
        return 'report'

    def get_output_file_extension(self):
        """
        Get the output file extension.

        Returns:
            str: Output file extension.

        """
        raise NotImplementedError()

    def get_content_type(self):
        """
        The content-type used for download.

        Returns:
            str: A HTTP-supported content-type
        """
        raise NotImplementedError()

    def validate(self):
        """
        Validate required input. Mostly used for validating
        :attr:`devilry.devilry_report.models.DevilryReport.generator_options`.
        This method is optional and does not have to be overridden.

        If everything is validated, do nothing, else raise ValidationError.
        """

    def generate(self, file_like_object):
        """
        Must be overridden in subclass.
        Should generated a byte format that can be stored in the :class:`devilry.devilry_report.models.DevilryReport`.

        Args:
            file_like_object: An object that can be read from.
        """
        raise NotImplementedError()

    def get_object_iterable(self):
        """
        Override this and and return an iterable of "objects".
        """
        return []


class AbstractExcelReportGenerator(AbstractReportGenerator):
    """
    Abstract generator class for generating an Excel worksheet with the xlsxwriter library.
    """
    def __init__(self, row=1, column=0, *args, **kwargs):
        super(AbstractExcelReportGenerator, self).__init__(*args, **kwargs)
        self.row = row
        self.column = column
        self.workbook = None

    def get_output_file_extension(self):
        return 'xlsx'

    def get_content_type(self):
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def add_worksheet_headers(self, worksheet):
        """
        Override and add worksheet headers.

        Args:
            worksheet: A xlsxwriter Worksheet instance.
        """
        raise NotImplementedError()

    def write_data_to_worksheet(self, worksheet_tuple, row, column, obj):
        """
        Override this and write the data to the worksheet.

        Args:
            worksheet_tuple: A tuple of type(str) and xlsxwriter Worksheet instance.
            row: Row position integer.
            column: Column position integer.
            obj: The object to write data from.
        """
        raise NotImplementedError()

    def get_work_sheets(self):
        """
        Override this method if want to add multiple worksheets.

        Adds a single worksheet by default.

        Must return a list of `xlsx.Worksheet`.
        """
        return [
            ('default', self.workbook.add_worksheet())
        ]

    def make_header_format(self):
        cell_format = self.workbook.add_format()
        cell_format.set_bold()
        return cell_format

    def make_date_cell_format(self):
        return self.workbook.add_format({'num_format': 'dd/mm/yyyy'})

    def make_datetime_cell_format(self):
        return self.workbook.add_format({'num_format': 'dd/mm/yyyy h:mm'})

    def write_datetime_cell(self, worksheet, row, column, datetime_object):
        if datetime_object:
            return worksheet.write_datetime(row, column, self.__make_excel_friendly_datetime(datetime_object),
                                            self.datetime_cell_format)
        return worksheet.write(row, column, '')

    def write_date_cell(self, worksheet, row, column, datetime_object):
        if datetime_object:
            return worksheet.write_datetime(row, column, self.__make_excel_friendly_datetime(datetime_object),
                                            self.date_cell_format)
        return worksheet.write(row, column, '')

    def __make_excel_friendly_datetime(self, datetime_object):
        datetime_object = timezone.localtime(datetime_object)
        datetime_object = datetime_object.replace(tzinfo=None)
        return datetime_object

    def initialize_workbook(self, file_like_object):
        self.workbook = xlsxwriter.Workbook(file_like_object, {'in_memory': True})
        self.header_cell_format = self.make_header_format()
        self.date_cell_format = self.make_date_cell_format()
        self.datetime_cell_format = self.make_datetime_cell_format()

    def write(self, file_like_object):
        self.initialize_workbook(file_like_object=file_like_object)
        row = 1
        column = 0
        for worksheet in self.get_work_sheets():
            self.add_worksheet_headers(worksheet=worksheet[1])
            for obj in self.get_object_iterable():
                self.write_data_to_worksheet(
                    worksheet_tuple=worksheet,
                    row=row,
                    column=column,
                    obj=obj
                )
                row += 1
            row = 1
        self.workbook.close()
