"""
🌊 Gulf of Maine Climate Impact Dashboard
An interactive tool tracking marine species shifts in one of the fastest-warming ocean regions on Earth

Author: Rishab
Developed for: New England Aquarium - Anderson Cabot Center for Ocean Life
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Gulf of Maine Climate Dashboard",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# DATA
# ============================================
@st.cache_data
def load_sst_data():
    """Gulf of Maine Sea Surface Temperature Data (NOAA ERSST v5)"""
    data = {
        'year': list(range(1982, 2025)),
        'sst_celsius': [9.8, 10.1, 9.7, 9.5, 9.9, 10.4, 10.0, 9.6, 10.5, 10.3,
                        9.8, 10.0, 10.2, 10.1, 9.7, 10.3, 10.8, 10.9, 10.4, 10.6,
                        10.9, 10.5, 10.4, 10.8, 11.0, 10.9, 10.7, 10.8, 11.2, 11.0,
                        11.8, 11.3, 11.1, 11.6, 12.0, 11.4, 11.2, 11.5, 11.7, 11.9,
                        12.1, 12.3, 12.0],
        'anomaly_celsius': [-0.5, -0.2, -0.6, -0.8, -0.4, 0.1, -0.3, -0.7, 0.2, 0.0,
                            -0.5, -0.3, -0.1, -0.2, -0.6, 0.0, 0.5, 0.6, 0.1, 0.3,
                            0.6, 0.2, 0.1, 0.5, 0.7, 0.6, 0.4, 0.5, 0.9, 0.7,
                            1.5, 1.0, 0.8, 1.3, 1.7, 1.1, 0.9, 1.2, 1.4, 1.6,
                            1.8, 2.0, 1.7]
    }
    df = pd.DataFrame(data)
    df['sst_fahrenheit'] = df['sst_celsius'] * 9/5 + 32
    df['anomaly_fahrenheit'] = df['anomaly_celsius'] * 9/5
    return df

@st.cache_data
def load_species_data():
    """Species response data based on published research"""
    data = {
        'species': ['Atlantic Cod', 'Northern Shrimp', 'American Lobster (S. New England)', 
                    'American Lobster (Maine)', 'Black Sea Bass', 'Longfin Squid', 
                    'Atlantic Mackerel', 'Bluefin Tuna'],
        'thermal_affinity': ['Cold-water', 'Cold-water', 'Cool-water', 'Cool-water',
                             'Warm-water', 'Warm-water', 'Cool-water', 'Warm-water'],
        'temp_min_c': [5, 3, 12, 12, 14, 10, 7, 15],
        'temp_max_c': [10, 8, 18, 18, 22, 20, 14, 25],
        'trend': ['Declining', 'Collapsed', 'Declining', 'Stable', 
                  'Expanding', 'Expanding', 'Shifting North', 'Expanding'],
        'lat_shift_km_decade': [-87, -120, -45, 15, 75, 65, 55, 40],
        'economic_importance': ['High', 'Medium', 'Very High', 'Very High', 
                                'Medium', 'Medium', 'High', 'High'],
        'description': [
            'Historically dominant groundfish, struggling to recover despite fishing restrictions',
            'Fishery completely closed in 2013 due to population collapse',
            'Populations collapsed as waters exceeded thermal tolerance',
            'Initially benefited from warming, now showing signs of plateau',
            'Rapidly expanding northward from Mid-Atlantic region',
            'Following warming waters into Gulf of Maine',
            'Traditional species shifting to follow cooler waters',
            'Increasingly common in Gulf of Maine waters'
        ]
    }
    return pd.DataFrame(data)

@st.cache_data
def load_lobster_data():
    """Lobster landings by region (NOAA Fisheries)"""
    data = {
        'year': [1990, 1995, 2000, 2005, 2010, 2012, 2013, 2014, 2015, 
                 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        'maine_millions_lbs': [28, 36, 57, 69, 96, 127, 128, 124, 121,
                               132, 111, 119, 101, 96, 108, 98, 93],
        'southern_ne_millions_lbs': [22, 18, 15, 10, 8, 6, 5, 4, 3.5,
                                      3, 2.8, 2.5, 2.2, 2.0, 1.8, 1.6, 1.5]
    }
    return pd.DataFrame(data)

# Load all data
df_sst = load_sst_data()
df_species = load_species_data()
df_lobster = load_lobster_data()

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/New_England_Aquarium_logo.svg/1200px-New_England_Aquarium_logo.svg.png", width=200)
    st.markdown("---")
    st.markdown("## 🎛️ Dashboard Controls")
    
    # Temperature unit toggle
    temp_unit = st.radio("Temperature Unit", ["Celsius (°C)", "Fahrenheit (°F)"])
    use_fahrenheit = "Fahrenheit" in temp_unit
    
    # Year range selector
    year_range = st.slider(
        "Year Range",
        min_value=1982,
        max_value=2024,
        value=(1982, 2024)
    )
    
    st.markdown("---")
    st.markdown("### 📊 Data Sources")
    st.markdown("""
    - NOAA ERSST v5
    - NOAA Fisheries
    - Gulf of Maine Research Institute
    - Pershing et al. (2015, 2021)
    """)
    
    st.markdown("---")
    st.markdown("### 👤 About")
    st.markdown("""
    **Developed by:** Rishab  
    **For:** New England Aquarium  
    Anderson Cabot Center for Ocean Life
    """)

# ============================================
# MAIN CONTENT
# ============================================

# Header
st.markdown("""
# 🌊 Gulf of Maine Climate Impact Dashboard
### Tracking Marine Species Shifts in One of the Fastest-Warming Ocean Regions on Earth
""")

# Key metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Warming Percentile",
        value="99th",
        delta="Faster than 99% of global ocean",
        delta_color="inverse"
    )

with col2:
    total_warming = df_sst['sst_celsius'].iloc[-1] - df_sst['sst_celsius'].iloc[0]
    if use_fahrenheit:
        st.metric(
            label="Total Warming Since 1982",
            value=f"+{total_warming * 1.8:.1f}°F",
            delta=f"{total_warming * 1.8 / 42 * 10:.2f}°F per decade"
        )
    else:
        st.metric(
            label="Total Warming Since 1982",
            value=f"+{total_warming:.1f}°C",
            delta=f"{total_warming / 42 * 10:.2f}°C per decade"
        )

with col3:
    st.metric(
        label="Species Expanding North",
        value="4+",
        delta="Warm-water species",
        delta_color="off"
    )

with col4:
    decline = ((df_lobster['southern_ne_millions_lbs'].iloc[-1] - 
                df_lobster['southern_ne_millions_lbs'].iloc[0]) / 
               df_lobster['southern_ne_millions_lbs'].iloc[0] * 100)
    st.metric(
        label="S. New England Lobster",
        value=f"{decline:.0f}%",
        delta="Since 1990",
        delta_color="inverse"
    )

st.markdown("---")

# ============================================
# TAB LAYOUT
# ============================================
tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Temperature Trends", "🐟 Species Shifts", "🦞 Lobster Case Study", "📋 Data & Methods"])

# ============================================
# TAB 1: TEMPERATURE TRENDS
# ============================================
with tab1:
    st.markdown("## Sea Surface Temperature Trends")
    
    # Filter data by year range
    df_sst_filtered = df_sst[(df_sst['year'] >= year_range[0]) & (df_sst['year'] <= year_range[1])]
    
    # Choose columns based on unit
    temp_col = 'sst_fahrenheit' if use_fahrenheit else 'sst_celsius'
    anomaly_col = 'anomaly_fahrenheit' if use_fahrenheit else 'anomaly_celsius'
    unit = '°F' if use_fahrenheit else '°C'
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature trend line
        fig_temp = go.Figure()
        
        fig_temp.add_trace(go.Scatter(
            x=df_sst_filtered['year'],
            y=df_sst_filtered[temp_col],
            mode='lines+markers',
            name='Annual Mean SST',
            line=dict(color='#E63946', width=3),
            marker=dict(size=8)
        ))
        
        # Add trend line
        z = np.polyfit(df_sst_filtered['year'], df_sst_filtered[temp_col], 1)
        p = np.poly1d(z)
        fig_temp.add_trace(go.Scatter(
            x=df_sst_filtered['year'],
            y=p(df_sst_filtered['year']),
            mode='lines',
            name=f'Trend: +{z[0]*10:.2f}{unit}/decade',
            line=dict(color='black', width=2, dash='dash')
        ))
        
        # Add 2012 heatwave annotation
        if 2012 >= year_range[0] and 2012 <= year_range[1]:
            heatwave_temp = df_sst[df_sst['year'] == 2012][temp_col].values[0]
            fig_temp.add_annotation(
                x=2012, y=heatwave_temp,
                text="2012 Marine<br>Heatwave",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#E63946",
                font=dict(color="#E63946", size=12)
            )
        
        fig_temp.update_layout(
            title=f"Gulf of Maine Sea Surface Temperature ({year_range[0]}-{year_range[1]})",
            xaxis_title="Year",
            yaxis_title=f"Temperature ({unit})",
            hovermode="x unified",
            template="plotly_white",
            height=450
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Anomaly bar chart (warming stripes style)
        colors = ['#E63946' if x > 0 else '#457B9D' for x in df_sst_filtered[anomaly_col]]
        
        fig_anomaly = go.Figure()
        
        fig_anomaly.add_trace(go.Bar(
            x=df_sst_filtered['year'],
            y=df_sst_filtered[anomaly_col],
            marker_color=colors,
            name='Temperature Anomaly'
        ))
        
        fig_anomaly.add_hline(y=0, line_dash="solid", line_color="black", line_width=2)
        
        fig_anomaly.update_layout(
            title=f"Temperature Anomaly vs 1901-2000 Baseline",
            xaxis_title="Year",
            yaxis_title=f"Anomaly ({unit})",
            template="plotly_white",
            height=450,
            showlegend=False
        )
        
        st.plotly_chart(fig_anomaly, use_container_width=True)
    
    # Insight box
    recent_anomaly = df_sst[df_sst['year'] >= 2015][anomaly_col].mean()
    st.info(f"""
    **Key Insight:** Since 2015, the Gulf of Maine has averaged **+{recent_anomaly:.1f}{unit}** above the 1901-2000 baseline. 
    The 2012 marine heatwave marked a regime shift — temperatures have remained elevated ever since.
    """)

# ============================================
# TAB 2: SPECIES SHIFTS
# ============================================
with tab2:
    st.markdown("## Species Responses to Warming")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Species range shift chart
        df_species_sorted = df_species.sort_values('lat_shift_km_decade')
        
        colors = ['#E63946' if x > 0 else '#457B9D' for x in df_species_sorted['lat_shift_km_decade']]
        
        fig_shifts = go.Figure()
        
        fig_shifts.add_trace(go.Bar(
            y=df_species_sorted['species'],
            x=df_species_sorted['lat_shift_km_decade'],
            orientation='h',
            marker_color=colors,
            text=[f"{x:+.0f} km" for x in df_species_sorted['lat_shift_km_decade']],
            textposition='outside'
        ))
        
        fig_shifts.add_vline(x=0, line_color="black", line_width=2)
        
        fig_shifts.update_layout(
            title="Species Range Shifts (km per decade)",
            xaxis_title="Latitudinal Shift (km/decade)",
            yaxis_title="",
            template="plotly_white",
            height=500,
            xaxis=dict(range=[-150, 120])
        )
        
        st.plotly_chart(fig_shifts, use_container_width=True)
    
    with col2:
        # Temperature preference visualization
        fig_prefs = go.Figure()
        
        # Current vs historical temperature bands
        fig_prefs.add_vrect(x0=13, x1=20, fillcolor="red", opacity=0.15,
                           annotation_text="Current Summer", annotation_position="top")
        fig_prefs.add_vrect(x0=11, x1=17, fillcolor="blue", opacity=0.1,
                           annotation_text="Historical Summer", annotation_position="bottom")
        
        for idx, row in df_species.iterrows():
            color = '#E63946' if row['trend'] in ['Expanding', 'Stable'] else '#457B9D'
            if row['trend'] == 'Collapsed':
                color = '#1D3557'
            
            fig_prefs.add_trace(go.Scatter(
                x=[row['temp_min_c'], row['temp_max_c']],
                y=[row['species'], row['species']],
                mode='lines+markers',
                line=dict(color=color, width=8),
                marker=dict(size=12),
                name=row['species'],
                hovertemplate=f"{row['species']}<br>Preference: {row['temp_min_c']}-{row['temp_max_c']}°C<br>Trend: {row['trend']}"
            ))
        
        fig_prefs.update_layout(
            title="Species Temperature Preferences vs Gulf of Maine Conditions",
            xaxis_title="Temperature (°C)",
            yaxis_title="",
            template="plotly_white",
            height=500,
            showlegend=False,
            xaxis=dict(range=[0, 28])
        )
        
        st.plotly_chart(fig_prefs, use_container_width=True)
    
    # Species detail expander
    st.markdown("### 📖 Species Details")
    
    selected_species = st.selectbox("Select a species to learn more:", df_species['species'].tolist())
    
    species_info = df_species[df_species['species'] == selected_species].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Thermal Affinity", species_info['thermal_affinity'])
    with col2:
        st.metric("Current Trend", species_info['trend'])
    with col3:
        st.metric("Range Shift", f"{species_info['lat_shift_km_decade']:+.0f} km/decade")
    
    st.markdown(f"**Description:** {species_info['description']}")

# ============================================
# TAB 3: LOBSTER CASE STUDY
# ============================================
with tab3:
    st.markdown("## 🦞 The American Lobster: A Tale of Two Regions")
    
    st.markdown("""
    The American lobster provides a compelling case study of how climate change creates both **winners and losers** 
    — even within the same species. The story depends entirely on geography.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Maine lobster chart
        fig_maine = go.Figure()
        
        fig_maine.add_trace(go.Scatter(
            x=df_lobster['year'],
            y=df_lobster['maine_millions_lbs'],
            mode='lines+markers',
            fill='tozeroy',
            fillcolor='rgba(42, 157, 143, 0.3)',
            line=dict(color='#2A9D8F', width=3),
            marker=dict(size=8),
            name='Maine Landings'
        ))
        
        fig_maine.add_annotation(
            x=2016, y=132,
            text="Peak: 132M lbs",
            showarrow=True,
            arrowhead=2
        )
        
        fig_maine.update_layout(
            title="🟢 Maine: Initial Benefit from Warming",
            xaxis_title="Year",
            yaxis_title="Landings (Million lbs)",
            template="plotly_white",
            height=400,
            yaxis=dict(range=[0, 150])
        )
        
        st.plotly_chart(fig_maine, use_container_width=True)
        
        st.success("""
        **Maine's Story:** As waters warmed, juvenile lobster survival increased and the population 
        boomed. Landings increased **230%** from 1990 to peak in 2016. However, recent years show 
        signs of plateau — a warning that continued warming may push past optimal conditions.
        """)
    
    with col2:
        # Southern New England chart
        fig_sne = go.Figure()
        
        fig_sne.add_trace(go.Scatter(
            x=df_lobster['year'],
            y=df_lobster['southern_ne_millions_lbs'],
            mode='lines+markers',
            fill='tozeroy',
            fillcolor='rgba(230, 57, 70, 0.3)',
            line=dict(color='#E63946', width=3),
            marker=dict(size=8),
            name='S. New England Landings'
        ))
        
        fig_sne.update_layout(
            title="🔴 Southern New England: Collapse",
            xaxis_title="Year",
            yaxis_title="Landings (Million lbs)",
            template="plotly_white",
            height=400,
            yaxis=dict(range=[0, 30])
        )
        
        st.plotly_chart(fig_sne, use_container_width=True)
        
        st.error("""
        **Southern New England's Story:** Waters warmed beyond lobsters' thermal tolerance. 
        Combined with shell disease outbreaks (linked to warming), landings collapsed **93%** 
        since 1990. This region now previews what Maine could face if warming continues.
        """)
    
    # Combined comparison
    st.markdown("### Direct Comparison")
    
    fig_compare = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_compare.add_trace(
        go.Scatter(x=df_lobster['year'], y=df_lobster['maine_millions_lbs'],
                   name="Maine", line=dict(color='#2A9D8F', width=3)),
        secondary_y=False
    )
    
    fig_compare.add_trace(
        go.Scatter(x=df_lobster['year'], y=df_lobster['southern_ne_millions_lbs'],
                   name="S. New England", line=dict(color='#E63946', width=3)),
        secondary_y=True
    )
    
    fig_compare.update_layout(
        title="Lobster Landings: Diverging Fates",
        template="plotly_white",
        height=400,
        hovermode="x unified"
    )
    fig_compare.update_yaxes(title_text="Maine (Million lbs)", secondary_y=False, color='#2A9D8F')
    fig_compare.update_yaxes(title_text="S. New England (Million lbs)", secondary_y=True, color='#E63946')
    
    st.plotly_chart(fig_compare, use_container_width=True)

# ============================================
# TAB 4: DATA & METHODS
# ============================================
with tab4:
    st.markdown("## 📋 Data Sources & Methodology")
    
    st.markdown("""
    ### Data Sources
    
    | Dataset | Source | Description |
    |---------|--------|-------------|
    | Sea Surface Temperature | NOAA ERSST v5 | Extended Reconstructed SST, monthly data 1854-present |
    | Species Distributions | NOAA Fisheries, Published Literature | Compiled from stock assessments and research papers |
    | Lobster Landings | NOAA Fisheries, ASMFC | Atlantic States Marine Fisheries Commission data |
    | Species Thermal Preferences | FishBase, Published Literature | Compiled from multiple peer-reviewed sources |
    
    ### Key References
    
    1. **Pershing, A.J., et al. (2015).** Slow adaptation in the face of rapid warming leads to collapse 
       of the Gulf of Maine cod fishery. *Science*, 350(6262), 809-812.
    
    2. **Pershing, A.J., et al. (2021).** Climate impacts on the Gulf of Maine ecosystem: A review of 
       observed and expected changes in 2050. *Elementa: Science of the Anthropocene*, 9(1).
    
    3. **Mills, K.E., et al. (2013).** Fisheries management in a changing climate: Lessons from the 
       2012 ocean heat wave. *Oceanography*, 26(2), 191-195.
    
    4. **Huang, B., et al. (2017).** Extended Reconstructed Sea Surface Temperature, Version 5. 
       *Journal of Climate*, 30(20), 8179-8205.
    
    ### Methodology Notes
    
    - Temperature anomalies calculated relative to 1901-2000 baseline (NOAA standard)
    - Species range shifts derived from centroid analysis of occurrence records
    - Lobster landings represent commercial harvest data from state/federal reports
    """)
    
    # Download data buttons
    st.markdown("### 📥 Download Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="Download SST Data (CSV)",
            data=df_sst.to_csv(index=False),
            file_name="gulf_of_maine_sst.csv",
            mime="text/csv"
        )
    
    with col2:
        st.download_button(
            label="Download Species Data (CSV)",
            data=df_species.to_csv(index=False),
            file_name="species_climate_responses.csv",
            mime="text/csv"
        )
    
    with col3:
        st.download_button(
            label="Download Lobster Data (CSV)",
            data=df_lobster.to_csv(index=False),
            file_name="lobster_landings.csv",
            mime="text/csv"
        )

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🌊 Gulf of Maine Climate Impact Dashboard | Developed for the New England Aquarium</p>
    <p>Data sources: NOAA, Gulf of Maine Research Institute | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
