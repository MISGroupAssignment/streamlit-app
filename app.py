import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. Setup Page & Connection
st.set_page_config(page_title="Greenleaf Grocery POS", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Define the 10 Grocery Items
items = [
    ("G001", "Full Cream Milk", 3.50), ("G002", "White Bread", 2.80),
    ("G003", "Grade A Eggs", 4.50), ("P001", "Bananas (kg)", 1.20),
    ("P002", "Red Apples (kg)", 3.80), ("S001", "Basmati Rice", 12.50),
    ("S002", "Cooking Oil", 7.20), ("B001", "Canned Soda", 1.50),
    ("H001", "Dishwashing Liquid", 5.00), ("H002", "Toilet Paper", 8.90)
]
staff_list = ["Alice", "Bob", "Charlie", "Diana"]

# 3. Create Tabs
tab1, tab2 = st.tabs(["🛒 Submit Sale", "📊 MIS Productivity Report"])

# --- TAB 1: SUBMIT SALE ---
with tab1:
    st.header("New Sale Entry")
    
    with st.form("sale_form"):
        staff = st.selectbox("Select Staff", staff_list)
        item_choice = st.selectbox("Select Item", [f"{i[0]} - {i[1]}" for i in items])
        quantity = st.number_input("Quantity", min_value=1, value=1)
        
        # Get item details based on selection
        selected_item = next(i for i in items if i[0] == item_choice.split(" - ")[0])
        
        submitted = st.form_submit_button("Submit Sale")
        
        if submitted:
            new_data = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Staff": staff,
                "Item_Code": selected_item[0],
                "Description": selected_item[1],
                "Quantity": quantity,
                "Unit_Price": selected_item[2],
                "Total_Price": round(quantity * selected_item[2], 2)
            }])
            
            # Read existing, add new, and update
            existing_df = conn.read(worksheet="Sales", ttl=0)
            updated_df = pd.concat([existing_df, new_data], ignore_index=True)
            conn.update(worksheet="Sales", data=updated_df)
            st.success("Transaction Committed! ✅")

# --- TAB 2: MIS REPORT ---
with tab2:
    st.header("Grocery Store Productivity Report")

    # SIMULATION BUTTON
    if st.button("🚀 Load 1,000 Test Transactions"):
        bulk_data = []
        start_date = datetime.now() - timedelta(days=7)
        for i in range(1000):
            tx_date = start_date + timedelta(minutes=random.randint(1, 10080))
            item = random.choice(items)
            qty = random.randint(1, 10)
            bulk_data.append({
                "Timestamp": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
                "Staff": random.choice(staff_list),
                "Item_Code": item[0],
                "Description": item[1],
                "Quantity": qty,
                "Unit_Price": item[2],
                "Total_Price": round(qty * item[2], 2)
            })
        
        sim_df = pd.DataFrame(bulk_data)
        existing_df = conn.read(worksheet="Sales", ttl=0)
        final_df = pd.concat([existing_df, sim_df], ignore_index=True)
        conn.update(worksheet="Sales", data=final_df)
        st.success("✅ 1,000 Grocery transactions added!")
        st.cache_data.clear()

    # DISPLAY CHARTS
    df = conn.read(worksheet="Sales", ttl=0)
    if not df.empty:
        # Metrics
        c1, c2 = st.columns(2)
        c1.metric("Total Revenue", f"${df['Total_Price'].sum():,.2f}")
        c2.metric("Sales Count", len(df))

        # Bar Chart 1
        st.subheader("Sales by Staff")
        st.bar_chart(df.groupby("Staff")["Total_Price"].sum())

        # Bar Chart 2
        st.subheader("Top Products")
        st.bar_chart(df.groupby("Description")["Total_Price"].sum(), horizontal=True)
    else:
        st.info("No data yet. Run the simulation above!")
