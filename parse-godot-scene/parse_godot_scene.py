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
                match = re.search(r'path="([^"]+)" id="([^"]+)"', line)
                if match:
                    resources[match.group(2)] = match.group(1)
            elif line.startswith('[node'):
                current_section = 'node'
                node = {}
                node['name'] = re.search(r'name="([^"]+)"', line).group(1)
                node['type'] = re.search(r'type="([^"]+)"', line).group(1)
                node['parent'] = re.search(r'parent="([^"]+)"', line).group(1) if 'parent=' in line else None
                # Add script detection
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

def generate_markdown(nodes, connections, resources, output_path):
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

    # Recursive helper to write nodes with hierarchy.
    def write_node_md(file, node, indent=0):
        prefix = "  " * indent + "- "
        file.write(f"{prefix}**{node['name']}** ({node['type']}")
        
        # Add script information if present
        if 'script' in node:
            script_value = node['script']
            if 'ExtResource' in script_value:
                res_match = re.search(r'ExtResource\("([^"]+)"\)', script_value)
                if res_match:
                    resource_id = res_match.group(1)
                    script_value = resources.get(resource_id, script_value)
            file.write(f", script: {script_value}")
        file.write(")\n")
        
        for key, value in node.get('properties', {}).items():
            if 'ExtResource' in value:
                res_match = re.search(r'ExtResource\("([^"]+)"\)', value)
                if res_match:
                    resource_id = res_match.group(1)
                    value = resources.get(resource_id, value)
            if is_relevant_property(key, value):
                file.write(f"{'  '*(indent+1)}- {key}: {value}\n")
        for child in node.get('children', []):
            write_node_md(file, child, indent+1)

    with open(output_path, 'w') as file:
        file.write('# Godot Scene\n\n')
        file.write('## Nodes\n')
        for root in roots:
            write_node_md(file, root)
        file.write('\n## Connections\n')
        for connection in connections:
            file.write(f"- {format_connection(connection, owner)}\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run parse_godot_scene.py <path_to_godot_scene_file>")
        sys.exit(1)

    scene_file_path = sys.argv[1]
    if not os.path.isfile(scene_file_path):
        print(f"File not found: {scene_file_path}")
        sys.exit(1)

    nodes, connections, resources = parse_godot_scene(scene_file_path)
    output_path = os.path.splitext(scene_file_path)[0] + '.md'
    generate_markdown(nodes, connections, resources, output_path)
    print(f"Markdown file generated: {output_path}")
