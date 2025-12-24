"""ASCII tree renderer for query plans."""

from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text

from .parser import PlanNode, QueryPlan, find_slowest_node


def render_plan(plan: QueryPlan, console: Console):
    """Render query plan as Rich tree."""
    # Header
    console.print()
    console.print(f"[bold]Planning Time:[/] {plan.planning_time:.2f}ms")
    console.print(f"[bold]Execution Time:[/] {plan.execution_time:.2f}ms")
    console.print()

    # Find slowest for highlighting
    slowest = find_slowest_node(plan.root)

    # Build tree
    tree = Tree(f"[bold]{_format_node_header(plan.root)}[/]")
    _add_children(tree, plan.root, slowest, plan.execution_time)

    console.print(tree)
    console.print()

    # Summary
    _print_summary(plan, slowest, console)


def _format_node_header(node: PlanNode) -> str:
    """Format node header line."""
    parts = [node.node_type]

    if node.relation:
        parts.append(f"on {node.relation}")
    if node.index_name:
        parts.append(f"using {node.index_name}")

    return ' '.join(parts)


def _format_node_details(node: PlanNode, total_time: float) -> Text:
    """Format node details."""
    text = Text()

    # Cost
    text.append(f"Cost: {node.startup_cost:.2f}..{node.total_cost:.2f}  ", style="dim")

    # Rows
    if node.rows_actual != node.rows_estimated:
        style = "yellow" if abs(node.rows_actual - node.rows_estimated) > node.rows_estimated * 0.5 else "dim"
        text.append(f"Rows: {node.rows_estimated} → {node.rows_actual}  ", style=style)
    else:
        text.append(f"Rows: {node.rows_actual}  ", style="dim")

    # Time with bar
    if total_time > 0:
        pct = (node.actual_time / total_time) * 100
        bar_len = int(pct / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        style = "red" if pct > 50 else "yellow" if pct > 20 else "green"
        text.append(f"Time: {node.actual_time:.1f}ms [{style}]{bar}[/{style}] ({pct:.0f}%)")

    return text


def _add_children(tree: Tree, node: PlanNode, slowest: PlanNode, total_time: float):
    """Recursively add children to tree."""
    for child in node.children:
        is_slowest = child is slowest
        style = "red bold" if is_slowest else ""

        header = _format_node_header(child)
        if is_slowest:
            header += " ⚠️ SLOWEST"

        branch = tree.add(f"[{style}]{header}[/{style}]")
        branch.add(_format_node_details(child, total_time))

        if child.filter:
            branch.add(Text(f"Filter: {child.filter}", style="dim italic"))

        _add_children(branch, child, slowest, total_time)


def _print_summary(plan: QueryPlan, slowest: PlanNode, console: Console):
    """Print summary panel."""
    lines = []
    lines.append(f"Slowest Node: {slowest.node_type} ({slowest.actual_time:.1f}ms)")

    # Suggestions
    suggestions = _get_suggestions(plan.root)
    if suggestions:
        lines.append("")
        lines.append("[yellow]Suggestions:[/yellow]")
        for s in suggestions:
            lines.append(f"  - {s}")

    console.print(Panel('\n'.join(lines), title="Summary"))


def _get_suggestions(node: PlanNode) -> List[str]:
    """Generate optimization suggestions."""
    suggestions = []

    # Check for Seq Scans
    if node.node_type == 'Seq Scan' and node.rows_actual > 1000:
        suggestions.append(f"Consider adding index on {node.relation}")

    # Check for row estimate errors
    if node.rows_estimated > 0:
        ratio = node.rows_actual / node.rows_estimated
        if ratio > 10 or ratio < 0.1:
            suggestions.append(f"Statistics may be outdated for {node.relation or node.node_type}")

    # Recurse
    for child in node.children:
        suggestions.extend(_get_suggestions(child))

    return suggestions
