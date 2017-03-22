# ProxyProvider

### Usage example

```python
import requests
from ProxyProvider import ProxyProvider

# Initialize
proxy_provider = ProxyProvider()

# Add tasks (query)
proxy_provider.add_task("https://google.com")
proxy_provider.add_task("https://yandex.ru")

# Create threads based on you own method
proxy_provider.add_proxy_workers(scrap_page)

# Run created threads
proxy_provider.start_all_workers()

# Wait for all threads stopped
proxy_provider.join_all()

# Delete all threads
proxy_provider.delete_all_workers()
```

### Your own method example

```python
def scrap_page(self, query_and_proxy):
    query = query_and_proxy[0]
    proxy = query_and_proxy[1].address
    req = requests.get(query, proxies={'http': proxy, 'https': proxy})
```
