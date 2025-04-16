
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from io import BytesIO

st.set_page_config(page_title="Excel to Dashboard", layout="wide")

# Dark mode toggle
theme_mode = st.sidebar.radio("🌓 Theme Mode", ["Light", "Dark"])

dark_mode = theme_mode == "Dark"

# CSS theme styling
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&display=swap');
    html, body, .stApp {{
        font-family: 'Inter', sans-serif;
        background-color: {'#181818' if dark_mode else '#F5F6F8'};
        color: {'#FFFFFF' if dark_mode else '#000000'} !important;
    }}
    label, h1, h2, h3, h4, h5, h6, p, span {{
        color: {'#FFFFFF' if dark_mode else '#000000'} !important;
    }}
    .stRadio > div > label[data-selected="true"] {{
        background-color: #1a73e8;
        color: white !important;
        border-color: #1a73e8;
    }}
    .stRadio > div > label {{
        color: white !important;
        background-color: #6c757d;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.4em 0.8em;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("📊 Excel to Dashboard")
st.write("Upload your Excel file, filter, analyze and export your charts with insight.")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [str(col).strip() for col in df.columns]

    for col in df.columns:
        df[col] = df[col].astype(str).str.replace("%", "").str.replace(",", ".")
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass

    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = [col for col in df.columns if col not in num_cols]

    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("📌 Select X Axis", cat_cols)
    with col2:
        y_axis = st.selectbox("📈 Select Y Axis", num_cols)

    # X-axis filtreleme
    selected_vals = st.multiselect(f"Filter values in {x_axis}", df[x_axis].unique().tolist(), default=df[x_axis].unique().tolist())
    filtered_df = df[df[x_axis].isin(selected_vals)][[x_axis, y_axis]].dropna()

    chart_type = st.radio("📊 Select Chart Type", ["Bar", "Line", "Area", "Pie", "Scatter"], horizontal=True)

    fig = None
    if chart_type == "Bar":
        fig = px.bar(filtered_df, x=x_axis, y=y_axis, title="Bar Chart", text_auto=True)
    elif chart_type == "Line":
        fig = px.line(filtered_df, x=x_axis, y=y_axis, title="Line Chart")
    elif chart_type == "Area":
        fig = px.area(filtered_df, x=x_axis, y=y_axis, title="Area Chart")
    elif chart_type == "Pie":
        fig = px.pie(filtered_df, names=x_axis, values=y_axis, title="Pie Chart")
    else:
        fig = px.scatter(filtered_df, x=x_axis, y=y_axis, title="Scatter Chart", color=x_axis)

    st.plotly_chart(fig, use_container_width=True)

    # 🎯 Export Button
    buffer = BytesIO()
    pio.write_image(fig, buffer, format='png')
    st.download_button(label="📥 Download Chart as PNG", data=buffer, file_name="chart_export.png", mime="image/png")

    # 🔍 Detaylı Analiz Kutusu
    st.markdown("### 📌 Insight Summary")
    max_val = filtered_df[y_axis].max()
    min_val = filtered_df[y_axis].min()
    avg_val = filtered_df[y_axis].mean()

    best = filtered_df[filtered_df[y_axis] == max_val][x_axis].values[0]
    worst = filtered_df[filtered_df[y_axis] == min_val][x_axis].values[0]

    st.markdown(f"""
    - 🟢 **Highest {y_axis}**: {max_val:.2f} ({best})  
    - 🔴 **Lowest {y_axis}**: {min_val:.2f} ({worst})  
    - 🟡 **Average {y_axis}**: {avg_val:.2f}
    """)
