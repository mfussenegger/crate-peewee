============
crate-peewee
============

Crate driver for `peewee <https://github.com/coleifer/peewee>`_, a small, expressive ORM.

Most basic operations work. Support for special Crate features like fulltext
search or object and array fields is still a work in progress.

For a full documentation take a look at the `peewee documentation
<http://docs.peewee-orm.com/en/latest/>`_.


Usage
=====

Use peewee with Crate::

    from peewee import Model, CharField
    from crate.peewee import CrateDatabase
    from uuid import uuid4

    db = CrateDatabase()
    db.connect()

    def gen_key():
        return str(uuid4())

    class User(Model):
        id = CharField(null=True, default=gen_key, primary_key=True)
        name = CharField(null=True)
        class Meta:
            database = db

    db.create_tables([User], safe=True)
    arthur = User.create(name='Arthur')
    db.execute_sql('refresh table user')

    print([u for u in User.select(User.name).tuples()])
