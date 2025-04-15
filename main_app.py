# main_app.py
import tkinter as tk
from tkinter import ttk # For themed widgets like Treeview
from tkinter import messagebox
from tkinter import simpledialog # For simple input dialogs
import db_handler # Import our database functions

# --- Main Application Class ---
class BusTicketingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bus Ticketing System")
        self.geometry("800x600") # Adjust size as needed

        # Store the currently logged-in user's ID
        self.current_user_id = None
        self.current_username = None # Store username for display

        # Container frame to hold different pages
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {} # Dictionary to hold page frames
        self.create_frames()
        self.show_frame("LoginPage") # Start with the login page

    def create_frames(self):
        """Creates instances of all page frames."""
        for F in (LoginPage, SignupPage, MainPage, ViewRoutesPage, BookingPage, ViewBookingsPage, ComplaintPage, ViewComplaintsPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            # Place each frame in the same grid cell; only the visible one will be raised
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        """Shows the specified frame."""
        frame = self.frames[page_name]
        # If logging out, clear user data
        if page_name == "LoginPage":
            self.current_user_id = None
            self.current_username = None
            # Clear sensitive fields in login/signup pages when showing them
            if hasattr(self.frames["LoginPage"], 'clear_fields'):
                 self.frames["LoginPage"].clear_fields()
            if hasattr(self.frames["SignupPage"], 'clear_fields'):
                 self.frames["SignupPage"].clear_fields()

        # Refresh data in frames that need it when shown
        if hasattr(frame, 'refresh_data'):
             frame.refresh_data()

        frame.tkraise() # Bring the desired frame to the front

    def set_user(self, user_id, username):
        """Sets the current logged-in user."""
        self.current_user_id = user_id
        self.current_username = username
        # Update user info label in MainPage if it exists
        if "MainPage" in self.frames and hasattr(self.frames["MainPage"], 'update_user_label'):
            self.frames["MainPage"].update_user_label()


# --- Page Frame Base Class (Optional but good practice) ---
class PageFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def refresh_data(self):
        """Placeholder for frames that need to refresh data when shown."""
        pass

    def clear_fields(self):
        """Placeholder for frames that need to clear input fields."""
        pass

# --- Login Page ---
class LoginPage(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        label = ttk.Label(self, text="Login", font=("Arial", 18))
        label.pack(pady=20)

        # Username
        ttk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        # Password
        ttk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        # Login Button
        login_button = ttk.Button(self, text="Login", command=self.login)
        login_button.pack(pady=15)

        # Signup Link
        signup_link = ttk.Label(self, text="Don't have an account? Sign Up", foreground="blue", cursor="hand2")
        signup_link.pack(pady=5)
        signup_link.bind("<Button-1>", lambda e: controller.show_frame("SignupPage"))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        user_id, message = db_handler.validate_user(username, password)

        if user_id:
            messagebox.showinfo("Success", message) # Simple notification
            self.controller.set_user(user_id, username) # Store user ID and username
            self.controller.show_frame("MainPage") # Go to main app
        else:
            messagebox.showerror("Login Failed", message) # Simple notification
            self.password_entry.delete(0, tk.END) # Clear password field on failure

    def clear_fields(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)


# --- Signup Page ---
class SignupPage(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        label = ttk.Label(self, text="Sign Up", font=("Arial", 18))
        label.pack(pady=20)

        # Username
        ttk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        # Email (Optional)
        ttk.Label(self, text="Email (Optional):").pack(pady=5)
        self.email_entry = ttk.Entry(self, width=30)
        self.email_entry.pack(pady=5)

        # Password
        ttk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        # Confirm Password
        ttk.Label(self, text="Confirm Password:").pack(pady=5)
        self.confirm_password_entry = ttk.Entry(self, width=30, show="*")
        self.confirm_password_entry.pack(pady=5)

        # Signup Button
        signup_button = ttk.Button(self, text="Sign Up", command=self.signup)
        signup_button.pack(pady=15)

        # Login Link
        login_link = ttk.Label(self, text="Already have an account? Login", foreground="blue", cursor="hand2")
        login_link.pack(pady=5)
        login_link.bind("<Button-1>", lambda e: controller.show_frame("LoginPage"))

    def signup(self):
        username = self.username_entry.get()
        email = self.email_entry.get() or None # Store None if empty
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in username and password fields.")
            return
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        # Basic password complexity could be added here

        success, message = db_handler.register_user(username, password, email)

        if success:
            messagebox.showinfo("Success", message) # Simple notification
            self.controller.show_frame("LoginPage") # Go to login page after signup
        else:
            messagebox.showerror("Signup Failed", message) # Simple notification

    def clear_fields(self):
        self.username_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)


# --- Main Application Page ---
class MainPage(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        self.user_label = ttk.Label(self, text="", font=("Arial", 12))
        self.user_label.pack(pady=10, anchor="ne", padx=10) # Top right corner

        label = ttk.Label(self, text="Main Menu", font=("Arial", 18))
        label.pack(pady=20)

        # --- Buttons for Features ---
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        btn_view_routes = ttk.Button(button_frame, text="View Available Routes", width=25,
                                    command=lambda: controller.show_frame("ViewRoutesPage"))
        btn_view_routes.grid(row=0, column=0, padx=10, pady=10)

        btn_book_ticket = ttk.Button(button_frame, text="Book a Ticket", width=25,
                                     command=lambda: controller.show_frame("BookingPage"))
        btn_book_ticket.grid(row=1, column=0, padx=10, pady=10)

        btn_view_bookings = ttk.Button(button_frame, text="View My Bookings", width=25,
                                       command=lambda: controller.show_frame("ViewBookingsPage"))
        btn_view_bookings.grid(row=0, column=1, padx=10, pady=10)

        btn_submit_complaint = ttk.Button(button_frame, text="Submit a Complaint", width=25,
                                          command=lambda: controller.show_frame("ComplaintPage"))
        btn_submit_complaint.grid(row=1, column=1, padx=10, pady=10)

        btn_view_complaints = ttk.Button(button_frame, text="View My Complaints", width=25,
                                        command=lambda: controller.show_frame("ViewComplaintsPage"))
        btn_view_complaints.grid(row=2, column=0, padx=10, pady=10)

        btn_logout = ttk.Button(button_frame, text="Logout", width=25,
                                command=lambda: controller.show_frame("LoginPage"))
        btn_logout.grid(row=2, column=1, padx=10, pady=10)


    def update_user_label(self):
        if self.controller.current_username:
            self.user_label.config(text=f"Welcome, {self.controller.current_username}!")
        else:
            self.user_label.config(text="")

    def refresh_data(self):
        """Update the welcome message when this frame is shown."""
        self.update_user_label()


# --- View Routes Page ---
class ViewRoutesPage(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        label = ttk.Label(self, text="Available Routes", font=("Arial", 16))
        label.pack(pady=10)

        # --- Treeview for displaying routes ---
        cols = ("ID", "Origin", "Destination", "Fare", "Departure", "Arrival", "Bus Details")
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=15)

        # Define headings
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER) # Adjust widths as needed
        self.tree.column("ID", width=40)
        self.tree.column("Fare", width=70)
        self.tree.column("Bus Details", width=150)


        # Add Scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        vsb.pack(side='right', fill='y')
        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Back Button
        back_button = ttk.Button(self, text="Back to Menu",
                                command=lambda: controller.show_frame("MainPage"))
        back_button.pack(pady=10)

    def refresh_data(self):
        """Fetch and display routes when the frame is shown."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch new data
        routes, message = db_handler.get_all_routes()
        if routes:
            for route in routes:
                self.tree.insert("", tk.END, values=route)
        else:
            messagebox.showinfo("Info", message) # Show error or "no routes" message


# --- Booking Page ---
class BookingPage(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        self.selected_route_id = tk.IntVar()
        self.selected_route_fare = tk.DoubleVar()

        label = ttk.Label(self, text="Book a Ticket", font=("Arial", 16))
        label.pack(pady=10)

        # --- Route Selection ---
        route_frame = ttk.LabelFrame(self, text="Select Route")
        route_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(route_frame, text="Available Routes:").pack(side=tk.LEFT, padx=5, pady=5)
        self.route_combobox = ttk.Combobox(route_frame, state="readonly", width=60)
        self.route_combobox.pack(side=tk.LEFT, padx=5, pady=5, fill="x", expand=True)
        self.route_combobox.bind("<<ComboboxSelected>>", self.on_route_select)

        # --- Seat Selection ---
        seat_frame = ttk.LabelFrame(self, text="Number of Seats")
        seat_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(seat_frame, text="Seats:").pack(side=tk.LEFT, padx=5, pady=5)
        self.num_seats_spinbox = ttk.Spinbox(seat_frame, from_=1, to=10, width=5) # Limit seats
        self.num_seats_spinbox.pack(side=tk.LEFT, padx=5, pady=5)
        self.num_seats_spinbox.set(1) # Default value

        # --- Fare Display ---
        self.fare_label = ttk.Label(seat_frame, text="Total Fare: ₹0.00")
        self.fare_label.pack(side=tk.LEFT, padx=20, pady=5)
        # Update fare when spinbox value changes
        self.num_seats_spinbox.config(command=self.update_fare_display)

        # --- Action Buttons ---
        action_frame = tk.Frame(self)
        action_frame.pack(pady=20)

        book_button = ttk.Button(action_frame, text="Confirm Booking", command=self.confirm_booking)
        book_button.pack(side=tk.LEFT, padx=10)

        back_button = ttk.Button(action_frame, text="Back to Menu",
                                command=lambda: controller.show_frame("MainPage"))
        back_button.pack(side=tk.LEFT, padx=10)

        self.routes_data = [] # To store route details (id, display_text, fare)


    def refresh_data(self):
        """Load available routes into the combobox."""
        self.routes_data.clear()
        routes, message = db_handler.get_all_routes()
        route_display_list = []
        if routes:
            for route in routes:
                # route format: (route_id, origin, dest, fare, dept, arr, bus_details)
                route_id = route[0]
                fare = float(route[3])
                display_text = f"ID:{route_id} | {route[1]} to {route[2]} ({route[6]}) - Dep: {route[4]} Arr: {route[5]} - ₹{fare:.2f}"
                self.routes_data.append({'id': route_id, 'text': display_text, 'fare': fare})
                route_display_list.append(display_text)
            self.route_combobox['values'] = route_display_list
            if route_display_list:
                 self.route_combobox.current(0) # Select first route by default
                 self.on_route_select(None) # Trigger update for default selection
            else:
                 self.route_combobox['values'] = ["No routes available"]
                 self.route_combobox.current(0)
                 self.selected_route_id.set(0)
                 self.selected_route_fare.set(0.0)
                 self.update_fare_display()

        else:
            messagebox.showinfo("Info", message)
            self.route_combobox['values'] = ["Error loading routes"]
            self.route_combobox.current(0)
            self.selected_route_id.set(0)
            self.selected_route_fare.set(0.0)
            self.update_fare_display()


    def on_route_select(self, event):
        """Handle route selection from combobox."""
        selected_index = self.route_combobox.current()
        if selected_index >= 0 and selected_index < len(self.routes_data):
            selected_route = self.routes_data[selected_index]
            self.selected_route_id.set(selected_route['id'])
            self.selected_route_fare.set(selected_route['fare'])
        else:
             # Handle cases where selection is invalid or "No routes" is shown
             self.selected_route_id.set(0)
             self.selected_route_fare.set(0.0)

        self.update_fare_display()


    def update_fare_display(self):
        """Calculate and display the total fare."""
        try:
            num_seats = int(self.num_seats_spinbox.get())
            fare_per_seat = self.selected_route_fare.get()
            total_fare = num_seats * fare_per_seat
            self.fare_label.config(text=f"Total Fare: ₹{total_fare:.2f}")
        except ValueError:
            self.fare_label.config(text="Total Fare: Invalid")
        except tk.TclError: # Handles cases where spinbox might be empty during init
             self.fare_label.config(text="Total Fare: ₹0.00")


    def confirm_booking(self):
        """Process the booking."""
        route_id = self.selected_route_id.get()
        if not route_id:
            messagebox.showerror("Error", "Please select a valid route.")
            return

        try:
            num_seats = int(self.num_seats_spinbox.get())
            if num_seats <= 0:
                messagebox.showerror("Error", "Number of seats must be positive.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid number of seats.")
            return

        if not self.controller.current_user_id:
             messagebox.showerror("Error", "User not logged in. Please log in again.")
             self.controller.show_frame("LoginPage")
             return

        # Ask for confirmation
        fare_per_seat = self.selected_route_fare.get()
        total_fare = num_seats * fare_per_seat
        confirm = messagebox.askyesno("Confirm Booking",
                                      f"Book {num_seats} seat(s) for Route ID {route_id}?\n"
                                      f"Total Fare: ₹{total_fare:.2f}")

        if confirm:
            booking_id, message = db_handler.add_booking(self.controller.current_user_id, route_id, num_seats)

            if booking_id:
                messagebox.showinfo("Booking Successful", message) # Notification
                # Optionally, generate and show ticket immediately
                self.show_ticket_details(booking_id)
                self.controller.show_frame("MainPage") # Go back to menu after booking
            else:
                messagebox.showerror("Booking Failed", message) # Notification

    def show_ticket_details(self, booking_id):
        """Fetches booking details and displays them in a Toplevel window."""
        details, message = db_handler.get_booking_details(booking_id)
        if not details:
            messagebox.showerror("Error", f"Could not fetch ticket details: {message}")
            return

        # Create a new top-level window for the ticket
        ticket_window = tk.Toplevel(self.controller)
        ticket_window.title(f"Ticket Details - Booking ID: {booking_id}")
        ticket_window.geometry("450x400")

        # --- Ticket Content ---
        tk.Label(ticket_window, text="--- E-Ticket ---", font=("Arial", 16, "bold")).pack(pady=10)

        info_frame = tk.Frame(ticket_window, padx=15, pady=10)
        info_frame.pack(fill=tk.BOTH, expand=True)

        # Grid layout for details
        row_num = 0
        details_map = {
            "Booking ID:": details['booking_id'],
            "Booked By:": details['username'],
            "Booking Date:": details['booked_on'],
            "Route:": f"{details['origin']} to {details['destination']}",
            "Bus Details:": details['bus_details'],
            "Departure Time:": details['dept_time'],
            "Arrival Time:": details['arr_time'],
            "Number of Seats:": details['num_seats'],
            "Total Fare:": f"₹{details['total_fare']:.2f}",
            "Status:": details['status']
        }

        for label_text, value_text in details_map.items():
            tk.Label(info_frame, text=label_text, anchor="w", font=("Arial", 10, "bold")).grid(row=row_num, column=0, sticky="w", pady=2)
            tk.Label(info_frame, text=value_text, anchor="w").grid(row=row_num, column=1, sticky="w", pady=2)
            row_num += 1

        tk.Label(ticket_window, text="Thank you for booking!", font=("Arial", 10, "italic")).pack(pady=10)

        close_button = ttk.Button(ticket_window, text="Close", command=ticket_window.destroy)
        close_button.pack(pady=10)

        ticket_window.transient(self.controller) # Keep ticket window on top
        ticket_window.grab_set() # Modal behavior
        self.controller.wait_window(ticket_window) # Wait until closed

# --- View Bookings Page ---
class ViewBookingsPage(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        label = ttk.Label(self, text="My Bookings", font=("Arial", 16))
        label.pack(pady=10)

        # --- Treeview for displaying bookings ---
        cols = ("Booking ID", "Origin", "Destination", "Departure", "Seats", "Total Fare", "Status", "Booked On")
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=15)

        # Define headings
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
        self.tree.column("Booking ID", width=70)
        self.tree.column("Total Fare", width=80)
        self.tree.column("Booked On", width=130)


        # Add Scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        vsb.pack(side='right', fill='y')
        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # --- Action Buttons ---
        action_frame = tk.Frame(self)
        action_frame.pack(pady=10)

        # Button to view details of selected booking (opens ticket window)
        details_button = ttk.Button(action_frame, text="View Ticket Details", command=self.view_selected_ticket)
        details_button.pack(side=tk.LEFT, padx=10)

        back_button = ttk.Button(action_frame, text="Back to Menu",
                                command=lambda: controller.show_frame("MainPage"))
        back_button.pack(side=tk.LEFT, padx=10)


    def refresh_data(self):
        """Fetch and display user's bookings."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.controller.current_user_id:
             # Don't try to fetch if not logged in (shouldn't happen often here, but good practice)
             return

        bookings, message = db_handler.get_user_bookings(self.controller.current_user_id)
        if bookings:
            for booking in bookings:
                self.tree.insert("", tk.END, values=booking)
        else:
             # Avoid showing error if it's just "no bookings found"
             if "Error" not in message:
                 messagebox.showinfo("Info", "You have no past bookings.")
             else: # Show actual database errors
                 messagebox.showerror("Error", message)

    def view_selected_ticket(self):
        """Show ticket details for the selected booking in the treeview."""
        selected_item = self.tree.focus() # Get selected item identifier
        if not selected_item:
            messagebox.showwarning("Select Booking", "Please select a booking from the list first.")
            return

        item_values = self.tree.item(selected_item, 'values')
        if not item_values:
            return # Should not happen if selection is valid

        booking_id = item_values[0] # Assuming Booking ID is the first column
        try:
            booking_id_int = int(booking_id)
            # Reuse the ticket display logic from BookingPage
            booking_page = self.controller.frames.get("BookingPage")
            if booking_page:
                 booking_page.show_ticket_details(booking_id_int)
            else:
                 messagebox.showerror("Error", "Internal error: Cannot find booking page reference.")
        except ValueError:
             messagebox.showerror("Error", "Invalid Booking ID selected.")


# --- Complaint Page ---
class ComplaintPage(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        label = ttk.Label(self, text="Submit a Complaint", font=("Arial", 16))
        label.pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10, padx=20, fill="x")

        # Booking ID (Optional)
        ttk.Label(form_frame, text="Related Booking ID (Optional):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.booking_id_entry = ttk.Entry(form_frame, width=50)
        self.booking_id_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Subject
        ttk.Label(form_frame, text="Subject:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.subject_entry = ttk.Entry(form_frame, width=50)
        self.subject_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        self.description_text = tk.Text(form_frame, height=8, width=50)
        self.description_text.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        # Add scrollbar to text widget
        desc_scroll = ttk.Scrollbar(form_frame, orient="vertical", command=self.description_text.yview)
        desc_scroll.grid(row=2, column=2, sticky='nsw')
        self.description_text['yscrollcommand'] = desc_scroll.set


        form_frame.columnconfigure(1, weight=1) # Make entry/text expand horizontally

        # --- Action Buttons ---
        action_frame = tk.Frame(self)
        action_frame.pack(pady=20)

        submit_button = ttk.Button(action_frame, text="Submit Complaint", command=self.submit_complaint)
        submit_button.pack(side=tk.LEFT, padx=10)

        back_button = ttk.Button(action_frame, text="Back to Menu",
                                command=lambda: controller.show_frame("MainPage"))
        back_button.pack(side=tk.LEFT, padx=10)

    def submit_complaint(self):
        subject = self.subject_entry.get()
        description = self.description_text.get("1.0", tk.END).strip() # Get text content
        booking_id_str = self.booking_id_entry.get().strip()

        if not subject or not description:
            messagebox.showerror("Error", "Subject and Description cannot be empty.")
            return

        booking_id = None
        if booking_id_str:
            try:
                booking_id = int(booking_id_str)
            except ValueError:
                messagebox.showerror("Error", "Invalid Booking ID. Please enter a number or leave blank.")
                return

        if not self.controller.current_user_id:
             messagebox.showerror("Error", "User not logged in. Please log in again.")
             self.controller.show_frame("LoginPage")
             return

        success, message = db_handler.add_complaint(self.controller.current_user_id, subject, description, booking_id)

        if success:
            messagebox.showinfo("Success", message) # Notification
            # Clear fields after successful submission
            self.booking_id_entry.delete(0, tk.END)
            self.subject_entry.delete(0, tk.END)
            self.description_text.delete("1.0", tk.END)
            self.controller.show_frame("MainPage") # Go back to menu
        else:
            messagebox.showerror("Submission Failed", message) # Notification

    def clear_fields(self):
        """Clear input fields when navigating away potentially."""
        self.booking_id_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)

# --- View Complaints Page ---
class ViewComplaintsPage(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        label = ttk.Label(self, text="My Complaints", font=("Arial", 16))
        label.pack(pady=10)

        # --- Treeview for displaying complaints ---
        cols = ("Complaint ID", "Booking ID", "Subject", "Status", "Submitted On")
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=15)

        # Define headings
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.W) # Use West anchor for text
        self.tree.column("Complaint ID", width=80, anchor=tk.CENTER)
        self.tree.column("Booking ID", width=80, anchor=tk.CENTER)
        self.tree.column("Subject", width=250)
        self.tree.column("Submitted On", width=130, anchor=tk.CENTER)

        # Add Scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        vsb.pack(side='right', fill='y')
        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # --- Display Description ---
        desc_frame = ttk.LabelFrame(self, text="Selected Complaint Description")
        desc_frame.pack(pady=10, padx=10, fill="x")

        self.desc_text = tk.Text(desc_frame, height=5, width=70, state=tk.DISABLED, wrap=tk.WORD) # Read-only
        desc_scroll = ttk.Scrollbar(desc_frame, orient="vertical", command=self.desc_text.yview)
        self.desc_text.config(yscrollcommand=desc_scroll.set)

        self.desc_text.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        desc_scroll.pack(side=tk.RIGHT, fill="y")

        # Bind selection event to show description
        self.tree.bind("<<TreeviewSelect>>", self.show_description)

        # Back Button
        back_button = ttk.Button(self, text="Back to Menu",
                                command=lambda: controller.show_frame("MainPage"))
        back_button.pack(pady=10)

        self.complaints_data = [] # Store full complaint data including description


    def refresh_data(self):
        """Fetch and display user's complaints."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.config(state=tk.DISABLED)
        self.complaints_data.clear()

        if not self.controller.current_user_id:
             return

        complaints, message = db_handler.get_user_complaints(self.controller.current_user_id)
        if complaints:
             self.complaints_data = complaints # Store all data
             for complaint in complaints:
                 # complaint format: (complaint_id, booking_id, subject, description, status, submitted_at)
                 display_values = (complaint[0], complaint[1] if complaint[1] else "N/A", complaint[2], complaint[4], complaint[5])
                 self.tree.insert("", tk.END, values=display_values, iid=complaint[0]) # Use complaint_id as item ID (iid)
        else:
             if "Error" not in message:
                 messagebox.showinfo("Info", "You have not submitted any complaints.")
             else:
                 messagebox.showerror("Error", message)


    def show_description(self, event):
        """Display the description of the selected complaint."""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        selected_iid = selected_items[0] # Get the iid (complaint_id)
        description = "Description not found."

        # Find the full complaint data using the iid
        for complaint in self.complaints_data:
             if str(complaint[0]) == str(selected_iid): # Compare complaint_id
                 description = complaint[3] # The description text
                 break

        # Update the text widget
        self.desc_text.config(state=tk.NORMAL) # Enable editing
        self.desc_text.delete("1.0", tk.END)     # Clear previous content
        self.desc_text.insert("1.0", description)# Insert new description
        self.desc_text.config(state=tk.DISABLED) # Disable editing again


# --- Run the Application ---
if __name__ == "__main__":
    app = BusTicketingApp()
    app.mainloop()