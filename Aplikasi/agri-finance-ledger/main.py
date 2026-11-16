#!/usr/bin/env python3
"""
Agri-Finance Ledger
Buku Kas Digital Usaha Pertanian & Arus Kas Operasional
Sesuai UI/05_agri_finance_ledger.md & PRD 7.5
"""

import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "common"))

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

try:
    from agristation_common import (
        init_db, get_connection, AgriWindow, AgriHeader, KPICard,
        PillTabs, format_rupiah, format_date_id, escape
    )
except ImportError:
    from common import (
        init_db, get_connection, AgriWindow, AgriHeader, KPICard,
        PillTabs, format_rupiah, format_date_id, escape
    )

class FinanceLedgerApp(AgriWindow):
    def __init__(self):
        super().__init__(
            title="Agri-Finance Ledger - Buku Kas Digital",
            icon_name="agri-finance-ledger",
            default_width=1120,
            default_height=750
        )
        init_db()

        self.current_filter = "Semua Transaksi"
        self.search_text = ""

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # 1. Custom Header with Dual Action Buttons
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        header_box.set_margin_start(20)
        header_box.set_margin_end(20)
        header_box.set_margin_top(16)
        header_box.set_margin_bottom(16)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        lbl_title = Gtk.Label(xalign=0)
        lbl_title.set_markup("<span size='x-large' weight='bold' color='#1E293B'>Buku Kas Pertanian</span>")
        title_box.pack_start(lbl_title, False, False, 0)
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_markup("<span size='small' color='#64748B'>Pencatatan Arus Kas Pemasukan Panen &amp; Pengeluaran Budidaya</span>")
        title_box.pack_start(lbl_sub, False, False, 0)
        header_box.pack_start(title_box, True, True, 0)

        # Controls right
        ctrl_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        btn_backup = Gtk.Button(label="💾 Cadangan")
        btn_backup.get_style_context().add_class("btn-secondary")
        btn_backup.connect("clicked", lambda w: self.open_backup_dialog())
        ctrl_box.pack_start(btn_backup, False, False, 0)

        btn_export = Gtk.Button(label="📊 Ekspor CSV")
        btn_export.get_style_context().add_class("btn-secondary")
        btn_export.connect("clicked", self._on_export_csv)
        ctrl_box.pack_start(btn_export, False, False, 0)

        btn_income = Gtk.Button(label="+ Catat Pemasukan")
        btn_income.get_style_context().add_class("btn-primary")
        btn_income.connect("clicked", lambda w: self._open_trans_dialog("Pemasukan"))
        ctrl_box.pack_start(btn_income, False, False, 0)

        btn_expense = Gtk.Button(label="- Catat Pengeluaran")
        btn_expense.get_style_context().add_class("btn-danger")
        btn_expense.connect("clicked", lambda w: self._open_trans_dialog("Pengeluaran"))
        ctrl_box.pack_start(btn_expense, False, False, 0)

        header_box.pack_end(ctrl_box, False, False, 0)
        main_box.pack_start(header_box, False, False, 0)

        # Scroller
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        content_box.set_margin_bottom(24)
        scroller.add(content_box)

        # 2. 3 Large KPI Cards
        kpi_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        content_box.pack_start(kpi_row, False, False, 0)

        self.kpi_saldo = KPICard("Sisa Saldo Kas Riil", "Rp 0", "Posisi Kas Berjalan", highlighted=True)
        self.kpi_masuk = KPICard("Total Pemasukan", "+Rp 0", "Penjualan Panen & Komoditas", value_color="green")
        self.kpi_keluar = KPICard("Total Pengeluaran", "-Rp 0", "Saprotan, BBM & Tenaga Kerja", value_color="red")

        kpi_row.pack_start(self.kpi_saldo, True, True, 0)
        kpi_row.pack_start(self.kpi_masuk, True, True, 0)
        kpi_row.pack_start(self.kpi_keluar, True, True, 0)

        # 3. Filter Bar (Pill Tabs & Search)
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content_box.pack_start(filter_box, False, False, 0)

        pill_options = ["Semua Transaksi", "Pemasukan", "Pengeluaran", "Penjualan Panen", "Pupuk & Obat", "Upah Tenaga", "BBM & Perawatan"]
        self.tabs = PillTabs(pill_options, self._on_filter_changed)
        filter_box.pack_start(self.tabs, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Cari uraian transaksi / kas...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        filter_box.pack_start(self.search_entry, True, True, 0)

        btn_delete = Gtk.Button(label="🗑 Hapus Transaksi")
        btn_delete.get_style_context().add_class("btn-secondary")
        btn_delete.connect("clicked", self._on_delete_selected)
        filter_box.pack_end(btn_delete, False, False, 0)

        # 4. Standard Ledger Table
        table_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        table_card.get_style_context().add_class("agri-card")
        content_box.pack_start(table_card, True, True, 0)

        # TreeStore: id, date, description, category, income, expense, balance
        self.store = Gtk.ListStore(int, str, str, str, str, str, str)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        cols = [
            ("ID", 0, 50, 0.0),
            ("Tanggal", 1, 110, 0.0),
            ("Keterangan Transaksi", 2, 280, 0.0),
            ("Kategori", 3, 140, 0.5),
            ("Pemasukan (+)", 4, 150, 1.0),
            ("Pengeluaran (-)", 5, 150, 1.0),
            ("Saldo Berjalan", 6, 170, 1.0)
        ]

        for title, col_idx, width, align in cols:
            renderer = Gtk.CellRendererText()
            renderer.set_alignment(align, 0.5)
            col = Gtk.TreeViewColumn(title, renderer, text=col_idx)
            col.set_min_width(width)
            col.set_resizable(True)
            self.tree.append_column(col)

        table_scroller = Gtk.ScrolledWindow()
        table_scroller.set_min_content_height(380)
        table_scroller.add(self.tree)
        table_card.pack_start(table_scroller, True, True, 0)

        self.refresh_data()

    def _on_filter_changed(self, option):
        self.current_filter = option
        self.refresh_data()

    def _on_search_changed(self, entry):
        self.search_text = entry.get_text().strip().lower()
        self.refresh_data()

    def _on_export_csv(self, widget):
        import csv
        downloads_dir = os.path.expanduser("~/Downloads")
        os.makedirs(downloads_dir, exist_ok=True)
        csv_file = os.path.join(downloads_dir, "laporan_keuangan_agristation.csv")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, transaction_date, category, transaction_type, description, amount_idr, source_module, created_at
                FROM finance_transactions
                ORDER BY transaction_date ASC, id ASC
            """)
            rows = cursor.fetchall()
            conn.close()

            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Tanggal", "Kategori", "Jenis Transaksi", "Keterangan", "Nominal (Rp)", "Sumber Modul", "Waktu Pencatatan"])
                for r in rows:
                    writer.writerow(r)

            self.show_info("Ekspor Berhasil", f"Laporan keuangan berhasil diekspor ke file CSV:\n{csv_file}")
        except Exception as e:
            self.show_error("Gagal Ekspor", f"Terjadi kesalahan saat mengekspor data:\n{e}")

    def refresh_data(self):
        conn = get_connection()
        cursor = conn.cursor()

        # Update KPIs
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN transaction_type = 'Pemasukan' THEN amount_idr ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN transaction_type = 'Pengeluaran' THEN amount_idr ELSE 0 END), 0)
            FROM finance_transactions
        """)
        row = cursor.fetchone()
        tot_masuk, tot_keluar = row[0], row[1]
        saldo = tot_masuk - tot_keluar

        self.kpi_saldo.update(format_rupiah(saldo), "Posisi Kas Bersih")
        self.kpi_masuk.update(f"+{format_rupiah(tot_masuk)}", "Total Dana Masuk")
        self.kpi_keluar.update(f"-{format_rupiah(tot_keluar)}", "Total Biaya Operasional")

        # Query all transactions chronologically to calculate running balance accurately
        cursor.execute("""
            SELECT id, transaction_date, description, category, transaction_type, amount_idr
            FROM finance_transactions
            ORDER BY transaction_date ASC, id ASC
        """)
        all_tx = cursor.fetchall()

        running_balance = 0.0
        calculated_rows = []

        for tx in all_tx:
            t_id, t_date, desc, cat, t_type, amt = tx
            if t_type == "Pemasukan":
                running_balance += amt
                inc_str = format_rupiah(amt)
                exp_str = "-"
            else:
                running_balance -= amt
                inc_str = "-"
                exp_str = format_rupiah(amt)

            bal_str = format_rupiah(running_balance)

            # Apply category or type filter
            if self.current_filter == "Pemasukan" and t_type != "Pemasukan":
                continue
            elif self.current_filter == "Pengeluaran" and t_type != "Pengeluaran":
                continue
            elif self.current_filter != "Semua Transaksi" and self.current_filter not in ("Pemasukan", "Pengeluaran"):
                if cat != self.current_filter:
                    continue

            # Apply search text filter
            if self.search_text:
                searchable = f"{desc} {cat} {t_date} {t_type} {inc_str} {exp_str}".lower()
                if self.search_text not in searchable:
                    continue

            calculated_rows.append((t_id, format_date_id(t_date), desc, cat, inc_str, exp_str, bal_str))

        # Show in descending order (latest on top)
        self.store.clear()
        for r in reversed(calculated_rows):
            self.store.append(list(r))

        conn.close()

    def _on_delete_selected(self, widget):
        selection = self.tree.get_selection()
        model, treeiter = selection.get_selected()
        if not treeiter:
            self.show_error("Peringatan", "Pilih transaksi yang ingin dihapus.")
            return

        tx_id = model[treeiter][0]
        desc = model[treeiter][2]

        # Double confirmation (REQ-APP05-003)
        if not self.confirm_action(
            "Konfirmasi Hapus Transaksi (Audit Trail)",
            f"Apakah Anda yakin ingin menghapus transaksi:\n'{desc}'?\n\nPenghapusan ini akan memengaruhi saldo kas berjalan."
        ):
            return

        conn = get_connection()
        with conn:
            conn.execute("DELETE FROM finance_transactions WHERE id = ?", (tx_id,))
        conn.close()

        self.show_info("Sukses", "Transaksi berhasil dihapus dari buku kas.")
        self.refresh_data()

    def _open_trans_dialog(self, trans_type):
        dialog = AddTransactionDialog(self, trans_type)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

class AddTransactionDialog(Gtk.Dialog):
    def __init__(self, parent, trans_type):
        title = "Catat Pemasukan Kas" if trans_type == "Pemasukan" else "Catat Pengeluaran Kas"
        super().__init__(title=title, transient_for=parent, flags=0)
        self.set_default_size(460, 380)
        self.parent_win = parent
        self.trans_type = trans_type

        box = self.get_content_area()
        box.set_spacing(10)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(16)
        box.set_margin_bottom(16)

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(10)
        box.pack_start(grid, True, True, 0)

        # Date
        grid.attach(Gtk.Label(label="Tanggal Transaksi (YYYY-MM-DD):", xalign=0), 0, 0, 1, 1)
        self.entry_date = Gtk.Entry()
        self.entry_date.set_text(datetime.date.today().strftime("%Y-%m-%d"))
        grid.attach(self.entry_date, 1, 0, 1, 1)

        # Category
        grid.attach(Gtk.Label(label="Kategori Buku Kas:", xalign=0), 0, 1, 1, 1)
        self.combo_cat = Gtk.ComboBoxText()
        if trans_type == "Pemasukan":
            categories = ["Penjualan Panen", "Sewa Lahan / Alsintan", "Bantuan / Subsidi", "Pemasukan Lainnya"]
        else:
            categories = ["Pupuk & Obat", "Upah Tenaga", "BBM & Perawatan", "Benih & Bibit", "Peralatan & Perlengkapan", "Pengeluaran Lainnya"]
        for c in categories:
            self.combo_cat.append_text(c)
        self.combo_cat.set_active(0)
        grid.attach(self.combo_cat, 1, 1, 1, 1)

        # Description
        grid.attach(Gtk.Label(label="Keterangan Uraian Transaksi:", xalign=0), 0, 2, 1, 1)
        self.entry_desc = Gtk.Entry()
        self.entry_desc.set_placeholder_text("Contoh: Penjualan gabah kering panen 3 ton")
        grid.attach(self.entry_desc, 1, 2, 1, 1)

        # Amount IDR
        grid.attach(Gtk.Label(label="Nominal Transaksi (Rp):", xalign=0), 0, 3, 1, 1)
        self.entry_amt = Gtk.Entry()
        self.entry_amt.set_placeholder_text("Contoh: 15000000")
        grid.attach(self.entry_amt, 1, 3, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label=f"Simpan {trans_type}")
        if trans_type == "Pemasukan":
            btn_save.get_style_context().add_class("btn-primary")
        else:
            btn_save.get_style_context().add_class("btn-danger")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_save(self, widget):
        t_date = self.entry_date.get_text().strip()
        cat = self.combo_cat.get_active_text()
        desc = self.entry_desc.get_text().strip()
        amt_str = self.entry_amt.get_text().strip().replace(".", "").replace(",", ".")

        if not desc or not amt_str or not t_date:
            self.parent_win.show_error("Peringatan", "Semua kolom wajib diisi.")
            return

        try:
            amt = float(amt_str)
            if amt <= 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Nominal transaksi harus berupa angka positif lebih besar dari 0.")
            return

        try:
            datetime.date.fromisoformat(t_date)
        except ValueError:
            self.parent_win.show_error("Peringatan", "Format tanggal harus YYYY-MM-DD.")
            return

        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO finance_transactions (transaction_date, category, transaction_type, description, amount_idr, source_module)
                    VALUES (?, ?, ?, ?, ?, 'Agri-Finance Ledger')
                """, (t_date, cat, self.trans_type, desc, amt))
            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Terjadi kesalahan saat menyimpan transaksi:\n{e}")
        finally:
            conn.close()

def main():
    GLib.set_prgname("agri-finance-ledger")
    GLib.set_application_name("Agri-Finance Ledger")
    try:
        Gdk.set_program_class("agri-finance-ledger")
    except Exception:
        pass
    app = FinanceLedgerApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
