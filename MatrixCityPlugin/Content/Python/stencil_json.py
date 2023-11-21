import sys
import json

input_json = sys.argv[1]
color_json = sys.argv[2]

with open(input_json, 'r') as f:
    input_data = json.load(f)
with open(color_json, 'r') as f:
    color_data = json.load(f)

max_len = 255

output_data = []
for key, value in input_data.items():
    if value >= max_len:
        print('Stencil Value out of range')
        break
    output_item = {}
    if 'separate' in input_json:
        value = pow(2, value-1)
    color = color_data[value]
    output_item['object name'] = key
    output_item['stencil value'] = value
    output_item['segment color(rgb)'] = color['rgb']
    output_item['segment color(hex)'] = color['hex']
    output_data.append(output_item)


with open(input_json, 'w') as f:
    json.dump(output_data, f, indent=4)
