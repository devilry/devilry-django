"""
Utilities for making migration scripts.
"""


def create_foreignkey_table_change_sql(table,
                                       field,
                                       old_constraint_name,
                                       new_referenced_table):
    """
    Change the ForeignKey identified by ``table`` and ``field``
    to point to the ``new_referenced_table`` table.

    We also need the ``old_constraint_name`` since Django creates
    """
    new_constraint_name = '{table}_{field}_id_fk_{new_referenced_table}_id'.format(
        table=table,
        field=field,
        new_referenced_table=new_referenced_table)
    return """
        ALTER TABLE {table}
          DROP CONSTRAINT {old_constraint_name};
        ALTER TABLE {table}
          ADD CONSTRAINT {new_constraint_name}
          FOREIGN KEY ({field}_id)
          REFERENCES {new_referenced_table}(id) DEFERRABLE INITIALLY DEFERRED;
    """.format(table=table,
               old_constraint_name=old_constraint_name,
               field=field,
               new_constraint_name=new_constraint_name,
               new_referenced_table=new_referenced_table)
