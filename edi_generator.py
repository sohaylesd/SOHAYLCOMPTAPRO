import xml.etree.ElementTree as ET
from xml.dom import minidom
import sqlite3
import zipfile
from datetime import datetime

DB = 'compta.db'

def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def generate_tva_xml(company_id, period_start, period_end):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # fetch company
    cur.execute('SELECT name, rif FROM companies WHERE id=?', (company_id,))
    row = cur.fetchone()
    if not row:
        raise Exception('Company not found')
    name, rif = row

    # compute summary (very simple example)
    cur.execute("SELECT SUM(total_ht), SUM(total_tva) FROM invoices WHERE company_id=? AND date BETWEEN ? AND ?",
                (company_id, period_start, period_end))
    s = cur.fetchone()
    total_ht = s[0] or 0.0
    total_tva = s[1] or 0.0
    total_ttc = total_ht + total_tva

    root = ET.Element('TVADeclaration')
    header = ET.SubElement(root,'Header')
    ET.SubElement(header,'CompanyRIF').text = rif
    ET.SubElement(header,'CompanyName').text = name
    ET.SubElement(header,'PeriodStart').text = period_start
    ET.SubElement(header,'PeriodEnd').text = period_end
    ET.SubElement(header,'DeclarationDate').text = datetime.now().strftime('%Y-%m-%d')

    summary = ET.SubElement(root,'Summary')
    ET.SubElement(summary,'TotalHT').text = f"{total_ht:.2f}"
    ET.SubElement(summary,'TotalTVA').text = f"{total_tva:.2f}"
    ET.SubElement(summary,'TotalTTC').text = f"{total_ttc:.2f}"

    details = ET.SubElement(root,'Details')
    line = ET.SubElement(details,'Line')
    ET.SubElement(line,'Account').text = '44571'
    ET.SubElement(line,'Base').text = f"{total_ht:.2f}"
    ET.SubElement(line,'Taux').text = '20'
    ET.SubElement(line,'TVA').text = f"{total_tva:.2f}"

    xml_str = prettify(root)

    # store in DB and write file
    cur.execute('INSERT INTO edi_files(company_id,type,filename,xml_content) VALUES(?,?,?,?)',
                (company_id,'TVA', f'tva_{company_id}_{period_start}_{period_end}.xml', xml_str))
    conn.commit()
    conn.close()

    filename = f'tva_{company_id}_{period_start}_{period_end}.xml'
    with open(filename,'w', encoding='utf-8') as f:
        f.write(xml_str)

    zipname = filename.replace('.xml','.zip')
    with zipfile.ZipFile(zipname, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.write(filename)

    return xml_str, filename, zipname

if __name__ == '__main__':
    print('Exemple generation TVA')
    xml,fn,z = generate_tva_xml(1,'2025-01-01','2025-01-31')
    print('Fichiers:', fn, z)
