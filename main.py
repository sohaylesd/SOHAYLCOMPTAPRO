import sqlite3
from tkinter import Tk, Label, Entry, Button, StringVar, ttk, messagebox, Toplevel, Text
from datetime import datetime
import edi_generator

DB = 'compta.db'

class ComptaApp:
    def __init__(self, master):
        self.master = master
        master.title('Compta Windows - Prototype')
        master.geometry('900x600')

        # Connexion DB
        self.conn = sqlite3.connect(DB)
        self.cur = self.conn.cursor()

        Label(master, text='Journal').grid(row=0, column=0)
        self.journal_cb = ttk.Combobox(master, values=self.get_journals())
        self.journal_cb.grid(row=0, column=1)
        Label(master, text='Date (YYYY-MM-DD)').grid(row=1, column=0)
        self.date_var = StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        Entry(master, textvariable=self.date_var).grid(row=1, column=1)
        Label(master, text='Réf pièce').grid(row=2, column=0)
        self.ref_var = StringVar()
        Entry(master, textvariable=self.ref_var).grid(row=2, column=1)

        Button(master, text='Nouvelle écriture', command=self.open_entry_window).grid(row=3, column=0)
        Button(master, text='Grand Livre', command=self.open_ledger).grid(row=3, column=1)
        Button(master, text='Balance', command=self.open_balance).grid(row=3, column=2)
        Button(master, text='Générer TVA XML (exemple)', command=self.generate_tva).grid(row=3, column=3)

    def get_journals(self):
        self.cur.execute('SELECT code FROM journals')
        return [r[0] for r in self.cur.fetchall()]

    def open_entry_window(self):
        w = Toplevel(self.master)
        w.title('Saisie écriture')
        Label(w, text='Journal').grid(row=0,column=0)
        journal_cb = ttk.Combobox(w, values=self.get_journals())
        journal_cb.grid(row=0,column=1)
        Label(w, text='Date').grid(row=1,column=0)
        date_e = Entry(w)
        date_e.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_e.grid(row=1,column=1)
        Label(w, text='Réf').grid(row=2,column=0)
        ref_e = Entry(w); ref_e.grid(row=2,column=1)

        # Lines area simple: up to 4 lines for prototype
        labels = []
        acc_cbs = []
        debit_es = []
        credit_es = []
        for i in range(4):
            Label(w,text=f'Ligne {i+1}').grid(row=3+i, column=0)
            acc = ttk.Combobox(w, values=self.get_account_codes()); acc.grid(row=3+i,column=1)
            debit = Entry(w); debit.grid(row=3+i,column=2)
            credit = Entry(w); credit.grid(row=3+i,column=3)
            acc_cbs.append(acc); debit_es.append(debit); credit_es.append(credit)

        def save():
            journal_code = journal_cb.get()
            datev = date_e.get(); refv = ref_e.get()
            # find journal id
            self.cur.execute('SELECT id FROM journals WHERE code=?', (journal_code,))
            j = self.cur.fetchone();
            if not j:
                messagebox.showerror('Erreur','Journal invalide')
                return
            jid = j[0]
            # compute totals
            totald = 0; totalc = 0
            for d in debit_es:
                try:
                    v = float(d.get()) if d.get() else 0
                except:
                    v = 0
                totald += v
            for c in credit_es:
                try:
                    v = float(c.get()) if c.get() else 0
                except:
                    v = 0
                totalc += v
            self.cur.execute('INSERT INTO journal_entries(company_id,journal_id,date,piece_ref,total_debit,total_credit) VALUES(?,?,?,?,?,?)',
                             (1,jid,datev,refv,totald,totalc))
            eid = self.cur.lastrowid
            for idx, acc_cb in enumerate(acc_cbs):
                acc_code = acc_cb.get()
                if not acc_code: continue
                self.cur.execute('SELECT id FROM accounts WHERE code=?', (acc_code,))
                ar = self.cur.fetchone()
                if not ar: continue
                aid = ar[0]
                try:
                    d = float(debit_es[idx].get()) if debit_es[idx].get() else 0
                except:
                    d = 0
                try:
                    c = float(credit_es[idx].get()) if credit_es[idx].get() else 0
                except:
                    c = 0
                self.cur.execute('INSERT INTO entry_lines(entry_id,account_id,debit,credit,description) VALUES(?,?,?,?,?)',
                                 (eid,aid,d,c,''))
            self.conn.commit()
            messagebox.showinfo('OK','Ecriture créée')
            w.destroy()
        Button(w,text='Enregistrer', command=save).grid(row=10,column=1)

    def get_account_codes(self):
        self.cur.execute('SELECT code FROM accounts ORDER BY code')
        return [r[0] for r in self.cur.fetchall()]

    def open_ledger(self):
        w = Toplevel(self.master); w.title('Grand Livre')
        Label(w,text='Compte (code)').grid(row=0,column=0)
        acc_e = Entry(w); acc_e.grid(row=0,column=1)
        def show():
            code = acc_e.get()
            self.cur.execute('SELECT id,label FROM accounts WHERE code=?',(code,))
            a = self.cur.fetchone()
            if not a:
                messagebox.showerror('Erreur','Compte introuvable')
                return
            aid = a[0]
            text = Text(w, width=100, height=30)
            text.grid(row=2,column=0,columnspan=4)
            self.cur.execute('''SELECT je.date, je.piece_ref, el.description, el.debit, el.credit
                                FROM entry_lines el
                                JOIN journal_entries je ON je.id = el.entry_id
                                WHERE el.account_id=? ORDER BY je.date''', (aid,))
            rows = self.cur.fetchall()
            s = 'Date | Piece | Description | Debit | Credit\n' + '-'*80 + '\n'
            for r in rows:
                s += f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}\n"
            text.insert('1.0', s)
        Button(w,text='Afficher', command=show).grid(row=1,column=1)

    def open_balance(self):
        w = Toplevel(self.master); w.title('Balance')
        text = Text(w, width=100, height=30); text.grid(row=0,column=0)
        self.cur.execute('SELECT id,code,label FROM accounts ORDER BY code')
        rows = self.cur.fetchall()
        s = 'Code | Intitulé | Total Debit | Total Credit | Solde\n' + '='*100 + '\n'
        for r in rows:
            aid, code, label = r
            self.cur.execute('SELECT COALESCE(SUM(debit),0), COALESCE(SUM(credit),0) FROM entry_lines WHERE account_id=?', (aid,))
            d,c = self.cur.fetchone()
            solde = d - c
            s += f"{code} | {label} | {d:.2f} | {c:.2f} | {solde:.2f}\n"
        text.insert('1.0', s)

    def generate_tva(self):
        # simple dialog: use first month
        try:
            xml,fn,z = edi_generator.generate_tva_xml(1,'2025-01-01','2025-01-31')
            messagebox.showinfo('OK', f'TVA XML généré: {fn} et archive {z}')
        except Exception as e:
            messagebox.showerror('Erreur', str(e))

if __name__ == '__main__':
    root = Tk()
    app = ComptaApp(root)
    root.mainloop()
