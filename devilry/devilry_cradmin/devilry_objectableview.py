#
# class DatetimeColumn(PlainTextColumn):
#     datetime_format = 'SHORT_DATETIME_FORMAT'
#
#     def render_value(self, obj):
#         value = super(DatetimeColumn, self).render_value(obj)
#         if value is None: #true
#             return None #translate yes
#         else:
#             return defaultfilters.date(value, self.datetime_format)

        #Also a template to override values yes, no
        #no: `text-warning`

#yes: `text-success
#override the template and dp everything in the template