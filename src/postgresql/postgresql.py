import psycopg2
import datetime
import requests
from tabulate import tabulate


class PostgreSQL:
    def __init__(self, ip, user, password, database):
        self.ip = ip
        self.user = user
        self.password = password
        self.database = database
        self.pgsConnection = None
        self.nodeExporterUrl=f'''http://{ip}:9100/metrics'''
        self.pgsExporterUrl=f'''http://{ip}:9187/metrics'''
        self.checkNodeExporter()
        self.checkPostgresqlExporter()
        self.connect()
        if self.connectedPostgresql:
            self.inactiveReplicationSlot()
            self.longrunningQuery()
            self.activeSessionCount()
            self.calculateBloat()
            self.lastAnalyze()
            self.prepareResults()
        else:
            self.allTablesMaintained=False
            self.inactivereplication=False
            self.longrunningquery=False
            self.sumofactivesessionslessthan50=False
            self.allTablesMaintained=False
            self.nobloattableexists=False
            self.prepareResults()


    def connect(self):
        try:
            self.pgsConnection = psycopg2.connect(
                host=self.ip,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Connected to PostgreSQL successfully.")
            self.connectedPostgresql=True
        except psycopg2.Error as e:
            self.connectedPostgresql=False


    def execute_query(self, query):
        if not self.pgsConnection:
            print("Not connected to PostgreSQL. Call connect() first.")
            return

        cursor = self.pgsConnection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def inactiveReplicationSlot(self):
        query = """
        SELECT active FROM pg_replication_slots WHERE active = false;
        """
        result = self.execute_query(query)
        self.inactivereplication = False if result else True

    def longrunningQuery(self):
        query = """
        SELECT pid, usename, state, query_start
        FROM pg_stat_activity
        WHERE state != 'idle'
          AND usename NOT IN ('postgres', 'test')
          AND query_start < NOW() - INTERVAL '1 minute';
        """
        result = self.execute_query(query)
        self.longrunningquery = False if result else True

    def activeSessionCount(self):
        query = """
        SELECT COUNT(*)
        FROM pg_stat_activity
        WHERE state != 'idle'
          AND usename NOT IN ('postgres', 'test');
        """
        result = self.execute_query(query)
        self.sumofactivesessionslessthan50 = True if result[0][0] <= 50 else False

    def calculateBloat(self):
        query = """
        SELECT schemaname, tablename, (pg_total_relation_size(schemaname || '.' || tablename) - pg_relation_size(schemaname || '.' || tablename)) / pg_total_relation_size(schemaname || '.' || tablename) * 100 AS bloat_ratio
        FROM pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
        """
        result = self.execute_query(query)
        self.nobloattableexists = all(row[2] <= 50 for row in result)

    def lastAnalyze(self):
        cursor = self.pgsConnection.cursor()

        # Get the list of tables in the database
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = cursor.fetchall()

        # Dictionary to store the results
        table_results = {}
        self.allTablesMaintained=True

        for table in tables:
            table_name = table[0]

            # Retrieve the last analyze date for the table
            cursor.execute(f"SELECT last_analyze FROM pg_stat_all_tables WHERE relname = '{table_name}'")
            last_analyze_result = cursor.fetchone()
            last_analyze_date = last_analyze_result[0] if last_analyze_result else None

            # Retrieve the last autovacuum date for the table
            cursor.execute(f"SELECT last_autovacuum FROM pg_stat_all_tables WHERE relname = '{table_name}'")
            last_autovacuum_result = cursor.fetchone()
            last_autovacuum_date = last_autovacuum_result[0] if last_autovacuum_result else None

            # Determine if the dates are older than 5 days
            current_date = datetime.date.today()
            five_days_ago = current_date - datetime.timedelta(days=5)
            if (last_autovacuum_date is None) or (last_analyze_date is None):
                pass
            else:
                try:
                    if (last_analyze_date.date() < five_days_ago) or (last_autovacuum_date.date() < five_days_ago):
                        self.allTablesMaintained=False
                except Exception as testExcep:
                    print(testExcep)
                    print(f'''Failed to collect stats for table {table_name}''')

        cursor.close()

    def checkNodeExporter(self):
        try:
            response = requests.get(self.nodeExporterUrl)
            result=response.status_code
            if result==200:
                self.nodeExporterWorking=True
                
            else:
                self.nodeExporterWorking=False
        except Exception as nodeExporterException:
            self.nodeExporterWorking=False

        return True
    

    def checkPostgresqlExporter(self):
        try:
            response = requests.get(self.pgsExporterUrl)
            result=response.status_code
            if result==200:
                self.pgsExporterWorking=True
                
            else:
                self.pgsExporterWorking=False
        except Exception as nodeExporterException:
            self.pgsExporterWorking=False

        return True

    def prepareResults(self):
        connection_text= "✓" if self.connectedPostgresql else "✗"
        inactivereplication_text = "✓" if self.inactivereplication else "✗"
        longrunningquery_text = "✓" if self.longrunningquery else "✗"
        sumofactivesessionslessthan50_text = "✓" if self.sumofactivesessionslessthan50 else "✗"
        lastautovacuumoranalyzeinthisweek_text = "✓" if self.allTablesMaintained else "✗"
        nobloattableexists_text = "✓" if self.nobloattableexists else "✗"
        exporterworking = "✓" if self.nodeExporterWorking else "✗"
        pgsexporterworking = "✓" if self.pgsExporterWorking else "✗"
        print(exporterworking)

        table_data = [
            ["Connected To PostgreSQL", connection_text,'PostgreSQL connection test.'],
            ["Long Running Query", longrunningquery_text,'There is no running query older than 1 minute'],
            ["Sum of Active Sessions < 50", sumofactivesessionslessthan50_text,'Active session count is less than 50'],
            ["Last Analyze/Autovacuum in the Last Week", lastautovacuumoranalyzeinthisweek_text,'All tables are maintained this week.'],
            ["No Bloat Table Exists", nobloattableexists_text,'There is no table with bloat ratio greater than 50'],
            ["No Inactive Replication Slot", inactivereplication_text,'All replication slots are working and active.'],
            ["Node Exporter Working", exporterworking,'Node exporter are working and running'],
            ["PostgreSQL Exporter Working", pgsexporterworking,'PostgreSQL exporter are working and running']
        ]
        headers = ["Issue", "Result","Description"]
        table = tabulate(table_data, headers, tablefmt="grid")
        print(table)