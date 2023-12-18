import psycopg2
from datetime import datetime


def fetch_data():
    # Dane do połączenia z bazą danych
    db_name = "postgres"
    db_user = "postgres"
    db_password = "postgres"
    db_host = "db-service"  # Nazwa usługi w Kubernetes
    db_port = "5432"

    try:
        # Nawiązanie połączenia z bazą danych
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )

        cur = conn.cursor()

        today = datetime.now().date()

        query = "SELECT groups_to_procced FROM job_status WHERE date::date = %s"

        cur.execute(query, (today,))

        results = cur.fetchall()

        cur.close()
        conn.close()

        return results

    except Exception as e:
        print(f"Błąd podczas łączenia z bazą danych: {e}")
        return None

