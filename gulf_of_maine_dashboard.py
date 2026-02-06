"""
Gulf of Maine Climate Impact Dashboard
An interactive research tool analyzing marine species redistribution
in response to accelerated ocean warming in the Northwest Atlantic

Author: Rishab
Developed for: New England Aquarium - Anderson Cabot Center for Ocean Life
Last Updated: February 2026

Data Sources:
    - NOAA ERSST v5 (Sea Surface Temperature)
    - NOAA Fisheries / Northeast Fisheries Science Center (Trawl Surveys)
    - Atlantic States Marine Fisheries Commission (Lobster Landings)
    - Gulf of Maine Research Institute (Ecosystem Indicators)
    - Published peer-reviewed literature (see Data & Methods tab)
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
    page_title="Gulf of Maine Climate Impact Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM STYLING
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1B3A4B;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4A6274;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }
    .section-description {
        font-size: 0.95rem;
        color: #3D5A6E;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .metric-context {
        font-size: 0.85rem;
        color: #5A7A8A;
        margin-top: -10px;
    }
    .insight-box {
        background-color: #F0F7FA;
        border-left: 4px solid #1B3A4B;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 4px 4px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATA: SEA SURFACE TEMPERATURE
# ============================================
@st.cache_data
def load_sst_data():
    """
    Gulf of Maine Sea Surface Temperature (NOAA ERSST v5).
    Annual mean SST and anomalies relative to the 1901-2000 baseline.
    Region: 42-44.5N, 66-70W (core Gulf of Maine).
    """
    data = {
        'year': list(range(1982, 2025)),
        'sst_celsius': [
            9.8, 10.1, 9.7, 9.5, 9.9, 10.4, 10.0, 9.6, 10.5, 10.3,
            9.8, 10.0, 10.2, 10.1, 9.7, 10.3, 10.8, 10.9, 10.4, 10.6,
            10.9, 10.5, 10.4, 10.8, 11.0, 10.9, 10.7, 10.8, 11.2, 11.0,
            11.8, 11.3, 11.1, 11.6, 12.0, 11.4, 11.2, 11.5, 11.7, 11.9,
            12.1, 12.3, 12.0
        ],
        'anomaly_celsius': [
            -0.5, -0.2, -0.6, -0.8, -0.4, 0.1, -0.3, -0.7, 0.2, 0.0,
            -0.5, -0.3, -0.1, -0.2, -0.6, 0.0, 0.5, 0.6, 0.1, 0.3,
            0.6, 0.2, 0.1, 0.5, 0.7, 0.6, 0.4, 0.5, 0.9, 0.7,
            1.5, 1.0, 0.8, 1.3, 1.7, 1.1, 0.9, 1.2, 1.4, 1.6,
            1.8, 2.0, 1.7
        ]
    }
    df = pd.DataFrame(data)
    df['sst_fahrenheit'] = df['sst_celsius'] * 9/5 + 32
    df['anomaly_fahrenheit'] = df['anomaly_celsius'] * 9/5

    # Compute decadal averages for context
    df['decade'] = (df['year'] // 10) * 10
    df['decade_label'] = df['decade'].astype(str) + 's'

    # Rolling 5-year average for smoothed trend
    df['sst_5yr_avg'] = df['sst_celsius'].rolling(window=5, center=True).mean()
    df['sst_5yr_avg_f'] = df['sst_5yr_avg'] * 9/5 + 32

    return df


# ============================================
# DATA: SPECIES RESPONSES (EXPANDED)
# ============================================
@st.cache_data
def load_species_data():
    """
    Species climate response data compiled from NOAA Northeast Fisheries Science
    Center bottom trawl surveys, published literature, and stock assessments.
    Range shift estimates derived from distribution centroid analysis.
    """
    data = {
        'species': [
            'Atlantic Cod', 'Northern Shrimp', 'American Lobster (S. New England)',
            'American Lobster (Maine)', 'Black Sea Bass', 'Longfin Squid',
            'Atlantic Mackerel', 'Bluefin Tuna', 'Summer Flounder',
            'Jonah Crab', 'Atlantic Herring', 'Calanus finmarchicus'
        ],
        'scientific_name': [
            'Gadus morhua', 'Pandalus borealis', 'Homarus americanus',
            'Homarus americanus', 'Centropristis striata', 'Doryteuthis pealeii',
            'Scomber scombrus', 'Thunnus thynnus', 'Paralichthys dentatus',
            'Cancer borealis', 'Clupea harengus', 'Calanus finmarchicus'
        ],
        'taxa_group': [
            'Groundfish', 'Invertebrate', 'Invertebrate', 'Invertebrate',
            'Reef Fish', 'Invertebrate', 'Pelagic Fish', 'Pelagic Fish',
            'Flatfish', 'Invertebrate', 'Pelagic Fish', 'Zooplankton'
        ],
        'thermal_affinity': [
            'Cold-water', 'Cold-water', 'Cool-water', 'Cool-water',
            'Warm-water', 'Warm-water', 'Cool-water', 'Warm-water',
            'Warm-water', 'Cool-water', 'Cold-water', 'Cold-water'
        ],
        'temp_min_c': [2, 0, 12, 12, 14, 10, 7, 15, 11, 5, 3, 0],
        'temp_max_c': [12, 8, 18, 18, 26, 22, 16, 25, 23, 16, 12, 12],
        'optimal_temp_c': [6, 4, 16, 16, 19, 15, 11, 20, 17, 10, 7, 5],
        'trend': [
            'Declining', 'Collapsed', 'Declining', 'Plateauing',
            'Expanding', 'Expanding', 'Shifting North', 'Expanding',
            'Expanding', 'Expanding', 'Declining', 'Declining'
        ],
        'lat_shift_km_decade': [-87, -120, -45, 15, 75, 65, 55, 40, 60, 30, -35, -50],
        'depth_shift_m_decade': [10, 15, 5, 2, -8, -5, 3, -3, -6, -4, 8, 12],
        'population_change_pct': [-78, -95, -93, 15, 350, 200, -40, 120, 250, 180, -55, -70],
        'economic_importance': [
            'High', 'Medium', 'Very High', 'Very High',
            'Medium', 'Medium', 'High', 'High',
            'High', 'Medium', 'Very High', 'Ecological'
        ],
        'economic_value_millions': [15, 2, 8, 725, 45, 30, 12, 50, 65, 35, 55, 0],
        'description': [
            'Once the economic foundation of New England fisheries, Gulf of Maine cod stocks '
            'have declined approximately 78% since the 1980s despite severe fishing restrictions. '
            'Warming waters reduce juvenile survival rates and shift prey availability, preventing '
            'recovery even under reduced fishing pressure (Pershing et al., 2015).',

            'The Gulf of Maine northern shrimp fishery was completely closed in 2013 after '
            'population collapse driven by thermal stress. Shrimp require cold bottom water '
            '(< 8C) for survival, and sustained warming has rendered the southern Gulf of Maine '
            'inhospitable for this species.',

            'Southern New England lobster populations have declined 93% since 1990 as summer '
            'bottom temperatures routinely exceed the species thermal stress threshold of 20C. '
            'Epizootic shell disease, strongly correlated with warmer temperatures, has '
            'compounded mortality in this region.',

            'Maine lobster landings surged 230% from 1990-2016 as moderate warming initially '
            'improved juvenile survival rates and accelerated growth. However, landings have '
            'plateaued and shown a downward trend since 2016, suggesting the population may be '
            'approaching its thermal optimum ceiling in the warming Gulf.',

            'Black sea bass have expanded their range northward by approximately 75 km per decade, '
            'establishing year-round populations in areas where they were previously rare seasonal '
            'visitors. First recorded in Maine trawl surveys in significant numbers after 2010.',

            'Longfin squid abundance in the Gulf of Maine has increased substantially as warming '
            'waters expand suitable habitat northward. This species is a key prey item for many '
            'marine predators and its redistribution has cascading food web implications.',

            'Atlantic mackerel, historically abundant throughout the Gulf of Maine, have shifted '
            'their center of distribution approximately 55 km northward per decade. Spawning timing '
            'has also shifted earlier in the season in response to warming.',

            'Bluefin tuna presence in the Gulf of Maine has increased markedly, with the species '
            'following northward-shifting forage fish populations. Commercial and recreational '
            'harvest in Maine waters has reached historic levels in recent years.',

            'Summer flounder have expanded northward into the Gulf of Maine from their historical '
            'range centered on the Mid-Atlantic Bight. This species has become increasingly common '
            'in Massachusetts and New Hampshire waters since the early 2000s.',

            'Jonah crab landings have increased 180% in New England waters as this cool-water '
            'species benefits from moderate warming. Some fishers have transitioned from declining '
            'lobster fisheries to Jonah crab as an economic adaptation.',

            'Atlantic herring, a critical forage species supporting marine mammals, seabirds, and '
            'predatory fish, have shown declining biomass in the Gulf of Maine. Reduced herring '
            'availability has been linked to poor foraging success in Atlantic puffin colonies.',

            'This copepod is the dominant zooplankton in the Gulf of Maine food web, serving as '
            'the primary energy link between phytoplankton and higher trophic levels. Its abundance '
            'has declined approximately 70% as warming waters favor smaller, less energy-rich '
            'copepod species (e.g., Centropages typicus).'
        ]
    }
    return pd.DataFrame(data)


# ============================================
# DATA: SPECIES SPATIAL DISTRIBUTIONS (MAP)
# ============================================
@st.cache_data
def load_spatial_data():
    """
    Historical and current distribution centroids and range boundaries for
    Gulf of Maine species. Centroids derived from NOAA NEFSC bottom trawl
    survey biomass-weighted calculations. Historical period = 1980s-1990s
    baseline; Current period = 2015-2024. Includes seasonal hotspot locations.
    """
    records = [
        # Atlantic Cod
        {
            'species': 'Atlantic Cod', 'scientific_name': 'Gadus morhua',
            'thermal_affinity': 'Cold-water', 'trend': 'Declining',
            'hist_centroid_lat': 42.0, 'hist_centroid_lon': -68.5,
            'curr_centroid_lat': 43.2, 'curr_centroid_lon': -67.8,
            'hist_range_south': 40.0, 'hist_range_north': 44.5,
            'curr_range_south': 41.5, 'curr_range_north': 45.5,
            'hotspot_1_name': 'Georges Bank (Historical)',
            'hotspot_1_lat': 41.5, 'hotspot_1_lon': -67.5,
            'hotspot_2_name': 'Eastern Gulf of Maine (Current)',
            'hotspot_2_lat': 43.8, 'hotspot_2_lon': -67.0,
            'shift_km': 140, 'shift_direction': 'NNE',
            'map_notes': 'Center of biomass has shifted ~140 km northeast over 3 decades. '
                         'Cod have largely vacated the western Gulf of Maine and southern '
                         'Georges Bank, concentrating in deeper, cooler eastern waters.'
        },
        # Northern Shrimp
        {
            'species': 'Northern Shrimp', 'scientific_name': 'Pandalus borealis',
            'thermal_affinity': 'Cold-water', 'trend': 'Collapsed',
            'hist_centroid_lat': 43.0, 'hist_centroid_lon': -69.0,
            'curr_centroid_lat': 44.5, 'curr_centroid_lon': -67.5,
            'hist_range_south': 41.5, 'hist_range_north': 45.0,
            'curr_range_south': 43.5, 'curr_range_north': 45.5,
            'hotspot_1_name': 'Western Gulf of Maine (Historical)',
            'hotspot_1_lat': 43.2, 'hotspot_1_lon': -69.5,
            'hotspot_2_name': 'Bay of Fundy Approaches (Remnant)',
            'hotspot_2_lat': 44.8, 'hotspot_2_lon': -66.5,
            'shift_km': 200, 'shift_direction': 'NE',
            'map_notes': 'Population collapsed; fishery closed since 2013. Remaining '
                         'individuals concentrated in the coldest deep-water pockets near '
                         'the Bay of Fundy. Effectively extirpated from southern Gulf of Maine.'
        },
        # American Lobster (S. New England)
        {
            'species': 'American Lobster (S. New England)', 'scientific_name': 'Homarus americanus',
            'thermal_affinity': 'Cool-water', 'trend': 'Declining',
            'hist_centroid_lat': 41.0, 'hist_centroid_lon': -71.5,
            'curr_centroid_lat': 41.3, 'curr_centroid_lon': -71.0,
            'hist_range_south': 39.5, 'hist_range_north': 42.0,
            'curr_range_south': 40.5, 'curr_range_north': 42.0,
            'hotspot_1_name': 'Long Island Sound (Historical)',
            'hotspot_1_lat': 41.1, 'hotspot_1_lon': -72.5,
            'hotspot_2_name': 'Narragansett Bay (Remnant)',
            'hotspot_2_lat': 41.5, 'hotspot_2_lon': -71.3,
            'shift_km': 50, 'shift_direction': 'NE',
            'map_notes': 'Population collapsed 93% due to chronic thermal stress and '
                         'shell disease. Southern range boundary has contracted northward. '
                         'Long Island Sound populations functionally eliminated.'
        },
        # American Lobster (Maine)
        {
            'species': 'American Lobster (Maine)', 'scientific_name': 'Homarus americanus',
            'thermal_affinity': 'Cool-water', 'trend': 'Plateauing',
            'hist_centroid_lat': 43.5, 'hist_centroid_lon': -69.0,
            'curr_centroid_lat': 43.8, 'curr_centroid_lon': -68.5,
            'hist_range_south': 42.5, 'hist_range_north': 45.0,
            'curr_range_south': 42.5, 'curr_range_north': 45.5,
            'hotspot_1_name': 'Midcoast Maine (Peak Harvest)',
            'hotspot_1_lat': 43.8, 'hotspot_1_lon': -69.2,
            'hotspot_2_name': 'Downeast Maine (Expanding)',
            'hotspot_2_lat': 44.5, 'hotspot_2_lon': -67.5,
            'shift_km': 45, 'shift_direction': 'NE',
            'map_notes': 'Harvest activity has gradually shifted eastward and into deeper '
                         'water. Downeast Maine and Canadian border waters show increasing '
                         'catch rates while traditional midcoast areas show early signs of '
                         'plateau.'
        },
        # Black Sea Bass
        {
            'species': 'Black Sea Bass', 'scientific_name': 'Centropristis striata',
            'thermal_affinity': 'Warm-water', 'trend': 'Expanding',
            'hist_centroid_lat': 38.5, 'hist_centroid_lon': -73.5,
            'curr_centroid_lat': 40.8, 'curr_centroid_lon': -71.0,
            'hist_range_south': 35.0, 'hist_range_north': 40.5,
            'curr_range_south': 35.0, 'curr_range_north': 43.5,
            'hotspot_1_name': 'Mid-Atlantic Bight (Historical Core)',
            'hotspot_1_lat': 38.5, 'hotspot_1_lon': -74.0,
            'hotspot_2_name': 'Southern New England / Cape Cod (Expanding)',
            'hotspot_2_lat': 41.5, 'hotspot_2_lon': -70.5,
            'shift_km': 280, 'shift_direction': 'NNE',
            'map_notes': 'One of the most dramatic northward range expansions in the Northwest '
                         'Atlantic. Black sea bass are now regularly caught in Maine waters where '
                         'they were virtually absent before 2005. Year-round populations now '
                         'established as far north as Cape Cod Bay.'
        },
        # Longfin Squid
        {
            'species': 'Longfin Squid', 'scientific_name': 'Doryteuthis pealeii',
            'thermal_affinity': 'Warm-water', 'trend': 'Expanding',
            'hist_centroid_lat': 39.5, 'hist_centroid_lon': -72.5,
            'curr_centroid_lat': 41.5, 'curr_centroid_lon': -70.0,
            'hist_range_south': 35.0, 'hist_range_north': 41.5,
            'curr_range_south': 35.0, 'curr_range_north': 44.0,
            'hotspot_1_name': 'Southern New England Shelf (Historical)',
            'hotspot_1_lat': 40.0, 'hotspot_1_lon': -72.0,
            'hotspot_2_name': 'Gulf of Maine Nearshore (Expanding)',
            'hotspot_2_lat': 42.5, 'hotspot_2_lon': -70.0,
            'shift_km': 250, 'shift_direction': 'NNE',
            'map_notes': 'Longfin squid have expanded their seasonal range substantially into '
                         'Gulf of Maine waters. As a key prey species for many marine predators, '
                         'this redistribution has significant food web implications throughout '
                         'the region.'
        },
        # Atlantic Mackerel
        {
            'species': 'Atlantic Mackerel', 'scientific_name': 'Scomber scombrus',
            'thermal_affinity': 'Cool-water', 'trend': 'Shifting North',
            'hist_centroid_lat': 41.0, 'hist_centroid_lon': -69.5,
            'curr_centroid_lat': 42.8, 'curr_centroid_lon': -68.0,
            'hist_range_south': 37.0, 'hist_range_north': 44.0,
            'curr_range_south': 39.0, 'curr_range_north': 46.0,
            'hotspot_1_name': 'Southern New England (Historical Spawning)',
            'hotspot_1_lat': 41.0, 'hotspot_1_lon': -70.0,
            'hotspot_2_name': 'Central Gulf of Maine (Current Spawning)',
            'hotspot_2_lat': 43.0, 'hotspot_2_lon': -68.0,
            'shift_km': 220, 'shift_direction': 'NNE',
            'map_notes': 'Spawning grounds have shifted northward and timing has moved earlier '
                         'in the season. The southern range boundary has contracted, reducing '
                         'mackerel availability in traditional Mid-Atlantic fishing grounds.'
        },
        # Bluefin Tuna
        {
            'species': 'Bluefin Tuna', 'scientific_name': 'Thunnus thynnus',
            'thermal_affinity': 'Warm-water', 'trend': 'Expanding',
            'hist_centroid_lat': 41.5, 'hist_centroid_lon': -69.0,
            'curr_centroid_lat': 43.0, 'curr_centroid_lon': -68.0,
            'hist_range_south': 38.0, 'hist_range_north': 43.0,
            'curr_range_south': 38.0, 'curr_range_north': 45.5,
            'hotspot_1_name': 'Cape Cod Bay (Historical)',
            'hotspot_1_lat': 41.8, 'hotspot_1_lon': -70.0,
            'hotspot_2_name': 'Downeast Maine (Expanding)',
            'hotspot_2_lat': 44.2, 'hotspot_2_lon': -67.5,
            'shift_km': 180, 'shift_direction': 'NNE',
            'map_notes': 'Bluefin tuna are following northward-shifting forage fish (herring, '
                         'mackerel, sand lance) into Maine and Canadian waters. The recreational '
                         'and commercial fishery has shifted substantially eastward along the '
                         'Maine coast.'
        },
        # Summer Flounder
        {
            'species': 'Summer Flounder', 'scientific_name': 'Paralichthys dentatus',
            'thermal_affinity': 'Warm-water', 'trend': 'Expanding',
            'hist_centroid_lat': 38.0, 'hist_centroid_lon': -74.0,
            'curr_centroid_lat': 40.0, 'curr_centroid_lon': -72.0,
            'hist_range_south': 34.0, 'hist_range_north': 41.0,
            'curr_range_south': 34.0, 'curr_range_north': 43.0,
            'hotspot_1_name': 'Mid-Atlantic Bight (Historical Core)',
            'hotspot_1_lat': 38.0, 'hotspot_1_lon': -74.5,
            'hotspot_2_name': 'Southern New England (Expanding)',
            'hotspot_2_lat': 41.0, 'hotspot_2_lon': -71.5,
            'shift_km': 240, 'shift_direction': 'NNE',
            'map_notes': 'Summer flounder have expanded into southern Gulf of Maine waters, '
                         'increasingly caught in Massachusetts and New Hampshire. This northward '
                         'shift has created interstate fishery management conflicts as quota '
                         'allocations are based on historical distribution patterns.'
        },
        # Jonah Crab
        {
            'species': 'Jonah Crab', 'scientific_name': 'Cancer borealis',
            'thermal_affinity': 'Cool-water', 'trend': 'Expanding',
            'hist_centroid_lat': 41.5, 'hist_centroid_lon': -69.5,
            'curr_centroid_lat': 42.5, 'curr_centroid_lon': -68.5,
            'hist_range_south': 38.0, 'hist_range_north': 44.0,
            'curr_range_south': 38.0, 'curr_range_north': 45.0,
            'hotspot_1_name': 'Georges Bank / SNE (Historical)',
            'hotspot_1_lat': 41.0, 'hotspot_1_lon': -68.5,
            'hotspot_2_name': 'Central Gulf of Maine (Expanding)',
            'hotspot_2_lat': 43.0, 'hotspot_2_lon': -68.0,
            'shift_km': 120, 'shift_direction': 'NNE',
            'map_notes': 'Jonah crab have become an increasingly important commercial species '
                         'as lobster fishers diversify. Landings have increased 180% as moderate '
                         'warming benefits this cool-water species.'
        },
        # Atlantic Herring
        {
            'species': 'Atlantic Herring', 'scientific_name': 'Clupea harengus',
            'thermal_affinity': 'Cold-water', 'trend': 'Declining',
            'hist_centroid_lat': 42.5, 'hist_centroid_lon': -68.5,
            'curr_centroid_lat': 43.5, 'curr_centroid_lon': -67.5,
            'hist_range_south': 39.0, 'hist_range_north': 45.0,
            'curr_range_south': 41.0, 'curr_range_north': 45.5,
            'hotspot_1_name': 'Georges Bank (Historical Spawning)',
            'hotspot_1_lat': 42.0, 'hotspot_1_lon': -67.5,
            'hotspot_2_name': 'Eastern Maine / Bay of Fundy (Current)',
            'hotspot_2_lat': 44.5, 'hotspot_2_lon': -67.0,
            'shift_km': 130, 'shift_direction': 'NNE',
            'map_notes': 'Atlantic herring biomass has declined 55% while the remaining '
                         'population has shifted northeast. As a critical forage species, '
                         'herring decline cascades through the food web, affecting seabirds '
                         '(puffins), marine mammals, and predatory fish.'
        },
        # Calanus finmarchicus
        {
            'species': 'Calanus finmarchicus', 'scientific_name': 'Calanus finmarchicus',
            'thermal_affinity': 'Cold-water', 'trend': 'Declining',
            'hist_centroid_lat': 42.5, 'hist_centroid_lon': -68.0,
            'curr_centroid_lat': 44.0, 'curr_centroid_lon': -66.5,
            'hist_range_south': 40.0, 'hist_range_north': 46.0,
            'curr_range_south': 42.5, 'curr_range_north': 47.0,
            'hotspot_1_name': 'Wilkinson Basin (Historical Peak)',
            'hotspot_1_lat': 42.8, 'hotspot_1_lon': -69.0,
            'hotspot_2_name': 'Gulf of St. Lawrence (Shifting)',
            'hotspot_2_lat': 47.0, 'hotspot_2_lon': -62.0,
            'shift_km': 250, 'shift_direction': 'NE',
            'map_notes': 'This lipid-rich copepod, the energy backbone of the Gulf of Maine '
                         'food web, has declined ~70% in abundance. Peak concentrations have '
                         'shifted from Wilkinson Basin toward the Scotian Shelf and Gulf of '
                         'St. Lawrence. North Atlantic right whales have followed this prey '
                         'shift, moving into less-protected Canadian waters.'
        },
    ]
    return pd.DataFrame(records)


# ============================================
# DATA: LOBSTER LANDINGS
# ============================================
@st.cache_data
def load_lobster_data():
    """
    Lobster landings by region (NOAA Fisheries, Atlantic States Marine
    Fisheries Commission). Maine data from Maine DMR; Southern New England
    data from CT, RI, NY combined.
    """
    data = {
        'year': [1990, 1993, 1995, 1998, 2000, 2002, 2005, 2007, 2010,
                 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                 2020, 2021, 2022, 2023],
        'maine_millions_lbs': [
            28, 31, 36, 47, 57, 63, 69, 82, 96,
            127, 128, 124, 121, 132, 111, 119, 101,
            96, 108, 98, 93
        ],
        'southern_ne_millions_lbs': [
            22, 20, 18, 16, 15, 13, 10, 9, 8,
            6, 5, 4, 3.5, 3, 2.8, 2.5, 2.2,
            2.0, 1.8, 1.6, 1.5
        ],
        'maine_value_millions': [
            138, 155, 185, 225, 280, 310, 340, 400, 460,
            545, 564, 557, 495, 533, 434, 485, 389,
            405, 730, 568, 505
        ],
        'sne_avg_bottom_temp_c': [
            14.2, 14.5, 14.8, 15.1, 15.5, 16.0, 16.3, 16.8, 17.2,
            17.8, 17.5, 17.9, 18.1, 18.4, 18.0, 18.3, 18.5,
            18.7, 19.0, 19.2, 19.4
        ]
    }
    return pd.DataFrame(data)


# ============================================
# DATA: ECOSYSTEM INDICATORS
# ============================================
@st.cache_data
def load_ecosystem_data():
    """
    Ecosystem-level indicators for the Gulf of Maine.
    Compiled from Gulf of Maine Research Institute, NOAA,
    and published literature.
    """
    data = {
        'year': list(range(2000, 2025)),
        'calanus_abundance_index': [
            100, 95, 98, 92, 88, 85, 80, 78, 72, 68,
            60, 55, 50, 48, 45, 42, 40, 38, 35, 33,
            30, 28, 32, 29, 27
        ],
        'warm_species_richness': [
            8, 9, 8, 10, 11, 12, 13, 14, 15, 16,
            18, 19, 21, 22, 24, 25, 27, 28, 30, 31,
            33, 34, 35, 36, 37
        ],
        'cold_species_richness': [
            42, 41, 42, 40, 39, 38, 37, 36, 35, 34,
            32, 31, 30, 29, 28, 27, 26, 25, 24, 23,
            22, 21, 22, 21, 20
        ],
        'marine_heatwave_days': [
            5, 8, 3, 10, 12, 15, 18, 20, 22, 25,
            30, 35, 80, 40, 28, 45, 55, 38, 42, 60,
            65, 70, 50, 72, 58
        ],
        'right_whale_sightings_gom': [
            120, 115, 110, 105, 100, 95, 90, 85, 75, 70,
            65, 55, 50, 45, 40, 35, 30, 28, 25, 22,
            20, 18, 22, 20, 18
        ]
    }
    return pd.DataFrame(data)


# ============================================
# DATA: FOOD WEB NETWORK
# ============================================
@st.cache_data
def load_foodweb_data():
    """
    Trophic network structure for the Gulf of Maine marine food web.
    Nodes represent species or functional groups at defined trophic levels.
    Edges represent predator-prey or energy transfer relationships.
    Compiled from published diet studies, NOAA food habits database,
    and ecosystem modeling literature.
    """
    nodes = [
        # Trophic Level 1: Primary Producers
        {'id': 'phyto', 'label': 'Phytoplankton', 'trophic_level': 1,
         'category': 'Primary Producer', 'trend': 'Variable',
         'status_color': '#8DB580',
         'notes': 'Diatoms and dinoflagellates forming the base of the food web. '
                  'Spring bloom timing has shifted 2-3 weeks earlier in the Gulf of Maine, '
                  'creating potential mismatches with zooplankton grazers.'},

        # Trophic Level 2: Zooplankton
        {'id': 'calanus', 'label': 'Calanus finmarchicus', 'trophic_level': 2,
         'category': 'Zooplankton (Cold-water)', 'trend': 'Declining',
         'status_color': '#457B9D',
         'notes': 'Lipid-rich copepod historically dominating Gulf of Maine zooplankton biomass. '
                  'Declined ~70% as warming favors smaller warm-water copepods. Keystone prey '
                  'for herring, sand lance, and right whales.'},
        {'id': 'centropages', 'label': 'Centropages typicus', 'trophic_level': 2,
         'category': 'Zooplankton (Warm-water)', 'trend': 'Expanding',
         'status_color': '#E63946',
         'notes': 'Smaller, less lipid-dense copepod increasing in abundance as waters warm. '
                  'Provides significantly less energy per individual than Calanus, forcing '
                  'predators to expend more effort for the same caloric intake.'},
        {'id': 'krill', 'label': 'Krill (Euphausiacea)', 'trophic_level': 2,
         'category': 'Zooplankton', 'trend': 'Variable',
         'status_color': '#D4A373',
         'notes': 'Important prey for baleen whales and forage fish. Abundance varies '
                  'interannually but shows a long-term declining trend in southern Gulf of Maine.'},

        # Trophic Level 3: Forage Species
        {'id': 'herring', 'label': 'Atlantic Herring', 'trophic_level': 3,
         'category': 'Forage Fish (Cold-water)', 'trend': 'Declining',
         'status_color': '#457B9D',
         'notes': 'Critical forage species linking zooplankton to upper trophic levels. '
                  'Biomass declined 55% as Calanus prey base eroded. Supports seabirds, '
                  'marine mammals, tuna, and cod.'},
        {'id': 'sandlance', 'label': 'Sand Lance', 'trophic_level': 3,
         'category': 'Forage Fish (Cold-water)', 'trend': 'Declining',
         'status_color': '#457B9D',
         'notes': 'Small burrowing fish critical for seabird breeding success. Particularly '
                  'important for Atlantic puffin chick survival on nesting islands. Declining '
                  'in southern portions of range.'},
        {'id': 'squid', 'label': 'Longfin Squid', 'trophic_level': 3,
         'category': 'Forage/Prey (Warm-water)', 'trend': 'Expanding',
         'status_color': '#E63946',
         'notes': 'Expanding northward into Gulf of Maine. Serves dual trophic role as both '
                  'predator (of small fish, zooplankton) and prey (for tuna, cod, marine mammals). '
                  'Partially replacing herring as a forage base.'},
        {'id': 'shrimp', 'label': 'Northern Shrimp', 'trophic_level': 3,
         'category': 'Invertebrate (Cold-water)', 'trend': 'Collapsed',
         'status_color': '#1D3557',
         'notes': 'Population collapsed; fishery closed since 2013. Was an important prey '
                  'item for cod and other groundfish. Its loss removes a trophic link between '
                  'benthic production and demersal predators.'},

        # Trophic Level 4: Mid-level Predators
        {'id': 'cod', 'label': 'Atlantic Cod', 'trophic_level': 4,
         'category': 'Groundfish (Cold-water)', 'trend': 'Declining',
         'status_color': '#457B9D',
         'notes': 'Historically the apex demersal predator in the Gulf of Maine. Declining '
                  '78% due to warming and reduced prey (shrimp, herring, sand lance). '
                  'Loss of cod releases predation pressure on crabs and lobster.'},
        {'id': 'mackerel', 'label': 'Atlantic Mackerel', 'trophic_level': 4,
         'category': 'Pelagic Fish (Cool-water)', 'trend': 'Shifting North',
         'status_color': '#D4A373',
         'notes': 'Shifting northward at 55 km/decade. Important prey for tuna and marine mammals, '
                  'and a significant predator of zooplankton and small fish.'},
        {'id': 'lobster', 'label': 'American Lobster', 'trophic_level': 3.5,
         'category': 'Invertebrate (Cool-water)', 'trend': 'Mixed',
         'status_color': '#D4A373',
         'notes': 'Omnivorous benthic feeder consuming crabs, mussels, sea urchins, and algae. '
                  'Booming in Maine, collapsing in Southern New England. Benefited from reduced '
                  'cod predation pressure on juveniles.'},
        {'id': 'bsb', 'label': 'Black Sea Bass', 'trophic_level': 4,
         'category': 'Reef Fish (Warm-water)', 'trend': 'Expanding',
         'status_color': '#E63946',
         'notes': 'Expanding northward at 75 km/decade. Feeds on crabs, shrimp, and small fish. '
                  'Now competing with native species for habitat and prey in areas where it was '
                  'previously absent.'},
        {'id': 'flounder', 'label': 'Summer Flounder', 'trophic_level': 4,
         'category': 'Flatfish (Warm-water)', 'trend': 'Expanding',
         'status_color': '#E63946',
         'notes': 'Expanding into Gulf of Maine from the Mid-Atlantic. Feeds on small fish, '
                  'squid, and crustaceans. Potential competition with winter flounder and '
                  'other native flatfish for benthic habitat.'},

        # Trophic Level 5: Top Predators
        {'id': 'tuna', 'label': 'Bluefin Tuna', 'trophic_level': 5,
         'category': 'Apex Predator (Warm-water)', 'trend': 'Expanding',
         'status_color': '#E63946',
         'notes': 'Following forage fish (herring, mackerel, sand lance) northward into Maine '
                  'and Canadian waters. Apex pelagic predator with increasing presence in the '
                  'Gulf of Maine.'},
        {'id': 'right_whale', 'label': 'North Atlantic Right Whale', 'trophic_level': 4.5,
         'category': 'Marine Mammal (Endangered)', 'trend': 'Declining',
         'status_color': '#1D3557',
         'notes': 'Critically endangered (<360 individuals). Obligate Calanus predator that has '
                  'shifted foraging from Gulf of Maine to the Gulf of St. Lawrence, following '
                  'northward-moving copepod prey into waters with less ship-strike protection.'},
        {'id': 'seals', 'label': 'Gray / Harbor Seals', 'trophic_level': 5,
         'category': 'Marine Mammal', 'trend': 'Stable/Increasing',
         'status_color': '#8DB580',
         'notes': 'Seal populations have recovered significantly under Marine Mammal Protection Act. '
                  'Feed on herring, sand lance, squid, and various groundfish. Their recovery adds '
                  'predation pressure on already-stressed forage fish populations.'},
        {'id': 'puffin', 'label': 'Atlantic Puffin', 'trophic_level': 4.5,
         'category': 'Seabird', 'trend': 'Declining',
         'status_color': '#457B9D',
         'notes': 'Gulf of Maine puffin colonies depend on herring and sand lance to feed chicks. '
                  'As these cold-water forage fish decline, puffins have been observed bringing '
                  'butterfish (a warm-water species) to chicks, which are too large for chicks '
                  'to swallow, reducing breeding success.'},
        {'id': 'humpback', 'label': 'Humpback Whale', 'trophic_level': 4.5,
         'category': 'Marine Mammal', 'trend': 'Variable',
         'status_color': '#D4A373',
         'notes': 'Generalist baleen whale feeding on herring, sand lance, krill, and other '
                  'small schooling fish. More dietary flexibility than right whales, but still '
                  'affected by declining forage fish abundance.'},
    ]

    # Directed edges: source (prey) -> target (predator)
    edges = [
        # Phytoplankton feeds zooplankton
        {'source': 'phyto', 'target': 'calanus', 'strength': 'strong'},
        {'source': 'phyto', 'target': 'centropages', 'strength': 'strong'},
        {'source': 'phyto', 'target': 'krill', 'strength': 'strong'},

        # Zooplankton feeds forage species
        {'source': 'calanus', 'target': 'herring', 'strength': 'strong'},
        {'source': 'calanus', 'target': 'sandlance', 'strength': 'strong'},
        {'source': 'calanus', 'target': 'right_whale', 'strength': 'critical'},
        {'source': 'calanus', 'target': 'mackerel', 'strength': 'moderate'},
        {'source': 'centropages', 'target': 'herring', 'strength': 'moderate'},
        {'source': 'centropages', 'target': 'sandlance', 'strength': 'weak'},
        {'source': 'krill', 'target': 'herring', 'strength': 'moderate'},
        {'source': 'krill', 'target': 'humpback', 'strength': 'strong'},
        {'source': 'krill', 'target': 'right_whale', 'strength': 'moderate'},

        # Forage species feed mid-level and top predators
        {'source': 'herring', 'target': 'cod', 'strength': 'strong'},
        {'source': 'herring', 'target': 'tuna', 'strength': 'strong'},
        {'source': 'herring', 'target': 'humpback', 'strength': 'strong'},
        {'source': 'herring', 'target': 'puffin', 'strength': 'critical'},
        {'source': 'herring', 'target': 'seals', 'strength': 'strong'},
        {'source': 'sandlance', 'target': 'puffin', 'strength': 'critical'},
        {'source': 'sandlance', 'target': 'cod', 'strength': 'moderate'},
        {'source': 'sandlance', 'target': 'tuna', 'strength': 'moderate'},
        {'source': 'sandlance', 'target': 'humpback', 'strength': 'moderate'},
        {'source': 'sandlance', 'target': 'seals', 'strength': 'moderate'},
        {'source': 'squid', 'target': 'tuna', 'strength': 'strong'},
        {'source': 'squid', 'target': 'cod', 'strength': 'moderate'},
        {'source': 'squid', 'target': 'seals', 'strength': 'moderate'},
        {'source': 'squid', 'target': 'bsb', 'strength': 'moderate'},
        {'source': 'shrimp', 'target': 'cod', 'strength': 'strong'},
        {'source': 'shrimp', 'target': 'flounder', 'strength': 'moderate'},

        # Benthic connections
        {'source': 'lobster', 'target': 'cod', 'strength': 'moderate'},
        {'source': 'lobster', 'target': 'seals', 'strength': 'weak'},

        # Mid-level predators feed top predators
        {'source': 'mackerel', 'target': 'tuna', 'strength': 'strong'},
        {'source': 'mackerel', 'target': 'seals', 'strength': 'moderate'},
        {'source': 'mackerel', 'target': 'humpback', 'strength': 'moderate'},
        {'source': 'cod', 'target': 'seals', 'strength': 'moderate'},
    ]

    return nodes, edges


# ============================================
# LOAD ALL DATA
# ============================================
df_sst = load_sst_data()
df_species = load_species_data()
df_spatial = load_spatial_data()
df_lobster = load_lobster_data()
df_ecosystem = load_ecosystem_data()
fw_nodes, fw_edges = load_foodweb_data()


# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/New_England_Aquarium_logo.svg/1200px-New_England_Aquarium_logo.svg.png",
        width=200
    )
    st.markdown("---")
    st.markdown("## Dashboard Controls")

    temp_unit = st.radio("Temperature Unit", ["Celsius (C)", "Fahrenheit (F)"])
    use_fahrenheit = "Fahrenheit" in temp_unit

    year_range = st.slider(
        "Year Range (SST Data)",
        min_value=1982,
        max_value=2024,
        value=(1982, 2024)
    )

    species_filter = st.multiselect(
        "Filter Species by Thermal Affinity",
        options=['Cold-water', 'Cool-water', 'Warm-water'],
        default=['Cold-water', 'Cool-water', 'Warm-water']
    )

    st.markdown("---")
    st.markdown("### Data Sources")
    st.markdown("""
    - NOAA ERSST v5
    - NOAA Northeast Fisheries Science Center
    - Atlantic States Marine Fisheries Commission
    - Gulf of Maine Research Institute
    - Pershing et al. (2015, 2021)
    - Mills et al. (2013)
    """)

    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **Developed by:** Rishab  
    **For:** New England Aquarium  
    Anderson Cabot Center for Ocean Life  

    This dashboard synthesizes publicly available oceanographic and fisheries
    data to visualize climate-driven ecological changes in the Gulf of Maine.
    """)


# ============================================
# MAIN CONTENT - HEADER
# ============================================
st.markdown('<p class="main-header">Gulf of Maine Climate Impact Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Analyzing Marine Species Redistribution in the Fastest-Warming '
    'Ocean Region in North America</p>',
    unsafe_allow_html=True
)

st.markdown("""
<p class="section-description">
The Gulf of Maine has warmed faster than 99% of the global ocean over recent decades, with
sea surface temperatures increasing at approximately three times the global average rate.
This accelerated warming is fundamentally restructuring the marine ecosystem, driving
cold-adapted species northward or to greater depths while enabling warm-water species to
colonize previously unsuitable habitat. This dashboard provides an interactive synthesis
of temperature trends, species-level responses, and ecosystem-wide indicators to
characterize the scope and pace of these changes.
</p>
""", unsafe_allow_html=True)

# Key metrics row
col1, col2, col3, col4, col5 = st.columns(5)

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
            label="Total Warming (1982-2024)",
            value=f"+{total_warming * 1.8:.1f}F",
            delta=f"{total_warming * 1.8 / 42 * 10:.2f}F per decade"
        )
    else:
        st.metric(
            label="Total Warming (1982-2024)",
            value=f"+{total_warming:.1f}C",
            delta=f"{total_warming / 42 * 10:.2f}C per decade"
        )

with col3:
    expanding = len(df_species[df_species['trend'].isin(['Expanding'])])
    declining = len(df_species[df_species['trend'].isin(['Declining', 'Collapsed'])])
    st.metric(
        label="Species Expanding North",
        value=f"{expanding}",
        delta=f"{declining} declining or collapsed",
        delta_color="inverse"
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

with col5:
    calanus_decline = ((df_ecosystem['calanus_abundance_index'].iloc[-1] -
                         df_ecosystem['calanus_abundance_index'].iloc[0]) /
                        df_ecosystem['calanus_abundance_index'].iloc[0] * 100)
    st.metric(
        label="Calanus Copepod Index",
        value=f"{calanus_decline:.0f}%",
        delta="Keystone zooplankton since 2000",
        delta_color="inverse"
    )

st.markdown("---")


# ============================================
# TAB LAYOUT
# ============================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Temperature Trends",
    "Species Redistribution",
    "Interactive Range Map",
    "Lobster Case Study",
    "Ecosystem Indicators",
    "Food Web",
    "Data & Methods"
])


# ============================================
# TAB 1: TEMPERATURE TRENDS
# ============================================
with tab1:
    st.markdown("## Sea Surface Temperature Analysis")
    st.markdown("""
    <p class="section-description">
    The Gulf of Maine's warming trajectory is among the most dramatic of any marine ecosystem
    globally. While the global ocean has warmed at approximately 0.1C per decade since 1982,
    the Gulf of Maine has warmed at roughly 0.5C per decade, a rate that accelerated sharply
    after the 2012 marine heatwave event. The following visualizations present annual mean
    sea surface temperature and anomalies relative to the NOAA standard 1901-2000 baseline.
    </p>
    """, unsafe_allow_html=True)

    df_sst_filtered = df_sst[
        (df_sst['year'] >= year_range[0]) & (df_sst['year'] <= year_range[1])
    ]

    temp_col = 'sst_fahrenheit' if use_fahrenheit else 'sst_celsius'
    anomaly_col = 'anomaly_fahrenheit' if use_fahrenheit else 'anomaly_celsius'
    smooth_col = 'sst_5yr_avg_f' if use_fahrenheit else 'sst_5yr_avg'
    unit = 'F' if use_fahrenheit else 'C'

    col1, col2 = st.columns(2)

    with col1:
        fig_temp = go.Figure()

        fig_temp.add_trace(go.Scatter(
            x=df_sst_filtered['year'],
            y=df_sst_filtered[temp_col],
            mode='lines+markers',
            name='Annual Mean SST',
            line=dict(color='#457B9D', width=2),
            marker=dict(size=5, color='#457B9D')
        ))

        # 5-year rolling average
        fig_temp.add_trace(go.Scatter(
            x=df_sst_filtered['year'],
            y=df_sst_filtered[smooth_col],
            mode='lines',
            name='5-Year Rolling Average',
            line=dict(color='#E63946', width=3)
        ))

        # Linear trend
        z = np.polyfit(df_sst_filtered['year'], df_sst_filtered[temp_col], 1)
        p = np.poly1d(z)
        fig_temp.add_trace(go.Scatter(
            x=df_sst_filtered['year'],
            y=p(df_sst_filtered['year']),
            mode='lines',
            name=f'Linear Trend: +{z[0]*10:.2f}{unit}/decade',
            line=dict(color='#1D3557', width=2, dash='dash')
        ))

        # 2012 heatwave annotation
        if 2012 >= year_range[0] and 2012 <= year_range[1]:
            heatwave_temp = df_sst[df_sst['year'] == 2012][temp_col].values[0]
            fig_temp.add_annotation(
                x=2012, y=heatwave_temp,
                text="2012 Marine<br>Heatwave",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#E63946",
                font=dict(color="#E63946", size=11)
            )

        fig_temp.update_layout(
            title=f"Gulf of Maine Annual Mean SST ({year_range[0]}-{year_range[1]})",
            xaxis_title="Year",
            yaxis_title=f"Temperature ({unit})",
            hovermode="x unified",
            template="plotly_white",
            height=470,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, font=dict(size=10))
        )

        st.plotly_chart(fig_temp, use_container_width=True)

    with col2:
        colors = ['#E63946' if x > 0 else '#457B9D' for x in df_sst_filtered[anomaly_col]]

        fig_anomaly = go.Figure()

        fig_anomaly.add_trace(go.Bar(
            x=df_sst_filtered['year'],
            y=df_sst_filtered[anomaly_col],
            marker_color=colors,
            name='Temperature Anomaly',
            hovertemplate='Year: %{x}<br>Anomaly: %{y:.2f}' + unit + '<extra></extra>'
        ))

        fig_anomaly.add_hline(y=0, line_dash="solid", line_color="black", line_width=2)

        fig_anomaly.update_layout(
            title=f"Temperature Anomaly Relative to 1901-2000 Baseline",
            xaxis_title="Year",
            yaxis_title=f"Anomaly ({unit})",
            template="plotly_white",
            height=470,
            showlegend=False
        )

        st.plotly_chart(fig_anomaly, use_container_width=True)

    # Decadal summary
    st.markdown("### Decadal Comparison")
    col1, col2 = st.columns(2)

    with col1:
        decadal_means = df_sst.groupby('decade_label').agg(
            mean_sst=('sst_celsius', 'mean'),
            mean_anomaly=('anomaly_celsius', 'mean'),
            max_anomaly=('anomaly_celsius', 'max')
        ).reset_index()

        fig_decadal = go.Figure()
        fig_decadal.add_trace(go.Bar(
            x=decadal_means['decade_label'],
            y=decadal_means['mean_anomaly'] if not use_fahrenheit
              else decadal_means['mean_anomaly'] * 1.8,
            marker_color=['#457B9D' if x < 0.3 else '#D4A373' if x < 0.8
                          else '#E63946' for x in decadal_means['mean_anomaly']],
            text=[f"{x:.2f}" for x in (decadal_means['mean_anomaly'] if not use_fahrenheit
                  else decadal_means['mean_anomaly'] * 1.8)],
            textposition='outside'
        ))
        fig_decadal.update_layout(
            title="Mean Temperature Anomaly by Decade",
            xaxis_title="Decade",
            yaxis_title=f"Mean Anomaly ({unit})",
            template="plotly_white",
            height=380,
            showlegend=False
        )
        st.plotly_chart(fig_decadal, use_container_width=True)

    with col2:
        recent_anomaly = df_sst[df_sst['year'] >= 2015][anomaly_col].mean()
        pre_2012_anomaly = df_sst[df_sst['year'] < 2012][anomaly_col].mean()

        st.markdown(f"""
        <div class="insight-box">
        <strong>Key Finding: Regime Shift After 2012</strong><br><br>
        The 2012 marine heatwave represents an inflection point in Gulf of Maine thermal dynamics.
        Prior to 2012, the mean temperature anomaly was <strong>{pre_2012_anomaly:.2f}{unit}</strong>
        relative to the 1901-2000 baseline. Since 2015, the mean anomaly has been
        <strong>+{recent_anomaly:.1f}{unit}</strong>, indicating that conditions once considered
        anomalous are now the norm.<br><br>
        This persistent warming has exceeded the adaptive capacity of several cold-water species
        and triggered large-scale community restructuring across the ecosystem.
        </div>
        """, unsafe_allow_html=True)


# ============================================
# TAB 2: SPECIES REDISTRIBUTION
# ============================================
with tab2:
    st.markdown("## Species Redistribution Analysis")
    st.markdown("""
    <p class="section-description">
    Marine species are responding to Gulf of Maine warming through multiple pathways:
    latitudinal range shifts (moving north or south), bathymetric shifts (moving to deeper,
    cooler water), changes in seasonal timing (phenological shifts), and population-level
    responses (abundance increases or declines). The following analyses characterize these
    responses across 12 ecologically and commercially significant species, grouped by
    thermal affinity. Range shift estimates are derived from NOAA Northeast Fisheries Science
    Center bottom trawl survey data and published centroid analyses.
    </p>
    """, unsafe_allow_html=True)

    df_species_filtered = df_species[df_species['thermal_affinity'].isin(species_filter)]

    col1, col2 = st.columns(2)

    with col1:
        # Latitudinal range shifts
        df_sorted = df_species_filtered.sort_values('lat_shift_km_decade')

        colors_shift = []
        for _, row in df_sorted.iterrows():
            if row['trend'] == 'Collapsed':
                colors_shift.append('#1D3557')
            elif row['trend'] == 'Declining':
                colors_shift.append('#457B9D')
            elif row['trend'] in ['Shifting North', 'Plateauing']:
                colors_shift.append('#D4A373')
            else:
                colors_shift.append('#E63946')

        fig_shifts = go.Figure()
        fig_shifts.add_trace(go.Bar(
            y=df_sorted['species'],
            x=df_sorted['lat_shift_km_decade'],
            orientation='h',
            marker_color=colors_shift,
            text=[f"{x:+.0f} km/dec" for x in df_sorted['lat_shift_km_decade']],
            textposition='outside',
            hovertemplate=(
                '<b>%{y}</b><br>'
                'Latitudinal Shift: %{x:+.0f} km/decade<br>'
                '<extra></extra>'
            )
        ))

        fig_shifts.add_vline(x=0, line_color="black", line_width=2)

        fig_shifts.update_layout(
            title="Latitudinal Range Shifts (km per decade)",
            xaxis_title="Northward Shift (km/decade)  |  Southward Shift",
            yaxis_title="",
            template="plotly_white",
            height=520,
            xaxis=dict(range=[-150, 120]),
            margin=dict(l=200)
        )

        st.plotly_chart(fig_shifts, use_container_width=True)

    with col2:
        # Thermal preference overlay
        fig_prefs = go.Figure()

        fig_prefs.add_vrect(
            x0=13, x1=20, fillcolor="#E63946", opacity=0.10,
            annotation_text="Current Summer Range (13-20C)",
            annotation_position="top left",
            annotation_font=dict(size=10)
        )
        fig_prefs.add_vrect(
            x0=9, x1=15, fillcolor="#457B9D", opacity=0.10,
            annotation_text="Historical Summer Range (9-15C)",
            annotation_position="bottom left",
            annotation_font=dict(size=10)
        )

        for _, row in df_species_filtered.iterrows():
            if row['trend'] in ['Expanding']:
                color = '#E63946'
            elif row['trend'] in ['Stable', 'Plateauing', 'Shifting North']:
                color = '#D4A373'
            elif row['trend'] == 'Collapsed':
                color = '#1D3557'
            else:
                color = '#457B9D'

            fig_prefs.add_trace(go.Scatter(
                x=[row['temp_min_c'], row['optimal_temp_c'], row['temp_max_c']],
                y=[row['species'], row['species'], row['species']],
                mode='lines+markers',
                line=dict(color=color, width=6),
                marker=dict(
                    size=[8, 14, 8],
                    symbol=['line-ew', 'diamond', 'line-ew'],
                    color=color
                ),
                name=row['species'],
                hovertemplate=(
                    f"<b>{row['species']}</b><br>"
                    f"Range: {row['temp_min_c']}-{row['temp_max_c']}C<br>"
                    f"Optimal: {row['optimal_temp_c']}C<br>"
                    f"Trend: {row['trend']}<extra></extra>"
                )
            ))

        fig_prefs.update_layout(
            title="Species Thermal Tolerance vs. Gulf of Maine Conditions",
            xaxis_title="Temperature (C)",
            yaxis_title="",
            template="plotly_white",
            height=520,
            showlegend=False,
            xaxis=dict(range=[-1, 30]),
            margin=dict(l=200)
        )

        st.plotly_chart(fig_prefs, use_container_width=True)

    # Depth shifts
    st.markdown("### Bathymetric (Depth) Shifts")
    st.markdown("""
    <p class="section-description">
    In addition to moving north, many species are shifting to deeper waters in search of
    cooler temperatures. This vertical redistribution can affect fisheries access patterns,
    predator-prey interactions, and survey catchability.
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        df_depth = df_species_filtered.sort_values('depth_shift_m_decade')

        fig_depth = go.Figure()
        fig_depth.add_trace(go.Bar(
            y=df_depth['species'],
            x=df_depth['depth_shift_m_decade'],
            orientation='h',
            marker_color=['#1D3557' if x > 0 else '#2A9D8F' for x in df_depth['depth_shift_m_decade']],
            text=[f"{x:+.0f} m/dec" for x in df_depth['depth_shift_m_decade']],
            textposition='outside'
        ))

        fig_depth.add_vline(x=0, line_color="black", line_width=2)

        fig_depth.update_layout(
            title="Depth Distribution Shifts (meters per decade)",
            xaxis_title="Deeper (positive)  |  Shallower (negative)",
            yaxis_title="",
            template="plotly_white",
            height=480,
            margin=dict(l=200)
        )
        st.plotly_chart(fig_depth, use_container_width=True)

    with col2:
        # Population change scatter
        fig_pop = go.Figure()

        for affinity in species_filter:
            subset = df_species_filtered[df_species_filtered['thermal_affinity'] == affinity]
            color_map = {'Cold-water': '#457B9D', 'Cool-water': '#D4A373', 'Warm-water': '#E63946'}

            fig_pop.add_trace(go.Scatter(
                x=subset['lat_shift_km_decade'],
                y=subset['population_change_pct'],
                mode='markers+text',
                marker=dict(
                    size=subset['economic_value_millions'].clip(lower=5) / 5 + 8,
                    color=color_map.get(affinity, '#999'),
                    opacity=0.8,
                    line=dict(width=1, color='#1D3557')
                ),
                text=subset['species'].str.split('(').str[0].str.strip(),
                textposition='top center',
                textfont=dict(size=9),
                name=affinity,
                hovertemplate=(
                    '<b>%{text}</b><br>'
                    'Range Shift: %{x:+.0f} km/decade<br>'
                    'Population Change: %{y:+.0f}%<br>'
                    '<extra></extra>'
                )
            ))

        fig_pop.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_pop.add_vline(x=0, line_dash="dash", line_color="gray")

        fig_pop.add_annotation(x=-80, y=-60, text="Declining &<br>Retreating South",
                               showarrow=False, font=dict(color='gray', size=10))
        fig_pop.add_annotation(x=60, y=250, text="Expanding &<br>Moving North",
                               showarrow=False, font=dict(color='gray', size=10))

        fig_pop.update_layout(
            title="Range Shift vs. Population Change (bubble size = economic value)",
            xaxis_title="Latitudinal Shift (km/decade)",
            yaxis_title="Population Change (%)",
            template="plotly_white",
            height=480,
            legend=dict(title="Thermal Affinity")
        )
        st.plotly_chart(fig_pop, use_container_width=True)

    # Species detail
    st.markdown("### Species Detail")

    selected_species = st.selectbox(
        "Select a species for detailed information:",
        df_species_filtered['species'].tolist()
    )

    species_info = df_species[df_species['species'] == selected_species].iloc[0]

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Scientific Name", species_info['scientific_name'])
    with col2:
        st.metric("Thermal Affinity", species_info['thermal_affinity'])
    with col3:
        st.metric("Population Trend", species_info['trend'])
    with col4:
        st.metric("Lat. Shift", f"{species_info['lat_shift_km_decade']:+.0f} km/dec")
    with col5:
        st.metric("Depth Shift", f"{species_info['depth_shift_m_decade']:+.0f} m/dec")

    st.markdown(f"""
    <div class="insight-box">
    <strong>{species_info['species']}</strong> (<em>{species_info['scientific_name']}</em>)
    | {species_info['taxa_group']}
    | Thermal Range: {species_info['temp_min_c']}-{species_info['temp_max_c']}C
    | Optimal: {species_info['optimal_temp_c']}C
    | Economic Importance: {species_info['economic_importance']}
    {f" | Est. Annual Value: ${species_info['economic_value_millions']}M" if species_info['economic_value_millions'] > 0 else ""}
    <br><br>
    {species_info['description']}
    </div>
    """, unsafe_allow_html=True)


# ============================================
# TAB 3: INTERACTIVE RANGE MAP
# ============================================
with tab3:
    st.markdown("## Interactive Species Range Shift Map")
    st.markdown("""
    <p class="section-description">
    This map displays the geographic redistribution of marine species across the Northwest
    Atlantic. For each species, the map shows the historical distribution centroid (1980s-1990s
    baseline) and the current distribution centroid (2015-2024), connected by an arrow indicating
    the direction and magnitude of the shift. Click on any marker for detailed information
    including shift distance, key habitat areas, and ecological context. Use the controls below
    to filter by species, thermal affinity, or view mode.
    </p>
    """, unsafe_allow_html=True)

    # Controls
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)

    with col_ctrl1:
        map_species = st.multiselect(
            "Select Species to Display",
            options=df_spatial['species'].tolist(),
            default=df_spatial['species'].tolist(),
            key='map_species_select'
        )

    with col_ctrl2:
        map_affinity = st.multiselect(
            "Filter by Thermal Affinity",
            options=['Cold-water', 'Cool-water', 'Warm-water'],
            default=['Cold-water', 'Cool-water', 'Warm-water'],
            key='map_affinity_filter'
        )

    with col_ctrl3:
        map_view = st.radio(
            "Map View",
            ["Migration Arrows", "Hotspot Locations", "Range Boundaries"],
            horizontal=True
        )

    # Filter spatial data
    df_map = df_spatial[
        (df_spatial['species'].isin(map_species)) &
        (df_spatial['thermal_affinity'].isin(map_affinity))
    ]

    # Color mapping
    affinity_colors = {
        'Cold-water': '#457B9D',
        'Cool-water': '#D4A373',
        'Warm-water': '#E63946'
    }

    trend_symbols = {
        'Declining': 'circle',
        'Collapsed': 'x',
        'Plateauing': 'diamond',
        'Expanding': 'star',
        'Shifting North': 'triangle-up'
    }

    # ---- VIEW 1: MIGRATION ARROWS ----
    if map_view == "Migration Arrows":

        fig_map = go.Figure()

        # Gulf of Maine boundary outline (approximate)
        gom_lats = [41.0, 41.0, 42.0, 43.5, 44.5, 45.0, 44.5, 43.0, 41.5, 41.0]
        gom_lons = [-71.0, -66.0, -65.5, -66.0, -66.5, -67.0, -68.5, -70.0, -71.0, -71.0]
        fig_map.add_trace(go.Scattermapbox(
            lat=gom_lats, lon=gom_lons,
            mode='lines',
            line=dict(color='rgba(27, 58, 75, 0.3)', width=2),
            name='Gulf of Maine (approx.)',
            hoverinfo='skip',
            showlegend=True
        ))

        for _, row in df_map.iterrows():
            color = affinity_colors.get(row['thermal_affinity'], '#999')
            symbol = trend_symbols.get(row['trend'], 'circle')

            # Historical centroid
            fig_map.add_trace(go.Scattermapbox(
                lat=[row['hist_centroid_lat']],
                lon=[row['hist_centroid_lon']],
                mode='markers',
                marker=dict(size=12, color=color, opacity=0.4, symbol='circle'),
                name=f"{row['species']} (Historical)",
                hovertemplate=(
                    f"<b>{row['species']}</b> | Historical Centroid<br>"
                    f"Lat: {row['hist_centroid_lat']:.1f}N, Lon: {row['hist_centroid_lon']:.1f}W<br>"
                    f"Period: 1980s-1990s<br>"
                    f"<extra></extra>"
                ),
                showlegend=False
            ))

            # Current centroid
            fig_map.add_trace(go.Scattermapbox(
                lat=[row['curr_centroid_lat']],
                lon=[row['curr_centroid_lon']],
                mode='markers+text',
                marker=dict(size=16, color=color, opacity=0.9, symbol=symbol),
                text=[row['species'].split('(')[0].strip()[:12]],
                textposition='top center',
                textfont=dict(size=9, color=color),
                name=f"{row['species']} (Current)",
                hovertemplate=(
                    f"<b>{row['species']}</b> | Current Centroid<br>"
                    f"<em>{row['scientific_name']}</em><br>"
                    f"Lat: {row['curr_centroid_lat']:.1f}N, Lon: {row['curr_centroid_lon']:.1f}W<br>"
                    f"Shift: {row['shift_km']} km {row['shift_direction']}<br>"
                    f"Thermal Affinity: {row['thermal_affinity']}<br>"
                    f"Trend: {row['trend']}<br>"
                    f"---<br>"
                    f"{row['map_notes'][:200]}<br>"
                    f"<extra></extra>"
                ),
                showlegend=False
            ))

            # Arrow line connecting historical to current
            n_points = 20
            lats = np.linspace(row['hist_centroid_lat'], row['curr_centroid_lat'], n_points).tolist()
            lons = np.linspace(row['hist_centroid_lon'], row['curr_centroid_lon'], n_points).tolist()

            fig_map.add_trace(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='lines',
                line=dict(color=color, width=2),
                hoverinfo='skip',
                showlegend=False
            ))

        # Legend traces
        for affinity, color in affinity_colors.items():
            if affinity in map_affinity:
                fig_map.add_trace(go.Scattermapbox(
                    lat=[None], lon=[None],
                    mode='markers',
                    marker=dict(size=12, color=color),
                    name=f"{affinity}",
                    showlegend=True
                ))

        fig_map.update_layout(
            mapbox=dict(
                style='carto-positron',
                center=dict(lat=42.5, lon=-68.0),
                zoom=5.3
            ),
            height=700,
            margin=dict(l=0, r=0, t=30, b=0),
            title="Species Distribution Centroid Shifts: Historical (faded) to Current (solid)",
            legend=dict(
                yanchor="top", y=0.98, xanchor="left", x=0.01,
                bgcolor="rgba(255,255,255,0.85)",
                font=dict(size=11)
            )
        )

        st.plotly_chart(fig_map, use_container_width=True)

    # ---- VIEW 2: HOTSPOT LOCATIONS ----
    elif map_view == "Hotspot Locations":

        fig_hotspot = go.Figure()

        for _, row in df_map.iterrows():
            color = affinity_colors.get(row['thermal_affinity'], '#999')

            # Historical hotspot
            fig_hotspot.add_trace(go.Scattermapbox(
                lat=[row['hotspot_1_lat']],
                lon=[row['hotspot_1_lon']],
                mode='markers',
                marker=dict(size=14, color=color, opacity=0.35, symbol='circle'),
                name=f"{row['species']} | Historical",
                hovertemplate=(
                    f"<b>{row['species']}</b><br>"
                    f"<em>{row['hotspot_1_name']}</em><br>"
                    f"Type: Historical Concentration Area<br>"
                    f"<extra></extra>"
                ),
                showlegend=False
            ))

            # Current hotspot
            fig_hotspot.add_trace(go.Scattermapbox(
                lat=[row['hotspot_2_lat']],
                lon=[row['hotspot_2_lon']],
                mode='markers+text',
                marker=dict(size=18, color=color, opacity=0.9, symbol='star'),
                text=[row['species'].split('(')[0].strip()[:10]],
                textposition='top center',
                textfont=dict(size=9, color=color),
                name=f"{row['species']} | Current",
                hovertemplate=(
                    f"<b>{row['species']}</b><br>"
                    f"<em>{row['hotspot_2_name']}</em><br>"
                    f"Type: Current Concentration / Expansion Area<br>"
                    f"---<br>"
                    f"{row['map_notes'][:200]}<br>"
                    f"<extra></extra>"
                ),
                showlegend=False
            ))

        # Legend
        for affinity, color in affinity_colors.items():
            if affinity in map_affinity:
                fig_hotspot.add_trace(go.Scattermapbox(
                    lat=[None], lon=[None], mode='markers',
                    marker=dict(size=12, color=color), name=affinity, showlegend=True
                ))
        fig_hotspot.add_trace(go.Scattermapbox(
            lat=[None], lon=[None], mode='markers',
            marker=dict(size=10, color='gray', opacity=0.4), name='Historical Hotspot', showlegend=True
        ))
        fig_hotspot.add_trace(go.Scattermapbox(
            lat=[None], lon=[None], mode='markers',
            marker=dict(size=14, color='gray', symbol='star'), name='Current Hotspot', showlegend=True
        ))

        fig_hotspot.update_layout(
            mapbox=dict(style='carto-positron', center=dict(lat=42.0, lon=-68.5), zoom=5.0),
            height=700,
            margin=dict(l=0, r=0, t=30, b=0),
            title="Key Habitat Areas: Historical Concentrations vs. Current Expansion Zones",
            legend=dict(
                yanchor="top", y=0.98, xanchor="left", x=0.01,
                bgcolor="rgba(255,255,255,0.85)", font=dict(size=11)
            )
        )

        st.plotly_chart(fig_hotspot, use_container_width=True)

    # ---- VIEW 3: RANGE BOUNDARIES ----
    else:

        fig_range = go.Figure()

        bar_data = []
        for _, row in df_map.iterrows():
            bar_data.append({
                'species': row['species'],
                'thermal_affinity': row['thermal_affinity'],
                'hist_south': row['hist_range_south'],
                'hist_north': row['hist_range_north'],
                'curr_south': row['curr_range_south'],
                'curr_north': row['curr_range_north'],
                'trend': row['trend']
            })

        df_range = pd.DataFrame(bar_data).sort_values('curr_south', ascending=True)

        fig_range = go.Figure()

        for _, row in df_range.iterrows():
            color = affinity_colors.get(row['thermal_affinity'], '#999')

            # Historical range (faded)
            fig_range.add_trace(go.Scatter(
                x=[row['hist_south'], row['hist_north']],
                y=[row['species'], row['species']],
                mode='lines+markers',
                line=dict(color=color, width=10, dash='dot'),
                marker=dict(size=8, symbol='line-ns', color=color),
                opacity=0.3,
                name=f"{row['species']} (Historical)",
                hovertemplate=(
                    f"<b>{row['species']}</b> | Historical Range<br>"
                    f"{row['hist_south']}N to {row['hist_north']}N<br>"
                    f"<extra></extra>"
                ),
                showlegend=False
            ))

            # Current range (solid)
            fig_range.add_trace(go.Scatter(
                x=[row['curr_south'], row['curr_north']],
                y=[row['species'], row['species']],
                mode='lines+markers',
                line=dict(color=color, width=10),
                marker=dict(size=10, symbol='line-ns', color=color),
                opacity=0.85,
                name=f"{row['species']} (Current)",
                hovertemplate=(
                    f"<b>{row['species']}</b> | Current Range<br>"
                    f"{row['curr_south']}N to {row['curr_north']}N<br>"
                    f"Trend: {row['trend']}<br>"
                    f"<extra></extra>"
                ),
                showlegend=False
            ))

        # Reference lines for key latitudes
        fig_range.add_vline(x=41.3, line_dash="dash", line_color="rgba(0,0,0,0.3)",
                            annotation_text="Cape Cod (41.3N)", annotation_position="top")
        fig_range.add_vline(x=43.5, line_dash="dash", line_color="rgba(0,0,0,0.3)",
                            annotation_text="Portland, ME (43.5N)", annotation_position="top")
        fig_range.add_vline(x=45.0, line_dash="dash", line_color="rgba(0,0,0,0.2)",
                            annotation_text="US-Canada Border", annotation_position="top")

        fig_range.update_layout(
            title="Latitudinal Range Boundaries: Historical (dotted) vs. Current (solid)",
            xaxis_title="Latitude (degrees N)",
            yaxis_title="",
            template="plotly_white",
            height=600,
            margin=dict(l=220),
            xaxis=dict(range=[33, 48])
        )

        st.plotly_chart(fig_range, use_container_width=True)

    # Species detail panel below map
    st.markdown("### Selected Species Detail")

    map_selected = st.selectbox(
        "Click a species for full migration context:",
        df_map['species'].tolist(),
        key='map_species_detail'
    )

    if map_selected:
        sp = df_spatial[df_spatial['species'] == map_selected].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Shift", f"{sp['shift_km']} km {sp['shift_direction']}")
        with col2:
            st.metric("Historical Centroid", f"{sp['hist_centroid_lat']}N, {abs(sp['hist_centroid_lon'])}W")
        with col3:
            st.metric("Current Centroid", f"{sp['curr_centroid_lat']}N, {abs(sp['curr_centroid_lon'])}W")
        with col4:
            range_expansion = (sp['curr_range_north'] - sp['curr_range_south']) - \
                              (sp['hist_range_north'] - sp['hist_range_south'])
            st.metric("Range Width Change", f"{range_expansion:+.1f} degrees lat")

        st.markdown(f"""
        <div class="insight-box">
        <strong>{sp['species']}</strong> (<em>{sp['scientific_name']}</em>)
        | Thermal Affinity: {sp['thermal_affinity']} | Trend: {sp['trend']}<br><br>
        <strong>Historical Range:</strong> {sp['hist_range_south']}N to {sp['hist_range_north']}N
        (Centroid: {sp['hist_centroid_lat']}N)  | Key area: {sp['hotspot_1_name']}<br><br>
        <strong>Current Range:</strong> {sp['curr_range_south']}N to {sp['curr_range_north']}N
        (Centroid: {sp['curr_centroid_lat']}N)  | Key area: {sp['hotspot_2_name']}<br><br>
        {sp['map_notes']}
        </div>
        """, unsafe_allow_html=True)


# ============================================
# TAB 4: LOBSTER CASE STUDY
# ============================================
with tab4:
    st.markdown("## The American Lobster: A Regional Divergence Case Study")
    st.markdown("""
    <p class="section-description">
    The American lobster (<em>Homarus americanus</em>) presents one of the most compelling
    illustrations of how climate change produces asymmetric outcomes across geography. In Maine,
    moderate warming initially created near-optimal conditions for lobster growth and survival,
    driving a historic boom in commercial landings. In Southern New England, where waters have
    warmed beyond the species' thermal tolerance, the fishery has collapsed by over 90%. This
    divergence, now well-documented in the scientific literature, serves as both a warning about
    the nonlinear nature of climate impacts and a preview of what Maine may face under
    continued warming. The estimated thermal stress threshold for lobster is approximately
    20C in bottom water temperature, a threshold that Southern New England waters now
    routinely exceed during summer months.
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        fig_maine = go.Figure()

        fig_maine.add_trace(go.Scatter(
            x=df_lobster['year'],
            y=df_lobster['maine_millions_lbs'],
            mode='lines+markers',
            fill='tozeroy',
            fillcolor='rgba(42, 157, 143, 0.2)',
            line=dict(color='#2A9D8F', width=3),
            marker=dict(size=7),
            name='Maine Landings',
            hovertemplate='Year: %{x}<br>Landings: %{y}M lbs<extra></extra>'
        ))

        fig_maine.add_annotation(
            x=2016, y=132,
            text="Peak: 132M lbs (2016)",
            showarrow=True,
            arrowhead=2,
            font=dict(size=10)
        )

        fig_maine.add_annotation(
            x=2023, y=93,
            text="93M lbs (2023)",
            showarrow=True,
            arrowhead=2,
            font=dict(size=10)
        )

        fig_maine.update_layout(
            title="Maine: Initial Benefit, Emerging Plateau",
            xaxis_title="Year",
            yaxis_title="Landings (Million lbs)",
            template="plotly_white",
            height=420,
            yaxis=dict(range=[0, 155])
        )

        st.plotly_chart(fig_maine, use_container_width=True)

        maine_peak = df_lobster['maine_millions_lbs'].max()
        maine_latest = df_lobster['maine_millions_lbs'].iloc[-1]
        maine_decline_from_peak = ((maine_latest - maine_peak) / maine_peak) * 100

        st.markdown(f"""
        <div class="insight-box">
        <strong>Maine: Boom Approaching a Ceiling</strong><br><br>
        Landings surged from 28 million lbs in 1990 to a peak of 132 million lbs in 2016, a
        371% increase driven by improved juvenile survival in warmer waters. However, since 2016
        landings have declined {abs(maine_decline_from_peak):.0f}% from peak. Rising bottom water
        temperatures are compressing the optimal thermal window, and shell disease, previously
        absent in Maine waters, has been detected with increasing frequency north of Cape Cod.
        The Maine lobster industry, valued at over $500M annually, faces significant economic
        exposure to continued warming.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        fig_sne = go.Figure()

        fig_sne.add_trace(go.Scatter(
            x=df_lobster['year'],
            y=df_lobster['southern_ne_millions_lbs'],
            mode='lines+markers',
            fill='tozeroy',
            fillcolor='rgba(230, 57, 70, 0.2)',
            line=dict(color='#E63946', width=3),
            marker=dict(size=7),
            name='S. New England Landings',
            hovertemplate='Year: %{x}<br>Landings: %{y:.1f}M lbs<extra></extra>'
        ))

        fig_sne.update_layout(
            title="Southern New England: Thermal Collapse",
            xaxis_title="Year",
            yaxis_title="Landings (Million lbs)",
            template="plotly_white",
            height=420,
            yaxis=dict(range=[0, 28])
        )

        st.plotly_chart(fig_sne, use_container_width=True)

        st.markdown("""
        <div class="insight-box">
        <strong>Southern New England: A Collapse Driven by Warming</strong><br><br>
        Landings fell from 22 million lbs (1990) to 1.5 million lbs (2023), a 93% decline.
        Bottom water temperatures in Long Island Sound and Narragansett Bay now regularly exceed
        20C during summer, surpassing the lobster thermal stress threshold. Epizootic shell
        disease prevalence, which is strongly temperature-dependent, reached over 30% of sampled
        lobsters in some years. The collapse was not primarily driven by overfishing; it was
        driven by habitat loss due to warming. This region now serves as a reference case for
        projecting future impacts in the Gulf of Maine.
        </div>
        """, unsafe_allow_html=True)

    # Combined comparison with temperature overlay
    st.markdown("### Regional Comparison with Temperature Context")

    fig_compare = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]]
    )

    fig_compare.add_trace(
        go.Scatter(
            x=df_lobster['year'], y=df_lobster['maine_millions_lbs'],
            name="Maine Landings (M lbs)", line=dict(color='#2A9D8F', width=3),
            mode='lines+markers', marker=dict(size=6)
        ),
        secondary_y=False
    )

    fig_compare.add_trace(
        go.Scatter(
            x=df_lobster['year'], y=df_lobster['southern_ne_millions_lbs'],
            name="S. New England Landings (M lbs)", line=dict(color='#E63946', width=3),
            mode='lines+markers', marker=dict(size=6)
        ),
        secondary_y=False
    )

    fig_compare.add_trace(
        go.Scatter(
            x=df_lobster['year'], y=df_lobster['sne_avg_bottom_temp_c'],
            name="S. New England Bottom Temp (C)",
            line=dict(color='#D4A373', width=2, dash='dot'),
            mode='lines'
        ),
        secondary_y=True
    )

    fig_compare.add_hline(y=20, line_dash="dash", line_color="red",
                          annotation_text="Lobster Thermal Stress Threshold (20C)",
                          annotation_position="top left",
                          secondary_y=True)

    fig_compare.update_layout(
        title="Lobster Landings and Bottom Water Temperature: Diverging Regional Trajectories",
        template="plotly_white",
        height=450,
        hovermode="x unified",
        legend=dict(yanchor="top", y=-0.15, xanchor="center", x=0.5, orientation="h")
    )
    fig_compare.update_yaxes(
        title_text="Landings (Million lbs)", secondary_y=False, color='#1D3557'
    )
    fig_compare.update_yaxes(
        title_text="Bottom Temperature (C)", secondary_y=True, color='#D4A373'
    )

    st.plotly_chart(fig_compare, use_container_width=True)

    # Economic context
    st.markdown("### Economic Impact")

    col1, col2 = st.columns(2)

    with col1:
        fig_value = go.Figure()
        fig_value.add_trace(go.Bar(
            x=df_lobster['year'],
            y=df_lobster['maine_value_millions'],
            marker_color='#2A9D8F',
            name='Maine Lobster Value',
            hovertemplate='Year: %{x}<br>Value: $%{y}M<extra></extra>'
        ))
        fig_value.update_layout(
            title="Maine Lobster Industry Annual Value",
            xaxis_title="Year",
            yaxis_title="Dockside Value ($ Millions)",
            template="plotly_white",
            height=380,
            showlegend=False
        )
        st.plotly_chart(fig_value, use_container_width=True)

    with col2:
        st.markdown("""
        <div class="insight-box">
        <strong>Economic Exposure</strong><br><br>
        The Maine lobster fishery is the most valuable single-species fishery on the U.S.
        Atlantic coast, with dockside value reaching $730 million in 2021. The industry
        supports an estimated 4,500 licensed harvesters and generates substantial economic
        activity across supply chains, tourism, and coastal communities.<br><br>
        The concentration of economic value in a single climate-sensitive species creates
        significant vulnerability. Diversification strategies, including expansion into Jonah
        crab, aquaculture, and emerging warm-water species, are under active exploration
        throughout the region.
        </div>
        """, unsafe_allow_html=True)


# ============================================
# TAB 5: ECOSYSTEM INDICATORS
# ============================================
with tab5:
    st.markdown("## Ecosystem-Level Indicators")
    st.markdown("""
    <p class="section-description">
    Individual species responses aggregate into broader ecosystem-level changes. The Gulf of
    Maine is experiencing a fundamental restructuring of its biological community, characterized
    by declining cold-water species richness, increasing warm-water species incursion, reduced
    zooplankton energy density, and increasing frequency of marine heatwave events. The following
    indicators provide a multi-dimensional view of ecosystem transformation.
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Community composition shift
        fig_community = go.Figure()

        fig_community.add_trace(go.Scatter(
            x=df_ecosystem['year'],
            y=df_ecosystem['cold_species_richness'],
            mode='lines+markers',
            name='Cold-Water Species Richness',
            line=dict(color='#457B9D', width=3),
            marker=dict(size=6)
        ))

        fig_community.add_trace(go.Scatter(
            x=df_ecosystem['year'],
            y=df_ecosystem['warm_species_richness'],
            mode='lines+markers',
            name='Warm-Water Species Richness',
            line=dict(color='#E63946', width=3),
            marker=dict(size=6)
        ))

        fig_community.update_layout(
            title="Community Composition Shift: Cold vs. Warm-Water Species",
            xaxis_title="Year",
            yaxis_title="Species Richness (Index)",
            template="plotly_white",
            height=430,
            hovermode="x unified",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )

        st.plotly_chart(fig_community, use_container_width=True)

    with col2:
        # Calanus copepod abundance
        fig_calanus = go.Figure()

        fig_calanus.add_trace(go.Scatter(
            x=df_ecosystem['year'],
            y=df_ecosystem['calanus_abundance_index'],
            mode='lines+markers',
            fill='tozeroy',
            fillcolor='rgba(69, 123, 157, 0.2)',
            line=dict(color='#457B9D', width=3),
            marker=dict(size=6),
            name='Calanus finmarchicus Index',
            hovertemplate='Year: %{x}<br>Index: %{y}<extra></extra>'
        ))

        fig_calanus.update_layout(
            title="Calanus finmarchicus Abundance (Keystone Zooplankton)",
            xaxis_title="Year",
            yaxis_title="Abundance Index (2000 = 100)",
            template="plotly_white",
            height=430,
        )

        st.plotly_chart(fig_calanus, use_container_width=True)

    # Marine heatwave days and right whale sightings
    col1, col2 = st.columns(2)

    with col1:
        fig_mhw = go.Figure()

        fig_mhw.add_trace(go.Bar(
            x=df_ecosystem['year'],
            y=df_ecosystem['marine_heatwave_days'],
            marker_color=[
                '#D4A373' if d < 30 else '#E07A5F' if d < 50 else '#E63946'
                for d in df_ecosystem['marine_heatwave_days']
            ],
            hovertemplate='Year: %{x}<br>MHW Days: %{y}<extra></extra>'
        ))

        fig_mhw.add_annotation(
            x=2012, y=80,
            text="2012: Unprecedented<br>heatwave event",
            showarrow=True, arrowhead=2,
            font=dict(size=10)
        )

        fig_mhw.update_layout(
            title="Annual Marine Heatwave Days in the Gulf of Maine",
            xaxis_title="Year",
            yaxis_title="Days Exceeding 90th Percentile SST",
            template="plotly_white",
            height=430,
            showlegend=False
        )

        st.plotly_chart(fig_mhw, use_container_width=True)

    with col2:
        fig_rw = go.Figure()

        fig_rw.add_trace(go.Scatter(
            x=df_ecosystem['year'],
            y=df_ecosystem['right_whale_sightings_gom'],
            mode='lines+markers',
            fill='tozeroy',
            fillcolor='rgba(29, 53, 87, 0.15)',
            line=dict(color='#1D3557', width=3),
            marker=dict(size=6),
            name='Right Whale Sightings'
        ))

        fig_rw.update_layout(
            title="North Atlantic Right Whale Sightings in Gulf of Maine",
            xaxis_title="Year",
            yaxis_title="Documented Sightings",
            template="plotly_white",
            height=430,
        )

        st.plotly_chart(fig_rw, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <strong>Ecosystem Restructuring: Interconnected Impacts</strong><br><br>
    The decline of <em>Calanus finmarchicus</em>, the lipid-rich copepod that historically
    dominated Gulf of Maine zooplankton, represents a foundational shift in the food web.
    <em>Calanus</em> is being replaced by smaller, less energy-dense copepod species
    (e.g., <em>Centropages typicus</em>) that favor warmer conditions. This shift propagates
    upward through the food web: Atlantic herring and sand lance, which depend on
    <em>Calanus</em>, have declined, reducing prey availability for seabirds (Atlantic puffins),
    marine mammals, and predatory fish.<br><br>
    The North Atlantic right whale, with fewer than 360 individuals remaining, has shifted
    its foraging distribution out of the Gulf of Maine and into the Gulf of St. Lawrence,
    following the northward movement of its copepod prey. This redistribution has moved whales
    into areas with less regulatory protection and higher ship strike risk, compounding
    conservation challenges for this critically endangered species.<br><br>
    Meanwhile, the increasing frequency and intensity of marine heatwave events accelerates
    species redistribution and creates acute stress episodes that can trigger sudden population
    declines, as observed with northern shrimp and lobster in Southern New England.
    </div>
    """, unsafe_allow_html=True)


# ============================================
# TAB 6: FOOD WEB
# ============================================
with tab6:
    st.markdown("## Gulf of Maine Trophic Network")
    st.markdown("""
    <p class="section-description">
    Climate-driven species redistribution does not occur in isolation. Changes at any trophic
    level cascade through the food web, amplifying or buffering impacts on connected species.
    The interactive network below maps the major energy transfer pathways in the Gulf of Maine
    ecosystem and illustrates how warming is restructuring these connections. Select any species
    to highlight its trophic relationships and understand how its decline, expansion, or shift
    propagates through the system.
    </p>
    """, unsafe_allow_html=True)

    # Build node lookup
    node_lookup = {n['id']: n for n in fw_nodes}

    # Controls
    col_fw1, col_fw2 = st.columns([1, 2])

    with col_fw1:
        fw_highlight = st.selectbox(
            "Highlight a Species / Group",
            options=['All Connections'] + [n['label'] for n in fw_nodes],
            index=0,
            key='fw_species_select'
        )

        fw_color_mode = st.radio(
            "Color By",
            ["Population Trend", "Thermal Affinity", "Trophic Level"],
            key='fw_color_mode'
        )

    # Determine which node is highlighted
    highlight_id = None
    if fw_highlight != 'All Connections':
        for n in fw_nodes:
            if n['label'] == fw_highlight:
                highlight_id = n['id']
                break

    # Get connected edges and nodes for highlighting
    connected_edges = []
    connected_node_ids = set()
    if highlight_id:
        for e in fw_edges:
            if e['source'] == highlight_id or e['target'] == highlight_id:
                connected_edges.append(e)
                connected_node_ids.add(e['source'])
                connected_node_ids.add(e['target'])
        connected_node_ids.add(highlight_id)

    # Position nodes by trophic level (y) with horizontal spread (x)
    # Manual x positioning to avoid overlap
    node_positions = {
        'phyto': (0.5, 0),
        'calanus': (0.2, 1), 'centropages': (0.5, 1), 'krill': (0.8, 1),
        'herring': (0.1, 2), 'sandlance': (0.3, 2), 'squid': (0.55, 2),
        'shrimp': (0.75, 2), 'lobster': (0.92, 2),
        'cod': (0.08, 3), 'mackerel': (0.28, 3), 'bsb': (0.48, 3),
        'flounder': (0.68, 3), 'puffin': (0.85, 3),
        'tuna': (0.12, 4), 'right_whale': (0.35, 4), 'humpback': (0.58, 4),
        'seals': (0.8, 4),
    }

    # Color logic
    def get_node_color(node, mode):
        if mode == "Population Trend":
            return node['status_color']
        elif mode == "Thermal Affinity":
            cat = node.get('category', '')
            if 'Cold-water' in cat:
                return '#457B9D'
            elif 'Warm-water' in cat:
                return '#E63946'
            elif 'Cool-water' in cat:
                return '#D4A373'
            else:
                return '#8DB580'
        else:  # Trophic Level
            tl = node['trophic_level']
            tl_colors = {1: '#8DB580', 2: '#A8D5BA', 3: '#D4A373',
                         3.5: '#C4956A', 4: '#E07A5F', 4.5: '#C0392B', 5: '#922B21'}
            return tl_colors.get(tl, '#999')

    # Build the network figure
    fig_fw = go.Figure()

    # Trophic level background bands
    tl_labels = ['Primary Producers', 'Zooplankton', 'Forage Species',
                 'Mid-Level Predators', 'Top Predators']
    for i, label in enumerate(tl_labels):
        fig_fw.add_shape(
            type="rect",
            x0=-0.05, x1=1.05,
            y0=i - 0.35, y1=i + 0.35,
            fillcolor=['rgba(141,181,128,0.08)', 'rgba(168,213,186,0.08)',
                       'rgba(212,163,115,0.08)', 'rgba(224,122,95,0.08)',
                       'rgba(146,43,33,0.08)'][i],
            line=dict(width=0),
            layer='below'
        )
        fig_fw.add_annotation(
            x=-0.08, y=i,
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(size=10, color='#4A6274'),
            textangle=-90,
            xanchor='right'
        )

    # Draw edges
    strength_width = {'critical': 4, 'strong': 2.5, 'moderate': 1.5, 'weak': 0.8}

    for e in fw_edges:
        src_pos = node_positions.get(e['source'])
        tgt_pos = node_positions.get(e['target'])
        if not src_pos or not tgt_pos:
            continue

        # Determine edge visibility
        if highlight_id:
            if e in connected_edges:
                edge_opacity = 0.7
                edge_width = strength_width.get(e['strength'], 1.5) * 1.3
            else:
                edge_opacity = 0.06
                edge_width = 0.5
        else:
            edge_opacity = 0.25
            edge_width = strength_width.get(e['strength'], 1.5)

        # Edge color based on source node trend
        src_node = node_lookup[e['source']]
        edge_color = src_node['status_color']

        # Slight curve using a bezier midpoint
        mid_x = (src_pos[0] + tgt_pos[0]) / 2 + np.random.uniform(-0.02, 0.02)
        mid_y = (src_pos[1] + tgt_pos[1]) / 2

        fig_fw.add_trace(go.Scatter(
            x=[src_pos[0], mid_x, tgt_pos[0]],
            y=[src_pos[1], mid_y, tgt_pos[1]],
            mode='lines',
            line=dict(
                color=edge_color,
                width=edge_width,
            ),
            opacity=edge_opacity,
            hoverinfo='skip',
            showlegend=False
        ))

    # Draw nodes
    for n in fw_nodes:
        pos = node_positions.get(n['id'])
        if not pos:
            continue

        color = get_node_color(n, fw_color_mode)

        # Determine node visibility
        if highlight_id:
            if n['id'] in connected_node_ids:
                opacity = 1.0
                size = 28 if n['id'] == highlight_id else 22
                border_width = 3 if n['id'] == highlight_id else 1
            else:
                opacity = 0.15
                size = 16
                border_width = 0
        else:
            opacity = 0.9
            size = 22
            border_width = 1

        # Trend indicator symbol
        trend_markers = {
            'Declining': 'triangle-down', 'Collapsed': 'x',
            'Expanding': 'triangle-up', 'Shifting North': 'arrow-up',
            'Variable': 'diamond', 'Stable/Increasing': 'circle',
            'Mixed': 'square', 'Plateauing': 'diamond'
        }
        symbol = trend_markers.get(n['trend'], 'circle')

        fig_fw.add_trace(go.Scatter(
            x=[pos[0]],
            y=[pos[1]],
            mode='markers+text',
            marker=dict(
                size=size,
                color=color,
                opacity=opacity,
                symbol=symbol,
                line=dict(width=border_width, color='#1D3557')
            ),
            text=[n['label']],
            textposition='top center',
            textfont=dict(size=9, color='#1D3557' if opacity > 0.5 else '#CCC'),
            hovertemplate=(
                f"<b>{n['label']}</b><br>"
                f"Category: {n['category']}<br>"
                f"Trophic Level: {n['trophic_level']}<br>"
                f"Trend: {n['trend']}<br>"
                f"---<br>"
                f"{n['notes'][:250]}<br>"
                f"<extra></extra>"
            ),
            showlegend=False
        ))

    fig_fw.update_layout(
        height=720,
        template='plotly_white',
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.15, 1.1]
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.6, 4.7],
            scaleanchor='x', scaleratio=0.6
        ),
        margin=dict(l=80, r=20, t=40, b=20),
        title=dict(
            text="Trophic Network: Energy Flow from Primary Producers to Top Predators",
            font=dict(size=14)
        ),
        plot_bgcolor='white'
    )

    st.plotly_chart(fig_fw, use_container_width=True)

    # Legend for color mode
    if fw_color_mode == "Population Trend":
        legend_items = [
            ('#E63946', 'Expanding / Warm-water increase'),
            ('#D4A373', 'Variable / Mixed / Shifting'),
            ('#457B9D', 'Declining'),
            ('#1D3557', 'Collapsed'),
            ('#8DB580', 'Stable or Variable baseline')
        ]
    elif fw_color_mode == "Thermal Affinity":
        legend_items = [
            ('#457B9D', 'Cold-water species'),
            ('#D4A373', 'Cool-water species'),
            ('#E63946', 'Warm-water species'),
            ('#8DB580', 'Not thermally classified')
        ]
    else:
        legend_items = [
            ('#8DB580', 'Trophic Level 1: Primary Producers'),
            ('#A8D5BA', 'Trophic Level 2: Zooplankton'),
            ('#D4A373', 'Trophic Level 3: Forage Species'),
            ('#E07A5F', 'Trophic Level 4: Mid-Level Predators'),
            ('#922B21', 'Trophic Level 5: Top Predators')
        ]

    legend_html = '<div style="display: flex; flex-wrap: wrap; gap: 1rem; margin: 0.5rem 0;">'
    for color, label in legend_items:
        legend_html += (
            f'<div style="display: flex; align-items: center; gap: 0.4rem;">'
            f'<span style="display: inline-block; width: 14px; height: 14px; '
            f'background-color: {color}; border-radius: 3px;"></span>'
            f'<span style="font-size: 0.85rem; color: #4A6274;">{label}</span></div>'
        )
    legend_html += '</div>'
    st.markdown(legend_html, unsafe_allow_html=True)

    # Detail panel for selected species
    if highlight_id:
        st.markdown("---")
        hl_node = node_lookup[highlight_id]

        # Find prey (what it eats) and predators (what eats it)
        prey_of = [node_lookup[e['source']]['label'] for e in connected_edges
                    if e['target'] == highlight_id]
        predators_of = [node_lookup[e['target']]['label'] for e in connected_edges
                        if e['source'] == highlight_id]

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            st.markdown(f"#### {hl_node['label']}")
            st.markdown(f"""
            <div class="insight-box">
            <strong>Category:</strong> {hl_node['category']}<br>
            <strong>Trophic Level:</strong> {hl_node['trophic_level']}<br>
            <strong>Population Trend:</strong> {hl_node['trend']}<br><br>
            {hl_node['notes']}
            </div>
            """, unsafe_allow_html=True)

        with col_d2:
            st.markdown("#### Trophic Connections")

            if prey_of:
                st.markdown(f"**Prey / Energy Sources ({len(prey_of)}):**")
                for p in prey_of:
                    # Find edge strength
                    strength = 'unknown'
                    for e in connected_edges:
                        if e['source'] == [n['id'] for n in fw_nodes if n['label'] == p][0] \
                                and e['target'] == highlight_id:
                            strength = e['strength']
                            break
                    strength_badge = {
                        'critical': 'CRITICAL', 'strong': 'Strong',
                        'moderate': 'Moderate', 'weak': 'Weak'
                    }.get(strength, '')
                    p_node = [n for n in fw_nodes if n['label'] == p][0]
                    st.markdown(
                        f"- **{p}** ({p_node['trend']}) "
                        f"*[{strength_badge}]*"
                    )
            else:
                st.markdown("*Primary producer / base of food web*")

            if predators_of:
                st.markdown(f"**Predators / Consumers ({len(predators_of)}):**")
                for pr in predators_of:
                    strength = 'unknown'
                    for e in connected_edges:
                        if e['target'] == [n['id'] for n in fw_nodes if n['label'] == pr][0] \
                                and e['source'] == highlight_id:
                            strength = e['strength']
                            break
                    strength_badge = {
                        'critical': 'CRITICAL', 'strong': 'Strong',
                        'moderate': 'Moderate', 'weak': 'Weak'
                    }.get(strength, '')
                    pr_node = [n for n in fw_nodes if n['label'] == pr][0]
                    st.markdown(
                        f"- **{pr}** ({pr_node['trend']}) "
                        f"*[{strength_badge}]*"
                    )

    # Cascade narrative
    st.markdown("---")
    st.markdown("### Climate Cascade Pathways")
    st.markdown("""
    <p class="section-description">
    Three primary cascade pathways are restructuring the Gulf of Maine food web:
    </p>
    """, unsafe_allow_html=True)

    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        st.markdown("""
        <div class="insight-box">
        <strong>The Copepod-to-Whale Cascade</strong><br><br>
        Warming reduces <em>Calanus finmarchicus</em> abundance, which diminishes
        the prey base for Atlantic herring and sand lance. Right whales, as obligate
        <em>Calanus</em> feeders, have relocated from the Gulf of Maine to the Gulf of
        St. Lawrence in search of adequate prey concentrations. This movement into
        less-regulated waters has increased their exposure to vessel strikes and
        fishing gear entanglement, compounding conservation risks for a species with
        fewer than 360 remaining individuals.
        </div>
        """, unsafe_allow_html=True)

    with col_c2:
        st.markdown("""
        <div class="insight-box">
        <strong>The Forage Fish-to-Seabird Cascade</strong><br><br>
        Declining herring and sand lance populations directly impact Atlantic puffin
        breeding colonies on Maine's offshore islands. Puffin adults, unable to find
        sufficient cold-water prey, have been documented bringing butterfish to their chicks.
        Butterfish, a warm-water species expanding northward, are too large for chicks to
        swallow, leading to reduced fledging success. This represents a tangible example
        of how gradual temperature change translates into abrupt reproductive failure.
        </div>
        """, unsafe_allow_html=True)

    with col_c3:
        st.markdown("""
        <div class="insight-box">
        <strong>The Predator Release Cascade</strong><br><br>
        The decline of Atlantic cod, historically the dominant groundfish predator in the
        Gulf of Maine, has released predation pressure on lobster, crabs, and other
        invertebrates. This "predator release" effect partially explains the Maine lobster
        boom: with fewer cod consuming juvenile lobsters, survival rates increased at the
        same time warming improved growth conditions. However, as the thermal window
        continues to shift, this temporary benefit may reverse if lobster populations are
        pushed past their own thermal tolerance.
        </div>
        """, unsafe_allow_html=True)


# ============================================
# TAB 7: DATA & METHODS
# ============================================
with tab7:
    st.markdown("## Data Sources and Methodology")

    st.markdown("""
    <p class="section-description">
    This dashboard synthesizes data from multiple authoritative sources to provide an integrated
    view of climate impacts on the Gulf of Maine marine ecosystem. All temperature and fisheries
    data are derived from publicly available federal and state databases. Species response
    parameters are compiled from peer-reviewed literature and validated against NOAA stock
    assessment reports.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### Primary Data Sources

    | Dataset | Source | Temporal Coverage | Spatial Resolution |
    |---------|--------|-------------------|--------------------|
    | Sea Surface Temperature | NOAA ERSST v5 (Huang et al., 2017) | 1854-present (monthly) | 2 x 2 degree grid |
    | Bottom Trawl Survey | NOAA NEFSC Spring/Fall Trawl Survey | 1963-present (biannual) | Station-level |
    | Lobster Landings | ASMFC, Maine DMR, NOAA Fisheries | 1981-present (annual) | State/region level |
    | Species Thermal Preferences | FishBase, SeaLifeBase, Published Literature | Varies | Species-level |
    | Ecosystem Indicators | Gulf of Maine Research Institute, NOAA | 2000-present | Regional |
    | Right Whale Sightings | NOAA, New England Aquarium | 1980-present | Sighting-level |

    ### Methodology

    **Temperature Analysis:** Annual mean sea surface temperature is calculated from NOAA ERSST
    v5 monthly data for the core Gulf of Maine region (42-44.5N, 66-70W). Anomalies are computed
    relative to the NOAA standard 1901-2000 baseline period. Linear trend estimation uses
    ordinary least squares regression. The 5-year rolling average provides a smoothed view of
    the underlying warming trend.

    **Species Range Shifts:** Latitudinal range shift estimates are derived from distribution
    centroid analysis of NOAA NEFSC bottom trawl survey data, supplemented by published
    literature values. Centroid analysis calculates the biomass-weighted mean latitude of each
    species across survey stations for each year, then fits a linear trend over the available
    time series. Bathymetric (depth) shifts are calculated analogously using biomass-weighted
    mean depth.

    **Population Change Estimates:** Population change percentages represent the approximate
    change in survey biomass indices or commercial landings over the available time series.
    These are simplified indicators and should be interpreted with caution, as population dynamics
    reflect multiple interacting factors including fishing pressure, predation, disease, and
    habitat quality in addition to temperature.

    **Ecosystem Indicators:** Community composition indices are derived from presence/absence
    data in NOAA trawl surveys, classified by species thermal affinity. Marine heatwave days
    are calculated as the number of days per year when SST exceeds the 90th percentile of the
    1982-2011 climatology for the Gulf of Maine region.

    ### Key References

    1. **Pershing, A.J., et al. (2015).** Slow adaptation in the face of rapid warming leads
       to collapse of the Gulf of Maine cod fishery. *Science*, 350(6262), 809-812.
       doi:10.1126/science.aac9819

    2. **Pershing, A.J., et al. (2021).** Climate impacts on the Gulf of Maine ecosystem:
       A review of observed and expected changes in 2050 from rising temperatures.
       *Elementa: Science of the Anthropocene*, 9(1), 00076.

    3. **Mills, K.E., et al. (2013).** Fisheries management in a changing climate: Lessons
       from the 2012 ocean heat wave in the Northwest Atlantic. *Oceanography*, 26(2), 191-195.

    4. **Huang, B., et al. (2017).** Extended Reconstructed Sea Surface Temperature, Version 5
       (ERSSTv5): Upgrades, validations, and intercomparisons. *Journal of Climate*, 30(20),
       8179-8205.

    5. **Kleisner, K.M., et al. (2017).** Marine species distribution shifts on the U.S.
       Northeast Continental Shelf under continued ocean warming. *Progress in Oceanography*,
       153, 24-36.

    6. **Steneck, R.S., & Wahle, R.A. (2013).** American lobster dynamics in a brave new
       ocean. *Canadian Journal of Fisheries and Aquatic Sciences*, 70(11), 1612-1624.

    7. **Record, N.R., et al. (2019).** Rapid climate-driven circulation changes threaten
       conservation of endangered North Atlantic right whales. *Oceanography*, 32(2), 162-169.

    8. **Meyer-Gutbrod, E.L., et al. (2021).** Ocean regime shift is driving collapse of the
       North Atlantic right whale population. *Oceanography*, 34(3), 22-31.

    ### Limitations and Caveats

    This dashboard presents a synthesis of multiple data sources with varying spatial and
    temporal resolutions. Species-level parameters (range shift rates, population changes)
    are compiled estimates that incorporate uncertainty not fully captured in the presented
    values. Economic values represent approximate dockside/landed values and do not capture
    full supply chain economic impacts. Ecosystem indicators are simplified indices designed
    to illustrate broad trends and should not be used as the basis for management decisions
    without consultation of primary data sources and stock assessments.

    The dashboard uses representative data values compiled from the cited sources. For
    research or management applications, users should consult the primary data sources
    directly.
    """)

    # Download buttons
    st.markdown("### Download Data")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.download_button(
            label="Sea Surface Temperature (CSV)",
            data=df_sst.to_csv(index=False),
            file_name="gulf_of_maine_sst_data.csv",
            mime="text/csv"
        )

    with col2:
        st.download_button(
            label="Species Response Data (CSV)",
            data=df_species.to_csv(index=False),
            file_name="species_climate_responses.csv",
            mime="text/csv"
        )

    with col3:
        st.download_button(
            label="Lobster Landings (CSV)",
            data=df_lobster.to_csv(index=False),
            file_name="lobster_landings_regional.csv",
            mime="text/csv"
        )

    with col4:
        st.download_button(
            label="Ecosystem Indicators (CSV)",
            data=df_ecosystem.to_csv(index=False),
            file_name="ecosystem_indicators.csv",
            mime="text/csv"
        )


# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #4A6274; font-size: 0.9rem;'>
    <p>Gulf of Maine Climate Impact Dashboard | Developed for the New England Aquarium
    - Anderson Cabot Center for Ocean Life</p>
    <p>Data Sources: NOAA ERSST v5, NOAA NEFSC, ASMFC, Gulf of Maine Research Institute
    | Built with Streamlit and Plotly</p>
    <p style='font-size: 0.8rem; color: #7A9AAA;'>Last Updated: February 2026 | For
    questions or collaboration inquiries, contact the author.</p>
</div>
""", unsafe_allow_html=True)
