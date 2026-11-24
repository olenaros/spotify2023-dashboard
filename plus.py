import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Spotify 2023 Analytics",
    page_icon="♪",
    layout="wide"
)

st.title("♪ Spotify 2023 | Music Data Analysis")
st.write(
    "Інтерактивний дашборд для дослідження популярних музичних треків "
    "за датасетом Spotify 2023."
)


@st.cache_data
def load_data():
    data = pd.read_csv("spotify-2023.csv", encoding="latin-1")

    data["streams"] = pd.to_numeric(data["streams"], errors="coerce")
    data["in_spotify_playlists"] = pd.to_numeric(
        data["in_spotify_playlists"], errors="coerce"
    )

    conditions = [
        data["released_year"] == 2023,
        data["released_year"] == 2022,
        data["released_year"] <= 2021
    ]
    labels = ["fresh release", "new_release", "older release"]
    data["release_type"] = pd.Series(
        pd.NA, index=data.index, dtype="object"
    )
    data.loc[conditions[0], "release_type"] = labels[0]
    data.loc[conditions[1], "release_type"] = labels[1]
    data.loc[conditions[2], "release_type"] = labels[2]
    data["release_type"] = data["release_type"].fillna("other")

    # Дата релізу та кількість днів від релізу.
    date_text = (
        data["released_year"].astype(str) + "-" +
        data["released_month"].astype(str) + "-" +
        data["released_day"].astype(str)
    )
    release_date = pd.to_datetime(date_text, errors="coerce")
    data["released_in_days"] = (
        pd.Timestamp.today().normalize() - release_date
    ).dt.days

    data["streams_per_playlist"] = (
        data["streams"] / data["in_spotify_playlists"].replace(0, pd.NA)
    )

    country_dict = {
        "Latto, Jung Kook": "USA / South Korea",
        "Myke Towers": "Puerto Rico",
        "Olivia Rodrigo": "USA",
        "Taylor Swift": "USA",
        "Bad Bunny": "Puerto Rico",
        "Dave, Central Cee": "England",
        "Eslabon Armado, Peso Pluma": "USA / Mexico",
        "Quevedo": "Spain",
        "Gunna": "USA",
        "Peso Pluma, Yng Lvcas": "Mexico",
        "Bad Bunny, Grupo Frontera": "Puerto Rico / USA",
        "NewJeans": "South Korea",
        "Miley Cyrus": "USA",
        "David Kushner": "USA",
        "Harry Styles": "England",
        "SZA": "USA",
        "Fifty Fifty": "South Korea",
        "Billie Eilish": "USA",
        "Feid, Young Miko": "Colombia / Puerto Rico",
        "Jimin": "South Korea",
        "The Weeknd": "Canada",
        "Kendrick Lamar": "USA",
        "Morgan Wallen": "USA",
        "Ed Sheeran": "England",
        "BTS": "South Korea",
        "Feid": "Colombia",
        "Drake": "Canada",
        "Labrinth": "England",
        "Doja Cat": "USA",
        "Bruno Mars": "USA",
        "Adele": "England",
        "Eminem": "USA"
    }
    label_dict = {
        "Latto, Jung Kook": "RCA Records; BIGHIT MUSIC",
        "Myke Towers": "Warner Music Latina; One World",
        "Olivia Rodrigo": "Geffen Records; Interscope Records",
        "Taylor Swift": "Republic Records; Big Machine Records",
        "Bad Bunny": "Rimas Entertainment",
        "Dave, Central Cee": "Neighbourhood Recordings; Live Yours",
        "Eslabon Armado, Peso Pluma": "DEL Records",
        "Quevedo": "Taste The Floor; Universal Music Spain",
        "Gunna": "YSL Records; 300 Entertainment",
        "Peso Pluma, Yng Lvcas": "Prajin Parlay; Warner Music Latina",
        "Bad Bunny, Grupo Frontera": "Rimas Entertainment",
        "NewJeans": "ADOR; Geffen Records",
        "Miley Cyrus": "Columbia Records",
        "David Kushner": "Miserable Music Group",
        "Harry Styles": "Erskine Records; Columbia Records",
        "SZA": "Top Dawg Entertainment; RCA Records",
        "Fifty Fifty": "ATTRAKT",
        "Billie Eilish": "Darkroom; Interscope Records",
        "Feid, Young Miko": "Universal Music Latino",
        "Jimin": "BIGHIT MUSIC",
        "The Weeknd": "XO; Republic Records",
        "Kendrick Lamar": "pgLang; Interscope Records",
        "Morgan Wallen": "Big Loud Records; Republic Records",
        "Ed Sheeran": "Gingerbread Man Records; Atlantic Records",
        "BTS": "BIGHIT MUSIC; Geffen Records",
        "Feid": "Universal Music Latino",
        "Drake": "OVO Sound; Republic Records",
        "Labrinth": "Columbia Records; RCA Records",
        "Doja Cat": "Kemosabe Records; RCA Records",
        "Bruno Mars": "Atlantic Records; Elektra",
        "Adele": "XL Recordings; Columbia Records",
        "Eminem": "Shady Records; Aftermath; Interscope Records"
    }
    data["artist_country"] = data["artist(s)_name"].map(country_dict).fillna("Other")
    data["music_labels"] = data["artist(s)_name"].map(label_dict).fillna("Other")

    return data

try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "Не знайдено файл spotify-2023.csv. "
        "Переконайтеся, що CSV-файл лежить в одній папці з app.py."
    )
    st.stop()


st.sidebar.header("Фільтри")

min_year = int(df["released_year"].min())
max_year = int(df["released_year"].max())
selected_years = st.sidebar.slider(
    "Оберіть діапазон років релізу",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

release_options = ["Усі типи"] + sorted(df["release_type"].dropna().unique().tolist())
selected_release = st.sidebar.selectbox(
    "Тип релізу",
    release_options
)

artist_options = ["Усі виконавці"] + sorted(df["artist(s)_name"].dropna().unique().tolist())
selected_artist = st.sidebar.selectbox(
    "Виконавець",
    artist_options
)

# Застосування фільтрів до таблиці.
filtered = df[
    df["released_year"].between(selected_years[0], selected_years[1])
].copy()

if selected_release != "Усі типи":
    filtered = filtered[filtered["release_type"] == selected_release]

if selected_artist != "Усі виконавці":
    filtered = filtered[filtered["artist(s)_name"] == selected_artist]

st.sidebar.caption("Фільтри одночасно оновлюють показники, таблицю та графіки.")

st.subheader("Загальна інформація")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Кількість треків", f"{len(filtered):,}".replace(",", " "))
col2.metric(
    "Виконавців",
    f"{filtered['artist(s)_name'].nunique():,}".replace(",", " ")
)
col3.metric(
    "Сумарні прослуховування",
    f"{filtered['streams'].sum(skipna=True) / 1_000_000_000:.2f} млрд"
)
col4.metric(
    "Середня енергетичність",
    f"{filtered['energy_%'].mean():.1f}%" if len(filtered) else "—"
)

tab1, tab2, tab3 = st.tabs(
    ["Огляд датасету", "Аналітика", "Висновки"]
)

with tab1:
    st.subheader("Перегляд даних Spotify 2023")
    st.write(
        "Натисніть кнопку нижче, щоб переглянути таблицю. "
        "Таблиця враховує вибрані фільтри з бічної панелі."
    )
    if st.button("Показати датасет"):
        st.session_state["show_dataset"] = True

    if st.session_state.get("show_dataset", False):
        st.dataframe(filtered, use_container_width=True, height=420)
        csv_data = filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Завантажити відфільтровані дані (CSV)",
            data=csv_data,
            file_name="spotify_filtered.csv",
            mime="text/csv"
        )

    st.caption(
        "Джерело: Spotify 2023 dataset. "
        "Датасет містить інформацію про популярні треки та їхні показники."
    )

with tab2:
    st.subheader("Графіки та порівняння")

    if filtered.empty:
        st.warning("За вибраними фільтрами треків не знайдено. Змініть фільтри.")
    else:
        left, right = st.columns(2)

        with left:
            st.markdown("**Кількість треків за типом релізу**")
            release_counts = filtered["release_type"].value_counts()
            plt.figure()
            plt.pie(
                release_counts.values,
                labels=release_counts.index,
                autopct="%1.1f%%",
                startangle=90
            )
            plt.title("Tracks by release type")
            st.pyplot(plt.gcf())
            plt.close()
            st.caption(
                "Діаграма показує розподіл треків за типами релізу: "
                "2023, 2022 та 2021 і раніше."
            )

        with right:
            st.markdown("**ТОП-10 треків за кількістю прослуховувань**")
            top_tracks = (
                filtered.dropna(subset=["streams"])
                .nlargest(10, "streams")
                .sort_values("streams", ascending=True)
            )
            plt.figure(figsize=(8, 5))
            plt.barh(top_tracks["track_name"], top_tracks["streams"])
            plt.xlabel("Кількість прослуховувань (streams)")
            plt.ylabel("Назва треку")
            plt.title("Top 10 tracks by streams")
            plt.tight_layout()
            st.pyplot(plt.gcf())
            plt.close()
            st.caption("Порівняння найпопулярніших композицій у вибірці.")

        st.markdown("**Зв'язок між танцювальністю та енергетичністю**")
        plt.figure(figsize=(9, 5))
        plt.scatter(
            filtered["danceability_%"],
            filtered["energy_%"],
            alpha=0.65
        )
        plt.xlabel("Танцювальність (%)")
        plt.ylabel("Енергетичність (%)")
        plt.title("Danceability vs Energy")
        plt.grid(True, alpha=0.25)
        plt.tight_layout()
        st.pyplot(plt.gcf())
        plt.close()
        st.caption(
            "Кожна точка — окремий трек. Графік допомагає порівняти "
            "танцювальність та енергетичність композицій."
        )

        st.markdown("**Середні прослуховування на один плейлист за типом релізу**")
        average_data = (
            filtered.groupby("release_type", as_index=False)["streams_per_playlist"]
            .mean()
            .dropna()
        )
        if not average_data.empty:
            plt.figure(figsize=(8, 4))
            plt.bar(
                average_data["release_type"],
                average_data["streams_per_playlist"]
            )
            plt.xlabel("Тип релізу")
            plt.ylabel("Середні streams на один плейлист")
            plt.title("Average streams per playlist by release type")
            plt.tight_layout()
            st.pyplot(plt.gcf())
            plt.close()
        else:
            st.info("Для цього набору фільтрів недостатньо даних для розрахунку.")

with tab3:
    st.subheader("Висновки аналізу")
    st.write(
        "1. Датасет дає змогу досліджувати популярні треки Spotify 2023 "
        "за кількістю прослуховувань, плейлистів та музичними характеристиками."
    )
    st.write(
        "2. Поділ на fresh release, new_release та older release допомагає "
        "порівнювати нові й давніші композиції."
    )
    st.write(
        "3. Показник streams_per_playlist показує середню кількість "
        "прослуховувань у розрахунку на кількість плейлистів Spotify, "
        "до яких додано трек."
    )
    st.write(
        "4. Показники danceability_% та energy_% дають змогу порівняти "
        "музичні характеристики композицій."
    )
    st.write(
        "5. Інтерактивні фільтри дозволяють досліджувати різні підгрупи "
        "треків, а графіки автоматично оновлюються відповідно до вибору."
    )

st.divider()
st.caption("Streamlit • Analysis • Spotify 2023")
