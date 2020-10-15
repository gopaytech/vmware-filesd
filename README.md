# This is a file discovery implementation utilizing VMware tags for Prometheus discovery

This repository utilizes code from Ansible VMware inventory and has been modified to work for Prometheus. It can be slow in large vmware environments.

An example of how to use it for Promethues operator:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  labels:
    prometheus: po-prometheus-vmware-filesd
  name: po-prometheus-vmware-filesd
spec:
  containers:
    - name: vmware-filesd
      image: gopaytech/vmware-filesd:latest
      imagePullPolicy: Never
      env:
        - name: HOSTNAME
          value: "10.0.0.1"
        - name: USERNAME
          value: "vmware-user"
        - name: PASSWORD
          value: "vmware-password"
        - name: OUTPUT
          value: "/opt/config/vmware-filesd.json"
        - name: FILTER
          value: '{"environment": "staging"}'
      volumeMounts:
        - name: config-out
          mountPath: /opt/config
          readOnly: false
  securityContext:
    fsGroup: 2000
    runAsNonRoot: true
    runAsUser: 1000
  serviceAccountName: po-prometheus-operator-prometheus
  serviceMonitorNamespaceSelector: {}
  serviceMonitorSelector:
    matchLabels:
      release: vmware-filesd
  additionalScrapeConfigs:
    name: additional-scrape-configs
    key: prometheus-additional.yaml
```

Example output
```json
[
    {
        "targets": [
            "10.0.1.1"
        ],
        "labels": {
            "name": "host1",
            "address": "10.0.1.1",
            "description": "sample host",
            "component": "pg",
            "environment": "staging"
        }
    }
]
```

Prometheus will read this output as a file discovery. It can be imported and relabled like the following:
```yaml
- job_name: "vmware/node-exporter"
  file_sd_configs:
    - files:
        - /etc/prometheus/config_out/vmware-filesd.json
  relabel_configs:
    - source_labels: [__address__]
      target_label: instance
    - source_labels: [__address__]
      target_label: __address__
      replacement: "${1}:9100"

- job_name: "vmware/pg-exporter"
  file_sd_configs:
    - files:
        - /etc/prometheus/config_out/vmware-filesd.json
  relabel_configs:
    - source_labels: [__address__]
      target_label: instance
    - source_labels: [component]
      regex: ^(?!(pg|postgres)$).*
      action: drop
    - source_labels: [__address__, component]
      target_label: __address__
      regex: "(.*);(pg)"
      replacement: "${1}:9187"
```

```bash
kubectl create secret generic additional-scrape-configs --from-file=prometheus-additional.yaml
```

It can also be called from the commandline directly: `python3 dynamic.py --hostname $HOSTNAME --username $USERNAME --password $PASSWORD --output $OUTPUT --loop --notls --filter "$FILTER"`
