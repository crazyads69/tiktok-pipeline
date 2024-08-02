import pandas as pd
import os

# read the proxy_list.csv file
proxy_list = pd.read_csv("proxy_list.csv")

# Filter only get protocol proxies that http
http_proxies = proxy_list[proxy_list["protocol"] == "http"]

# Get the ip and port columns from the http_proxies DataFrame and create a list of proxy URLs
proxy_urls = [
    f"http://{row['ip']}:{row['port']}" for index, row in http_proxies.iterrows()
]

# Print the list of proxy URLs
print(proxy_urls)
