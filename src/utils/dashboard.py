import numpy as np
import base64
import seaborn as sns 
import streamlit as st
import os
import matplotlib.pyplot as plt
import pandas as pd
import src.utils.css as css


def show_sales_chart():
        
        st.subheader("Sales Data Charts")
        if not os.path.exists("data/sales_data.csv"):
            st.error("Your file does not exist")
            return
        df = pd.read_csv("data/sales_data.csv")
        st.dataframe(df)
        st.bar_chart(data=df, x="City", y="Total")
        data = {'Name': ['Omkar', 'Lakshman', 'Ajay'], 'Sales': [24, 25, 23], 'Location': ['Nellore', 'Chennai', 'Hyderabad']}
        df_chart = pd.DataFrame(data)
        st.title("Sales")
        fig, ax = plt.subplots()
        ax.bar(df_chart["Name"], df_chart["Sales"], color="blue")
        ax.set_title("Sales by Person")
        ax.set_xlabel("Name")
        ax.set_ylabel("Sales")
        st.pyplot(fig)

def show_budgeting_section():
        
        st.write("📋 This is the budgeting area.")
        budget_data = {"Department": ["Sales", "Marketing", "HR"], "Budget": [150000, 100000, 80000]}
        df_budget = pd.DataFrame(budget_data)
        st.dataframe(df_budget)
        st.bar_chart(df_budget.set_index("Department"))
def load_purchase_data(file_path="data/lpo_data.csv"):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Purchase file not found: {file_path}")

        # Try reading as CSV first
        try:
            df = pd.read_csv(file_path)
        except Exception:
            # If CSV read fails, try tab-delimited
            df = pd.read_csv(file_path, sep="\t")

        # If only 1 column, maybe it's tab or space separated
        if len(df.columns) == 1:
            # Try again with tab separation
            try:
                df = pd.read_csv(file_path, sep="\t")
            except Exception:
                # If still not right, try whitespace separation
                df = pd.read_csv(file_path, delim_whitespace=True)

        # Clean column names: strip spaces, remove special chars
        df.columns = df.columns.str.strip()
        
        
        # Check if 'Project' column exists
        if 'Project' not in df.columns:
            raise KeyError(f"'Project' column not found after cleanup. Found columns: {df.columns.tolist()}")

        return df

def lpo_data():
        st.title("📊 Purchase Dashboard")

        df =load_purchase_data()

        # Create a proper Date column from Year + Month
        df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01")

        # Sidebar filters
        projects = st.multiselect(
            "Select Projects",
            options=sorted(df["Project"].unique()),
            default=[],
            placeholder="Choose project(s)..."
        )

        view_mode = st.radio(
            "View Mode",
            options=["Yearly", "Monthly"],
            index=0,
            horizontal=True,
            key="radio"
        )

        # Only move forward if projects are selected
        if not projects:
            st.info("👆 Please select at least one project to view data.")
            return

        # Apply project filter
        df_filtered = df[df["Project"].isin(projects)]

        if df_filtered.empty:
            st.warning("No data available for the selected project(s).")
            return

        if view_mode == "Yearly":
            df_grouped = df_filtered.groupby("Year", as_index=False)["Amount"].sum()
            fig, ax = plt.subplots()
            ax.bar(df_grouped["Year"].astype(str), df_grouped["Amount"])
            ax.set_title("Yearly Purchase Amount")
            ax.set_xlabel("Year")
            ax.set_ylabel("Amount")
            st.pyplot(fig)

        elif view_mode == "Monthly":
            # Don’t auto-show until a year is picked
            selected_year = st.selectbox(
                "Select Year", 
                sorted(df_filtered["Year"].unique()),
                index=None,
                placeholder="Choose a year..."
            )

            if not selected_year:
                st.info("👆 Please select a year to see monthly details.")
                return

            df_year = df_filtered[df_filtered["Year"] == selected_year]
            df_grouped = df_year.groupby("Month", as_index=False)["Amount"].sum()
            fig, ax = plt.subplots()
            ax.bar(df_grouped["Month"].astype(str), df_grouped["Amount"])
            ax.set_title(f"Monthly Purchase Amount - {selected_year}")
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount")
            st.pyplot(fig)
def GRN():
        st.subheader("GOOD RECIEVE NOTE DATA")
        if not os.path.exists("data/grn_data.csv"):
            raise FileNotFoundError(f"Purchase file not found: {"data/grn_data.csv"}")

        # Try reading as CSV first
        try:
            df = pd.read_csv("data/grn_data.csv")
        except Exception:
            # If CSV read fails, try tab-delimited
            df = pd.read_csv("data/grn_data.csv", sep="\t")

        # If only 1 column, maybe it's tab or space separated
        if len(df.columns) == 1:
            # Try again with tab separation
            try:
                df = pd.read_csv("data/grn_data.csv", sep="\t")
            except Exception:
                # If still not right, try whitespace separation
                df = pd.read_csv("data/grn_data.csv", delim_whitespace=True)

        # Clean column names: strip spaces, remove special chars
        df.columns = df.columns.str.strip()
        
        # Check if 'Project' column exists
        if 'Project' not in df.columns:
            raise KeyError(f"'Project' column not found after cleanup. Found columns: {df.columns.tolist()}")

        df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01")

        # Sidebar filters
        projects = st.multiselect(
            "Select Projects",
            options=sorted(df["Project"].unique()),
            default=[]
        )

        view_mode = st.radio(
            "View Mode",
            options=["Yearly", "Monthly"],
            index=0,
            horizontal=True
        )

        # Apply project filter
        df_filtered = df[df["Project"].isin(projects)]

        if view_mode == "Yearly":
            df_grouped = df_filtered.groupby("Year", as_index=False)["Amount"].sum()
            fig, ax = plt.subplots()
            ax.bar(df_grouped["Year"].astype(str), df_grouped["Amount"])
            ax.set_title("Yearly Purchase Amount")
            ax.set_xlabel("Year")
            ax.set_ylabel("Amount")
            st.pyplot(fig)

        elif view_mode == "Monthly":
            # Let user choose year for monthly view
            selected_year = st.selectbox("Select Year", sorted(df_filtered["Year"].unique()))
            df_year = df_filtered[df_filtered["Year"] == selected_year]
            df_grouped = df_year.groupby("Month", as_index=False)["Amount"].sum()
            fig, ax = plt.subplots()
            ax.bar(df_grouped["Month"].astype(str), df_grouped["Amount"])
            ax.set_title(f"Monthly Purchase Amount - {selected_year}")
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount")
            st.pyplot(fig)
        
def lpo_grn_gross_amount():
        csv_path = "data/lpo_grn.csv"

        st.title("LPO vs GRN – By Project")


        # Load the CSV with utf-8-sig encoding to handle BOM if present
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
        except Exception as e:
            st.error(f"Error loading CSV with pandas: {e}")
            return
        # Strip whitespace from column headers
        df.columns = df.columns.str.strip()
       

        # Check if 'Project' column exists
        if 'Project' not in df.columns:
            st.error("Required column 'Project' not found in data.")
            return

        projects = df['Project'].unique().tolist()
        selected_projects = st.multiselect("Select Projects (max 15)", projects, default=[])

        if len(selected_projects) > 15:
            st.warning("Please select 15 or fewer projects.")
            st.stop()

        if not selected_projects:
            st.info("Please select at least one project.")
            st.stop()

        filtered_df = df[df['Project'].isin(selected_projects)].reset_index(drop=True)

        x = np.arange(len(filtered_df))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 7))
        ax.bar(x - width/2, filtered_df['PO_Value'], width, label='LPO Value')
        ax.bar(x + width/2, filtered_df['GRN_Value'], width, label='GRN Value')

        ax.set_xticks(x)
        ax.set_xticklabels(filtered_df['Project'], rotation=45, ha='right')
        ax.set_xlabel("Project Codes")
        ax.set_ylabel("Value in OMR")
        ax.set_title("LPO vs GRN Values by Project")
        ax.legend()

        plt.tight_layout()
        st.pyplot(fig)
def lpo_grn_net_values():
            data = pd.read_csv("data/lpo_grn_net_value.csv")
            data.columns = data.columns.str.strip()

            # Add Net_Cost column
            data['Net_Cost'] = data['PO_Net Value'] + data['GRN_Net Value']

            projects = sorted(data['Project'].unique().tolist())
            selected_projects = st.multiselect(
        "Select Projects (max 15)", 
        projects, 
        default=[], 
        key="lpo_grn_projects"    # 👈 unique key
    )
            if len(selected_projects) > 15:
                st.warning("⚠️ Please select 15 or fewer projects.")
                return

            if not selected_projects:
                st.info("👆 Please select at least one project to view data.")
                return

            # Filter data
            filtered_df = data[data['Project'].isin(selected_projects)]

            # Aggregate net cost
            net_cost_by_project = filtered_df.groupby('Project')['Net_Cost'].sum()

            # If only 1 project, pie makes no sense → use bar
            if len(net_cost_by_project) == 1:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.bar(net_cost_by_project.index, net_cost_by_project.values)
                ax.set_title("Net Cost (OMR) by Project")
                ax.set_ylabel("Net Cost")
                st.pyplot(fig)
                return

            # Pie chart
            fig, ax = plt.subplots(figsize=(8, 8))
            wedges, texts, autotexts = ax.pie(
                net_cost_by_project, 
                labels=net_cost_by_project.index, 
                autopct='%1.1f%%', 
                startangle=90
            )

            # Improve text size & readability
            for t in texts:
                t.set_size(10)
            for t in autotexts:
                t.set_size(9)

            ax.set_title("Net Cost (OMR) by Project", fontsize=14)
            st.pyplot(fig)