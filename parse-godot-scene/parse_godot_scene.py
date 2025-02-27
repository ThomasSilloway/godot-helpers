import sys
import os
import re

def parse_godot_scene(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    nodes = []
    connections = []
    resources = {}
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
            
        # Detect section changes
        if line.startswith('['):
            if line.startswith('[ext_resource'):
                current_section = 'resource'
                match = re.search(r'path="([^"]+)".*?id="([^"]+)"', line)
                if match:
                    resources[match.group(2)] = match.group(1)
            elif line.startswith('[node'):
                current_section = 'node'
                node = {}
                
                # Extract required attributes
                name_match = re.search(r'name="([^"]+)"', line)
                type_match = re.search(r'type="([^"]+)"', line)
                instance_match = re.search(r'instance=ExtResource\("([^"]+)"\)', line)
                
                if name_match:
                    node['name'] = name_match.group(1)
                    # For instanced scenes, use the instance path as type if no explicit type
                    if instance_match:
                        node['type'] = resources.get(instance_match.group(1), 'Unknown Instance')
                        node['is_instance'] = True
                    elif type_match:
                        node['type'] = type_match.group(1)
                    
                    # Optional parent extraction
                    parent_match = re.search(r'parent="([^"]+)"', line)
                    node['parent'] = parent_match.group(1) if parent_match else None

                    # Optional script extraction
                    script_match = re.search(r'script="([^"]+)"', line)
                    if script_match:
                        node['script'] = script_match.group(1)

                    node['properties'] = {}
                    nodes.append(node)

            elif line.startswith('[connection'):
                current_section = 'connection'
                connections.append(line)
            else:
                current_section = None
        # Handle properties within a node section
        elif current_section == 'node' and '=' in line:
            parts = line.split(' = ', 1)
            if len(parts) == 2:
                key, value = parts
                if nodes:  # Only add properties if we have a node
                    nodes[-1]['properties'][key] = value

    return nodes, connections, resources

def is_relevant_property(key, value):
    # Only include properties that are UI text, link to art assets, scripts, or resources
    key_lower = key.lower()
    if key_lower in ["text", "label", "tooltip"]:
        return True
    if value.startswith("http://") or value.startswith("https://"):
        return True
    if re.search(r'\.(png|jpg|jpeg|gif|ogg|wav)$', value, re.IGNORECASE):
        return True
    # Add detection for scripts and resources
    if re.search(r'\.(gd|tres|tscn)$', value, re.IGNORECASE):
        return True
    return False

def format_connection(conn_str, owner):
    # Convert a connection string to a human-readable sentence.
    pattern = r'\[connection\s+(.*?)\]$'
    match = re.search(pattern, conn_str)
    if not match:
        return conn_str.strip()
    content = match.group(1)
    pairs = re.findall(r'(\w+)="([^"]+)"', content)
    info = dict(pairs)
    signal = info.get('signal', '')
    frm = info.get('from', '')
    to = info.get('to', '')
    if to == ".":
        to = owner  # use the scene's root node path instead of "itself"
    method = info.get('method', '')
    return f"When signal '{signal}' is emitted from '{frm}', call method '{method}' on '{to}'."

def generate_markdown(nodes, connections, resources, scene_name):
    # Modified to return markdown content instead of writing to file
    output = []
    output.append(f'# {scene_name}\n')
    output.append('## Nodes\n')
    
    # Build node hierarchy
    for node in nodes:
        node['children'] = []
    nodes_by_name = { node['name']: node for node in nodes }
    roots = []
    for node in nodes:
        parent_name = node.get('parent')
        if parent_name is None:
            roots.append(node)
        elif parent_name == ".":
            if roots:
                roots[0]['children'].append(node)
            else:
                roots.append(node)
        else:
            parent_node = nodes_by_name.get(parent_name)
            if parent_node:
                parent_node['children'].append(node)
            else:
                roots.append(node)
    
    # Determine owner from the scene root node.
    owner = roots[0]['name'] if roots else ""

    def write_node_md(node, indent=0):
        lines = []
        prefix = "  " * indent + "- "
        node_line = f"{prefix}**{node['name']}** ({node['type']}"
        
        if node.get('is_instance'):
            node_line += ", instanced scene"
        
        if 'script' in node:
            script_value = node['script']
            if 'ExtResource' in script_value:
                res_match = re.search(r'ExtResource\("([^"]+)"\)', script_value)
                if res_match:
                    resource_id = res_match.group(1)
                    script_value = resources.get(resource_id, script_value)
            node_line += f", script: {script_value}"
        node_line += ")\n"
        lines.append(node_line)
        
        for key, value in node.get('properties', {}).items():
            if 'ExtResource' in value:
                res_match = re.search(r'ExtResource\("([^"]+)"\)', value)
                if res_match:
                    resource_id = res_match.group(1)
                    value = resources.get(resource_id, value)
            if is_relevant_property(key, value):
                lines.append(f"{'  '*(indent+1)}- {key}: {value}\n")
        for child in node.get('children', []):
            lines.extend(write_node_md(child, indent+1))
        return lines

    for root in roots:
        output.extend(write_node_md(root))
    
    if connections:
        output.append('\n## Connections\n')
        for connection in connections:
            output.append(f"- {format_connection(connection, owner)}\n")
    
    return ''.join(output)

def process_folder(folder_path):
    # Find all .tscn files in the folder
    scene_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.tscn'):
                scene_files.append(os.path.join(root, file))
    
    if not scene_files:
        print(f"No .tscn files found in {folder_path}")
        return
    
    # Get the folder name for the output file
    folder_name = os.path.basename(folder_path)
    output_path = os.path.join(folder_path, f"{folder_name}.md")
    
    # Process each scene file and combine the results
    all_scenes_md = []
    for scene_file in scene_files:
        scene_name = os.path.splitext(os.path.basename(scene_file))[0]
        try:
            nodes, connections, resources = parse_godot_scene(scene_file)
            scene_md = generate_markdown(nodes, connections, resources, scene_name)
            all_scenes_md.append(scene_md)
        except Exception as e:
            print(f"Error processing {scene_file}: {str(e)}")
    
    # Write combined markdown to file
    if all_scenes_md:
        with open(output_path, 'w') as f:
            f.write('\n\n---\n\n'.join(all_scenes_md))
        print(f"Generated markdown file: {output_path}")
    else:
        print("No scenes were successfully processed")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run parse_godot_scene.py <path_to_godot_folder>")
        sys.exit(1)

    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print(f"Directory not found: {folder_path}")
        sys.exit(1)

    process_folder(folder_path)
