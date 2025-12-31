# pg-explain-viz

> **Documentation**: https://takawasi-social.com/tools/pg-explain-viz/

Visualize PostgreSQL EXPLAIN ANALYZE as ASCII tree.

EXPLAIN, but readable.

## Quick Start

```bash
# 1. Install
pip install pg-explain-viz

# 2. Visualize
pg-explain "SELECT * FROM users WHERE id = 1" -d mydb
```

## Features

- **ASCII tree**: Hierarchical plan visualization
- **Time highlighting**: See where time is spent
- **Suggestions**: Automatic optimization hints
- **Row comparison**: Estimated vs actual rows

## Output Example

```
Planning Time: 0.12ms
Execution Time: 2.34ms

Query Plan
├── Hash Join
│   Cost: 800.00..1200.00  Rows: 100 → 98  Time: 1.5ms [████░░░░░░] (45%)
│   ├── Seq Scan on orders ⚠️ SLOWEST
│   │   Cost: 0.00..500.00  Rows: 1000 → 1523  Time: 2.1ms [██████░░░░] (64%)
│   │   Filter: date > '2025-01-01'
│   └── Hash
│       └── Index Scan on users using users_pkey
│           Cost: 0.15..8.17  Rows: 1 → 1  Time: 0.02ms

╭──────────────────── Summary ────────────────────╮
│ Slowest Node: Seq Scan (2.1ms)                  │
│                                                 │
│ Suggestions:                                    │
│   - Consider adding index on orders             │
╰─────────────────────────────────────────────────╯
```

## Usage

```bash
# Direct query
pg-explain "SELECT * FROM users" -d mydb

# From file
pg-explain -f query.sql -d mydb

# Full connection string
pg-explain "SELECT 1" --dsn "postgresql://user:pass@localhost/mydb"

# Parse existing EXPLAIN JSON
pg-explain --json-input explain.json
```

## Connection Options

| Option | Description |
|--------|-------------|
| `--dsn` | Full connection string |
| `-h, --host` | Database host (default: localhost) |
| `-p, --port` | Database port (default: 5432) |
| `-d, --database` | Database name |
| `-U, --user` | Database user |
| `-W, --password` | Database password |

## Pre-generated JSON

If you can't connect directly, export EXPLAIN JSON and visualize:

```sql
-- In psql
EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM users;
-- Copy output to explain.json
```

```bash
pg-explain --json-input explain.json
```

## More Tools

See all dev tools: https://takawasi-social.com/en/

## License

MIT
