import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage  # Import PhotoImage
from tkinter import Label
import mysql.connector
from admin import AdminLoginPage

# Replace with your MySQL database credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'foodapp',
}

# Initialize MySQL connection
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Global variables for entry widgets
name_entry = None
address_entry = None
email_entry = None
pin_code_entry = None


def create_users_table():
    # Create a table for users if not exists
    create_table_query = (
        "CREATE TABLE IF NOT EXISTS users ("
        "  id INT AUTO_INCREMENT PRIMARY KEY,"
        "  username VARCHAR(255) NOT NULL UNIQUE,"
        "  password VARCHAR(255) NOT NULL"
        ")"
    )
    cursor.execute(create_table_query)
    conn.commit()


def create_orders_table():
    # Create a table for orders if not exists
    create_table_query = (
        "CREATE TABLE IF NOT EXISTS orders ("
        "  id INT AUTO_INCREMENT PRIMARY KEY,"
        "  items TEXT NOT NULL,"
        "  total_price FLOAT NOT NULL,"
        "  name VARCHAR(255) NOT NULL,"
        "  address VARCHAR(255) NOT NULL,"
        "  email VARCHAR(255) NOT NULL,"
        "  pin_code VARCHAR(10) NOT NULL"
        ")"
    )
    cursor.execute(create_table_query)
    conn.commit()

def fetch_products():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        fetch_products_query = "SELECT name, price FROM products"
        cursor.execute(fetch_products_query)
        products = cursor.fetchall()
        return products
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error fetching products: {err}")
    finally:
        cursor.close()
        conn.close()


def add_to_cart(item, price, cart_listbox, total_price_label):
    cart_listbox.insert(tk.END, f"{item} - ₹{price:.2f}")
    update_total_price(cart_listbox, total_price_label)


def update_total_price(cart_listbox, total_price_label):
    total_price = sum(float(item.split('- ₹')[1].strip()) for item in cart_listbox.get(0, tk.END))
    total_price_label.config(text=f"Total Price: ₹{total_price:.2f}")


def remove_from_cart(cart_listbox, total_price_label):
    selected_indices = cart_listbox.curselection()

    if not selected_indices:
        messagebox.showwarning("Warning", "Please select an item to remove.")
        return

    # Check if only one item is selected
    if len(selected_indices) == 1:
        # Get the selected item
        selected_item = cart_listbox.get(selected_indices[0])

        # Check if it's the last item
        if cart_listbox.size() == 1:
            messagebox.showwarning("Warning", "The last item cannot be removed.")
            return

    # Remove selected items from the cart
    for index in reversed(selected_indices):
        cart_listbox.delete(index)

    # Update total price
    update_total_price(cart_listbox, total_price_label)


def checkout(cart_listbox, total_price_label, name, address, email, pin_code):
    items_in_cart = cart_listbox.get(0, tk.END)

    if not items_in_cart:
        messagebox.showwarning("Warning", "Your cart is empty. Add products before checkout.")
        return

    total_price = sum(float(item.split('- ₹')[1].strip()) for item in items_in_cart)

    # Insert the order into the MySQL database
    insert_order_query = "INSERT INTO orders (items, total_price, name, address, email, pin_code) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_order_query, (", ".join(items_in_cart), total_price, name, address, email, pin_code))
    conn.commit()

    # Clear the cart
    cart_listbox.delete(0, tk.END)
    update_total_price(cart_listbox, total_price_label)

    # Clear the checkout form after successful checkout
    name_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    pin_code_entry.delete(0, tk.END)

    # Show thanks for ordering message
    show_thanks_window()


def show_thanks_window():
    thanks_window = tk.Toplevel()
    thanks_window.title("Thanks for Ordering")

    tk.Label(thanks_window, text="Thanks for ordering! Your order has been placed.", font=("Helvetica", 16)).pack()

    ok_button = tk.Button(thanks_window, text="OK", command=thanks_window.destroy, font=("Helvetica", 14))
    ok_button.pack()


def logout(root):
    confirmation = messagebox.askyesno("Logout Confirmation", "Are you sure you want to logout?")

    if confirmation:
        root.destroy()


def open_admin_login():
    # Create an instance of the AdminLoginPage and open the admin login window
    admin_login_window = tk.Toplevel()
    admin_login_page = AdminLoginPage(admin_login_window)


def show_main_menu():
    # Create the main menu window
    root = tk.Tk()
    root.title("FoodieDelight cart")

    # Set window size twice as large as the previous tablet-sized window
    window_width = 1200
    window_height = 1200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = 50  # Vertical center from the top

    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Create Users and Orders tables
    create_users_table()
    create_orders_table()

    # Nav Bar (Black)
    nav_bar = tk.Frame(root, bg="#bec5d1", height=10)
    nav_bar.pack(side=tk.TOP, fill=tk.BOTH)

    # Heading "Food Ordering App" in the Nav Bar
    tk.Label(nav_bar, text="FoodieDelight", font=("Helvetica", 20, 'bold'), fg="white", bg="#bec5d1").pack(pady=10,padx=20)

    # Logout button in the Nav Bar
    tk.Button(nav_bar, text="Logout", command=lambda: logout(root), font=("Helvetica", 16), width=10, bg="white",fg="red").pack(
        pady=10, side=tk.RIGHT)

    # Left Box (Black)
    left_box = tk.Frame(root, bg="black", width=600, height=1600)
    left_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Fetch products from the MySQL database
    products = fetch_products()

    cart_listbox = tk.Listbox(left_box, selectmode=tk.MULTIPLE, font=("Helvetica", 16), width=50, bg="#bec5d1")
    cart_listbox.pack(pady=40)

    total_price_label = tk.Label(left_box, text="Total Price: ₹0.00", font=("Helvetica", 18), bg="black", fg="white")
    total_price_label.pack()

    for product in products:
        product_name, product_price = product
        tk.Button(left_box, text=f"{product_name} - ₹{product_price:.2f}", font=("Helvetica", 16), width=40,bg="#bec5d1",
                  command=lambda p=product_name, pr=product_price: add_to_cart(p, pr, cart_listbox,
                                                                               total_price_label)).pack()

    tk.Button(left_box, text="Remove from Cart", command=lambda: remove_from_cart(cart_listbox, total_price_label),
              font=("Helvetica", 16), width=20, bg="#1877f2", fg="white").pack(pady=10)


    # Right Box (Black)
    right_box = tk.Frame(root, bg="black", width=600, height=1600)
    right_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Add space at the top of the checkout form
    tk.Label(right_box, text="", height=3, bg="black").pack()

    # Checkout form in the Right Box
    checkout_frame = tk.Frame(right_box, bg="black")
    checkout_frame.pack(pady=10)

    global name_entry, address_entry, email_entry, pin_code_entry

    tk.Label(checkout_frame, text="Checkout Form", font=("Helvetica", 18), fg="white", bg="black").pack()

    tk.Label(checkout_frame, text="Name:", font=("Helvetica", 14), fg="white", bg="black").pack()
    name_entry = tk.Entry(checkout_frame, font=("Helvetica", 14),bg="#bec5d1")
    name_entry.pack()

    tk.Label(checkout_frame, text="Address:", font=("Helvetica", 14), fg="white", bg="black").pack()
    address_entry = tk.Entry(checkout_frame, font=("Helvetica", 14),bg="#bec5d1")
    address_entry.pack()

    tk.Label(checkout_frame, text="Email:", font=("Helvetica", 14), fg="white", bg="black").pack()
    email_entry = tk.Entry(checkout_frame, font=("Helvetica", 14),bg="#bec5d1")
    email_entry.pack()

    tk.Label(checkout_frame, text="Pin Code:", font=("Helvetica", 14), fg="white", bg="black").pack()
    pin_code_entry = tk.Entry(checkout_frame, font=("Helvetica", 14),bg="#bec5d1")
    pin_code_entry.pack()

    # Checkout button in the Right Box
    tk.Button(right_box, text="Checkout",
              command=lambda: checkout(cart_listbox, total_price_label, name_entry.get(), address_entry.get(),
                                       email_entry.get(), pin_code_entry.get()), font=("Helvetica", 16), width=15,
              bg="#42b72a", fg="white").pack(pady=10)


    # Run the Tkinter event loop
    root.mainloop()


def signup(username, password):
    # Add a new user to the database
    insert_user_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    cursor.execute(insert_user_query, (username, password))
    conn.commit()


def login(username, password):
    # Check if the username and password match a user in the database
    select_user_query = "SELECT * FROM users WHERE username=%s AND password=%s"
    cursor.execute(select_user_query, (username, password))
    return cursor.fetchone() is not None


def signup_window(root):
    signup_window = tk.Toplevel(root)
    signup_window.title("Sign Up")

    # Center the signup window along the y-axis
    window_width = 400
    window_height = 300
    screen_width = signup_window.winfo_screenwidth()
    screen_height = signup_window.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    signup_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Set the background color
    signup_window.configure(bg="#bec5d1")


    tk.Label(signup_window, text="Username:", font=("Helvetica", 16),bg="#bec5d1").pack()
    signup_username_entry = tk.Entry(signup_window, font=("Helvetica", 16))
    signup_username_entry.pack()

    tk.Label(signup_window, text="Password:", font=("Helvetica", 16),bg="#bec5d1").pack()
    signup_password_entry = tk.Entry(signup_window, show="*", font=("Helvetica", 16))
    signup_password_entry.pack()

    def sign_up():
        username = signup_username_entry.get()
        password = signup_password_entry.get()

        if username and password:
            signup(username, password)
            signup_window.destroy()
            messagebox.showinfo("Success", "Sign Up Successful! Now you can log in.")
            login_window()
        else:
            messagebox.showerror("Error", "Both fields are required!")

    tk.Button(signup_window, text="Sign Up", command=sign_up, font=("Helvetica", 16), bg="#42b72a", fg="white").pack(pady=10)


def login_window():
    login_window = tk.Toplevel(root)
    login_window.title("Login")

    # Center the login window along the y-axis
    window_width = 300
    window_height = 200
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    login_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    tk.Label(login_window, text="Username:", font=("Helvetica", 16)).pack()
    login_username_entry = tk.Entry(login_window, font=("Helvetica", 16))
    login_username_entry.pack()

    tk.Label(login_window, text="Password:", font=("Helvetica", 16)).pack()
    login_password_entry = tk.Entry(login_window, show="*", font=("Helvetica", 16))
    login_password_entry.pack()

    def log_in():
        username = login_username_entry.get()
        password = login_password_entry.get()

        if login(username, password):
            messagebox.showinfo("Success", "Login successful!")
            login_window.destroy()
            show_main_menu()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    tk.Button(login_window, text="Login", command=log_in, font=("Helvetica", 16), bg="#1877f2", fg="white").pack(pady=10)





# Create the main window
root = tk.Tk()
root.configure(bg='#bec5d1')
root.title("FoodieDelight home")

# Set initial window size and position
window_width = 600
window_height = 800
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")



try:
    # Load the image
    image_path = "foodiedelight.png"
    image = PhotoImage(file=image_path)

    # Create a Label to display the image
    image_label = Label(root, image=image, bg='#bec5d1')
    image_label.pack(pady=10)

except Exception as e:
    print(f"Error loading image: {e}")



# Initial screen - signup, login, and admin login
tk.Label(root, text="Welcome to FoodieDelight🍔", font=("Helvetica", 24, 'bold'),bg="#bec5d1").pack(pady=20)

# Set a common width for the buttons
button_width = 20

tk.Button(root, text="Login", command=lambda: login_window(), font=("Helvetica", 20), width=button_width, bg="#1877f2", fg="white").pack(pady=10)
tk.Button(root, text="Sign Up", command=lambda: signup_window(root), font=("Helvetica", 20), width=button_width,bg="#42b72a", fg="white" ).pack(pady=10)
tk.Button(root, text="Admin Login", command=open_admin_login, font=("Helvetica", 20), width=button_width, fg="#1877f2").pack(pady=10)


# Run the Tkinter event loop
root.mainloop()