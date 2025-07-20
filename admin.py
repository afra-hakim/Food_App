import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class AdminLoginPage:
    def __init__(self, master):
        self.master = master
        self.master.title("Admin Login")

        # Increase height and width of the window
        window_width = 600
        window_height = 400
        self.master.geometry(f"{window_width}x{window_height}")

        self.heading_label = tk.Label(self.master, text="Admin Login", font=("Helvetica", 24))
        self.heading_label.pack(pady=20)

        self.username_label = tk.Label(self.master, text="Admin Username:", font=("Helvetica", 16))
        self.username_label.pack()

        self.username_entry = tk.Entry(self.master, font=("Helvetica", 16))
        self.username_entry.pack()

        self.password_label = tk.Label(self.master, text="Admin Password:", font=("Helvetica", 16))
        self.password_label.pack()

        self.password_entry = tk.Entry(self.master, show="*", font=("Helvetica", 16))
        self.password_entry.pack()

        self.login_button = tk.Button(self.master, text="Login", command=self.login, font=("Helvetica", 16), fg="#1877f2")
        self.login_button.pack(pady=10)

    def login(self):
        admin_username = self.username_entry.get()
        admin_password = self.password_entry.get()

        # Check if the entered credentials match the default admin credentials
        if admin_username == "admin" and admin_password == "123":
            messagebox.showinfo("Success", "Admin Login successful!")
            self.master.destroy()  # Close the admin login window

            # Implement the functionality you want to perform after admin login
            # For example, you can open the Admin Main Menu
            admin_main_menu = tk.Tk()
            admin_main_menu.title("Admin Main Menu")

            # Add your admin main menu components and functionalities here
            AdminMainMenu(admin_main_menu)

            admin_main_menu.mainloop()
        else:
            messagebox.showerror("Error", "Invalid admin username or password!")

class AdminMainMenu:
    def __init__(self, master):
        self.master = master
        self.master.title("Admin Main Menu")


        # Set the size of the Admin Main Menu window (adjust width and height based on your preference)
        window_width = 800
        window_height = 800
        self.master.geometry(f"{window_width}x{window_height}")


        # Create a notebook to switch between tabs
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        list_products_tab = ListProductsTab(self.notebook)
        add_product_tab = AddProductTab(self.notebook, list_products_tab)
        list_orders_tab = ListOrdersTab(self.notebook)  # Add the new tab

        # Add Logout button
        self.logout_button = tk.Button(self.master, text="Logout", command=self.logout, font=("Helvetica", 16),width=10,bg="red", fg="white")
        self.logout_button.pack(pady=10,side=tk.RIGHT)

    def logout(self):
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to logout?")
        if confirmation:
            self.master.destroy()
            admin_login_window = tk.Tk()
            admin_login_window.title("Admin Login")
            AdminLoginPage(admin_login_window)

class AddProductTab:
    def __init__(self, master, list_products_tab):
        self.master = master

        # Create a frame for the tab
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        #tk.Label(self.frame, text="Add Product", font=("Helvetica", 24)).pack(pady=20)

        # Add product form fields
        tk.Label(self.frame, text="Product Name:", font=("Helvetica", 16)).pack()
        self.product_name_entry = tk.Entry(self.frame, font=("Helvetica", 16))
        self.product_name_entry.pack()

        tk.Label(self.frame, text="Product Price:", font=("Helvetica", 16)).pack()
        self.product_price_entry = tk.Entry(self.frame, font=("Helvetica", 16))
        self.product_price_entry.pack()

        # Add submit button
        tk.Button(self.frame, text="Add", command=self.add_product, font=("Helvetica", 16),width=15,bg="#42b72a", fg="white").pack(pady=10)

        # Reference to ListProductsTab instance for real-time updates
        self.list_products_tab = list_products_tab

    def add_product(self):
        product_name = self.product_name_entry.get()
        product_price = self.product_price_entry.get()

        # Validate input
        if not product_name or not product_price:
            messagebox.showerror("Error", "Both product name and price are required!")
            return

        try:
            product_price = float(product_price)
        except ValueError:
            messagebox.showerror("Error", "Invalid product price. Please enter a valid number.")
            return

        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='1234', database='foodapp')
            cursor = conn.cursor()
            insert_product_query = "INSERT INTO products (name, price) VALUES (%s, %s)"
            cursor.execute(insert_product_query, (product_name, product_price))
            conn.commit()

            messagebox.showinfo("Success", "Product added!")

            # Clear form fields
            self.product_name_entry.delete(0, tk.END)
            self.product_price_entry.delete(0, tk.END)

            # Update the product list in ListProductsTab
            self.list_products_tab.update_product_list()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error adding product: {err}")
        finally:
            cursor.close()
            conn.close()

class ListProductsTab:
    def __init__(self, master):
        self.master = master

        # Create a frame for the tab
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="Products List", font=("Helvetica", 24)).pack(pady=20)

        # Create a treeview to display products
        self.tree = ttk.Treeview(self.frame, columns=("ID", "Name", "Price"), show="headings", height=6)
        self.tree.heading("ID", text="Product ID")
        self.tree.heading("Name", text="Product Name")
        self.tree.heading("Price", text="Product Price")
        self.tree.pack()

        # Fetch and display products from the MySQL database
        self.fetch_and_display_products()

    def fetch_and_display_products(self):
        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='1234', database='foodapp')
            cursor = conn.cursor()
            fetch_products_query = "SELECT * FROM products"
            cursor.execute(fetch_products_query)
            products = cursor.fetchall()

            for product in products:
                item_id = product[0]
                product_name = product[1]
                product_price = product[2]

                # Add row to the treeview
                self.tree.insert("", "end", values=(item_id, product_name, product_price))

                # Create a popup menu for each row
                popup_menu = tk.Menu(self.master, tearoff=0)
                popup_menu.add_command(label="Delete", command=lambda p=item_id: self.delete_product(p))

                # Bind the right-click event to show the menu
                self.tree.bind("<Button-3>", lambda event, menu=popup_menu: menu.post(event.x_root, event.y_root))
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error fetching products: {err}")
        finally:
            cursor.close()
            conn.close()

    def update_product_list(self):
        # Refresh the list of products
        self.tree.delete(*self.tree.get_children())  # Clear existing items
        self.fetch_and_display_products()

    def delete_product(self, product_id):
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this product?")
        if confirmation:
            try:
                conn = mysql.connector.connect(host='localhost', user='root', password='1234', database='foodapp')
                cursor = conn.cursor()
                delete_product_query = "DELETE FROM products WHERE id = %s"
                cursor.execute(delete_product_query, (product_id,))
                conn.commit()

                messagebox.showinfo("Deleted", "Product deleted!")

                # Update the product list after deletion
                self.update_product_list()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error deleting product: {err}")
            finally:
                cursor.close()
                conn.close()

class ListOrdersTab:
    def __init__(self, master):
        self.master = master

        # Create a frame for the tab
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="Orders List", font=("Helvetica", 24)).pack(pady=20)

        # Create a treeview to display orders
        self.tree = ttk.Treeview(self.frame,
                                 columns=("ID", "Items", "Total Price", "Name", "Address", "Email", "Pin Code"),
                                 show="headings", height=6)
        self.tree.heading("ID", text="Order ID", anchor=tk.CENTER)
        self.tree.heading("Items", text="Items", anchor=tk.CENTER)
        self.tree.heading("Total Price", text="Total Price", anchor=tk.CENTER)
        self.tree.heading("Name", text="Name", anchor=tk.CENTER)
        self.tree.heading("Address", text="Address", anchor=tk.CENTER)
        self.tree.heading("Email", text="Email", anchor=tk.CENTER)
        self.tree.heading("Pin Code", text="Pin Code", anchor=tk.CENTER)

        # Set column widths (adjust these values based on your preference)
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Items", width=150, anchor=tk.CENTER)
        self.tree.column("Total Price", width=80, anchor=tk.CENTER)
        self.tree.column("Name", width=100, anchor=tk.CENTER)
        self.tree.column("Address", width=150, anchor=tk.CENTER)
        self.tree.column("Email", width=120, anchor=tk.CENTER)
        self.tree.column("Pin Code", width=80, anchor=tk.CENTER)

        self.tree.pack()

        # Fetch and display orders from the MySQL database
        self.fetch_and_display_orders()

    def fetch_and_display_orders(self):
        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='1234', database='foodapp')
            cursor = conn.cursor()
            fetch_orders_query = "SELECT * FROM orders"
            cursor.execute(fetch_orders_query)
            orders = cursor.fetchall()

            for order in orders:
                order_id, items, total_price, name, address, email, pin_code = order

                # Truncate items for display (adjust the length as needed)
                truncated_items = items[:30] + '...' if len(items) > 30 else items

                # Add row to the treeview
                self.tree.insert("", "end", values=(order_id, truncated_items, total_price, name, address, email, pin_code))

                # Create a popup menu for each row
                popup_menu = tk.Menu(self.master, tearoff=0)
                popup_menu.add_command(label="Delete", command=lambda o=order_id: self.delete_order(o))

                # Bind the right-click event to show the menu
                self.tree.bind("<Button-3>", lambda event, menu=popup_menu: menu.post(event.x_root, event.y_root))
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error fetching orders: {err}")
        finally:
            cursor.close()
            conn.close()

    def delete_order(self, order_id):
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this order?")
        if confirmation:
            try:
                conn = mysql.connector.connect(host='localhost', user='root', password='1234', database='foodapp')
                cursor = conn.cursor()
                delete_order_query = "DELETE FROM orders WHERE id = %s"
                cursor.execute(delete_order_query, (order_id,))
                conn.commit()

                messagebox.showinfo("Deleted", "Order deleted!")

                # Update the order list after deletion
                self.fetch_and_display_orders()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error deleting order: {err}")
            finally:
                cursor.close()
                conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    admin_login_page = AdminLoginPage(root)
    root.mainloop()