# -*- coding: utf-8 -*-


import htmls
from django import test
from devilry.devilry_cradmin.devilry_tablebuilder import base as tablebuilder


class TestTableBuilder(test.TestCase):

    def test_table_structure(self):
        table = tablebuilder.Table()
        row1 = tablebuilder.RowRenderer()
        row1.append(tablebuilder.DataItemRenderer(value="Item value in row 1"))
        row1.append(tablebuilder.DataItemRenderer(value="Item value in row 1"))
        row2 = tablebuilder.RowRenderer()
        row2.append(tablebuilder.DataItemRenderer(value="Item value in row 2"))
        row2.append(tablebuilder.DataItemRenderer(value="Item value in row 2"))
        row3 = tablebuilder.RowRenderer()
        row3.append(tablebuilder.DataItemRenderer(value="Item value in row 3"))
        row3.append(tablebuilder.DataItemRenderer(value="Item value in row 3"))

        table.append(row1)
        table.append(row2)
        table.append(row3)

        selector = htmls.S(table.render())

        self.assertTrue(selector.one('.devilry-tablebuilder-table'))
        self.assertEqual(3, len(selector.list('.devilry-tablebuilder-row')))
        self.assertEqual(6, len(selector.list('.devilry-tablebuilder-data')))
