"""
Charts API routes.

Single endpoint to serve Charts
"""

from typing import Any

from fastapi import APIRouter

from dlo.api.deps.project import CManifest, CRuntime
from dlo.common.exception import errors

router = APIRouter(tags=["chart"])


@router.get("/charts")
async def get_charts(manifest: CManifest) -> dict[str, Any]:
    """
    Get the all charts present
    """
    charts_json = {}

    for chart_name, chart in manifest.charts.items():
        d = chart.to_dict()
        d.pop("option", None)
        charts_json[chart_name] = d

    return charts_json


_query_cache: dict[str, list] = {}


def cached_fetch_data(sql: str, runtime):
    if sql not in _query_cache:
        _query_cache[sql] = runtime.execute_query(sql).to_list()
    return _query_cache[sql]


def inject_data(
    obj: dict, data_map: dict[str, list], lookup: str = "data_key", target: str = "data"
):
    if isinstance(obj, dict):
        if lookup in obj:
            obj[target] = data_map.get(obj[lookup], [])

        for value in obj.values():
            inject_data(value, data_map, lookup, target)

    elif isinstance(obj, list):
        for item in obj:
            inject_data(item, data_map, lookup, target)


@router.get("/charts/{chart_uid}")
async def get_chart_option(runtime: CRuntime, chart_uid: str) -> dict[str, Any]:
    """
    Get chart option for ui to show
    """
    manifest = runtime.manifest
    chart = manifest.charts.get(chart_uid)

    if chart is None:
        raise errors.NotFoundError(f"Chart `{chart_uid}` not found.")

    chart_option = chart.option

    if chart.data_source == "sql":
        data = cached_fetch_data(chart.sql, runtime)

        inject_data(obj=chart_option, data_map=data)

    return {
        "engine": chart.engine,
        "option": chart_option,
    }
