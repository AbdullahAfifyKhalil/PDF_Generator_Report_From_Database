import os
import psycopg2
    
 #Dont Forget To set the database parameters to connect
   
os.environ[''] = ''

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            "host= dbname= user="" password=%s  port=" % (
                os.getenv('')))
        self.cur = self.conn.cursor()

    def fetch_incident(self, incident_id):
        self.cur.execute("""
            SELECT
                incidents.id,
                incidents.data,
                TO_CHAR(incidents.created_at, 'DD/MM/YY HH24:MI') AS created_at,
                incidents.user_group_id,
                users.email,
                CONCAT(users."firstName", ' ', users."lastName") AS full_name,
                users.phone,
                incident_types.name AS incident_type_name,
                companies.primary as company_primary,
                companies."primaryTwo" as company_accent,
                companies."imageUrl" as company_image
            FROM
                incidents
            LEFT JOIN
                users ON incidents."userId" = users.id
            LEFT JOIN
                incident_types ON incidents."typeId" = incident_types.id
            LEFT JOIN
                companies ON incidents."companyId" = companies.id
            WHERE
                incidents.id = %s
        """, (incident_id,))
        return self.cur.fetchone()

    def fetch_groups(self, user_group_id):
        self.cur.execute("""
            WITH RECURSIVE parent_chain AS (
              SELECT
                ug.id,
                ug.name as value,
                ug."parentId",
                ugt.name AS key,
                1 AS depth
              FROM
                user_groups ug
              LEFT JOIN user_group_types ugt ON ug.type_id = ugt.id
              WHERE
                ug.id = %s
              UNION ALL

              SELECT
                p.id,
                p.name,
                p."parentId",
                pgt.name AS key,
                pc.depth + 1 AS depth
              FROM
                user_groups p
              INNER JOIN parent_chain pc ON pc."parentId" = p.id
              LEFT JOIN user_group_types pgt ON p.type_id = pgt.id
            )
            SELECT
              id,
              value,
              "parentId",
              key,
              depth
            FROM
              parent_chain
            ORDER BY depth DESC;
        """, (user_group_id,))
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()
