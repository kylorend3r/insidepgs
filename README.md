
# InsidePostgreSQL Package
This Python package provides functionality to interact with a PostgreSQL database and perform various checks and calculations. It includes the following features:

- Connection to a PostgreSQL database
- Checking for inactive replication slots
- Checking for long-running queries
- Counting active sessions
- Calculating table bloat ratio
- Checking the last analyze and autovacuum dates for tables


# Getting Started

```bash
pip3 install insidepostgresql
```

```python
import postgresql
db = postgresql.PostgreSQL("172.17.0.2", "demo", "test123", "test")
```

```
Connected to PostgreSQL successfully.
+------------------------------------------+---------+
| Metric                                   | Value   |
+==========================================+=========+
| Long Running Query                       | ✓       |
+------------------------------------------+---------+
| Sum of Active Sessions < 50              | ✓       |
+------------------------------------------+---------+
| Last Analyze/Autovacuum in the Last Week | ✓       |
+------------------------------------------+---------+
| No Bloat Table Exists                    | ✓       |
+------------------------------------------+---------+
| No Inactive Replication Slot             | ✓       |
+------------------------------------------+---------+
```

# Contributing

If you would like to contribute to insidepostgresql, please submit a pull request with your changes. Before submitting a pull request, please make sure that your changes are properly tested and documented.

# License
InsideCouchbase is licensed under the MIT license. See the LICENSE file for more information.