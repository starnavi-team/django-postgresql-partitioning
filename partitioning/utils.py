from django.db import connection


def setup(model):
    parent_table = model._meta.db_table
    column = model.partitioning.get('column')

    if not column:
        return 'Set column in partitioning config for model {}'.format(model.__name___)

    with connection.cursor() as cursor:
        cursor.execute('''
            CREATE OR REPLACE FUNCTION {parent_table}_insert_child()
            RETURNS TRIGGER AS $$
                DECLARE
                    tablename VARCHAR;
                    checks TEXT;
                BEGIN
                    tablename := '{parent_table}__{column}_' || NEW.{column};
                    checks := '{column} = ' || NEW.{column};                    
                    
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
        '''.format(
            parent_table=parent_table,
            column=column
        ))
