import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import csv

# Database class to handle SQLite operations
class PhoneBookDB:
    def __init__(self, db_name="phonebook.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                email TEXT,
                address TEXT
            )
        ''')
        self.conn.commit()

    def add_contact(self, name, phone, email, address):
        try:
            self.cursor.execute('''
                INSERT INTO contacts (name, phone, email, address)
                VALUES (?, ?, ?, ?)
            ''', (name, phone, email, address))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def view_all_contacts(self):
        self.cursor.execute("SELECT * FROM contacts")
        return self.cursor.fetchall()

    def search_contacts(self, search_term):
        search_term = f"%{search_term}%"
        self.cursor.execute("SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ?", (search_term, search_term))
        return self.cursor.fetchall()

    def update_contact(self, contact_id, name, phone, email, address):
        try:
            self.cursor.execute('''
                UPDATE contacts
                SET name = ?, phone = ?, email = ?, address = ?
                WHERE id = ?
            ''', (name, phone, email, address, contact_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_contact(self, contact_id):
        self.cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

# Phone Book GUI class using Tkinter
class PhoneBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phone Book App")

        # Database object
        self.db = PhoneBookDB()

        # Initialize GUI elements
        self.setup_ui()

    def setup_ui(self):
        # Labels and input fields
        tk.Label(self.root, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Phone:").grid(row=1, column=0, padx=10, pady=5)
        self.phone_entry = tk.Entry(self.root)
        self.phone_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Email:").grid(row=2, column=0, padx=10, pady=5)
        self.email_entry = tk.Entry(self.root)
        self.email_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Address:").grid(row=3, column=0, padx=10, pady=5)
        self.address_entry = tk.Entry(self.root)
        self.address_entry.grid(row=3, column=1, padx=10, pady=5)

        # Buttons
        tk.Button(self.root, text="Add Contact", command=self.add_contact).grid(row=4, column=0, padx=10, pady=10)
        tk.Button(self.root, text="View All Contacts", command=self.view_contacts).grid(row=4, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Search Contact", command=self.search_contact).grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        # Search field
        tk.Label(self.root, text="Search by Name/Phone:").grid(row=6, column=0, padx=10, pady=5)
        self.search_entry = tk.Entry(self.root)
        self.search_entry.grid(row=6, column=1, padx=10, pady=5)

        # Listbox to display contacts
        self.contact_listbox = tk.Listbox(self.root, width=60)
        self.contact_listbox.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        # Buttons for Update and Delete
        tk.Button(self.root, text="Update Contact", command=self.update_contact).grid(row=8, column=0, padx=10, pady=5)
        tk.Button(self.root, text="Delete Contact", command=self.delete_contact).grid(row=8, column=1, padx=10, pady=5)

        # Export Button
        tk.Button(self.root, text="Export to CSV", command=self.export_to_csv).grid(row=9, column=0, columnspan=2, padx=10, pady=10)

    def add_contact(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        address = self.address_entry.get()

        if name and phone:
            if self.db.add_contact(name, phone, email, address):
                messagebox.showinfo("Success", "Contact added successfully.")
                self.clear_entries()
            else:
                messagebox.showerror("Error", "Phone number already exists.")
        else:
            messagebox.showerror("Error", "Name and Phone fields are mandatory.")

    def view_contacts(self):
        self.contact_listbox.delete(0, tk.END)
        contacts = self.db.view_all_contacts()
        for contact in contacts:
            self.contact_listbox.insert(tk.END, f"ID: {contact[0]}, Name: {contact[1]}, Phone: {contact[2]}, Email: {contact[3]}, Address: {contact[4]}")

    def search_contact(self):
        search_term = self.search_entry.get()
        if search_term:
            self.contact_listbox.delete(0, tk.END)
            contacts = self.db.search_contacts(search_term)
            if contacts:
                for contact in contacts:
                    self.contact_listbox.insert(tk.END, f"ID: {contact[0]}, Name: {contact[1]}, Phone: {contact[2]}, Email: {contact[3]}, Address: {contact[4]}")
            else:
                messagebox.showinfo("No Results", "No contacts found.")
        else:
            messagebox.showwarning("Input Error", "Please enter a search term.")

    def update_contact(self):
        selected = self.contact_listbox.curselection()
        if selected:
            contact_info = self.contact_listbox.get(selected[0])
            contact_id = int(contact_info.split(",")[0].split(":")[1].strip())

            # Update contact with new values
            name = self.name_entry.get()
            phone = self.phone_entry.get()
            email = self.email_entry.get()
            address = self.address_entry.get()

            if name and phone:
                if self.db.update_contact(contact_id, name, phone, email, address):
                    messagebox.showinfo("Success", "Contact updated successfully.")
                    self.clear_entries()
                    self.view_contacts()
                else:
                    messagebox.showerror("Error", "Phone number already exists.")
            else:
                messagebox.showerror("Error", "Name and Phone fields are mandatory.")
        else:
            messagebox.showwarning("Selection Error", "Please select a contact to update.")

    def delete_contact(self):
        selected = self.contact_listbox.curselection()
        if selected:
            contact_info = self.contact_listbox.get(selected[0])
            contact_id = int(contact_info.split(",")[0].split(":")[1].strip())

            self.db.delete_contact(contact_id)
            messagebox.showinfo("Success", "Contact deleted successfully.")
            self.view_contacts()
        else:
            messagebox.showwarning("Selection Error", "Please select a contact to delete.")

    def export_to_csv(self):
        contacts = self.db.view_all_contacts()
        if not contacts:
            messagebox.showwarning("No Data", "There are no contacts to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Name", "Phone", "Email", "Address"])
                for contact in contacts:
                    writer.writerow(contact)

            messagebox.showinfo("Success", "Contacts exported to CSV successfully.")

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)

# Main function to run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneBookApp(root)
    root.mainloop()