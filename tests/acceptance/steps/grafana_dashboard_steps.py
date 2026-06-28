"""
Step definitions for Grafana dashboard feature.

Contains step for validating datasource UID format in the provisioning YAML.
"""

from pytest_bdd import then

import yaml


@then("each provisioned datasource should have a string uid")
def then_datasources_have_string_uids(grafana_datasources_path) -> None:
    """Assert that every datasource in the provisioning file has a string uid."""
    content = grafana_datasources_path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    datasources = data.get("datasources", [])
    for ds in datasources:
        uid = ds.get("uid", "")
        assert isinstance(uid, str) and len(uid) > 0, (
            f"Datasource '{ds.get('name', 'unknown')}' has missing or non-string uid: {uid!r}"
        )
        assert not uid.isdigit(), (
            f"Datasource '{ds.get('name', 'unknown')}' has numeric uid: {uid}"
        )
