from base64 import standard_b64encode
from os import getenv
from time import sleep

from pyhive import hive
from thrift.transport.THttpClient import THttpClient
from thrift.Thrift import TApplicationException


HOST = "https://" + getenv("DBT_DATABRICKS_HOST_NAME")
CLUSTER = getenv("DBT_DATABRICKS_CLUSTER_NAME")
TOKEN = getenv("DBT_DATABRICKS_TOKEN")
PORT = 443
ORGANIZATION = "0"
SPARK_CONNECTION_URL = "{host}:{port}/sql/protocolv1/o/{organization}/{cluster}"


def _wait_for_databricks_cluster() -> None:
    """
    It takes roughly 3-5 minutes for the cluster to start, to be safe we'll wait for 10 minutes
    """
    transport_client = _transport_client()

    for _ in range(20):
        try:
            hive.connect(thrift_transport=transport_client)
            return
        except TApplicationException:
            sleep(30)

    raise Exception("Databricks cluster did not start in time")


def _transport_client() -> THttpClient:
    conn_url = SPARK_CONNECTION_URL.format(
        host=HOST,
        cluster=CLUSTER,
        port=PORT,
        organization=ORGANIZATION,
    )

    transport_client = THttpClient(conn_url)
    raw_token = f"token:{TOKEN}".encode()
    token = standard_b64encode(raw_token).decode()
    transport_client.setCustomHeaders({"Authorization": f"Basic {token}"})
    return transport_client


if __name__ == "__main__":
    _wait_for_databricks_cluster()
