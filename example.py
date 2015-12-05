#!/usr/bin/env python
# -*- coding: utf-8 -*-


from datetime import datetime
from crate.peewee import CrateDatabase, ObjectField
from peewee import (Model,
                    CharField,
                    DateTimeField,
                    BooleanField,
                    TextField,
                    ForeignKeyField,
                    fn)
from uuid import uuid4


db = CrateDatabase()
db.connect()


def gen_key():
    return str(uuid4())


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = CharField(null=True, default=gen_key, primary_key=True)
    username = CharField(null=True)


class Tweet(BaseModel):
    id = CharField(null=True, default=gen_key, primary_key=True)
    user = ForeignKeyField(User, related_name='tweets', null=True)
    message = TextField(null=True)
    details = ObjectField(null=True)
    created_date = DateTimeField(default=datetime.utcnow, null=True)
    is_published = BooleanField(default=True, null=True)

    def __repr__(self):
        return '<Tweet ({0}: {1}, details: {2})>'.format(
            self.user and self.user.username or None,
            self.message,
            self.details)


def print_tweets():
    for tweet in Tweet.select().join(User):
        print(tweet)



db.drop_tables([User, Tweet], safe=True)
db.create_tables([User, Tweet], safe=True)

arthur = User.create(username='Arthur')
db.execute_sql('refresh table user')

with db.atomic():
    Tweet.insert(user=arthur,
                 message='hello world',
                 details={"a": 1, "b": "foo"}).execute()
    t2 = Tweet.create(user=arthur, message='foobar')

db.execute_sql('refresh table tweet')
db.execute_sql('refresh table user')
print_tweets()

print('update')
t2.message = 'hello foobar'
t2.save()

db.execute_sql('refresh table tweet')
print_tweets()


print('')
print('where in')
for t in Tweet.select().where(Tweet.message << ['hello world', 'hello foobar']):
    print(t)

print('')
print('regex')
for t in Tweet.select().where(Tweet.message.regexp('hell.*')):
    print(t)

print('')
print('startswith')
for t in Tweet.select().where(Tweet.message.startswith('hell')):
    print(t)

print('')
print('select single field and filter by subscript')
for t in Tweet.select(Tweet.message).where(Tweet.details['a'] == 1):
    print('message: ' + t.message)

print('')
print('date filter')
for t in Tweet.select().join(User).where(
        User.username == 'Arthur',
        Tweet.created_date > datetime(2015, 10, 10)).order_by(Tweet.created_date):
    print(t)


print('')
print('count tweets')
print(Tweet.select().count())


print('')
print('distinct')
print(Tweet.select(fn.Distinct(Tweet.user)).scalar())


print('')
print('group by')
for t in Tweet.select(Tweet.user, fn.Count(Tweet.id).alias('ct'))\
        .group_by(Tweet.user)\
        .tuples():
    print(t)


print('')
print('extract')
for t in Tweet.select(Tweet).where(Tweet.created_date.year == '2015'):
    print(t)
