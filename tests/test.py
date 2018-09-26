from datetime import datetime

from django.db import connection
from django.test import TestCase

from .app.models import Message


class MessageTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from django.core.management import call_command
        call_command('setup_partitioning', 'app')

    def setUp(self):
        Message.objects.create(text='msg1', tag='private', created=datetime(2018, 9, 1))
        Message.objects.create(text='msg2', tag='work', created=datetime(2018, 9, 1))
        Message.objects.create(text='msg2', tag='work', created=datetime(2018, 9, 15))
        Message.objects.create(text='msg2', tag='work', created=datetime(2018, 10, 1))

    def test_object_create(self):
        new_message = Message.objects.create(text='test', tag='private', created=datetime(2018, 9, 15))
        self.assertEqual(Message.objects.count(), 5)
        self.assertTrue(Message.objects.filter(pk=new_message.pk).exists())

    def test_object_retrieve(self):
        message = Message.objects.get(text='msg1')
        self.assertEqual(message.text, 'msg1')

    def test_object_update(self):
        message = Message.objects.get(text='msg1')
        message.text = 'msg3'
        message.save()

        message = Message.objects.get(pk=message.pk)
        self.assertEqual(message.text, 'msg3')

    def test_objects_delete(self):
        message = Message.objects.get(text='msg1')
        message.delete()

        self.assertFalse(Message.objects.filter(pk=message.pk).exists())

    def test_master_empty(self):
        with connection.cursor() as cursor:
            cursor.execute('SELECT count(*) FROM ONLY app_message')
            row = cursor.fetchone()
            self.assertEqual(row[0], 0)

    def test_child(self):
        with connection.cursor() as cursor:
            cursor.execute('SELECT count(*) FROM app_message__tag_private__created_2018_09')
            row = cursor.fetchone()
            self.assertEqual(row[0], 1)

            cursor.execute('SELECT count(*) FROM app_message__tag_work__created_2018_09')
            row = cursor.fetchone()
            self.assertEqual(row[0], 2)

            cursor.execute('SELECT count(*) FROM app_message__tag_work__created_2018_10')
            row = cursor.fetchone()
            self.assertEqual(row[0], 1)
