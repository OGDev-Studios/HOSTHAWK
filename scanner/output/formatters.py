import json
import csv
import xml.etree.ElementTree as ET
import xml.dom.minidom
from datetime import datetime

class OutputFormatter:
    @staticmethod
    def to_json(results, output_file=None):
        if not isinstance(results, (list, dict)):
            results = [results] if results else []
        
        output = {
            'scan_results': results,
            'timestamp': datetime.utcnow().isoformat(),
            'scan_type': 'network_scan'
        }
        
        json_data = json.dumps(output, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_data)
        return json_data

    @staticmethod
    def to_csv(results, output_file=None):
        if not results:
            return ""
            
        if not isinstance(results, list):
            results = [results]
            
        if not results:
            return ""
            
        fieldnames = set()
        for item in results:
            if isinstance(item, dict):
                fieldnames.update(item.keys())
        fieldnames = sorted(fieldnames)
        
        output = []
        output.append(','.join(fieldnames))
        
        for item in results:
            if not isinstance(item, dict):
                continue
            row = []
            for field in fieldnames:
                value = item.get(field, '')
                if isinstance(value, (list, dict)):
                    value = str(value)
                row.append(f'"{str(value).replace("\"", "\"\"")}"')
            output.append(','.join(row))
        
        csv_data = '\n'.join(output)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(csv_data)
        return csv_data

    @staticmethod
    def to_xml(results, output_file=None):
        root = ET.Element('scan_results')
        root.set('timestamp', datetime.utcnow().isoformat())
        root.set('scan_type', 'network_scan')
        
        def add_items(parent, data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        elem = ET.SubElement(parent, key.replace(' ', '_'))
                        add_items(elem, value)
                    else:
                        elem = ET.SubElement(parent, key.replace(' ', '_'))
                        elem.text = str(value)
            elif isinstance(data, list):
                for item in data:
                    elem = ET.SubElement(parent, 'item')
                    add_items(elem, item)
            else:
                parent.text = str(data)
        
        add_items(root, {'result': results} if not isinstance(results, list) else {'results': results})
        
        xmlstr = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(xmlstr)
        
        return xmlstr

    @classmethod
    def format(cls, results, output_format='json', output_file=None):
        formatters = {
            'json': cls.to_json,
            'csv': cls.to_csv,
            'xml': cls.to_xml
        }
        
        if output_format.lower() not in formatters:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        return formatters[output_format.lower()](results, output_file)
