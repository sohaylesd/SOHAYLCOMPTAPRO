import sqlite3
from datetime import date

DB = 'compta.db'

schema = '''
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  rif TEXT,
  adresse TEXT,
  currency TEXT DEFAULT 'MAD',
  exercice_start TEXT,
  exercice_end TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL,
  classe INTEGER,
  type TEXT,
  allow_balance INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS journals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT NOT NULL,
  label TEXT NOT NULL,
  type TEXT
);

CREATE TABLE IF NOT EXISTS partners (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER,
  rif TEXT,
  name TEXT,
  adresse TEXT,
  FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS invoices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER,
  partner_id INTEGER,
  date TEXT,
  number TEXT,
  total_ht REAL,
  total_tva REAL,
  total_ttc REAL,
  status TEXT DEFAULT 'draft',
  FOREIGN KEY(company_id) REFERENCES companies(id),
  FOREIGN KEY(partner_id) REFERENCES partners(id)
);

CREATE TABLE IF NOT EXISTS journal_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER,
  journal_id INTEGER,
  date TEXT,
  piece_ref TEXT,
  total_debit REAL,
  total_credit REAL,
  FOREIGN KEY(company_id) REFERENCES companies(id),
  FOREIGN KEY(journal_id) REFERENCES journals(id)
);

CREATE TABLE IF NOT EXISTS entry_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_id INTEGER,
  account_id INTEGER,
  partner_id INTEGER,
  debit REAL DEFAULT 0,
  credit REAL DEFAULT 0,
  description TEXT,
  FOREIGN KEY(entry_id) REFERENCES journal_entries(id) ON DELETE CASCADE,
  FOREIGN KEY(account_id) REFERENCES accounts(id),
  FOREIGN KEY(partner_id) REFERENCES partners(id)
);

CREATE TABLE IF NOT EXISTS edi_files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER,
  type TEXT,
  filename TEXT,
  xml_content TEXT,
  status TEXT DEFAULT 'generated',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
'''

sample_accounts = [
    ('101','Capital social',1,'actif'),
    ('211','Immobilisations incorporelles',2,'actif'),
    ('345','Fournisseurs',4,'passif'),
    ('44571','TVA collectée',4,'passif'),
    ('44566','TVA déductible',4,'actif'),
    ('601','Achats',6,'charge'),
    ('701','Ventes',7,'produit'),
    ('512','Banque',5,'actif')
]

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.executescript(schema)

# insert sample company
cur.execute("INSERT OR IGNORE INTO companies(id,name,rif,adresse,exercice_start,exercice_end) VALUES(?, ?, ?, ?, ?, ?)",
            (1, 'Société Exemple', 'AB123456789', 'Casablanca', '2025-01-01', '2025-12-31'))

# insert journals
cur.execute("INSERT OR IGNORE INTO journals(id,code,label,type) VALUES(?, ?, ?, ?)", (1,'VN','Ventes','vente'))
cur.execute("INSERT OR IGNORE INTO journals(id,code,label,type) VALUES(?, ?, ?, ?)", (2,'AC','Achats','achat'))
cur.execute("INSERT OR IGNORE INTO journals(id,code,label,type) VALUES(?, ?, ?, ?)", (3,'BQ','Banque','banque'))

for code,label,classe,t in sample_accounts:
    try:
        cur.execute('INSERT OR IGNORE INTO accounts(code,label,classe,type) VALUES(?,?,?,?)', (code,label,classe,t))
    except Exception as e:
        print('err',e)

conn.commit()
conn.close()
print('Initialisation DB terminée ->', DB)
