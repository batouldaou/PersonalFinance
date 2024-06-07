#%%
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


token = "iqDRMaumr6DB_7mSubFUJRxhfd0M5MBd0vrtFF9d8XOeVz09ak6W1HTBe-_BdQjIjpTjwqEYlX0pYPnl9LqMDA=="
org = "Personal Budget"
url = "http://localhost:8086"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org) #client connection is established
#%%

bucket="transactions"

write_api = write_client.write_api(write_options=SYNCHRONOUS)
   
for value in range(5):
  point = (
    Point("measurement1")
    .tag("tagname1", "tagvalue1")
    .field("field1", value)
  )
  write_api.write(bucket=bucket, org="Personal Budget", record=point)
  time.sleep(1) # separate points by 1 second

# %%
query_api = write_client.query_api()

query = """from(bucket: "transactions")
 |> range(start: -10m)
 |> filter(fn: (r) => r._measurement == "measurement1")"""
tables = query_api.query(query, org="Personal Budget")

for table in tables:
  for record in table.records:
    print(record)

# %%
