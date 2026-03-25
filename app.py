import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

st.set_page_config(page_title="1000 Groceries Market TPS", layout="wide")
st.title("🛒 GreenLeaf Market - Point of Sale")

# 1. Database Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Product Catalog
inventory = {
    "1001": {"desc": "Whole Milk (1L)", "cat": "Dairy", "price": 3.50},
    "2005": {"desc": "Organic Bananas (kg)", "cat": "Produce", "price": 2.20},
    "3002": {"desc": "White Bread", "cat": "Bakery", "price": 2.80},
    "4009": {"desc": "Chicken Breast (kg)", "cat": "Meat", "price": 12.00}
}

# 3. TPS Entry Screen (Sidebar)
st.sidebar.header("Current Transaction")
cashier = st.sidebar.selectbox("Cashier", ["Staff_01", "Staff_02", "Staff_03"])
item_code = st.sidebar.selectbox("Select Item", list(inventory.keys()))
qty = st.sidebar.number_input("Quantity", min_value=0.1, step=0.1, value=1.0)

selected_item = inventory[item_code]
total = qty * selected_item["price"]

if st.sidebar.button("Submit Sale"):
    new_row = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Transaction_ID": str(uuid.uuid4())[:8],
        "Cashier_ID": cashier,
        "Item_Code": item_code,
        "Description": selected_item["desc"],
        "Category": selected_item["cat"],
        "Quantity": qty,
        "Unit_Price": selected_item["price"],
        "Total_Price": total
    }])
    # Append to Sheet
    existing = conn.read()
    updated = pd.concat([existing, new_row], ignore_index=True)
    conn.update(data=updated)
    st.sidebar.success("Transaction Committed!")

# 4. MIS Dashboard (Main Screen)
st.header("MIS Productivity Report")
data = conn.read()

if not data.empty:
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Weekly Revenue", f"${data['Total_Price'].sum():,.2f}")
    kpi2.metric("Total Transactions", len(data))
    kpi3.metric("Top Category", data.groupby("Category")["Total_Price"].sum().idxmax())

    st.subheader("Sales by Staff Member")
    st.bar_chart(data.groupby("Cashier_ID")["Total_Price"].sum())