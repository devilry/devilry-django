from __future__ import unicode_literals

from django import test

from devilry.devilry_dbcache.devilry_dbcache_testapp.models import Person


class TestBulkCreateQuerySetMixin(test.TestCase):
    def test_sanity(self):
        bulk_operation = Person.objects.postgres_bulk_create([
            Person(name='test1'),
            Person(name='test2'),
            Person(name='test3'),
        ])
        # print bulk_operation.explain(compact=False)
        ids = bulk_operation.execute()
        self.assertEqual(len(ids), 3)
        self.assertTrue(Person.objects.filter(name='test1').exists())
        self.assertTrue(Person.objects.filter(name='test2').exists())
        self.assertTrue(Person.objects.filter(name='test3').exists())

    def test_works_with_defaults(self):
        bulk_operation = Person.objects.postgres_bulk_create([
            Person(name='test1'),
        ])
        bulk_operation.execute()
        created_person = Person.objects.get(name='test1')
        self.assertEqual(20, created_person.age)

    def test_batch_size(self):
        bulk_operation = Person.objects.postgres_bulk_create([
            Person(name='test1'),
            Person(name='test2'),
            Person(name='test3'),
            Person(name='test4'),
            Person(name='test5'),
        ], batch_size=2)
        ids = bulk_operation.execute()
        self.assertEqual(len(ids), 5)
        self.assertTrue(Person.objects.filter(name='test1').exists())
        self.assertTrue(Person.objects.filter(name='test2').exists())
        self.assertTrue(Person.objects.filter(name='test3').exists())
        self.assertTrue(Person.objects.filter(name='test4').exists())
        self.assertTrue(Person.objects.filter(name='test5').exists())

    def test_return_objects(self):
        bulk_operation = Person.objects.postgres_bulk_create([
            Person(name='test1'),
            Person(name='test2'),
            Person(name='test3'),
        ])
        people = bulk_operation.execute_and_return_objects()
        self.assertEqual(len(people), 3)
        self.assertEqual(people[0], Person.objects.get(name='test1'))
        self.assertEqual(people[1], Person.objects.get(name='test2'))
        self.assertEqual(people[2], Person.objects.get(name='test3'))

    # def test_performance(self):
    #     people = [Person(name='test{}'.format(x)) for x in range(10000)]
    #     bulk_operation = Person.objects.postgres_bulk_create(people)
    #     bulk_operation.execute()
    #     self.assertEqual(10000, Person.objects.count())
