import os
import yaml
import json
from jinja2 import Template

# For Grafana Cloud, we'll use the Prometheus datasource UID
# This can be set as an environment variable or passed as a parameter
datasource = os.getenv('GRAFANA_CLOUD_PROMETHEUS_UID', 'grafanacloud-prom')

# Function to load additional JSON content from a file
def load_extra_json(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file '{file_path}': {e}")
        return []

# Function to load markdown content from a file
def load_markdown(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().replace("\\", "\\\\").replace("\n", "\\n").replace("\"", "\\\"")
    except FileNotFoundError:
        print(f"Markdown file '{file_path}' not found.")
        return ""

# Function to list all JSON files in a directory
def list_json_files(directory):
    try:
        return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]
    except FileNotFoundError:
        print(f"Directory '{directory}' not found.")
        return []

# Read the YAML file
with open("config.yaml", "r") as yaml_file:
    data = yaml.safe_load(yaml_file)

# Add the list of JSON files in each dashboard directory to the data structure
for folder_key, folder in data.items():
    if 'dashboards' in folder and 'dir' in folder['dashboards']:
        dashboard_dir = folder['dashboards']['dir']
        json_files = list_json_files(dashboard_dir)
        folder['dashboards']['json_files'] = json_files

# Read the Jinja2 templates
# Use the Grafana Cloud version of the templates
with open("./templates/terraform_cloud.template", "r") as tf_template_file:
    tf_template_content = tf_template_file.read()
tf_template = Template(tf_template_content)

with open("./templates/dashboard.template", "r") as db_template_file:
    db_template_content = db_template_file.read()
db_template = Template(db_template_content)

with open("./templates/sli_row.template", "r") as row_template_file:
    row_template_content = row_template_file.read()
row_template = Template(row_template_content)

with open("./templates/main_cloud.tf.template", "r") as main_template_file:
    main_template_content = main_template_file.read()

with open("./templates/sli_dashboard.template", "r") as sli_dashboard_template_file:
    sli_dashboard_template_content = sli_dashboard_template_file.read()
sli_dashboard_template = Template(sli_dashboard_template_content)

# Initialize the content for the new main.tf file
new_main_tf_content = main_template_content + "\n"

# Function to merge extra rows into the dashboard template
def append_extra_rows_to_template(dashboard_template, extra_rows):
    if extra_rows:
        extra_rows_json = ',\n'.join(json.dumps(row, indent=2) for row in extra_rows)
        return dashboard_template.replace('<<APPEND_HERE>>', extra_rows_json).replace('<<APPEND_EXTRA_ROW_COMMA>>', ',')
    else:
        return dashboard_template.replace('<<APPEND_HERE>>', '').replace('<<APPEND_EXTRA_ROW_COMMA>>', '')

# Loop through each folder, services, and service to generate JSON files and append content to main.tf
start_id = 9
start_y = 13

for folder_key, folder in data.items():
    services = folder.get('services', {})

    for service_key, service in services.items():
        # Load extra rows if defined
        extra_rows = []
        if 'extra_rows' in service:
            extra_rows_file = service['extra_rows']
            extra_rows = load_extra_json(extra_rows_file)

        # Load markdown content for each service
        description_path = service.get('description')
        if description_path:
            service['markdown'] = load_markdown(description_path)
        else:
            service['markdown'] = ""

        # Accumulate SLI row content
        all_slis_content = ""
        has_non_availability_sli = False  # Flag to check if there are any non-availability SLIs

        # Iterate over each SLI in the service
        for sli_key, sli in service.get('sli', {}).items():
            if sli_key == 'availability':
                continue
            has_non_availability_sli = True

            # Render the SLI row content
            slis_content = row_template.render(
                service=service,
                datasource=datasource,
                folder_key=folder_key,
                service_key=service_key,
                sli_key=sli_key,
                sli=sli,
                start_id=start_id,
                start_y=start_y
            )

            # Append current SLI content to accumulated content
            all_slis_content += slis_content + "\n"

            # Update start_id and start_y for the next SLI
            start_id += 4  # Assuming each SLI generates 4 panels
            start_y += 9

        # Render the dashboard content regardless of SLIs
        dashboard_content = db_template.render(
            datasource=datasource,
            folder_key=folder_key,
            service_key=service_key,
            service=service
        )

        # Append extra rows to the rendered content
        dashboard_content_with_extra_rows = append_extra_rows_to_template(dashboard_content, extra_rows)

        # Parse the JSON to ensure it's properly formatted
        dashboard_json = json.loads(dashboard_content_with_extra_rows)

        # Write the dashboard JSON to a file
        dashboard_filename = f"{folder_key.lower()}_{service_key.lower()}_dashboard.json"
        with open(dashboard_filename, "w") as dashboard_file:
            json.dump(dashboard_json, dashboard_file, indent=2)
            print(f"Generated {dashboard_filename}")

        # Only create the SLI dashboard file if there are non-availability SLIs
        if has_non_availability_sli:
            sli_dashboard_content = sli_dashboard_template.render(
                datasource=datasource,
                folder_key=folder_key,
                service_key=service_key,
                service=service,
                slis_content=all_slis_content
            )

            final_dashboard_filename = f"sli_dashboard_{service_key.lower()}.json"
            with open(final_dashboard_filename, "w") as final_dashboard_file:
                final_dashboard_file.write(sli_dashboard_content)
                print(f"Generated {final_dashboard_filename}")

            # Add SLI dashboard to the data structure
            folder.setdefault('sli_dashboards', []).append(final_dashboard_filename)

# Render the folder and recording rule content using the Grafana Cloud template
new_main_tf_content += tf_template.render(data=data) + "\n"

# Write the final content to main.tf
with open("main.tf", "w") as main_tf_file:
    main_tf_file.write(new_main_tf_content)

print("\nDon't forget to set the following environment variables or terraform variables:")
print("- TF_VAR_grafana_cloud_url (e.g., https://myorg.grafana.net)")
print("- TF_VAR_grafana_cloud_api_key (your Grafana Cloud API key)")
print("- TF_VAR_grafana_cloud_stack_id (your stack ID)")
print("- TF_VAR_grafana_cloud_prometheus_uid (if different from default 'grafanacloud-prom')")
