import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry

st.set_page_config(page_title=None, page_icon=None, layout='wide', initial_sidebar_state='expanded')

st.title('Shining a light on the dark web')

shipping_from_countries = ['All countries', 'Germany', 'Netherlands', 'United Kingdom', 'United States',
                           'China', 'Australia', 'India', 'Nepal', 'Canada', 'France',
                           'Latvia', 'Lithuania', 'Austria', 'Poland', 'Spain', 'New Zealand',
                           'Italy', 'Hong Kong', 'Norway', 'Peru', 'Mexico', 'Bulgaria',
                           'Portugal', 'Colombia', 'Sweden', 'Slovenia', 'Switzerland',
                           'Belgium', 'Greece', 'Czech Republic', 'Turks and Caicos Islands',
                           'Finland', 'Chile', np.nan]
with st.sidebar:
    st.header("A dashboard for Data Forensics")

    chapter = st.radio("Navigate to:", ("0. Preface",
                                        "1. Data and data preprocessing",
                                        "2. Drug offer graphs",
                                        "3. Vendor graphs",
                                        "4. Create your own reports"))

    if chapter == "1. Data and data preprocessing" or chapter == "4. Create your own reports":
        st.subheader("Additional options")
        st_country_select = st.multiselect("Select what country/countries you want to see the data of.",
                                           options=shipping_from_countries, default=['Netherlands'])
        st.info("The option 'All countries' might be convenient.")
        if 'All countries' in st_country_select:
            st_country_select = shipping_from_countries[1:]
    elif chapter == "2. Drug offer graphs":
        st_country_select = shipping_from_countries
        st_slider_offer_min = st.slider("What should be the minimum amount of offers?", 10, 500, value=50, step=10)
    else:
        st_country_select = shipping_from_countries

if chapter == "0. Preface":
    col_left, col_right = st.beta_columns((2, 1))
    with col_left, col_right:
        col_left.subheader("A dashboard highlighting insights into dark web drug selling.")
        col_left.write("""
        In the context of the course Data Forensics of their master's degree Data Science & Entrepreneurship, two 
        students - Thaibinh Luu and Rodger van der Heijden - were tasked to develop insights into criminal behaviour on 
        the web. Drawn by the interesting nature of the assignment, they shared an extreme motivation to not only finish
        this assignment, but to make something truly special of it. 
        
        Data was collected by crawling and scraping the dark web marketplace TorreZ. To do so, and to be able to extract
        exactly the desired data, they wrote their own crawler and scraper. Data collection occurred on the 5th of 
        March. Be aware that any offers, vendors and pricing therefore may already be outdated.
        
        Insights derived from the retrieved data were diligently analysed, with the key takeaways shared in the 
        dashboard in front of you. The side panel on the left contains a table of contents, which allows for navigation.
        The first pages contain a guided read with interesting insights extracted and highlighted by us. The latter 
        pages (from 4 onwards) act as a sandbox for the reader to investigate; interactivity is incorporated as much as 
        possible and strongly encouraged. On some pages additional controls are provided; generally they are in the left
        sidebar panel.   
        
        In case any question remains, or we missed some valuable insights, please do contact us. Wishing you the best 
        reading experience possible, 
            
        Thaibinh Luu and Rodger van der Heijden
        """)
        col_right.subheader("About the authors")
        col_right.write("""
            Group 17, consisting of Thaibinh Luu and Rodger van der Heijden, has chosen to tackle online drug selling. Both
            students are close to finishing the master's degree Data Science & Entrepreneurship at the Jheronimus Academy of
            Data Science (JADS). 
        """)


# Load in the data
@st.cache
def get_all_data():
    drugs = pd.read_csv('dataset_1.csv')
    # to do: add country of origin to the vendor dataset. Can be extracted from drugs dataset.
    vendors = pd.read_csv('dataset_vendor.csv')
    return drugs, vendors


# Given the countries the user inputs in the sidebar, select the relevant data.
@st.cache
def return_specified_data(countries):
    drugs, vendors = get_all_data()
    df_country_offers = drugs.loc[drugs['shipping_from'].isin(countries)]
    unique_vendors = df_country_offers['vendor'].unique().tolist()
    df_unique_vendors = vendors.loc[vendors['vendor'].isin(unique_vendors)]
    return df_country_offers, df_unique_vendors


df_drugs, df_vendors = return_specified_data(st_country_select)

if chapter == "1. Data and data preprocessing":
    col_left, col_right = st.beta_columns((3, 1))
    with col_left, col_right:
        col_left.header("Data")
        col_left.write("""
                 The scraped data looks like this. We have scraped two datasets; one dataset is centered around offers, while the second 
                 one shows data about the vendors. In total over 13.000 offers and over 600 vendors were scraped.
                 """)
        col_left.subheader("Offer data")
        col_left.write(""" At the moment of scraping 13277 offers were posted on Torrez in the Drugs and Chemicals-category. We 
        scraped all of those; below you can find an overview of the data. If desired, you can (de)select columns, you can pick 
        how many observations are shown and/or you can order any column by clicking on the column name.""")
        st_ms = col_left.multiselect("Select which columns you want to display.", df_drugs.columns.tolist(),
                                     default=df_drugs.columns.tolist())
        st_slider = col_left.slider("Number of observations to display.", 0, len(df_drugs), 10)
        col_left.dataframe(df_drugs[st_ms].tail(st_slider))

        col_left.subheader("Vendor data")
        col_left.write(""" At the moment of scraping 642 vendors had active offers on Torrez in the Drugs and Chemicals-category. We 
        scraped their profiles; below you can find an overview of the data. Again, if desired, you can (de)select columns, you 
        can pick how many observations are shown and/or you can order any column by clicking on the column name.""")
        st_ms_vendor = col_left.multiselect("Select which columns you want to display.", df_vendors.columns.tolist(),
                                            default=df_vendors.columns.tolist())
        st_slider_vendor = col_left.slider("Number of observations to display.", 0, len(df_vendors), 10)
        col_left.dataframe(df_vendors[st_ms_vendor].tail(st_slider_vendor))

if chapter == "2. Drug offer graphs":
    st.header("Graphs")
    st.subheader("Shipping locations")
    col_shipping_from, col_shipping_to = st.beta_columns(2)
    with col_shipping_from, col_shipping_to:
        df_origin = pd.DataFrame(df_drugs.shipping_from.value_counts()).reset_index()
        df_origin.columns = ['country', 'shipping_from']
        df_2 = df_origin.copy()
        df_origin.loc[df_origin[
                          'shipping_from'] < st_slider_offer_min, 'country'] = 'Other countries'  # Represent only large countries
        fig3 = px.pie(df_origin, values='shipping_from', names='country',
                      title=f'Shipping from (having at least {st_slider_offer_min} offers):')
        fig7 = go.Figure()
        destination = df_drugs.shipping_to.value_counts()
        df_destination = pd.DataFrame(destination)
        df_destination.reset_index(inplace=True)
        df_destination.columns = ['country', 'shipping_from']
        df_destination.loc[
            df_destination[
                'shipping_from'] < st_slider_offer_min, 'country'] = 'Other countries'  # Represent only large countries
        fig7 = px.pie(df_destination, values='shipping_from', names='country',
                      title=f'Shipping to (having at least {st_slider_offer_min} offers):')
        col_shipping_from.plotly_chart(fig3)
        col_shipping_to.plotly_chart(fig7)

    input_countries = df_2.country
    country_3 = []
    for country in input_countries:
        try:
            country_3.append(pycountry.countries.get(name=country).alpha_3)
        except:
            country_3.append(pycountry.countries.search_fuzzy(country)[0].alpha_3)

    df_2['iso_alpha'] = country_3
    fig4 = px.choropleth(df_2, locations="iso_alpha",
                         color="shipping_from",
                         hover_name="country",  # column to add to hover information
                         color_continuous_scale=px.colors.sequential.ice_r, )
    fig4.update_layout(title_text='A map displaying the (self-reported) locations of the cocaine dealers.', title_x=0.5)
    fig4.update_layout(coloraxis_showscale=False,
                       width=800, height=700)
    st.plotly_chart(fig4, use_container_width=True)


    #
    # @st.cache()
    # def third_violin_block():
    #     colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', len(df_drugs['highest_category'].unique()),
    #                       colortype='rgb')
    #     fig13 = go.Figure()
    #     fig13.update_layout(
    #         autosize=True,
    #     )
    #     # https://plotly.com/python/violin/#violin-plot-with-only-points
    #     for category, color in zip(df_drugs['highest_category'].unique(), colors):
    #         cat_price = df_drugs[df_drugs['highest_category'] == category]['price in $'].values
    #         fig13.add_trace(go.Violin(x=cat_price, line_color=color, name=category))
    #
    #     fig13.update_traces(orientation='h', side='positive', width=3, points=False)
    #     fig13.update_layout(xaxis_showgrid=False, xaxis_zeroline=False)
    #     return fig13
    #
    #
    # fig13 = third_violin_block()
    # st.plotly_chart(fig13, use_container_width=True)

    category_prices, category_avg_prices = st.beta_columns(2)
    with category_prices, category_avg_prices:
        fig_category_prices = px.strip(df_drugs, x="price in $", y="highest_category", color="highest_category")
        fig_category_avg_prices = px.strip(df_drugs.groupby('highest_category').mean().reset_index().sort_values(
            by='price in $', ascending=False),
            x="price in $", y="highest_category", color="highest_category")
        category_prices.subheader("Drug prices for all categories.")
        category_prices.plotly_chart(fig_category_prices, use_container_width=True)
        category_avg_prices.subheader("Average prices for each category.")
        category_avg_prices.plotly_chart(fig_category_avg_prices, use_container_width=True)


    @st.cache()
    def fifth_block():
        freq = df_drugs['highest_category'].value_counts()
        # Select frequent values. Value is in the index.
        frequent_values = freq[freq >= 100].index
        # Return only rows with value frequency above threshold.
        df_3 = df_drugs[df_drugs['highest_category'].isin(frequent_values)]

        fig8 = px.strip(df_3, x="price in $", y="highest_category", color="highest_category")
        fig10 = px.strip(
            df_3.groupby('highest_category').mean().reset_index().sort_values(by='price in $', ascending=False),
            x="price in $", y="highest_category", color="highest_category")
        return fig8, fig10


    col4, col6 = st.beta_columns(2)
    with col4, col6:
        fig8, fig10 = fifth_block()
        col4.subheader(f"Drug prices for categories with at least {st_slider_offer_min} offers.")
        col4.plotly_chart(fig8, use_container_width=True)
        col6.subheader(f"Average prices for each category with at least {st_slider_offer_min} offers.")
        col6.plotly_chart(fig10, use_container_width=True)


    @st.cache()
    def sixth_block():
        freq = df_drugs['highest_category'].value_counts()
        # Select frequent values. Value is in the index.
        frequent_values = freq[freq >= 500].index
        # Return only rows with value frequency above threshold.
        df_4 = df_drugs[df_drugs['highest_category'].isin(frequent_values)]

        fig11 = px.strip(df_4, x="price in $", y="highest_category", color="highest_category")
        fig12 = px.strip(
            df_4.groupby('highest_category').mean().reset_index().sort_values(by='price in $', ascending=False),
            x="price in $", y="highest_category", color="highest_category")
        return fig11, fig12

if chapter == "3. Vendor graphs":
    st.header("Graphs")
    st.subheader("Some hypotheses to be investigated")
    st.write(" * Do vendors select one specialty within drugs or sell a wide range?\n "
             " * Does the country of origin factor in the prices?\n"
             " * Is trust a factor in prices?\n"
             " * Is worldwide shipping a predictor for number of deals?")
    col_shipping_from, col_shipping_to = st.beta_columns(2)
    with col_shipping_from, col_shipping_to:
        pass


if chapter == "4. Create your own reports":
    df_drugs, df_vendors = return_specified_data(st_country_select)
    st.header("Data")
    st.write("""
    The scraped data looks like this. We have scraped two datasets; one dataset is centered around offers, while the second 
    one shows data about the vendors. In total over 13.000 offers and over 600 vendors were scraped.
    """)

    st.subheader("Offer data")
    st.write(""" At the moment of scraping 13277 offers were posted on Torrez in the Drugs and Chemicals-category. We 
    scraped all of those; below you can find an overview of the data. If desired, you can (de)select columns, you can pick 
    how many observations are shown and/or you can order any column by clicking on the column name.""")
    st_ms = st.multiselect("Select which columns you want to display.", df_drugs.columns.tolist(),
                           default=df_drugs.columns.tolist())
    st_slider = st.slider("Number of observations to display.", 0, len(df_drugs), 5)
    st.dataframe(df_drugs[st_ms].tail(st_slider))

    st.subheader("Vendor data")
    st.write(""" At the moment of scraping 642 vendors had active offers on Torrez in the Drugs and Chemicals-category. We 
    scraped their profiles; below you can find an overview of the data. Again, if desired, you can (de)select columns, you 
    can pick how many observations are shown and/or you can order any column by clicking on the column name.""")
    st_ms_vendor = st.multiselect("Select which columns you want to display.", df_vendors.columns.tolist(),
                                  default=df_vendors.columns.tolist())
    st_slider_vendor = st.slider("Number of observations to display.", 0, len(df_vendors), 3)
    st.dataframe(df_vendors[st_ms_vendor].tail(st_slider_vendor))
