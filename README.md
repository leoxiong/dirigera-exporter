# `dirigera-exporter`

Prometheus metrics exporter for the [IKEA Dirigera Hub](https://www.ikea.com/au/en/p/dirigera-hub-for-smart-products-white-smart-90503407/).

1. Fetch authorization code from Dirigera Hub.

```bash
$ python pkce.py
waiting for button press
waiting for button press
waiting for button press
waiting for button press
waiting for button press
{'access_token': '<access_token>'}
```

2. Build container image.

```bash
$ docker build -t registry.leoxiong.com/dirigera-exporter .
```

3. Run image..

```yaml
services:
  ...
  dirigera-exporter:
    image: registry.leoxiong.com/dirigera-exporter
    environment:
      DIRIGERA_HUB_HOST: <dirigera_hub_host>
      DIRIGERA_HUB_AUTHORIZATION_CODE: <dirigera_hub_authorization_code>
    expose:
      - 8080
    restart: unless-stopped
```

4. Add Prometheus scrape config.

```yaml
scrape_configs:
  ...
  - job_name: dirigera-exporter
    metrics_path: /metrics
    static_configs:
      - targets:
        - dirigera-exporter:8080
```
