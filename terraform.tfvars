# Example Terraform variables file for Grafana Cloud
# Copy this to terraform.tfvars and fill in your values

# Your Grafana Cloud instance URL
# Find this in your Grafana Cloud portal
grafana_cloud_url = "some_url"

# Your Grafana Cloud API key
# Generate this from your Grafana Cloud instance with Admin permissions
# Go to: Configuration → API keys → Add API key
grafana_cloud_api_key = "some_key" 

# Your Grafana Cloud stack ID
# This is usually the first part of your Grafana URL
grafana_cloud_stack_id = "stack_id"

# The UID of your Prometheus datasource in Grafana Cloud
# To find this:
# 1. Go to Configuration → Data sources
# 2. Click on your Prometheus datasource  
# 3. Look for the UID in the settings or URL
# Default for Grafana Cloud is usually "grafanacloud-prom"
grafana_cloud_prometheus_uid = "grafanacloud-prom"
grafana_cloud_contact_point = "grafana-default-email"
