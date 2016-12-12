# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import htmls
from django import test
from devilry.devilry_cradmin.devilry_tablebuilder import base as tablebuilder


class TestTableBuilder(test.TestCase):

    def test_table_tag(self):
        row_header = tablebuilder.RowRenderer()
        row_header.extend([
            tablebuilder.ColumnHeaderRenderer(value='item'),
            tablebuilder.ColumnHeaderRenderer(value='item')
        ])
        tb = tablebuilder.Table(table_headers=row_header)
        tr = tablebuilder.RowRenderer()
        tr.extend([
            tablebuilder.ColumnItemRenderer(value='item'),
            tablebuilder.ColumnItemRenderer(value='item')
        ])
        tb.append(tr)
        selector = htmls.S(tb.render())
        selector.prettyprint()
