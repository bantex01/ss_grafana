import yaml
import json
from jinja2 import Template

# Read the YAML file
with open("config.yaml", "r") as yaml_file:
    data = yaml.safe_load(yaml_file)

# Read the Jinja2 templates
with open("terraform.template", "r") as tf_template_file:
    tf_template_content = tf_template_file.read()
tf_template = Template(tf_template_content)

with open("./grafana_json/dashboard.template", "r") as db_template_file:
    db_template_content = db_template_file.read()
db_template = Template(db_template_content)

# Read the main.tf.template file
with open("main.tf.template", "r") as main_template_file:
    main_template_content = main_template_file.read()

# Initialize the content for the new main.tf file
new_main_tf_content = main_template_content + "\n"

# Function to load additional JSON content from a file
def load_extra_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

# Loop through each folder and service to generate JSON files and append content to main.tf
for folder_key, folder in data.items():
    # Render the folder content
    folder_content = tf_template.render(data={folder_key: folder})
    new_main_tf_content += folder_content + "\n"
    
    for service_key, service in folder.items():
        # Render the dashboard JSON content
        dashboard_content = db_template.render(folder_key=folder_key, service_key=service_key, service=service)
        dashboard_json = json.loads(dashboard_content)

        # Append extra rows if specified
        if "extra_rows" in service:
            extra_json_content = load_extra_json(service["extra_rows"]["row_file"])
            dashboard_json["panels"].extend(extra_json_content)

        
        # Write the dashboard JSON to a file
        dashboard_filename = f"{folder_key.lower()}_{service_key.lower()}_dashboard.json"
        with open(dashboard_filename, "w") as dashboard_file:
           json.dump(dashboard_json, dashboard_file, indent=2) 

# Write the final content to main.tf
with open("main.tf", "w") as main_tf_file:
    main_tf_file.write(new_main_tf_content)

