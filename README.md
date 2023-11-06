
# InsidePostgreSQL Package
This Python package provides functionality to interact with a PostgreSQL database and perform various checks and calculations. It includes the following features:

- Connection to a PostgreSQL database
- Checking for inactive replication slots
- Checking for long-running queries
- Counting active sessions
- Calculating table bloat ratio
- Checking the last analyze and autovacuum dates for tables
- Checking node and postgresql exporter endpoints
- Checking average lock count on database
- Checking archiver process failure.

# Getting Started

```bash
pip3 install insidepostgresql
```

```python
import postgresql
db = postgresql.PostgreSQL("172.17.0.2", "demo", "test123", "test")
```

```
+------------------------------------------+----------+----------------------------------------------------------------------------------------------------+
| Issue                                    | Result   | Description                                                                                        |
+==========================================+==========+====================================================================================================+
| Connected To PostgreSQL                  | ✓        | PostgreSQL connection test.                                                                        |
+------------------------------------------+----------+----------------------------------------------------------------------------------------------------+
| Long Running Query                       | ✓        | There is no running query older than 1 minute                                                      |
+------------------------------------------+----------+----------------------------------------------------------------------------------------------------+
| Sum of Active Sessions < 50              | ✓        | Active session count is less than 50                                                               |
+------------------------------------------+----------+----------------------------------------------------------------------------------------------------+
| Average Important Lock Count < 10        | ✓        | Average of RowExclusiveLock,ShareUpdateExclusiveLock,ShareLock,AccessExclusiveLock is less than 10 |
+------------------------------------------+----------+----------------------------------------------------------------------------------------------------+
| Last Analyze/Autovacuum in the Last Week | ✓        | All tables are maintained this week.                                                               |
+------------------------------------------+----------+----------------------------------------------------------------------------------------------------+
| No Bloat Table Exists                    | ✓        | There is no table with bloat ratio greater than 50                                                 |
+------------------------------------------+----------+----------------------------------------------------------------------------------------------------+
| No Inactive Replication Slot             | ✓        | All replication slots are working and active.                                                      |
+------------------------------------------+----------+----------------------------------------------------------------------------------------------------+
| Node Exporter Working                    | ✗        | Node exporter are working and running                                                              |
+------------------------------------------+----------+----------------------------------------------------------------------------------------------------+
| PostgreSQL Exporter Working              | ✗        | PostgreSQL exporter are working and running                                                        |
+------------------------------------------+----------+----------------------------------------------------------------------------------------------------+
| Archiver Process                         | ✓        | Archiver process is working.                                                                       |
+------------------------------------------+----------+----------------------------------------------------------------------------------------------------+


# Contributing

If you would like to contribute to insidepostgresql, please submit a pull request with your changes. Before submitting a pull request, please make sure that your changes are properly tested and documented.

# License
InsideCouchbase is licensed under the MIT license. See the LICENSE file for more information.