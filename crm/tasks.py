from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    query {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """)

    try:
        result = client.execute(query)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = (
            f"{timestamp} - Report: "
            f"{result['totalCustomers']} customers, "
            f"{result['totalOrders']} orders, "
            f"${result['totalRevenue']:.2f} revenue"
        )
        
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(report + "\n")
        
        return report
    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error: {str(e)}\n")
        raise