from django import test
from model_bakery import baker

from cradmin_legacy.tests.sortable.cradmin_sortable_testapp.models import SortableItem
from cradmin_legacy.tests.sortable.cradmin_sortable_testapp.models import ItemContainer


class TestSortableItem(test.TestCase):
    """
    Test that classes inherit :class:`SortableBase` works as advertised!
    """

    def setUp(self):
        pass

    def _create_container(self):
        container = ItemContainer(name="test container")
        container.save()
        return container

    def _create_items(self, num_items, container=None):
        container = container or self._create_container()
        items = []
        for i in range(0, num_items, 1):
            items.append(SortableItem(container=container, name=f"test{i}", sort_index=i))
        SortableItem.objects.bulk_create(items)
        return SortableItem.objects.all()

    def test_has_sort_index_field(self):
        item = self._create_items(1)[0]
        self.assertTrue(hasattr(item, "sort_index"))
        self.assertEqual(item.sort_index, 0)

    def test_sort_item_last(self):
        i1, i2, i3, i4, i5, i6 = self._create_items(6)
        SortableItem.objects.sort_last(i1)
        reordered = [si.id for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(reordered, [i2.id, i3.id, i4.id, i5.id, i6.id, i1.id])

    def test_sort_item_3_last(self):
        i1, i2, i3, i4, i5, i6 = self._create_items(6)
        SortableItem.objects.sort_last(i3)
        reordered = [si.id for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(reordered, [i1.id, i2.id, i4.id, i5.id, i6.id, i3.id])

    def test_sort_last_item_first(self):
        i1, i2, i3, i4, i5, i6 = self._create_items(6)
        SortableItem.objects.sort_before(i6, i1.id)
        reordered = [si.id for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(reordered, [i6.id, i1.id, i2.id, i3.id, i4.id, i5.id])

    def test_sort_item_3_first(self):
        i1, i2, i3, i4, i5, i6 = self._create_items(6)
        SortableItem.objects.sort_before(i3, i1.id)
        reordered = [si.id for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(reordered, [i3.id, i1.id, i2.id, i4.id, i5.id, i6.id])

    def test_sort_item_move_first_before_id_4(self):
        i1, i2, i3, i4, i5, i6 = self._create_items(6)
        SortableItem.objects.sort_before(i1, i4.id)
        reordered = [si.id for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(reordered, [i2.id, i3.id, i1.id, i4.id, i5.id, i6.id])

    def test_sort_item_move_second_before_id_4(self):
        i1, i2, i3, i4, i5, i6 = self._create_items(6)
        SortableItem.objects.sort_before(i2, i4.id)
        reordered = [si.id for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(reordered, [i1.id, i3.id, i2.id, i4.id, i5.id, i6.id])

    def test_sort_item_move_second_before_id_4_in_allready_reordered_list(self):
        i1, i2, i3, i4, i5, i6 = self._create_items(6)
        SortableItem.objects.sort_last(i1)
        # now list is [i2,i3,i4,i5,i6,i1]
        SortableItem.objects.sort_before(i2, i4.id)
        reordered = [si.id for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(reordered, [i3.id, i2.id, i4.id, i5.id, i6.id, i1.id])

    def test_set_sort_index_to_last_no_siblings(self):
        container = self._create_container()
        item = SortableItem(container=container, name="My test")
        SortableItem.objects.set_newitem_sort_index_to_last(item)
        self.assertEqual(item.sort_index, 0)
        self.assertIsNone(item.pk)  # The item was not saved

    def test_set_sort_index_to_last_has_siblings(self):
        container = self._create_container()
        self._create_items(2, container=container)
        item = SortableItem(container=container, name="My test")
        SortableItem.objects.set_newitem_sort_index_to_last(item)
        self.assertEqual(item.sort_index, 2)
        self.assertIsNone(item.pk)  # The item was not saved

    def test_set_sort_index_to_last_refuse_with_sort_index(self):
        container = self._create_container()
        item = SortableItem(container=container, name="My test", sort_index=1)
        with self.assertRaises(ValueError):
            SortableItem.objects.set_newitem_sort_index_to_last(item)

    def test_set_sort_index_to_last_refuse_existing(self):
        container = self._create_container()
        item = SortableItem(container=container, name="My test", sort_index=1)
        item.save()
        item.sort_index = None
        with self.assertRaises(ValueError):
            SortableItem.objects.set_newitem_sort_index_to_last(item)

    #####
    # Additional tests to locate bug where sort_before gives value of 0
    #####

    def test_sort_before_two_objects_last_to_first_not_lessthan_zero(self):
        i1, i2 = self._create_items(2)
        SortableItem.objects.sort_before(i2, i1.id)

        for object in SortableItem.objects.all():
            self.assertTrue(object.sort_index >= 0)

    def test_sort_before_three_objects_last_to_first_not_lessthan_zero(self):
        i1, i2, i3 = self._create_items(3)
        SortableItem.objects.sort_before(i3, i1.id)

        for object in SortableItem.objects.all():
            self.assertTrue(object.sort_index >= 0)

    def test_sort_before_four_objects_last_to_first_not_lessthan_zero(self):
        i1, i2, i3, i4 = self._create_items(4)
        SortableItem.objects.sort_before(i4, i1.id)

        for object in SortableItem.objects.all():
            self.assertTrue(object.sort_index >= 0)

    def test_sort_before_two_objects_last_to_second_not_lessthan_zero(self):
        i1, i2 = self._create_items(2)
        SortableItem.objects.sort_before(i1, i1.id)

        for object in SortableItem.objects.all():
            self.assertTrue(object.sort_index >= 0)

    def test_sort_before_three_objects_last_to_second_not_lessthan_zero(self):
        i1, i2, i3 = self._create_items(3)
        SortableItem.objects.sort_before(i3, i2.id)

        for object in SortableItem.objects.all():
            self.assertTrue(object.sort_index >= 0)

    def test_sort_before_four_objects_last_to_second_not_lessthan_zero(self):
        i1, i2, i3, i4 = self._create_items(4)
        SortableItem.objects.sort_before(i4, i2.id)

        for object in SortableItem.objects.all():
            self.assertTrue(object.sort_index >= 0)

    def test_sort_before_two_objects_first_to_last_not_lessthan_zero(self):
        i1, i2 = self._create_items(2)
        SortableItem.objects.sort_before(i1, i2.id)

        for object in SortableItem.objects.all():
            self.assertTrue(object.sort_index >= 0)

    def test_sort_before_three_objects_first_to_last_not_lessthan_zero(self):
        i1, i2, i3 = self._create_items(3)
        SortableItem.objects.sort_before(i1, i3.id)

        for object in SortableItem.objects.all():
            self.assertTrue(object.sort_index >= 0)

    def test_sort_before_four_objects_first_to_last_not_lessthan_zero(self):
        i1, i2, i3, i4 = self._create_items(4)
        SortableItem.objects.sort_before(i1, i4.id)

        for object in SortableItem.objects.all():
            self.assertTrue(object.sort_index >= 0)

    def test_sortindex_is_none_sanity(self):
        container = baker.make(ItemContainer)
        item1 = baker.make(SortableItem, sort_index=None, container=container)
        item2 = baker.make(SortableItem, sort_index=None, container=container)
        item3 = baker.make(SortableItem, sort_index=None, container=container)
        SortableItem.objects.sort_last(item1)
        SortableItem.objects.sort_last(item2)
        SortableItem.objects.sort_last(item3)
        item1.refresh_from_db()
        item2.refresh_from_db()
        item3.refresh_from_db()
        self.assertEqual(0, item1.sort_index)
        self.assertEqual(1, item2.sort_index)
        self.assertEqual(2, item3.sort_index)


class TestRepairSortable(test.TestCase):
    def setUp(self):
        pass

    def _create_container(self):
        container = ItemContainer(name="test container")
        container.save()
        return container

    def _create_items(self, num_items, container=None, first_sort_index=0):
        container = container or self._create_container()
        items = []
        for i in range(first_sort_index, num_items):
            items.append(self._create_item(container, i))
        return items

    def _create_item(self, container, sort_index):
        si = SortableItem.objects.create(container=container, name=f"test{sort_index}", sort_index=sort_index)
        return si

    def test_repairs_empty_hole(self):
        container = self._create_container()
        items = self._create_items(2, container)
        items.append(self._create_item(container, items[1].sort_index + 2))

        SortableItem.objects.sort_before(items[1], items[0].id)

        indexes = [si.sort_index for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(indexes, [0, 1, 2])

    def test_repairs_duplicate_index(self):
        container = self._create_container()
        items = self._create_items(2, container)
        items.append(self._create_item(container, items[1].sort_index))

        SortableItem.objects.sort_before(items[1], items[0].id)

        indexes = [si.sort_index for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(indexes, [0, 1, 2])

    def test_repair_multiple_duplicate_indexes(self):
        container = self._create_container()
        items = self._create_items(2, container)
        items.append(self._create_item(container, items[1].sort_index))
        items.append(self._create_item(container, items[1].sort_index + 1))
        items.append(self._create_item(container, items[1].sort_index + 2))
        items.append(self._create_item(container, items[1].sort_index + 2))

        SortableItem.objects.sort_before(items[1], items[0].id)

        indexes = [si.sort_index for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(indexes, [0, 1, 2, 3, 4, 5])

    def test_repair_multiple_holes_in_indexes(self):
        container = self._create_container()
        items = self._create_items(2, container)
        items.append(self._create_item(container, items[1].sort_index + 2))
        items.append(self._create_item(container, items[1].sort_index + 3))
        items.append(self._create_item(container, items[1].sort_index + 5))
        items.append(self._create_item(container, items[1].sort_index + 7))

        SortableItem.objects.sort_before(items[1], items[0].id)

        indexes = [si.sort_index for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(indexes, [0, 1, 2, 3, 4, 5])

    def test_repair_holes_and_duplicates_in_indexes(self):
        container = self._create_container()
        items = self._create_items(2, container)
        items.append(self._create_item(container, items[1].sort_index))
        items.append(self._create_item(container, items[1].sort_index + 2))
        items.append(self._create_item(container, items[1].sort_index + 3))

        SortableItem.objects.sort_before(items[1], items[0].id)

        indexes = [si.sort_index for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(indexes, [0, 1, 2, 3, 4])

    def test_repair_several_indexes_hole(self):
        container = self._create_container()
        items = self._create_items(2, container)
        items.append(self._create_item(container, items[1].sort_index + 3))

        SortableItem.objects.sort_before(items[1], items[0].id)

        indexes = [si.sort_index for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(indexes, [0, 1, 2])

    def test_repair_hole_at_beginning(self):
        container = self._create_container()
        i1 = self._create_item(container, 1)
        i2 = self._create_item(container, 2)

        SortableItem.objects.sort_before(i2, i1.id)
        indexes = [si.sort_index for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(indexes, [0, 1])

    def test_repair_duplicate_at_beginning(self):
        container = self._create_container()
        i1 = self._create_item(container, 0)
        i2 = self._create_item(container, 0)
        self._create_item(container, 1)

        SortableItem.objects.sort_before(i2, i1.id)
        indexes = [si.sort_index for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(indexes, [0, 1, 2])

    def test_repair_duplicate_at_end(self):
        container = self._create_container()
        i1 = self._create_item(container, 0)
        i2 = self._create_item(container, 1)
        self._create_item(container, 1)

        SortableItem.objects.sort_before(i2, i1.id)
        indexes = [si.sort_index for si in SortableItem.objects.all().order_by("sort_index")]
        self.assertEqual(indexes, [0, 1, 2])
