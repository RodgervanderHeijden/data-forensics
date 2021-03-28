import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry


# INITIAL SETUP
st.set_page_config(page_title=None, page_icon=None, layout='wide', initial_sidebar_state='expanded')
st.title('Shining a light on the dark web')


# LOAD THE DATA
@st.cache(allow_output_mutation=True)
def get_all_data():
    drugs = pd.read_csv(r'Product_dataset_new.csv')
    drugs.drop(drugs.columns[0], axis=1, inplace=True)
    # to do: add country of origin to the vendor dataset. Can be extracted from drugs dataset.
    # vendor can have multiple shiipping from locations --> unable to trace exact country of origin
    vendors = pd.read_csv(r'Vendor_dataset_new.csv')
    vendors.drop(vendors.columns[0], axis=1, inplace=True)
    return drugs, vendors

df_drugs, df_vendors = get_all_data()


# FUNCTIONS
def country_multiselect():
    global st_country_select
    shipping_from_countries = list(df_drugs.shipping_from.unique())
    shipping_from_countries_copy = ['All countries'] + shipping_from_countries
    st_country_select = st.multiselect('Select what country/countries you want to see the data of.',
                                       options=shipping_from_countries_copy, default=['All countries'])
    if 'All countries' in st_country_select:
        st_country_select = shipping_from_countries
    return st_country_select


# SIDEBAR
with st.sidebar:
    st.header("A dashboard for Data Forensics")

    chapter = st.radio("Navigate to:", ("0. Preface",
                                        "1. Data and data preprocessing",
                                        "2. Drug offer graphs",
                                        "3. Vendor graphs",
                                        "4. Insights",
                                        "5. Create your own reports"))

    # create options
    # shipping_from_countries = list(df_drugs.shipping_from.unique())
    # shipping_from_countries_copy = ['All countries'] + shipping_from_countries

    if chapter == "1. Data and data preprocessing" or chapter == "5. Create your own reports":
        st.subheader("Additional options")
        country_multiselect()

        # st_country_select = st.multiselect("Select what country/countries you want to see the data of.",
        #                                    options=shipping_from_countries_copy, default=['All countries'])

        # if 'All countries' in st_country_select:
        #     st_country_select = shipping_from_countries

    elif chapter == "2. Drug offer graphs":
        country_multiselect()
        # st_country_select = shipping_from_countries
        st_slider_offer_min = st.slider("What should be the minimum amount of offers?", 10, 500, value=50, step=10)

    elif chapter == "3. Vendor graphs" or chapter == "4. Insights":
        pass

    else:
        # st_country_select = shipping_from_countries
        country_multiselect()


# CHAPTER 0
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


# Given the countries the user inputs in the sidebar, select the relevant data.
@st.cache(allow_output_mutation=True)
def return_specified_data(countries):
    drugs, vendors = get_all_data()
    df_country_offers = drugs.loc[drugs['shipping_from'].isin(countries)]
    unique_vendors = df_country_offers['vendor'].unique().tolist()
    df_unique_vendors = vendors.loc[vendors['vendor'].isin(unique_vendors)]
    return df_country_offers, df_unique_vendors




if chapter == "1. Data and data preprocessing":
    df_drugs, df_vendors = return_specified_data(st_country_select)
    col_left, col_right = st.beta_columns((3, 1))
    with col_left, col_right:
        col_left.header("Data")
        col_left.write("""
                 The scraped data looks like this. We have scraped two datasets; one dataset is centered around offers, while the second 
                 one shows data about the vendors. In total over 14.000 offers and over 650 vendors were scraped.
                 """)
        col_left.subheader("Offer data")
        col_left.write(""" At the moment of scraping 14013 offers were posted on Torrez in the Drugs and Chemicals-category. We 
        scraped all of those; below you can find an overview of the data. If desired, you can (de)select columns, you can pick 
        how many observations are shown and/or you can order any column by clicking on the column name.""")
        st_ms = col_left.multiselect("Select which columns you want to display.", df_drugs.columns.tolist(),
                                     default=df_drugs.columns.tolist())
        st_slider = col_left.slider("Number of observations to display.", 0, len(df_drugs), 10)
        col_left.dataframe(df_drugs[st_ms].head(st_slider))

        col_left.subheader("Vendor data")
        col_left.write(""" At the moment of scraping 668 vendors had active offers on Torrez in the Drugs and Chemicals-category. We 
        scraped their profiles; below you can find an overview of the data. Again, if desired, you can (de)select columns, you 
        can pick how many observations are shown and/or you can order any column by clicking on the column name.""")
        st_ms_vendor = col_left.multiselect("Select which columns you want to display.", df_vendors.columns.tolist(),
                                            default=df_vendors.columns.tolist())
        st_slider_vendor = col_left.slider("Number of observations to display.", 0, len(df_vendors), 10)
        col_left.dataframe(df_vendors[st_ms_vendor].head(st_slider_vendor))


@st.cache(allow_output_mutation=False)
def fifth_block(df_drugs):
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


if chapter == "2. Drug offer graphs":
    df_drugs, df_vendors = return_specified_data(st_country_select)
    st.subheader("Shipping locations")
    col_left, col_right = st.beta_columns(2)
    with col_left, col_right:
        df_origin = pd.DataFrame(df_drugs.shipping_from.value_counts()).reset_index()
        df_origin.columns = ['country', 'shipping_from']
        df_2 = df_origin.copy()
        df_origin.loc[df_origin[
                          'shipping_from'] < st_slider_offer_min, 'country'] = 'Other countries'  # Represent only large countries
        fig3 = px.pie(df_origin, values='shipping_from', names='country',
                      title=f'Shipping from (having at least {st_slider_offer_min} offers):')
        fig7 = go.Figure()

        df_destination = pd.DataFrame(df_drugs.shipping_to.value_counts())
        df_destination.reset_index(inplace=True)
        df_destination.columns = ['country', 'shipping_from']
        df_destination.loc[
            df_destination[
                'shipping_from'] < st_slider_offer_min, 'country'] = 'Other countries'  # Represent only large countries
        fig7 = px.pie(df_destination, values='shipping_from', names='country',
                      title=f'Shipping to (having at least {st_slider_offer_min} offers):')

        fig3.update_layout(autosize=False,
            width=600,
            height=450)

        fig7.update_layout(autosize=False,
            width=600,
            height=450)

        col_left.plotly_chart(fig3)
        col_right.plotly_chart(fig7)

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
                         color_continuous_scale=px.colors.sequential.ice_r)
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
        df_drugs['price in $'] = df_drugs['price in $'].astype(str).str.replace(",","").astype(float)
        fig_category_avg_prices = px.strip(df_drugs.groupby('highest_category').mean().reset_index().sort_values(
            by='price in $', ascending=False),
            x="price in $", y="highest_category", color="highest_category")
        category_prices.subheader("Drug prices for all categories")
        category_prices.plotly_chart(fig_category_prices, use_container_width=True)
        category_avg_prices.subheader("Average prices for each category")
        category_avg_prices.plotly_chart(fig_category_avg_prices, use_container_width=True)

        # fig20 = px.scatter(df_drugs, x="price in $", y="highest_category")
        # fig20.update_layout(autosize=False,
        #     width=600,
        #     height=900)
        # category_prices.plotly_chart(fig20)

    col4, col6 = st.beta_columns(2)
    with col4, col6:
        fig8, fig10 = fifth_block(df_drugs)
        col4.subheader(f"Drug prices for categories with at least {st_slider_offer_min} offers.")
        col4.plotly_chart(fig8, use_container_width=True)
        col6.subheader(f"Average prices for each category with at least {st_slider_offer_min} offers.")
        col6.plotly_chart(fig10, use_container_width=True)

# rename misspelled column
df_vendors.rename(columns={'verifcation': 'verification'}, inplace=True)

# Add number of offers to vendor df
nr_offers = pd.DataFrame(df_drugs.groupby('vendor').vendor.count())
nr_offers.columns = ['nr_offers']
nr_offers.reset_index(inplace=True)
df_vendors = df_vendors.merge(nr_offers, on='vendor', how='left')

# count rank
ranks = pd.DataFrame(df_vendors['rank'].value_counts())
ranks.reset_index(inplace=True)
ranks.columns = ['rank', 'count']

# verification rank
verification = pd.DataFrame(df_vendors['verification'].value_counts())
verification.reset_index(inplace=True)
verification.columns = ['verification', 'count']

if chapter == "3. Vendor graphs":
    st.header("Vendors")
    st.subheader("Total number of vendors over time")

    df_vendors['date'] = pd.to_datetime(df_vendors['since'])
    df_vendor_month = df_vendors.groupby(df_vendors['date'].dt.strftime('%B %Y'))['vendor'].count().reset_index()
    df_vendor_month['date'] = pd.to_datetime(df_vendor_month["date"], format='%B %Y')
    df_vendor_month = df_vendor_month.sort_values('date')
    df_vendor_month['cumulative_sum_vendor'] = df_vendor_month['vendor'].cumsum()
    df_vendor_month.date = df_vendor_month.date.dt.strftime('%B %Y')

    # cumulative number of vendors over time
    fig11 = px.area(df_vendor_month, x="date", y="cumulative_sum_vendor", labels={
                     "cumulative_sum_vendor": "number of vendors",
                     "date": "" },)
    fig11.update_layout(
        autosize=True,
        height=500)
    fig11.update_traces(mode='markers+lines')
    st.plotly_chart(fig11, use_container_width=True)

    st.subheader("Rank")
    st.write("The rank indicates the number of sales of the vendor on the market."
             "Rank 0 represents 0-9 items sold, Rank 1 represents 10-99 items sold, Rank 3 represents 100-199 items sold, etc. "
             "A Top seller has over 1000 sales.")
    col_vendor_1, col_vendor_2 = st.beta_columns(2)
    with col_vendor_1, col_vendor_2:
        # pie chart ranks
        fig12 = px.pie(ranks, names='rank', values='count')
        col_vendor_1.plotly_chart(fig12, use_container_width=True)

        # bar chart ranks
        fig21 = px.bar(ranks, x='rank', y='count')
        col_vendor_2.plotly_chart(fig21, use_container_width=True)

    st.subheader("Verification")
    st.write("Every vendor on TorreZ that has a positive history from other markets can get a verification badge."
             "The level indicates the number of markets.")

    col_vendor_1, col_vendor_2 = st.beta_columns(2)
    with col_vendor_1, col_vendor_2:
        verification['verification'] = verification['verification'].str.replace('Verification ', "")
        # pie chart verification
        fig13 = px.pie(verification, names='verification', values='count')
        col_vendor_1.plotly_chart(fig13, use_container_width=True)

        # bar chart verification
        fig13 = px.bar(verification, x='verification', y='count')
        col_vendor_2.plotly_chart(fig13, use_container_width=True)



    st.subheader("Transactions")

    # verification levels filter
    df_vendors['verification'].fillna("No verification level", inplace=True)
    all_verifications = df_vendors['verification'].unique().tolist()
    all_verifications.append('All levels')
    st_ms_ver = st.multiselect("Select which verification level(s) you want to display.", all_verifications,
                           default=['All levels'])
    if 'All levels' in st_ms_ver:
        st_ms_ver = df_vendors['verification'].unique().tolist()

    col_vendor_3, col_vendor_4 = st.beta_columns([2.5,1])
    with col_vendor_3, col_vendor_4:

        fig12 = px.histogram(df_vendors[df_vendors['verification'].isin(st_ms_ver)],
        x="transactions", title='Distribution of Transactions', nbins=50)
        col_vendor_3.plotly_chart(fig12, use_container_width=True)

        fig12 = px.box(df_vendors[df_vendors['verification'].isin(st_ms_ver)],
        y="transactions", title='Boxplot')
        col_vendor_4.plotly_chart(fig12, use_container_width=True)


    st.subheader("Number of offers per vendor")
    # rank filter
    all_ranks = df_vendors['rank'].unique().tolist()
    all_ranks.append('All ranks')
    st_ms_rank = st.multiselect("Select which rank(s) you want to display.", all_ranks,
                           default=['All ranks'])
    if 'All ranks' in st_ms_rank:
        st_ms_rank = df_vendors['rank'].unique().tolist()

    col_vendor_3, col_vendor_4 = st.beta_columns([2.5,1])
    with col_vendor_3, col_vendor_4:

        # number of offers per vendor
        fig13 = px.histogram(
            df_vendors[df_vendors['rank'].isin(st_ms_rank)],
            x="nr_offers",
            title='Distribution of the number of offers per vendor', nbins=50)
        col_vendor_3.plotly_chart(fig13, use_container_width=True)

        fig12 = px.box(df_vendors[df_vendors['rank'].isin(st_ms_rank)],
        y="nr_offers", title='Boxplot')
        col_vendor_4.plotly_chart(fig12, use_container_width=True)

    st.subheader("Feedback")
    fig13 = px.histogram(
        df_vendors,
        x="feedback_total",
        title='Distribution of the number of feedback per vendor', nbins=50)
    st.plotly_chart(fig13, use_container_width=True)

    # col_vendor_3, col_vendor_4 = st.beta_columns(2)
    # with col_vendor_3, col_vendor_4:
    #     # number of transcations per vendor
    #     fig12 = px.histogram(df_vendors[(df_vendors['rank'].isin(st_ms_rank)) & (df_vendors['verification'].isin(st_ms_ver))],
    #     x="transactions", title='Distribution of Transactions', nbins=50)
    #     col_vendor_3.plotly_chart(fig12, use_container_width=True)
    #
    #     # number of offers per vendor
    #     fig13 = px.histogram(df_vendors[(df_vendors['rank'].isin(st_ms_rank)) & (df_vendors['verification'].isin(st_ms_ver))],
    #                          x="nr_offers",
    #                          title='Distribution of the number of offers per vendor', nbins=50)
    #     col_vendor_4.plotly_chart(fig13, use_container_width=True)


if chapter == "4. Insights":
    # st.header("Graphs")
    st.subheader("Some hypotheses to be investigated")
    st.write(" * Do vendors select one specialty within drugs or sell a wide range?\n "
             " * Does the country of origin factor in the prices?\n"
             " * Is trust a factor in prices?\n"
             " * Do trusted vendors have more transactions per month?\n"
             " * Is worldwide shipping a predictor for number of deals?\n"
             " * Do higher ranked vendors sell special kind of drugs?\n"
             " * Do higher ranked vendors have higher prices?")

    df_vendors['date'] = pd.to_datetime(df_vendors['since'])
    now = pd.to_datetime('Apr 18, 2021')
    df_vendors['num_months'] = (now.year - df_vendors.date.dt.year) * 12 + (now.month - df_vendors.date.dt.month)
    df_vendors['transactions_month'] = df_vendors['transactions']/df_vendors['num_months']
    fig = px.box(df_vendors, x='verification',
                   y="transactions_month", title='Boxplot')
    st.plotly_chart(fig, use_container_width=True)


    col_1, col_2 = st.beta_columns(2)
    with col_1, col_2:
        # boxplot rank vs price
        df_drugs = df_drugs.merge(df_vendors[['vendor', 'rank', 'verification']], on='vendor', how='left')
        fig14 = px.box(df_drugs, x='rank', y="price in $")
        col_1.plotly_chart(fig14)

        # boxplot verification vs price
        df_drugs.verification = df_drugs.verification.str.replace('Verification', "")
        fig15 = px.box(df_drugs, x='verification', y="price in $")
        col_2.plotly_chart(fig15)

        # distribution of categories level 2 for the vendors
        unique_cat_level_2 = pd.DataFrame(df_drugs.groupby('vendor').category_level_2.nunique()).reset_index()
        fig16 = px.histogram(unique_cat_level_2,
            x="category_level_2", title='Distribution of number of categories (level 2)', nbins=50)
        col_1.plotly_chart(fig16)

        unique_cat_level_highest = pd.DataFrame(df_drugs.groupby('vendor').highest_category.nunique()).reset_index()
        fig17 = px.histogram(unique_cat_level_highest,
                             x="highest_category", title='Distribution of number of categories (highest_category)', nbins=50)
        col_2.plotly_chart(fig17)

        pass

if chapter == "5. Create your own reports":
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

