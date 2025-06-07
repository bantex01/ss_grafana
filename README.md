# AutoGraf Claude - SRE Monitoring & Alerting

An automated SRE (Site Reliability Engineering) monitoring solution that generates Grafana dashboards, recording rules, and alerting rules for Grafana Cloud using Terraform. This project implements SLI/SLO-based monitoring with multi-burn-rate alerting.

## Overview

This project automates the creation of:
- **Grafana Dashboards** for service monitoring
- **Recording Rules** for SLI (Service Level Indicator) metrics
- **Alerting Rules** with multi-burn-rate alerting (fast, medium, slow)
- **SLI Dashboards** for error budget tracking

## Features

- 🎯 **SLO-Based Monitoring**: Configure SLOs with error budget tracking
- ⚡ **Multi-Burn Rate Alerting**: Fast, medium, and slow burn rate alerts
- 📊 **Auto-Generated Dashboards**: Service overview and SLI-specific dashboards
- 🔄 **Template-Driven**: Jinja2 templates for easy customization
- ☁️ **Grafana Cloud Ready**: Built for Grafana Cloud with Terraform

## Project Structure

```
├── config.yaml                    # Main configuration file
├── createGrafanaResources.py      # Python script to generate resources
├── terraform.tfvars              # Terraform variables
└── templates/                     # Jinja2 templates
    ├── dashboard.template         # Main dashboard template
    ├── sli_dashboard.template     # SLI dashboard template
    ├── sli_row.template          # SLI row template
    ├── main_cloud.tf.template    # Main Terraform template
    └── terraform_cloud.template  # Terraform resources template
```

## Configuration

### Service Configuration (`config.yaml`)

Configure your services and SLIs in the `config.yaml` file:

```yaml
SRE:
  services:
    otel:
      name: "OTEL Collector"
      description: "sre/descriptions/otel.md"
      rate_expression: 'rate(otelcol_receiver_accepted_metric_points_total[2m])'
      error_expression: 'rate(otelcol_exporter_send_failed_metric_points_total[2m])'
      sli:
        availability:
          slo: 99.5
          period: 10080
          expression: 'up{instance="localhost:8888"}'
          alerting:
            fast:
              percentage: 10
              long: 60
              short: 10
```

### SLI Types

1. **Availability SLI**: Uses uptime/availability metrics
2. **Custom SLIs**: Define error_expression and total_expression

### Alerting Configuration

Multi-burn rate alerting with three tiers:
- **Fast**: Quick detection (10% burn in 1 hour)
- **Medium**: Balanced detection (25% burn in 24 hours)  
- **Slow**: Long-term trending (50% burn in 3.5 days)

## Setup

### Prerequisites

- Python 3.x
- Terraform
- Grafana Cloud account
- Required Python packages: `pyyaml`, `jinja2`

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd autograf_claude
```

2. **Install Python dependencies**
```bash
pip install pyyaml jinja2
```

3. **Configure Grafana Cloud credentials**
   
   Update `terraform.tfvars` with your Grafana Cloud details:
```hcl
grafana_cloud_url = "https://yourdomain.grafana.net/"
grafana_cloud_api_key = "your-api-key"
grafana_cloud_stack_id = "yourdomain"
grafana_cloud_prometheus_uid = "grafanacloud-prom"
```

4. **Configure your services**
   
   Edit `config.yaml` to define your services and SLIs.

### Usage

1. **Generate Terraform resources**
```bash
python createGrafanaResources.py
```

2. **Initialize Terraform**
```bash
terraform init
```

3. **Plan deployment**
```bash
terraform plan
```

4. **Deploy to Grafana Cloud**
```bash
terraform apply
```

## Generated Resources

### Terraform Resources

- `grafana_folder.sre_folder` - SRE folder in Grafana
- `grafana_dashboard.*` - Service dashboards
- `grafana_rule_group.*_recording` - Recording rules for SLI metrics
- `grafana_rule_group.*_alerting` - Alerting rules with burn rates

### Dashboard Features

**Service Dashboard**:
- Service overview metrics (rate, errors, duration)
- CPU and memory usage
- Service availability

**SLI Dashboard**:
- Error budget tracking
- Burn rate visualization
- SLO compliance metrics

## Environment Variables

Set these environment variables or use terraform.tfvars:

- `TF_VAR_grafana_cloud_url` - Your Grafana Cloud URL
- `TF_VAR_grafana_cloud_api_key` - API key with Admin permissions
- `TF_VAR_grafana_cloud_stack_id` - Your stack ID
- `TF_VAR_grafana_cloud_prometheus_uid` - Prometheus datasource UID

## Customization

### Adding New Services

1. Add service configuration to `config.yaml`
2. Run `python createGrafanaResources.py`
3. Apply with `terraform apply`

### Custom Templates

Modify templates in the `templates/` directory:
- `dashboard.template` - Main service dashboard
- `sli_dashboard.template` - SLI-specific dashboard
- `terraform_cloud.template` - Terraform resource generation

### Custom Metrics

Define custom expressions in your service configuration:
- `rate_expression` - Request rate metric
- `error_expression` - Error rate metric  
- `duration_expression` - Latency metric

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify your API key has Admin permissions
   - Check your Grafana Cloud URL format

2. **Datasource UID Error**
   - Find your Prometheus datasource UID in Grafana Cloud
   - Update `grafana_cloud_prometheus_uid` variable

3. **Template Errors**
   - Validate your `config.yaml` syntax
   - Check Jinja2 template syntax in templates/

### Logs

Check Terraform logs for detailed error information:
```bash
TF_LOG=DEBUG terraform apply
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with your Grafana Cloud instance
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
- Check the troubleshooting section
- Review Terraform and Grafana Cloud documentation
- Create an issue in this repository
