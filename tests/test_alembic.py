# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-FileCopyrightText: 2024 Graz University of Technology.
# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Test invenio-pidstore alembic."""

import pytest
from invenio_db.utils import alembic_test_context, drop_alembic_version_table


def test_alembic(app, db):
    """Test Alembic recipes."""
    ext = app.extensions["invenio-db"]

    if db.engine.name == "sqlite":
        raise pytest.skip("Upgrades are not supported on SQLite.")

    app.config["ALEMBIC_CONTEXT"] = alembic_test_context()

    # Check that pidstore models have been properly registered.
    expected_tables = {
        "pidstore_pid",
        "pidstore_recid",
        "pidstore_redirect",
    }
    assert expected_tables <= set(db.metadata.tables)

    # The schema created by db.create_all() must match the models.
    assert not ext.alembic.compare_metadata()

    # Recreate the schema using Alembic migrations.
    db.drop_all()
    drop_alembic_version_table()
    ext.alembic.upgrade()

    assert not ext.alembic.compare_metadata()

    # Test downgrading to the base Invenio-DB migration and upgrading again.
    ext.alembic.stamp()
    ext.alembic.downgrade(target="96e796392533")
    ext.alembic.upgrade()

    assert not ext.alembic.compare_metadata()

    drop_alembic_version_table()
