import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import base64

@st.cache_data
def load_file_data(file):
    return pd.read_csv(file)

def plot_multiple_files(dataframes, columns, colors):
    fig = go.Figure()

    # Create y-axes for each file if needed
    for i, (df, col) in enumerate(zip(dataframes, columns)):
        if col not in df.columns:
            st.error(f"Column '{col}' not found in DataFrame {i+1}. Available columns: {list(df.columns)}")
            return
        
        # Dynamically create y-axes for different scales
        y_axis_name = f'y{i+1}'
        y_axis_title = f'Value - Data from {col}'
        
        fig.add_trace(go.Scatter(
            x=df['Timestamp'], 
            y=df[col],
            mode='lines', 
            name=f'Data from {col}', 
            line=dict(color=colors[i % len(colors)]),
            yaxis=y_axis_name
        ))

        # Add y-axis configuration
        if i == 0:
            fig.update_layout(yaxis=dict(title=y_axis_title))
        else:
            fig.update_layout(**{
                f'yaxis{i+1}': dict(
                    title=y_axis_title,
                    overlaying='y',  # Overlay on the first y-axis
                    side='right' if i % 2 == 1 else 'left',  # Alternate sides
                    position=0.1 * i  # Adjust position slightly to avoid overlap
                )
            })

    # Update layout
    fig.update_layout(
        title='Comparison of Data from Multiple Files',
        xaxis_title='Timestamp'
    )

    st.plotly_chart(fig)

    # Provide option to download the Plotly HTML file
    html = fig.to_html()
    b64 = base64.b64encode(html.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:text/html;base64,{b64}" download="plotly_figure.html">Download Plotly HTML File</a>'
    st.markdown(href, unsafe_allow_html=True)

# Allow users to upload multiple files
uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    dataframes = [load_file_data(file) for file in uploaded_files]

    # Convert 'Timestamp' column to datetime for each dataframe
    for df in dataframes:
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        else:
            st.error(f"'Timestamp' column not found in DataFrame. Available columns: {list(df.columns)}")
            st.stop()

    # Display dropdown to select columns for plotting
    columns = []
    for i, df in enumerate(dataframes):
        selected_column = st.selectbox(f"Select a column to plot from File {i+1}:", df.columns)
        columns.append(selected_column)

    # Define colors for the plots
    colors = ['blue', 'red', 'green', 'orange', 'purple']  # Add more colors if needed

    plot_multiple_files(dataframes, columns, colors)

else:
    st.write("Please upload at least one CSV file.")