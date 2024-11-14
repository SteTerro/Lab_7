import streamlit as st
import polars as pl

st.write("""
# Emissioni inquinanti in Europa
""")

url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/sdg_13_10?format=TSV&compressed=true"
st.write(f"""
     La seguente tabella mostra i dati sulle emissioni ottenuti dal [sito Eurostat]({url}).
 """)

data = (
    pl
    .read_csv(url, separator="\t")
    .select(
        pl.col("freq,airpol,src_crf,unit,geo\\TIME_PERIOD").str.split(",").list.to_struct(fields=["freq", "airpol", "src_crf", "unit", "geo"]).alias("combined_info"),
        pl.col("*").exclude("freq,airpol,src_crf,unit,geo\\TIME_PERIOD")
    ).unnest("combined_info")
    .unpivot(index=["freq", "airpol", "src_crf", "unit", "geo"], 
            value_name="emissions", 
            variable_name="year")
    .with_columns(
        year = pl.col("year").str.replace(" ", "").cast(pl.Int64),
        emissions = pl.col("emissions").str.strip_chars_end(" bep").cast(pl.Float64, strict=True)
    )
    .pivot(on="unit", values="emissions")
    .filter(pl.col("src_crf") == "TOTXMEMONIA")
)

st.write("""
## Quali sono gli stati più inquinati in un dato anno?
""")

years = range(1990, 2023)
year = st.select_slider("seleziona l'anno", years, value=2022)
bar_chart_data = (
    data
    .filter(pl.col("year") == year)
    .sort("T_HAB")
    .with_columns(
        pl.col("geo").cast(pl.Categorical())
    )
    .sort("geo")
)

st.bar_chart(
    bar_chart_data,
    x="geo",
    y="T_HAB",
    horizontal=True
)

st.write("""
## Come sono cambiate le emissioni nel corso degli anni?

Il seguente grafico consente di selezionare alcuni stati, confrontandone l'andamento nel tempo
""")

# st.write(data)
countries = data.select("geo").unique().sort("geo")

selected_country = st.multiselect(
    "Seleziona uno stato",
    countries,
    default="IT"
)

st.line_chart(
    data.filter(pl.col("geo").is_in(selected_country)),
    x="year",
    y="T_HAB",
    color="geo"
)

import pandas as pd

# Create a sample DataFrame
data2 = pd.DataFrame({
    'latitude': [37.7749, 34.0522, 40.7128],
    'longitude': [-122.4194, -118.2437, -74.0060]
})

# Create an interactive map
st.map(data2)
