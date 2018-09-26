from django.db import connection

ALLOWED_TYPES = ['list', 'range_day', 'range_week', 'range_month', 'range_year']
DATE_FORMAT = {
    'day': 'YYYY_MM_DD',
    'week': 'YYYY_WW',
    'month': 'YYYY_MM',
    'year': 'YYYY',
}
DATE_FIELDS = ['DateTimeField', 'DateField']


class Partitioning:
    def __init__(self, model):
        self.model = model

    def validate(self, config):
        if not config['column'] or not config['type']:
            raise ValueError('({}) Invalid configuration. type, column are required.'.format(
                self.model
            ))

        if not config['type'] in ALLOWED_TYPES:
            raise ValueError('({}) Type {} unsupported. Allowed types: {}.'.format(
                self.model, config['type'], ', '.join(ALLOWED_TYPES)
            ))

        if config['type'].startswith('range_') and \
                not self.model._meta.get_field(config['column']).get_internal_type() in DATE_FIELDS:
            raise ValueError('({}) Invalid field type for {}. Allowed field types: {}.'.format(
                self.model, config['type'], ', '.join(DATE_FIELDS)
            ))

    def get_list_tablename(self, column):
        return "'{column}_' || NEW.{column}".format(column=column)

    def get_list_check(self, column):
        return "'{column} = ''' || NEW.{column} || ''''".format(column=column)

    def get_date_range_tablename(self, column, interval):
        return "'{column}_' || TO_CHAR(NEW.{column}, '{format}')".format(
            column=column, format=DATE_FORMAT[interval]
        )

    def get_date_range_check(self, column, interval):
        start = "DATE_TRUNC('{interval}', NEW.{column})".format(column=column, interval=interval)
        end = "{start} + INTERVAL '1 {interval}'".format(start=start, interval=interval)
        return "'{column} >= ''' || {start} || ''' AND {column} < ''' || {end} || ''''" \
            .format(column=column, start=start, end=end)

    def get_variables(self):
        parent_table = self.model._meta.db_table
        table_name = ["'{}'".format(parent_table)]
        checks = []

        for config in self.model.partitioning:
            self.validate(config)

            if config['type'] == 'list':
                table_name.append(self.get_list_tablename(config['column']))
                checks.append(self.get_list_check(config['column']))

            if config['type'].startswith('range_'):
                _, interval = config['type'].split('_')
                table_name.append(self.get_date_range_tablename(config['column'], interval))
                checks.append(self.get_date_range_check(config['column'], interval))

        table_name = " || '__' || ".join(table_name)
        checks = " || ' AND ' || ".join(checks)

        return {
            'parent_table': parent_table,
            'table_name': table_name,
            'checks': checks
        }

    def setup(self):
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE OR REPLACE FUNCTION {parent_table}_insert_child()
                RETURNS TRIGGER AS $$
                    DECLARE
                        tablename TEXT;
                        checks TEXT;
                    BEGIN
                        tablename := {table_name};
                        checks := {checks};

                        IF NOT EXISTS(
                            SELECT 1 FROM information_schema.tables WHERE table_name = tablename
                        )
                        THEN
                            BEGIN
                                EXECUTE 'CREATE TABLE ' || tablename || ' (
                                    CHECK (' || checks || '),
                                    LIKE {parent_table} INCLUDING DEFAULTS INCLUDING CONSTRAINTS INCLUDING INDEXES
                                ) INHERITS ({parent_table});';
                            END;
                        END IF;

                        EXECUTE 'INSERT INTO ' || tablename || ' VALUES (($1).*);' USING NEW;
                        RETURN NEW;
                    END;
                $$ LANGUAGE plpgsql;

                DO $$
                BEGIN
                IF NOT EXISTS(
                    SELECT 1
                    FROM information_schema.triggers
                    WHERE event_object_table = '{parent_table}'
                    AND trigger_name = 'before_insert_{parent_table}_trigger'
                ) THEN
                    CREATE TRIGGER before_insert_{parent_table}_trigger
                        BEFORE INSERT ON {parent_table}
                        FOR EACH ROW EXECUTE PROCEDURE {parent_table}_insert_child();
                END IF;
                END $$;

                CREATE OR REPLACE FUNCTION {parent_table}_delete_master()
                RETURNS TRIGGER AS $$
                    BEGIN
                        DELETE FROM ONLY {parent_table} WHERE id = NEW.id;
                        RETURN NEW;
                    END;
                $$ LANGUAGE plpgsql;

                DO $$
                BEGIN
                IF NOT EXISTS(
                    SELECT 1
                    FROM information_schema.triggers
                    WHERE event_object_table = '{parent_table}'
                    AND trigger_name = 'after_insert_{parent_table}_trigger'
                ) THEN
                    CREATE TRIGGER after_insert_{parent_table}_trigger
                        AFTER INSERT ON {parent_table}
                        FOR EACH ROW EXECUTE PROCEDURE {parent_table}_delete_master();
                END IF;
                END $$
            '''.format(**self.get_variables()))
