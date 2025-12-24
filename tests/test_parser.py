"""Tests for EXPLAIN parser."""

import json

from pg_explain.parser import parse_explain_json, find_slowest_node


SAMPLE_EXPLAIN = '''[
  {
    "Plan": {
      "Node Type": "Hash Join",
      "Startup Cost": 100.0,
      "Total Cost": 500.0,
      "Plan Rows": 100,
      "Actual Rows": 98,
      "Actual Total Time": 10.5,
      "Actual Loops": 1,
      "Plans": [
        {
          "Node Type": "Seq Scan",
          "Relation Name": "orders",
          "Startup Cost": 0.0,
          "Total Cost": 200.0,
          "Plan Rows": 1000,
          "Actual Rows": 1523,
          "Actual Total Time": 8.2,
          "Actual Loops": 1,
          "Filter": "date > '2025-01-01'"
        },
        {
          "Node Type": "Index Scan",
          "Relation Name": "users",
          "Index Name": "users_pkey",
          "Startup Cost": 0.15,
          "Total Cost": 8.17,
          "Plan Rows": 1,
          "Actual Rows": 1,
          "Actual Total Time": 0.02,
          "Actual Loops": 1
        }
      ]
    },
    "Planning Time": 0.12,
    "Execution Time": 10.8
  }
]'''


def test_parse_explain():
    """Parse sample EXPLAIN output."""
    plan = parse_explain_json(SAMPLE_EXPLAIN)

    assert plan.planning_time == 0.12
    assert plan.execution_time == 10.8
    assert plan.root.node_type == "Hash Join"
    assert len(plan.root.children) == 2


def test_parse_children():
    """Parse child nodes correctly."""
    plan = parse_explain_json(SAMPLE_EXPLAIN)

    seq_scan = plan.root.children[0]
    assert seq_scan.node_type == "Seq Scan"
    assert seq_scan.relation == "orders"
    assert seq_scan.filter == "date > '2025-01-01'"

    index_scan = plan.root.children[1]
    assert index_scan.node_type == "Index Scan"
    assert index_scan.index_name == "users_pkey"


def test_find_slowest():
    """Find slowest node in tree."""
    plan = parse_explain_json(SAMPLE_EXPLAIN)
    slowest = find_slowest_node(plan.root)

    assert slowest.node_type == "Hash Join"
    assert slowest.actual_time == 10.5


def test_row_estimates():
    """Parse row estimate vs actual."""
    plan = parse_explain_json(SAMPLE_EXPLAIN)

    seq_scan = plan.root.children[0]
    assert seq_scan.rows_estimated == 1000
    assert seq_scan.rows_actual == 1523
