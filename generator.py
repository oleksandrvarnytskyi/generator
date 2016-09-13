import sys
import yaml
import psycopg2

SCHEMA_FILE_PATH = "/Users/savar/PycharmProjects/junior/db2/schema2.yaml"
DATABASE_NAME = 'library'
USER_NAME = 'savar'

CREATE_TABLE = """CREATE TABLE "{table_name}" (
    "{table_name}_id" SERIAL PRIMARY KEY,
    {fields},
    "{table_name}_created" timestamp NOT NULL DEFAULT now(),
    "{table_name}_updated" timestamp DEFAULT NULL
);\n
"""
CREATE_TABLE_SIBLINGS = """CREATE TABLE "{table}__{rel_table}" (
    "{table}_id" INTEGER NOT NULL,
    "{rel_table}_id" INTEGER NOT NULL,
    "{table}__{rel_table}_quantity" INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY ("{table}_id", "{rel_table}_id")
);\n
"""

ALTER_TABLE_CHILD = """ALTER TABLE "{child}" ADD "{parent}_id" INTEGER NOT NULL,
    ADD CONSTRAINT "fk_{child}_{parent}_id" FOREIGN KEY ("{parent}_id")
    REFERENCES "{parent}" ("{parent}_id");\n
"""

ALTER_TABLE_SIBLINGS = """ALTER TABLE "{table}__{rel_table}"
    ADD CONSTRAINT "fk_{table}__{rel_table}_{table}_id"
    FOREIGN KEY ("{table}_id") REFERENCES "{table}" ("{table}_id");

ALTER TABLE "{table}__{rel_table}"
    ADD CONSTRAINT "fk_{table}__{rel_table}_{rel_table}_id"
    FOREIGN KEY ("{rel_table}_id") REFERENCES "{rel_table}" ("{rel_table}_id");
\n"""

CREATE_FUNCTION = """CREATE OR REPLACE FUNCTION update_{table}_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.{table}_updated = now();
   RETURN NEW;
END;
$$ language 'plpgsql';
\n"""

CREATE_TRIGGER = """CREATE TRIGGER "tr_{table}_updated" BEFORE UPDATE
ON "{table}" FOR EACH ROW EXECUTE PROCEDURE update_{table}_timestamp();\n
"""


class Generator(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.file_sql = None
        self.__tables = []
        self.parents_children = {}
        self.siblings = {}

    def drop_tables(self):
        con = None
        try:
            con = psycopg2.connect(database=DATABASE_NAME, user=USER_NAME)
            cur = con.cursor()
            con.c = True
            for tab in self.__tables:
                drop_query = "DROP TABLE IF EXISTS {} CASCADE;".format(tab)
                cur.execute(drop_query)
        except psycopg2.DatabaseError, e:
            if con:
                con.rollback()
            print 'Error %s' % e
            sys.exit(1)
        finally:
            if con:
                con.close()

    @staticmethod
    def getting_yaml_dict(path_with_file=SCHEMA_FILE_PATH):
        yaml_dict = {}
        with open(path_with_file, 'r') as stream:
            try:
                yaml_dict = yaml.load(stream)
            except yaml.YAMLError as er:
                print(er)
        return yaml_dict

    @staticmethod
    def format_fields(fields):
        return ',\n    '.join(f for f in fields)

    def get_fields(self, dictionary, tab_name, fields):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.get_fields(value, tab_name, fields)
            else:
                note = '"{table}_{column}" {type}'.format(
                    table=tab_name, column=key, type=value)
                fields.append(note)
        return fields

    def get_relations(self, table_content, tab_name, relations):
        for key, value in table_content.items():
            if isinstance(value, dict):
                self.get_relations(value, tab_name, relations)
            else:
                key = key.lower()
                relations[key] = value
        return relations

    def define_relations(self, all_relations):
        for table, relation in all_relations.items():
            for rel_tab, type_rel in relation.items():
                relations = all_relations[rel_tab]
                if type_rel == relations[table]:
                    sibl_lst = [rel_tab, table]
                    sibl_lst.sort()
                    self.siblings[sibl_lst[0]] = sibl_lst[1]
                if type_rel != relations[table]:
                    if type_rel == 'one':
                        self.parents_children[rel_tab] = table
                    else:
                        self.parents_children[table] = rel_tab

    def create_tables(self, config_db):
        all_relations = {}
        for table, content in config_db.items():
            fields = []
            for key, value in content.items():
                relations = {}
                if key == 'fields':
                    fields = self.get_fields(value, table, fields)
                if key == 'relations':
                    all_relations[table] = self.get_relations(value, table,
                                                              relations)
            query = CREATE_TABLE.format(table_name=table,
                                        fields=self.format_fields(fields))
            self.file_sql.write(query)

        self.define_relations(all_relations)

        for tab, rel_tab in self.siblings.items():
            create_query = CREATE_TABLE_SIBLINGS.format(
                               table=tab, rel_table=rel_tab)
            self.__tables.append('%s__%s' % (tab, rel_tab))
            alter_query = ALTER_TABLE_SIBLINGS.format(
                               table=tab, rel_table=rel_tab)
            self.file_sql.write(create_query)
            self.file_sql.write(alter_query)

        for tab, rel_tab in self.parents_children.items():
            alter_query = ALTER_TABLE_CHILD.format(parent=tab,
                                                   child=rel_tab)
            self.file_sql.write(alter_query)

    def create_functions(self, config_db):
        for key in config_db.keys():
            function = CREATE_FUNCTION.format(table=key)
            self.file_sql.write(function)

    def create_triggers(self, config_db):
        for key in config_db.keys():
            trigger = CREATE_TRIGGER.format(table=key)
            self.file_sql.write(trigger)

    def file_sql_creator(self):
        self.file_sql = open(self.file_name, 'w')
        db_config = self.getting_yaml_dict()
        db_config = dict((k.lower(), v) for k, v in db_config.items())
        self.__tables = db_config.keys()
        self.create_tables(db_config)
        self.create_functions(db_config)
        self.create_triggers(db_config)

        self.file_sql.close()


if __name__ == "__main__":
    name_sql_file = 'schema_gen.sql'

    gen = Generator(name_sql_file)
    gen.file_sql_creator()
    gen.drop_tables()
