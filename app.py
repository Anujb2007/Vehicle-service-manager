import sqlite3
from datetime import date
import streamlit as st

DB = "vehicle_service.db"

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            vehicle_no TEXT NOT NULL,
            model TEXT NOT NULL,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            service_date TEXT NOT NULL,
            service_type TEXT NOT NULL,
            cost REAL NOT NULL,
            notes TEXT,
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
        )
    """)
    con.commit()
    con.close()

def add_customer(name, phone):
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO customers(name, phone) VALUES (?, ?)", (name, phone))
    con.commit()
    con.close()

def get_customers():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT id, name, phone FROM customers ORDER BY id DESC").fetchall()
    con.close()
    return rows

def add_vehicle(customer_id, vehicle_no, model):
    con = sqlite3.connect(DB)
    con.execute(
        "INSERT INTO vehicles(customer_id, vehicle_no, model) VALUES (?, ?, ?)",
        (customer_id, vehicle_no.upper(), model)
    )
    con.commit()
    con.close()

def get_vehicles():
    con = sqlite3.connect(DB)
    rows = con.execute("""
        SELECT v.id, v.vehicle_no, v.model, c.name
        FROM vehicles v JOIN customers c ON v.customer_id = c.id
        ORDER BY v.id DESC
    """).fetchall()
    con.close()
    return rows

def add_service(vehicle_id, service_date, service_type, cost, notes):
    con = sqlite3.connect(DB)
    con.execute("""
        INSERT INTO services(vehicle_id, service_date, service_type, cost, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (vehicle_id, service_date, service_type, cost, notes))
    con.commit()
    con.close()

def get_services():
    con = sqlite3.connect(DB)
    rows = con.execute("""
        SELECT s.service_date, v.vehicle_no, v.model, c.name,
               s.service_type, s.cost, COALESCE(s.notes, '')
        FROM services s
        JOIN vehicles v ON s.vehicle_id = v.id
        JOIN customers c ON v.customer_id = c.id
        ORDER BY s.service_date DESC
    """).fetchall()
    con.close()
    return rows

init_db()

st.set_page_config(page_title="Vehicle Service Management", page_icon="🚗")
st.title("🚗 Vehicle Service Management System")
st.caption("A beginner-friendly Python + SQLite project for managing customers, vehicles and service records.")

tab1, tab2, tab3, tab4 = st.tabs(["Customers", "Vehicles", "Add Service", "Service History"])

with tab1:
    st.subheader("Add Customer")
    with st.form("customer_form"):
        name = st.text_input("Customer name")
        phone = st.text_input("Phone number")
        if st.form_submit_button("Add Customer"):
            if name and phone:
                add_customer(name, phone)
                st.success("Customer added.")
            else:
                st.warning("Please enter both fields.")
    rows = get_customers()
    if rows:
        st.dataframe(rows, column_config={"0": "ID", "1": "Name", "2": "Phone"}, use_container_width=True)

with tab2:
    st.subheader("Add Vehicle")
    customers = get_customers()
    if customers:
        customer_map = {f"{r[1]} ({r[2]})": r[0] for r in customers}
        with st.form("vehicle_form"):
            selected = st.selectbox("Customer", list(customer_map))
            vehicle_no = st.text_input("Vehicle number")
            model = st.text_input("Vehicle model")
            if st.form_submit_button("Add Vehicle"):
                if vehicle_no and model:
                    add_vehicle(customer_map[selected], vehicle_no, model)
                    st.success("Vehicle added.")
                else:
                    st.warning("Please enter vehicle number and model.")
    else:
        st.info("Add a customer first.")

    rows = get_vehicles()
    if rows:
        st.dataframe(rows, use_container_width=True)

with tab3:
    st.subheader("Record Service")
    vehicles = get_vehicles()
    if vehicles:
        vehicle_map = {f"{r[1]} — {r[2]} — {r[3]}": r[0] for r in vehicles}
        with st.form("service_form"):
            selected = st.selectbox("Vehicle", list(vehicle_map))
            service_date = st.date_input("Service date", value=date.today())
            service_type = st.selectbox(
                "Service type",
                ["General Service", "Oil Change", "Brake Service", "Engine Repair", "Other"]
            )
            cost = st.number_input("Cost (₹)", min_value=0.0, step=100.0)
            notes = st.text_area("Notes")
            if st.form_submit_button("Save Service"):
                add_service(vehicle_map[selected], str(service_date), service_type, cost, notes)
                st.success("Service record saved.")
    else:
        st.info("Add a vehicle first.")

with tab4:
    st.subheader("Service History")
    rows = get_services()
    if rows:
        st.dataframe(
            rows,
            column_config={
                "0": "Date", "1": "Vehicle No.", "2": "Model",
                "3": "Customer", "4": "Service", "5": "Cost", "6": "Notes"
            },
            use_container_width=True
        )
    else:
        st.info("No service records yet.")
