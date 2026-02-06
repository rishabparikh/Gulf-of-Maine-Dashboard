# Gulf of Maine Climate Impact Dashboard

An interactive research dashboard analyzing marine species redistribution in response to accelerated ocean warming in the Northwest Atlantic. Developed as an independent research project for the New England Aquarium — Anderson Cabot Center for Ocean Life.

**Author:** Rishab  
**Affiliation:** Northeastern University  
**Prepared for:** New England Aquarium — Anderson Cabot Center for Ocean Life

---

## Overview

The Gulf of Maine has warmed faster than 99% of the global ocean over the past four decades, with sea surface temperatures increasing at approximately three times the global average rate. This accelerated warming is fundamentally restructuring the marine ecosystem — driving cold-adapted species northward or to greater depths while enabling warm-water species to colonize previously unsuitable habitat.

This dashboard provides an interactive synthesis of temperature trends, species-level responses, fisheries case studies, and ecosystem-wide indicators to characterize the scope and pace of these changes. It is designed to communicate complex ecological data in an accessible format for researchers, educators, policymakers, and the general public.

---

## Dashboard Sections

### 1. Sea Surface Temperature Analysis
- 42-year annual mean SST time series (1982-2024) with linear trend and 5-year rolling average
- Temperature anomaly visualization relative to the NOAA 1901-2000 baseline
- Decadal comparison showing the acceleration of warming over time
- Adjustable year range and unit conversion (Celsius / Fahrenheit)

### 2. Species Redistribution Analysis
- Latitudinal range shift estimates for 12 ecologically and commercially significant species
- Thermal tolerance profiles overlaid against current and historical Gulf of Maine conditions
- Bathymetric (depth) shift analysis showing vertical redistribution patterns
- Population change vs. range shift scatter plot with economic value context
- Detailed species profiles with scientific names, thermal parameters, and trend descriptions

### 3. Lobster Case Study: Regional Divergence
- Side-by-side comparison of Maine vs. Southern New England lobster landings (1990-2023)
- Bottom water temperature overlay illustrating the thermal stress mechanism
- Economic impact analysis including dockside value trends for the Maine industry
- Discussion of shell disease prevalence and its relationship to warming

### 4. Ecosystem-Level Indicators
- Cold-water vs. warm-water species richness trends (community composition shift)
- Calanus finmarchicus copepod abundance index (foundational food web change)
- Annual marine heatwave frequency (days exceeding 90th percentile SST)
- North Atlantic right whale sighting trends in the Gulf of Maine
- Integrated narrative on cascading food web impacts

### 5. Data and Methods
- Complete source documentation with temporal and spatial resolution details
- Methodology descriptions for all derived metrics
- Eight peer-reviewed references with DOIs
- Limitations and caveats disclosure
- Downloadable CSV exports for all datasets

---

## Species Covered

| Species | Scientific Name | Thermal Affinity | Trend |
|---------|----------------|-------------------|-------|
| Atlantic Cod | *Gadus morhua* | Cold-water | Declining |
| Northern Shrimp | *Pandalus borealis* | Cold-water | Collapsed |
| American Lobster (Maine) | *Homarus americanus* | Cool-water | Plateauing |
| American Lobster (S. New England) | *Homarus americanus* | Cool-water | Declining |
| Atlantic Herring | *Clupea harengus* | Cold-water | Declining |
| Atlantic Mackerel | *Scomber scombrus* | Cool-water | Shifting North |
| Black Sea Bass | *Centropristis striata* | Warm-water | Expanding |
| Summer Flounder | *Paralichthys dentatus* | Warm-water | Expanding |
| Longfin Squid | *Doryteuthis pealeii* | Warm-water | Expanding |
| Bluefin Tuna | *Thunnus thynnus* | Warm-water | Expanding |
| Jonah Crab | *Cancer borealis* | Cool-water | Expanding |
| *Calanus finmarchicus* | *Calanus finmarchicus* | Cold-water | Declining |

---

## Running Locally

```bash
# Clone or download the project files
# Navigate to the project directory

# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run gulf_of_maine_dashboard.py
```

The application will open in your default browser at `http://localhost:8501`.

---

## Deployment (Streamlit Community Cloud)

1. Create a GitHub repository containing `gulf_of_maine_dashboard.py` and `requirements.txt`.
2. Navigate to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Select your repository and set the main file path to `gulf_of_maine_dashboard.py`.
4. Deploy. The application will be publicly accessible within approximately two minutes.

---

## Project Structure

```
gulf-of-maine-dashboard/
    gulf_of_maine_dashboard.py          Main Streamlit application
    requirements.txt                    Python dependencies
    README.md                           Project documentation
```

---

## Data Sources

| Dataset | Source | Description |
|---------|--------|-------------|
| Sea Surface Temperature | NOAA ERSST v5 | Extended Reconstructed SST, monthly gridded data (1854-present) |
| Bottom Trawl Survey | NOAA NEFSC | Northeast Fisheries Science Center spring/fall survey (1963-present) |
| Lobster Landings | ASMFC, Maine DMR | Atlantic States Marine Fisheries Commission regional data |
| Species Thermal Preferences | FishBase, Published Literature | Compiled from peer-reviewed sources |
| Ecosystem Indicators | Gulf of Maine Research Institute | Regional ecosystem monitoring data |
| Right Whale Sightings | NOAA, New England Aquarium | Systematic sighting records |

---

## Key References

1. Pershing, A.J., et al. (2015). Slow adaptation in the face of rapid warming leads to collapse of the Gulf of Maine cod fishery. *Science*, 350(6262), 809-812.

2. Pershing, A.J., et al. (2021). Climate impacts on the Gulf of Maine ecosystem: A review of observed and expected changes in 2050. *Elementa: Science of the Anthropocene*, 9(1).

3. Mills, K.E., et al. (2013). Fisheries management in a changing climate: Lessons from the 2012 ocean heat wave. *Oceanography*, 26(2), 191-195.

4. Huang, B., et al. (2017). Extended Reconstructed Sea Surface Temperature, Version 5. *Journal of Climate*, 30(20), 8179-8205.

5. Kleisner, K.M., et al. (2017). Marine species distribution shifts on the U.S. Northeast Continental Shelf under continued ocean warming. *Progress in Oceanography*, 153, 24-36.

6. Steneck, R.S., & Wahle, R.A. (2013). American lobster dynamics in a brave new ocean. *Canadian Journal of Fisheries and Aquatic Sciences*, 70(11), 1612-1624.

7. Record, N.R., et al. (2019). Rapid climate-driven circulation changes threaten conservation of endangered North Atlantic right whales. *Oceanography*, 32(2), 162-169.

8. Meyer-Gutbrod, E.L., et al. (2021). Ocean regime shift is driving collapse of the North Atlantic right whale population. *Oceanography*, 34(3), 22-31.

---

## Limitations

This dashboard presents a synthesis of multiple data sources with varying spatial and temporal resolutions. Species-level parameters are compiled estimates that incorporate uncertainty not fully captured in the presented values. Economic values represent approximate dockside/landed values. For research or management applications, users should consult primary data sources and stock assessments directly.

---

## License

This project is for educational and research purposes. All data sources retain their original licenses and usage terms.
