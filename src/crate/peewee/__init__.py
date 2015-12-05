
from crate.client import connect
from peewee import (Database,
                    QueryCompiler,
                    Clause,
                    Field,
                    OP,
                    SQL,
                    R,
                    EnclosedClause,
                    Node,
                    fn)


def no_modifiers():
    return None


class SubscriptNode(Node):
    _node_type = 'subscript'

    def __init__(self, node, parts):
        self.node = node
        self.parts = parts
        super().__init__()

    def __getitem__(self, value):
        return SubscriptNode(self.node, self.parts + [value])


class ObjectField(Field):
    db_field = 'object'

    def db_value(self, value):
        return value

    def python_value(self, value):
        return value

    def __getitem__(self, value):
        return SubscriptNode(self, [value])


class CrateCompiler(QueryCompiler):

    def _parse_subscript(self, node, alias_map, conv):
        sql, params = self.parse_node(node.node, alias_map, conv)
        subscript = '[' + ''.join(["'" + p + "'" for p in node.parts]) + ']'
        return sql + subscript, params

    def get_parse_map(self):
        parse_map = super().get_parse_map()
        parse_map['subscript'] = self._parse_subscript
        return parse_map

    def field_definition(self, field):
        field.get_modifiers = no_modifiers
        return super().field_definition(field)

    def _create_table(self, model_class, safe=False):
        statement = 'CREATE TABLE IF NOT EXISTS' if safe else 'CREATE TABLE'
        meta = model_class._meta

        columns, constraints = [], []
        if meta.composite_key:
            pk_cols = [meta.fields[f].as_entity()
                       for f in meta.primary_key.field_names]
            constraints.append(Clause(
                SQL('PRIMARY KEY'), EnclosedClause(*pk_cols)))
        for field in meta.sorted_fields:
            columns.append(self.field_definition(field))
            ## No ForeignKeyField support
            #if isinstance(field, ForeignKeyField) and not field.deferred:
            #    constraints.append(self.foreign_key_constraint(field))

        if model_class._meta.constraints:
            for constraint in model_class._meta.constraints:
                if not isinstance(constraint, Node):
                    constraint = SQL(constraint)
                constraints.append(constraint)

        return Clause(
            SQL(statement),
            model_class.as_entity(),
            EnclosedClause(*(columns + constraints)))



class CrateDatabase(Database):
    foreign_keys = False
    compiler_class = CrateCompiler
    field_overrides = {
        'string': 'string',
        'text': 'string',
        'datetime': 'timestamp',
        'bool': 'boolean'
    }
    op_overrides = {
        OP.REGEXP: '~',
        OP.ILIKE: 'LIKE',
    }

    def __init__(self, hosts=None):
        super().__init__(self, 'default')

    def _connect(self, database, **kwargs):
        return connect(**kwargs)

    def get_tables(self, schema='doc'):
        query = ('select table_name from information_schema.tables '
                 'where schema_name = ? order by table_name')
        rows = self.execute_sql(query, (schema,)).fetchall()
        return [r[0] for r in rows]

    def create_index(self, model_class, fields, unique=False):
        pass

    def extract_date(self, date_part, date_field):
        return fn.EXTRACT(Clause(R(date_part), R('FROM'), date_field))
