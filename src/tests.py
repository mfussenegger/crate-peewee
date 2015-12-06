
import os
import socket
from unittest import TestCase, TestSuite, makeSuite
from peewee import Model, CharField
from crate.peewee import CrateDatabase
from crate.client.cursor import Cursor
from crate.testing.layer import CrateLayer
from uuid import uuid4


def rnd_port():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    return port


here = os.path.dirname(__file__)
root = os.path.join(here, '..')
crate_layer = CrateLayer('crate',
                         port=rnd_port(),
                         transport_port=rnd_port(),
                         crate_home=os.path.join(root, 'parts', 'crate'))


db = CrateDatabase(servers=crate_layer.crate_servers)


def gen_key():
    return str(uuid4())


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = CharField(null=True, default=gen_key, primary_key=True)
    name = CharField(null=True)


class CratePeeweeTest(TestCase):

    def setUp(self):
        db.create_tables([User])

    def test_simple_select(self):
        User.insert(name='Arthur').execute()
        db.execute_sql('refresh table user')
        rows = [r for r in User.select()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].name, 'Arthur')


def test_suite():
    suite = TestSuite()
    s = makeSuite(CratePeeweeTest)
    s.layer = crate_layer
    suite.addTest(s)
    return suite
