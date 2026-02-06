# 🌊 Gulf of Maine Climate Impact Dashboard

An interactive dashboard tracking marine species shifts in one of the fastest-warming ocean regions on Earth.

**Developed by:** Rishab  
**For:** New England Aquarium - Anderson Cabot Center for Ocean Life

---

## 🚀 Live Demo

[**View the Dashboard →**](https://your-app-name.streamlit.app)  
*(Update this link after deployment)*

---

## 📊 Features

- **Interactive Temperature Trends**: Explore 40+ years of sea surface temperature data with adjustable year ranges and unit conversion (°C/°F)
- **Species Range Shifts**: Visualize how marine species are moving in response to warming waters
- **Lobster Case Study**: Compare the diverging fates of lobster populations in Maine vs. Southern New England
- **Downloadable Data**: Export all datasets as CSV files

---

## 🖥️ Run Locally

```bash
# Clone or download the files
# Navigate to the project folder

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run gulf_of_maine_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 🌐 Deploy to Streamlit Cloud (Free!)

1. **Create a GitHub repository** and upload these files:
   - `gulf_of_maine_dashboard.py`
   - `requirements.txt`

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Click "New app"** and connect your GitHub repo

4. **Set the main file path** to `gulf_of_maine_dashboard.py`

5. **Click "Deploy"** — your app will be live in ~2 minutes!

---

## 📁 Project Structure

```
gulf-of-maine-dashboard/
├── gulf_of_maine_dashboard.py   # Main Streamlit app
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── gulf_of_maine_climate_research.ipynb  # Jupyter notebook (optional)
```

---

## 📚 Data Sources

| Dataset | Source |
|---------|--------|
| Sea Surface Temperature | NOAA ERSST v5 |
| Species Distributions | NOAA Fisheries, Published Literature |
| Lobster Landings | Atlantic States Marine Fisheries Commission |

---

## 📖 Key References

1. Pershing, A.J., et al. (2015). Slow adaptation in the face of rapid warming leads to collapse of the Gulf of Maine cod fishery. *Science*, 350(6262).

2. Pershing, A.J., et al. (2021). Climate impacts on the Gulf of Maine ecosystem. *Elementa: Science of the Anthropocene*, 9(1).

3. Mills, K.E., et al. (2013). Fisheries management in a changing climate. *Oceanography*, 26(2).

---

## 📝 License

This project is for educational and research purposes. Data sources retain their original licenses.

---

*Built with ❤️ for ocean conservation*
