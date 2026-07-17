import os
import zipfile
import xml.etree.ElementTree as ET
import shutil

def fix_walmart_xml(xlsx_path, log_callback=None):
    """
    Walmart's system strictly requires sharedStrings for Excel files and rejects inlineStr.
    Openpyxl drops sharedStrings.xml and writes inlineStr.
    This function modifies the XML of the xlsx file directly to convert inlineStr to sharedStrings,
    avoiding the need for Microsoft Excel (win32com) automation.
    """
    temp_dir = xlsx_path + "_temp_xmlfix"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(xlsx_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        shared_strings = []
        string_to_index = {}
        
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        ET.register_namespace('', ns['main'])
        
        worksheets_dir = os.path.join(temp_dir, 'xl', 'worksheets')
        if not os.path.exists(worksheets_dir):
            shutil.rmtree(temp_dir)
            return False
            
        modified_any = False
            
        for sheet_file in os.listdir(worksheets_dir):
            if not sheet_file.endswith('.xml'): continue
            sheet_path = os.path.join(worksheets_dir, sheet_file)
            
            tree = ET.parse(sheet_path)
            root = tree.getroot()
            modified = False
            
            for c in root.findall('.//main:c[@t="inlineStr"]', ns):
                is_el = c.find('main:is', ns)
                if is_el is not None:
                    t_el = is_el.find('main:t', ns)
                    if t_el is not None:
                        text = t_el.text or ""
                        
                        if text not in string_to_index:
                            string_to_index[text] = len(shared_strings)
                            shared_strings.append(text)
                        
                        idx = string_to_index[text]
                        
                        c.set('t', 's')
                        c.remove(is_el)
                        v_el = ET.SubElement(c, 'v')
                        v_el.text = str(idx)
                        modified = True
                        modified_any = True
                        
            if modified:
                tree.write(sheet_path, xml_declaration=True, encoding='UTF-8')
                
        if not modified_any:
            shutil.rmtree(temp_dir)
            return True # Nothing to fix
            
        # Create sharedStrings.xml
        sst_root = ET.Element('sst', {'xmlns': ns['main'], 'count': str(len(shared_strings)), 'uniqueCount': str(len(shared_strings))})
        for s in shared_strings:
            si = ET.SubElement(sst_root, 'si')
            t = ET.SubElement(si, 't')
            t.text = s
        
        sst_tree = ET.ElementTree(sst_root)
        sst_tree.write(os.path.join(temp_dir, 'xl', 'sharedStrings.xml'), xml_declaration=True, encoding='UTF-8')
        
        # Update workbook.xml.rels
        rels_path = os.path.join(temp_dir, 'xl', '_rels', 'workbook.xml.rels')
        if os.path.exists(rels_path):
            rels_tree = ET.parse(rels_path)
            rels_root = rels_tree.getroot()
            rels_ns = {'rels': 'http://schemas.openxmlformats.org/package/2006/relationships'}
            ET.register_namespace('', rels_ns['rels'])
            
            exists = False
            max_id = 0
            for rel in rels_root.findall('rels:Relationship', rels_ns):
                if 'sharedStrings.xml' in rel.get('Target', ''):
                    exists = True
                rId = rel.get('Id', '')
                if rId.startswith('rId'):
                    try:
                        num = int(rId[3:])
                        max_id = max(max_id, num)
                    except:
                        pass
                        
            if not exists:
                ET.SubElement(rels_root, 'Relationship', {
                    'Id': f'rId{max_id + 1}',
                    'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings',
                    'Target': 'sharedStrings.xml'
                })
                rels_tree.write(rels_path, xml_declaration=True, encoding='UTF-8')
                
        # Update [Content_Types].xml
        ct_path = os.path.join(temp_dir, '[Content_Types].xml')
        if os.path.exists(ct_path):
            ct_tree = ET.parse(ct_path)
            ct_root = ct_tree.getroot()
            ct_ns = {'ct': 'http://schemas.openxmlformats.org/package/2006/content-types'}
            ET.register_namespace('', ct_ns['ct'])
            
            ct_exists = False
            for override in ct_root.findall('ct:Override', ct_ns):
                if override.get('PartName') == '/xl/sharedStrings.xml':
                    ct_exists = True
                    break
                    
            if not ct_exists:
                ET.SubElement(ct_root, 'Override', {
                    'PartName': '/xl/sharedStrings.xml',
                    'ContentType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml'
                })
                ct_tree.write(ct_path, xml_declaration=True, encoding='UTF-8')
                
        # Zip it back
        with zipfile.ZipFile(xlsx_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
                    
        shutil.rmtree(temp_dir)
        if log_callback:
            log_callback("File optimized successfully using Python XML fixer (Walmart Compatible).")
        return True
        
    except Exception as e:
        if log_callback:
            log_callback(f"XML fix failed: {e}")
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        return False
