"""EXPLAIN JSON parser."""

import json
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class PlanNode:
    """Single node in query plan."""
    node_type: str
    relation: str
    alias: str
    startup_cost: float
    total_cost: float
    rows_estimated: int
    rows_actual: int
    actual_time: float
    loops: int
    filter: str
    index_name: str
    children: List['PlanNode']


@dataclass
class QueryPlan:
    """Parsed query plan."""
    planning_time: float
    execution_time: float
    root: PlanNode


def parse_explain_json(json_str: str) -> QueryPlan:
    """Parse EXPLAIN (FORMAT JSON) output.

    PostgreSQL returns a list with single element containing the plan.
    """
    data = json.loads(json_str)

    # Handle list wrapper
    if isinstance(data, list):
        data = data[0]

    plan_data = data.get('Plan', data)

    return QueryPlan(
        planning_time=data.get('Planning Time', 0),
        execution_time=data.get('Execution Time', 0),
        root=_parse_node(plan_data),
    )


def _parse_node(data: Dict) -> PlanNode:
    """Parse single plan node."""
    children = []
    for child_data in data.get('Plans', []):
        children.append(_parse_node(child_data))

    return PlanNode(
        node_type=data.get('Node Type', 'Unknown'),
        relation=data.get('Relation Name', ''),
        alias=data.get('Alias', ''),
        startup_cost=data.get('Startup Cost', 0),
        total_cost=data.get('Total Cost', 0),
        rows_estimated=data.get('Plan Rows', 0),
        rows_actual=data.get('Actual Rows', 0),
        actual_time=data.get('Actual Total Time', 0),
        loops=data.get('Actual Loops', 1),
        filter=data.get('Filter', '') or data.get('Index Cond', ''),
        index_name=data.get('Index Name', ''),
        children=children,
    )


def find_slowest_node(node: PlanNode) -> PlanNode:
    """Find the slowest node in the plan tree."""
    slowest = node
    max_time = node.actual_time

    for child in node.children:
        child_slowest = find_slowest_node(child)
        if child_slowest.actual_time > max_time:
            slowest = child_slowest
            max_time = child_slowest.actual_time

    return slowest
