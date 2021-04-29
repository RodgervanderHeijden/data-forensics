import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry
import altair as alt

# INITIAL SETUP
st.set_page_config(page_title=None, page_icon=None, layout='wide', initial_sidebar_state='expanded')
st.title('Shining a Light on the Dark Web')


# LOAD THE DATA
@st.cache(allow_output_mutation=True)
def get_all_data():
    drugs = pd.read_csv(r'Product_dataset_new.csv')
    drugs.drop(drugs.columns[0], axis=1, inplace=True)
    # The price in $s is captured as a string, containing both decimal points and commas. Here we clean that to a float
    drugs['price'] = [round(float(x)) if len(x) <= 6 else float(x[:-3].replace(",", "")) for x in drugs['price in $']]
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
                                        "2. Product Insights",
                                        "3. Vendor Insights",
                                        "4. Advanced Insights",
                                        "5. Create your own reports"))

    if chapter == "5. Create your own reports":
        st.subheader("Additional options")
        country_multiselect()

    elif chapter == "2. Product Insights":
        country_multiselect()
        # st_country_select = shipping_from_countries
        st_slider_offer_min = st.slider("What should be the minimum amount of offers?", 10, 500, value=50, step=10)

    else:
        pass




# CHAPTER 0
if chapter == "0. Preface":
    col_left, col_right = st.beta_columns((2, 1))
    with col_left, col_right:
        col_left.subheader("A dashboard highlighting insights into dark web drug selling")
        col_left.write("""
        In the context of the course Data Forensics of their master's degree Data Science & Entrepreneurship, two 
        students - Thaibinh Luu and Rodger van der Heijden - were tasked to develop insights into criminal behaviour on 
        the web. Drawn by the interesting nature of the assignment, they shared an extreme motivation to not only finish
        this assignment, but to make something truly special of it. 

        This project is heavily focused on counterfeit/falsified medicine, drugs and NPS.
        We saw the most potential in this ANITA scenario and believe it has the most information available. 
        As these illicit goods may negatively impact public health, it is of great essence to monitor and analyse these trafficking flows.
        As a lot of illegal trafficking is facilitated by marketplaces on the dark web, we were motivated to analyse the supply and demand on this specific level of the internet. 
        
        The ultimate goal of this project is to gain valuable insights in one of the largest dark web marketplaces for drugs: ToRReZ.
        By thoroughly analysing this market, we hope to get a sense of the popular types of drugs, the trafficking flow, supply, demand and so on. 
        Better understanding the market may help in identifying key players and keeping track of illegal drug flows. 

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



# CHAPTER 1
if chapter == "1. Data and data preprocessing":
    # df_drugs, df_vendors = return_specified_data(st_country_select)
    col_left, col_right = st.beta_columns((3, 1))
    with col_left, col_right:
        col_left.header("Architecture overview")
        col_left.write("""
                    To obtain data of the Torrez market we had to visit the dark web. To achieve this, the following 
                    enviornment is implemented. First, a virtual machine is downloaded to create a safe place te experiment in. 
                    To add another layer of protection, we connected to a 
                    VPN within the virtual machine. Finally, we downloaded the Tor browser which allowed us to visit the dark web 
                    and subsequently Torrez. 
                 """)

        col_left.write("___")
        col_left.header("Data collection")
        col_left.write("""
                 By accessing the market, we were exposed to a lot of interesting data. We found that the marketplace 
                 offers all kinds of illicit goods. Besides drugs and chemicals, also software & malware, fraud and many more 
                 are offered. Our category of interest, however, is 'Drugs and Chemicals'. 
                 This section contains all drug and chemical related products offered on the market. 
                 At the time of scraping, this section had 14.013 product offerings. Besides all these products, 
                 the vendor pages also contain a lot of valuable information.
                 
                 To capture all this relevant information required for analysis, we built our own crawler and scraper 
                 from scratch. Scraping is done using the BeautifulSoup package in Python. This package allowed us to 
                 pick the relevant information from the HTML we are interested in. For the product pages we scraped the 
                 vendor name, category levels, product name, price and shipping locations. The same approach is used for 
                 the vendor pages. However, this time we scraped the vendor name, rank, verification, number of 
                 transactions, feedback, and disputes. The crawler that we made allowed us to go through pages to scrape 
                 all the information. For the product pages, the crawler goes through all of the 721 pages and for the 
                 vendors, it goes through all vendor pages that have at least one offer in the category 
                 ‘Drugs and Chemicals’. More specific information can be found in the code, where comments are also 
                 provided for better understanding the workflow. 
                 """)

        col_left.write("___")
        col_left.header("Data description")
        col_left.write("""
        Crawling and scraping eventually led to a dataset that can be used for analysis. 
        We ended up with two different datasets, one that contains the product information and one that contains 
        the vendor information. We wanted specific insights on the Torrez market and hence only this market is scraped. 
        The type of data scraped is textual data. Images were not scraped as they were not useful for the analysis we intended to do. 
        Below you can find the data description; the variable name, the data type and the explanation.
        """)

        data_description_product = pd.read_excel(r'Data description.xlsx', sheet_name='Blad1')
        data_description_vendor = pd.read_excel(r'Data description.xlsx', sheet_name='Blad2')

        col_left.subheader("Product data")
        col_left.table(data_description_product)
        col_left.subheader("Vendor data")
        col_left.table(data_description_vendor)


        col_left.write("___")
        col_left.header("Raw data")
        col_left.write("""
                Have a look at the raw data that we scraped. Two datasets are provided, the product dataset and the vendor dataset.
                """)
        col_left.subheader("Product data")
        col_left.write(""" At the moment of scraping 14.013 offers were posted on Torrez in the Drugs and Chemicals-category. We 
        scraped all of those; below you can find an overview of the raw data. If desired, you can (de)select columns, you can pick 
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


#CHAPTER 2
if chapter == "2. Product Insights":
    st.header("Product insights")
    df_drugs, df_vendors = return_specified_data(st_country_select)
    st.subheader("Shipping locations")
    st.write('The distribution of the shipping from & shipping to locations of all drug and chemical related products on Torrez. '
             'The majority of products is shipped from either the UK, US, Germany or the Netherlands and almost half of all products can be shipped worldwide.')
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
    fig4.update_layout(title_text='A map displaying the (self-reported) locations of the dealers. The darker the color, the more dealers.'
                       , title_x=0.5)
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

    col4, col6 = st.beta_columns(2)
    with col4, col6:
        fig8, fig10 = fifth_block(df_drugs)
        col4.subheader(f"Drug prices for categories with at least {st_slider_offer_min} offers.")
        col4.plotly_chart(fig8, use_container_width=True)
        col6.subheader(f"Average prices for each category with at least {st_slider_offer_min} offers.")
        col6.plotly_chart(fig10, use_container_width=True)

# rename misspelled column
df_vendors.rename(columns={'verifcation': 'verification'}, inplace=True)

# # Add number of offers to vendor df
# nr_offers = pd.DataFrame(df_drugs.groupby('vendor').vendor.count())
# nr_offers.columns = ['nr_offers']
# nr_offers.reset_index(inplace=True)
# df_vendors = df_vendors.merge(nr_offers, on='vendor', how='left')

# count rank
ranks = pd.DataFrame(df_vendors['rank'].value_counts())
ranks.reset_index(inplace=True)
ranks.columns = ['rank', 'count']

# verification rank
verification = pd.DataFrame(df_vendors['verification'].value_counts())
verification.reset_index(inplace=True)
verification.columns = ['verification', 'count']

if chapter == "3. Vendor Insights":
    st.header("Vendor insights")
    st.subheader("Total number of vendors over time in the category 'Drugs & Chemicals'")
    st.write("Torrez launched in February 2020 and has become very popular. After a modest start we observe one rapid increase in the number of vendors with at least a listing in the category 'Drugs & Chemicals'. ")

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

    # Add number of offers to vendor df
    nr_offers = pd.DataFrame(df_drugs.groupby('vendor').vendor.count())
    nr_offers.columns = ['nr_offers']
    nr_offers.reset_index(inplace=True)
    df_vendors = df_vendors.merge(nr_offers, on='vendor', how='left')

    st.subheader("Rank")
    st.write("The rank indicates the number of sales of the vendor on the market. "
             "Rank 0 represents 0-9 items sold, Rank 1 represents 10-99 items sold, Rank 3 represents 100-199 items sold, etc. "
             "A Top seller has over 1000 sales. Only a small percentage of the vendors have a high rank.")

    import plotly.graph_objects as go

    rank_order = ['Rank 0', 'Rank 1', 'Rank 2', 'Rank 3', 'Rank 4', 'Rank 5', 'Rank 6',
                  'Rank 7', 'Rank 8', 'Rank 9', 'Rank 10', 'TOP',]
    col_vendor_1, col_vendor_2 = st.beta_columns(2)
    with col_vendor_1, col_vendor_2:
        # pie chart ranks
        ranks = ranks.sort_values('rank')
        fig12 = go.Figure(data=[go.Pie(labels=ranks['rank'], values=ranks['count'], hole=.4)])
        fig12.update_layout(legend_traceorder="normal")
        #fig12 = px.pie(ranks, names='rank', values='count', category_orders={'rank':rank_order})
        col_vendor_1.plotly_chart(fig12, use_container_width=True)

        # bar chart ranks
        fig21 = px.bar(ranks, x='rank', y='count', category_orders={'rank':rank_order}, labels={
                     "rank": "", 'count':'frequency'})
        col_vendor_2.plotly_chart(fig21, use_container_width=True)

    st.subheader("Verification level")
    st.write("Every vendor on Torrez that has a positive history from other markets can get a verification badge. "
             "The level indicates the number of other markets the vendor is active on.")

    verification_order = ["Level 0", "Level 1", "Level 2", "Level 3", "Level 4",
                          "Level 5", "Level 6", "Level 7", "Level 8",
                          'Level 9', 'Level 10', 'Level 11', 'Level 12',
                          'Level 13', 'Level 14', 'Level 15', 'Level 16',
                          'Level 19']

    col_vendor_1, col_vendor_2 = st.beta_columns(2)
    with col_vendor_1, col_vendor_2:
        verification['verification'] = verification['verification'].str.replace('Verification ', "").str.replace('No verification level', 'Level 0')
        # pie chart verification
        fig13 = go.Figure(data=[go.Pie(labels=verification['verification'], values=verification['count'], hole=.4)])
        #fig13 = px.pie(verification, names='verification', values='count')
        col_vendor_1.plotly_chart(fig13, use_container_width=True)

        # bar chart verification
        fig13 = px.bar(verification, x='verification', y='count', category_orders={'verification':verification_order},
                       labels={"verification": "", 'count':'frequency'})
        col_vendor_2.plotly_chart(fig13, use_container_width=True)



    st.subheader("Transactions")
    st.write('The number of sales a vendor has made so far. We observe a skewed distribution when taking all vendors into account. '
             'You can adjust the verification levels to see specific distributions.')

    # verification levels filter
    df_vendors['verification'].fillna("Level 0", inplace=True)
    all_verifications = df_vendors['verification'].unique().tolist()
    all_verifications.append('All levels')
    st_ms_ver = st.multiselect("Select which verification level(s) you want to display.", all_verifications,
                           default=['All levels'])
    if 'All levels' in st_ms_ver:
        st_ms_ver = df_vendors['verification'].unique().tolist()

    col_vendor_3, col_vendor_4 = st.beta_columns([2.5,1])
    with col_vendor_3, col_vendor_4:

        fig12 = px.histogram(df_vendors[df_vendors['verification'].isin(st_ms_ver)],
        x="transactions", title='Distribution of Transactions', nbins=50,
                       labels={"transactions": "number of transactions", 'count':'frequency'})
        col_vendor_3.plotly_chart(fig12, use_container_width=True)

        fig12 = px.box(df_vendors[df_vendors['verification'].isin(st_ms_ver)],
        y="transactions", title='Boxplot',
                       labels={'transactions':'number of transactions'})
        col_vendor_4.plotly_chart(fig12, use_container_width=True)


    st.subheader("Number of offers")
    st.write('The number of offers a vendor has in the category "Drugs & Chemicals". We again observe a skewed distribution when taking all vendors into account. '
             'You can adjust the ranks to see specific distributions.')
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
            title='Distribution of the number of offers per vendor', nbins=50,
                       labels={"nr_offers": "number of offers"})
        col_vendor_3.plotly_chart(fig13, use_container_width=True)

        fig12 = px.box(df_vendors[df_vendors['rank'].isin(st_ms_rank)],
        y="nr_offers", title='Boxplot',
                       labels={"nr_offers": "number of offers"})
        col_vendor_4.plotly_chart(fig12, use_container_width=True)


# if chapter == "4. Insights":
#     # st.header("Graphs")
#     st.subheader("Some hypotheses to be investigated")
#     st.write(" * Do vendors select one specialty within drugs or sell a wide range?\n "
#              " * Does the country of origin have an effect on prices?\n"
#              " * Is trust a factor in prices?\n"
#              " * Do trusted vendors have more transactions?\n"
#              " * Is worldwide shipping a predictor for number of deals?\n"
#              " * Do higher ranked vendors sell special kind of drugs?\n"
#              " * Do higher ranked vendors have higher prices?")
#
#     df_vendors['date'] = pd.to_datetime(df_vendors['since'])
#     now = pd.to_datetime('Apr 18, 2021')
#     df_vendors['num_months'] = (now.year - df_vendors.date.dt.year) * 12 + (now.month - df_vendors.date.dt.month)
#     df_vendors['transactions_month'] = df_vendors['transactions']/df_vendors['num_months']
#     fig = px.box(df_vendors, x='verification',
#                    y="transactions_month", title='Boxplot')
#     st.plotly_chart(fig, use_container_width=True)


    #col_1, col_2 = st.beta_columns(2)
    #with col_1, col_2:
    #    # boxplot rank vs price
    #    df_drugs = df_drugs.merge(df_vendors[['vendor', 'rank', 'verification']], on='vendor', how='left')
    #    fig14 = px.box(df_drugs, x='rank', y="price in $")
    #    col_1.plotly_chart(fig14)

    #    # boxplot verification vs price
    #    df_drugs.verification = df_drugs.verification.str.replace('Verification', "")
    #    fig15 = px.box(df_drugs, x='verification', y="price in $")
    #    col_2.plotly_chart(fig15)

    #    # distribution of categories level 2 for the vendors
    #    unique_cat_level_2 = pd.DataFrame(df_drugs.groupby('vendor').category_level_2.nunique()).reset_index()
    #    fig16 = px.histogram(unique_cat_level_2,
    #        x="category_level_2", title='Distribution of number of categories (level 2)', nbins=50)
    #    col_1.plotly_chart(fig16)

    #    unique_cat_level_highest = pd.DataFrame(df_drugs.groupby('vendor').highest_category.nunique()).reset_index()
    #    fig17 = px.histogram(unique_cat_level_highest,
    #                         x="highest_category", title='Distribution of number of categories (highest_category)', nbins=50)
    #    col_2.plotly_chart(fig17)

    #    pass

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


elif chapter == '4. Advanced Insights':
    st.header("Advanced insights")
    st.write("In the previous sections we have provided some general but interesting insights regarding the product "
             "offerings and vendors on Torrez. In this section we will go a step further and analyse the market in "
             "more detail. We are specifically interested in relationships that enable us to better grasp the dynamics "
             "and interactions within this market. With these new insights the drug trafficking flow becomes more understandable. "
             "We will first dive into the drugs sold by the top vendors after which we will investigate the effect of trust in this market.")

    # st.header("Hypotheses")
    # st.subheader("Some hypotheses to be investigated")
    # df_drugs, df_vendors = get_all_data()
    # st.write(" * Do vendors select one specialty within drugs or sell a wide range?\n "
    #          " * Do higher ranked vendors sell special kind of drugs?\n"
    #          " * Do trusted vendors have more transactions?\n"
    #          " * Is worldwide shipping a predictor for number of deals?\n"
    #          " * Is trust a factor in prices?\n"
    #          " * Does the country of origin have an effect on prices?\n"
    #          " * Do higher ranked vendors have higher prices?")

    st.write("___")
    st.header("Do vendors select one specialty within drugs or do they sell a wide range of drugs?")
    st.write("We wondered whether the vendors on the dark web are well-versed in the entire criminal circuit or might just "
             "have a connection with one kind of drugs and are experts in that. Additionally, it would be possible that "
             "several drugs are often sold in conjunction. For instance, cocaine and psychedelics have vastly different "
             "effects, and one could imagine that expertise in one category would not necessarily translate into knowledge "
             "of the other. We set out to investigate that. ")

    st.write("Torrez works with a hierarchy that can be selected by the vendor. However, this is optional, and vendors "
             "can decide not to further specify their offers. Our dataset is specifically selected within the first level, "
             "'Drugs & Chemicals'. The chart beneath showcases the spread of the second level categories. "
             " We have selected the 50 vendors with the highest amount of active offers at the time of the scraping,"
             " as that would give us the most insight. The results in a cut-off of 63 offers. The categories are sorted "
             "on the quantity of the offers (descending), similarly, the vendors are sorted as well (descending). "
             "The size of the dots refers to the amount of offers for that specific category and vendor combination; "
             "specific numbers are visible in the tooltip when hovering. The color is based on the same metric, with "
             "more blue matching to more offers. As not all offers had a specified category assigned, we assigned those "
             "offers an 'Not provided' label, plotted them on the bottom and colored them gray.")

    st.write("The resulting figure, as shown below, is very information dense. We will cover some interesting insights, "
             "but have left some others to be discovered by the reader. ")

    # Quite a chained operation, so explanation:
    # Groupby vendor, then show count. Sort values by product (the column here doesn't matter too much, as long as these no missings)
    # Show the top 10 highest # of offers and take the index (the account names) to convert that to a list for further selection
    top_vendors = df_drugs.groupby("vendor").count().sort_values('product', ascending=False).head(50).index.tolist()
    top_vendors_offers = df_drugs[df_drugs['vendor'].isin(top_vendors)]
    top_vendors_offers.fillna("Not provided", inplace=True)

    # A new groupby such that the index is (vendor, category) and the resulting value is frequency ("count").
    df_plot_data = top_vendors_offers.groupby(['vendor', 'category_level_2']).count().reset_index()[['vendor', 'category_level_2', 'product']]
    df_not_provided_2 = df_plot_data[df_plot_data['category_level_2'] == 'Not provided']
    df_rest_2 = df_plot_data[~df_plot_data.isin(df_not_provided_2)].dropna(axis=0)

    level_2_order = ['Cannabis & Hash', 'Dissociatives', 'Ecstasy', 'Opiates', 'Stimulants',
                                        'Psychedelics', 'Benzos', 'Prescriptions Drugs', 'Steroids', 'Weight Loss',
                                        'Accessories', 'Not provided']

    vendor_top = alt.Chart(df_rest_2).mark_circle().encode(
        alt.Y('category_level_2:O', sort=level_2_order, title='Categories'),
        alt.X('vendor:N', sort=top_vendors, title='Vendors'),
        alt.Size('product:Q', legend=None),
        alt.Color('product:Q', legend=None), # sort='descending'),
        opacity=alt.value(1),
        tooltip = [alt.Tooltip('vendor', title='Vendor'),
                   alt.Tooltip('category_level_2', title='Category'),
                   alt.Tooltip('product', title='Number of offers')
                   ]
    )

    vendor_top_missing = alt.Chart(
        df_not_provided_2
    ).mark_circle(
        color='gray'
    ).encode(
        alt.Y('category_level_2:N', sort=level_2_order),
        alt.X('vendor',
              sort=top_vendors),
        alt.Size('product:Q', legend=None),
        tooltip = [alt.Tooltip('vendor', title='Vendor'),
                   alt.Tooltip('category_level_2', title='Category'),
                   alt.Tooltip('product', title='Number of offers')
                   ]
    )

    st.altair_chart(
        (vendor_top + vendor_top_missing).configure_axis(
            labelFontSize=12,
            titleFontSize=20,
            labelAngle=-30,
        ).configure_title(
            fontSize=32
        ).properties(
            height=500, title="What categories of drugs are sold in conjunction?"
        ), use_container_width=True
    )

    st.markdown("""
        ### 1. _Cannabis & Hash_ is the most popular category on the marketplace. 

        Ten out of the top 50 vendors have over 50 offers just on these drugs, with 3 out of the top 4 vendors selling
        either exclusively or almost exclusively these drugs. 

        ### 2. There are two kinds of _Cannabis & Hash_ vendors.

        Vendors like California420service, PitStopUK or kandykones only offer weed (100% of offers), 
        while RoyalMailer (84%), StrainPirate (98%) and topmoneymaker (92%) clearly prioritize the category. Vendors 
        for whom _cannabis & hash_ aren't the main priority generally sell in a lot of other categories, but almost 
        all of them sell _Stimulants_ and _Psychedelics_.
        
        ### 3. _Prescription drugs_ vendors and _Steroids_ vendors specialize in these drugs.
        
        Similar to the main _cannabis & hash_ vendors, vendors of _prescription drugs_ and vendors of _steroids_ 
        barely sell anything else. Vendors as akgeneric, SteroidWarehouse, thebodyshop, bestgroup and PSteroids almost 
        exclusively sell drugs from within these two categories. Curiously, none of the vendors sell _cannabis & hash_, 
        despite that being the most popular drug.
        
        ### 4. Three distinct types of vendors can be identified.   

        Based on the available offers per vendor, we can identify three blocks of vendors. 
        #### &ensp;&ensp;&ensp;&ensp; 1. _Cannabis & Hash_
        #### &ensp;&ensp;&ensp;&ensp; 2. _Dissociatives, Ecstacy, Opiates, Stimulants, Psychedelics_
        #### &ensp;&ensp;&ensp;&ensp; 3. _Benzos, Prescriptions Drugs, Steroids, Weight Loss, Accessories_
        
        After noting the peculiarities of the weed sales, the remaining categories can very distinctively be separated 
        into two separate groups: drugs sold by almost all vendors and drugs sold by a select few vendors. Drugs in the
        second group have vendors which also basically sell all drugs in that group, while the drugs in the last group
        have specialized vendors that do not or barely sell anything else. 
        
        """)

    st.write("___")

    st.write("Because our marketplace allowed vendors to also select a subcategory, we will delve into that as well. "
             "Similar to the figure above, this figure is very information dense (even more so!), yet some (expanded) "
             "insights will be described. Changes to the layout were kept to a minimum, with the axes and the order "
             "staying the same. The size of the dots, again, represents the amount of offers. As each category represents "
             "multiple subcategories, we changed the color coding to match a block of the main category. Thus, the first "
             "color (blue) refers to the main category _Cannabis & Hash_, and this category starts at _Buds & Flowers_ "
             "and extends to _Vaping_. Subcategories were sorted alphebetically, while the main categories retain their "
             "order of the graph above. Notably, one exception is in place: _benzos_ (red). Torrez uses the subcategory "
             "_pills_ for _Ecstacy_ as well, and thus these are plotted together. The color coding is correct, for a "
             "more convenient interpretation the other _benzos_ category is plotted next to the _pills_. ")


    # Quite a chained operation, so explanation:
    # Groupby vendor, then show count. Sort values by product (the column here doesn't matter too much, as long as these no missings)
    # Show the top 50 highest # of offers and take the index (the account names) to convert that to a list for further selection
    top_vendors = df_drugs.groupby("vendor").count().sort_values('product', ascending=False).head(50).index.tolist()
    top_vendors_offers = df_drugs[df_drugs['vendor'].isin(top_vendors)]
    top_vendors_offers.fillna("Not provided", inplace=True)

    # A new groupby such that the index is (vendor, category) and the resulting value is frequency ("count").
    df_plot_data = top_vendors_offers.groupby(['vendor', 'category_level_3', 'category_level_2']).count().reset_index()[['vendor', 'category_level_2', 'category_level_3', 'product']]
    df_not_provided = df_plot_data[df_plot_data['category_level_3'] == 'Not provided']
    df_rest = df_plot_data[~df_plot_data.isin(df_not_provided)].dropna(axis=0)

    level_3_order = [
        'Buds & Flowers', 'Edibles', 'Hash', 'Prerolls', 'Seeds', 'Shake', 'Synthetic', 'Topical', 'Vaping', # Cannabis & Hash
        'GBL', 'Ketamine', # Dissociatives
        'MDMA', 'Pills', # Ecstacy
        'Powder', # Benzos
        'Codeine', 'Heroin', 'Oxycodone', 'RC', # Opiates
        '4-FA', 'Adderal', 'Crack', 'Cocaine', 'Meth', 'Speed', 'TMA', # Stimulants
        '2C-B', '5-MeO-DMT', 'DMT', 'LSD', 'Mescaline', 'Mushrooms', # Psychedelics
        'Not provided']

    vendors_top = alt.Chart(df_rest).mark_circle().encode(
        alt.Y('category_level_3:O', title='Categories', sort=level_3_order),
        alt.X('vendor:N', sort=top_vendors, title='Vendors'),
        alt.Size('product:Q', legend=None),
        alt.Color('category_level_2:N', legend=None, sort=level_2_order,
                   scale=alt.Scale(scheme='category20'),
                  ),
        opacity=alt.value(1),
        tooltip = [alt.Tooltip('vendor', title='Vendor'),
                   alt.Tooltip('category_level_2', title='Category lvl 2'),
                   alt.Tooltip('category_level_3', title='Category lvl 3'),
                   alt.Tooltip('product', title='Number of offers'),
                   ]
    )

    vendor_top_missing = alt.Chart(
        df_not_provided
    ).mark_circle(
        color='gray'
    ).encode(
        alt.Y('category_level_3:N', sort=level_3_order
             ),
        alt.X('vendor',
              sort=top_vendors),
        alt.Size('product:Q', legend=None),
        tooltip = [alt.Tooltip('vendor', title='Vendor'),
                   alt.Tooltip('category_level_2', title='Category lvl 2'),
                   alt.Tooltip('category_level_3', title='Category lvl 3'),
                   alt.Tooltip('product', title='Number of offers'),
                   ]
    )

    st.altair_chart(
        (vendors_top + vendor_top_missing).configure_axis(
            labelFontSize=12,
            titleFontSize=20,
            labelAngle=-30,
        ).configure_axisY(
            labelAngle=0,
        ).configure_title(
            fontSize=32
        ).properties(
            height=700, title="What subcategories of drugs are sold in conjunction?"
        ), use_container_width=True
    )

    st.markdown("""
        ### 1. _Buds & Flowers_ explains popularity _Cannabis & Hash_
        
        With the noted presence of _Cannabis & Hash_, we see that _Buds & Flowers_ are mainly responsible for this 
        effect. Most subcategories however are barely sold, not in quantity in offers nor in quantity of vendors. A 
        possible explanation would be that there are a lot of strains for cannabis, and logically the type of flower
        matters to prospective buyers. For other types of drugs, say cocaine, only purity matters, and individual 
        vendors do not have dozens of types of cocaine. 
        
        ### 2. _Ketamine_, _MDMA_ and _Cocaine_ are popular
        
        On the other hand, _Ketamine_, _MDMA_ and _Cocaine_ are sold by a lot of different vendors (and often the same 
        vendors), but a single vendor has at most 28 offers of one category. We can hypothesize about the underlying 
        reasons, partly already explained in the previous finding, but it's peculiar nonetheless. 
    """)


    st.markdown("""
        ### 3. Several subcategories are only sold by one or a few vendors
        
        For instance, the subcategories as _Seeds_, _Synthetic_, _GBL_, _Powder_, _Codeine_, _4-FA_, _TMA_, _DMT_ and 
        _Mescaline_ are only offered by at most two vendors out of the top 50. In a similar vain, vendors that offer 
        drugs in the _Cannabis & Hash_ (blue), _Ecstacy_ (orange) or _Stimulants_ (green) categories generally offer 
        multiple subcategories if not all. On the flipside, vendors that sell drugs within the _Benzos_ (red) or 
        _Opiates_ (beige) categories only sell one specific subcategory. Due to our limited expertise we cannot 
        formulate a hypothesis that could potentially explain this.
        
        ### 4. _Prescription drugs_, _Steroids_ and _Weight Loss_ drugs do not have subcategories
 
        With a total of 1158 offers within these categories, one could propose that further specification is in place. 
        Torrez however does not allow any subcategories within these categories. Scrolling through the offers here show
        a wide variety of drugs in each one, though we're unaware whether a proper (categorical) distinction could 
        possibly be created. 
        
        Furthermore, the accessories category does not have subcategories as well. However, with only 10 offers this 
        would not benefit anyone. Additionally, several listings should not have been placed in the _Drugs & Chemicals_
        main category of Torrez at all, such as a "Facebook hack", tasers or a Netflix gift card.          
    """)

    st.write(df_drugs[df_drugs['category_level_2'].isin(['Weight Loss', 'Prescriptions Drugs', 'Steroids'])].reset_index(drop=True).head(10))
    st.write(df_drugs[df_drugs['category_level_2'].isin(['Accessories'])].reset_index(drop=True).head(10))

    st.markdown("""
        As shown above, 
    """)

# Highlight some notable users, pivot the same table. Size = average price (say vendor, category, category 3 as index, indiv offers as data). 
# Helps answer whether specialists are more expensive or not, or diversification:
        
        # Also add tool that allows for individual users to be plotted 

    st.write("___")

    # Quite a chained operation, so explanation:
    # Groupby vendor, then show count. Sort values by product (the column here doesn't matter too much, as long as these no missings)
    # Show the top 50 highest # of offers and take the index (the account names) to convert that to a list for further selection
    top_vendors = df_drugs.groupby("vendor").count().sort_values('product', ascending=False).head(50).index.tolist()
    top_vendors_offers = df_drugs[df_drugs['vendor'].isin(top_vendors)]
    top_vendors_offers.fillna("Not provided", inplace=True)

    # A new groupby such that the index is (vendor, category) and the resulting value is frequency ("count").
    list_of_dollars = [round(float(x)) if len(x) <= 6 else float(x[:-3].replace(",", "")) for x in top_vendors_offers['price in $']]


    #top_vendors_offers['conv_price'] = list_of_dollars

    plot_df = top_vendors_offers.groupby(['vendor', 'category_level_2', 'category_level_3', 'shipping_from']).agg(['mean', 'count'])
    plot_df.columns = ['Mean product price', 'Count']
    plot_df['Mean product price'].astype(int)
    plot_df.reset_index(inplace=True)

    #df_plot_data = top_vendors_offers.groupby(['vendor', 'category_level_3', 'category_level_2']).count().reset_index()[['vendor', 'category_level_2', 'category_level_3', 'product', 'price in $']]
    df_not_provided = plot_df[plot_df['shipping_from'] == 'Not provided']
    df_rest = plot_df[~plot_df.isin(df_not_provided)].dropna(axis=0)
    st.write(df_rest)
    st.write(df_not_provided)
    st.write(df_drugs)

    for seller in df_rest['vendor']:
        country_of_origin = df_vendors[df_vendors['vendor'] == seller]

    level_3_order = [
        'Buds & Flowers', 'Edibles', 'Hash', 'Prerolls', 'Seeds', 'Shake', 'Synthetic', 'Topical', 'Vaping', # Cannabis & Hash
        'GBL', 'Ketamine', # Dissociatives
        'MDMA', 'Pills', # Ecstacy
        'Powder', # Benzos
        'Codeine', 'Heroin', 'Oxycodone', 'RC', # Opiates
        '4-FA', 'Adderal', 'Crack', 'Cocaine', 'Meth', 'Speed', 'TMA', # Stimulants
        '2C-B', '5-MeO-DMT', 'DMT', 'LSD', 'Mescaline', 'Mushrooms', # Psychedelics
        'Not provided']

    vendors_top = alt.Chart(df_rest).mark_circle().encode(
        alt.X('category_level_2:O', title='Categories', sort=level_2_order),
        alt.Y('vendor:N', sort=top_vendors, title='Vendors'),
        alt.Size('Count:Q', legend=None),
        alt.Color('shipping_from',
                   scale=alt.Scale(scheme='category20'),
                  ),
        opacity=alt.value(1),
        tooltip = [alt.Tooltip('vendor', title='Vendor'),
                   alt.Tooltip('category_level_2', title='Category lvl 2'),
                   alt.Tooltip('category_level_3', title='Category lvl 3'),
                   alt.Tooltip('Count', title='Number of offers'),
                   alt.Tooltip('Mean product price', title='Average price of listing'),
                   alt.Tooltip('shipping_from', title='Country of origin')
                   ]
    )

    vendor_top_missing = alt.Chart(
        df_not_provided
    ).mark_circle(
        color='gray'
    ).encode(
        alt.X('category_level_2:N', sort=level_2_order
             ),
        alt.Y('vendor',
              sort=top_vendors),
        alt.Size('Count:Q', legend=None),
        tooltip = [alt.Tooltip('vendor', title='Vendor'),
                   alt.Tooltip('category_level_2', title='Category lvl 2'),
                   alt.Tooltip('category_level_3', title='Category lvl 3'),
                   alt.Tooltip('Count', title='Number of offers'),
                   alt.Tooltip('Mean product price', title='Average price of listing'),
                   alt.Tooltip('shipping_from', title='Country of origin')
                   ]
    )


    col2, col4 = st.beta_columns(2)
    col2.altair_chart(
        (vendors_top + vendor_top_missing).configure_axis(
            labelFontSize=12,
            titleFontSize=20,
            labelAngle=-30,
        ).configure_axisY(
            labelAngle=0,
        ).configure_title(
            fontSize=32
        ).properties(
            height=1000, width=700, title="Number of offers"
        ),
    )


    # EXTENTION:
    # Order such that continents are together

    # Above: size = counts, color is country of origin. Order them together

    # Below: size = mean price


    vendors_top = alt.Chart(df_rest).mark_circle().encode(
        alt.X('category_level_2:O', title='Categories', sort=level_2_order),
        alt.Y('vendor:N', sort=top_vendors, title='Vendors'),
        alt.Size('Mean product price:Q', legend=None),
        alt.Color('shipping_from',
                   scale=alt.Scale(scheme='category20'),
                  ),
        opacity=alt.value(1),
        tooltip = [alt.Tooltip('vendor', title='Vendor'),
                   alt.Tooltip('category_level_2', title='Category lvl 2'),
                   alt.Tooltip('category_level_3', title='Category lvl 3'),
                   alt.Tooltip('Count', title='Number of offers'),
                   alt.Tooltip('Mean product price', title='Average price of listing'),
                   alt.Tooltip('shipping_from', title='Country of origin')
                   ]
    )

    vendor_top_missing = alt.Chart(
        df_not_provided
    ).mark_circle(
        color='gray'
    ).encode(
        alt.X('category_level_2:N', sort=level_2_order
             ),
        alt.Y('vendor',
              sort=top_vendors),
        alt.Size('Mean product price:Q', legend=None),
        tooltip = [alt.Tooltip('vendor', title='Vendor'),
                   alt.Tooltip('category_level_2', title='Category lvl 2'),
                   alt.Tooltip('category_level_3', title='Category lvl 3'),
                   alt.Tooltip('Count', title='Number of offers'),
                   alt.Tooltip('Mean product price', title='Average price of listing'),
                   alt.Tooltip('shipping_from', title='Country of origin')
                   ]
    )

    col4.altair_chart(
        (vendors_top + vendor_top_missing).configure_axis(
            labelFontSize=12,
            titleFontSize=20,
            labelAngle=-30,
        ).configure_axisY(
            labelAngle=0,
        ).configure_axisX(
            labelFontSize=12,
        ).configure_title(
            fontSize=32
        ).properties(
            height=1000, width=700, title="Mean product price"
        ),
    )

    strip = alt.Chart(df_drugs).mark_tick().encode(
        x= #alt.X('jitter:Q',

            'shipping_from', # prices also works well
        y='category_level_2',
        color='shipping_from',
        tooltip=[alt.Tooltip('vendor', title='Vendor'),
                 alt.Tooltip('category_level_2', title='Category lvl 2'),
                 alt.Tooltip('category_level_3', title='Category lvl 3'),
                 alt.Tooltip('shipping_from', title='Country of origin')
                 ]
    )

    st.altair_chart(strip)



    shipping_from_countries = list(df_drugs.shipping_from.unique())
    shipping_from_countries_copy = ['All countries'] + shipping_from_countries
    select_country = st.multiselect('Select what country/countries you want to see the data of.',
                                       options=shipping_from_countries_copy, default=['Netherlands', 'Australia', 'United States'])
    if 'All countries' in select_country:
        select_country = shipping_from_countries

    df_under_50 = df_drugs[df_drugs['price'] <= 10000]
    df_country = df_under_50[df_under_50['shipping_from'].isin(select_country)] # 1000/len(select_country)


    stripplot_by_category =  alt.Chart(df_country, width=120).mark_point().encode(
        x=alt.X(
            'jitter:Q',
            title=None,
            axis=alt.Axis(values=[0], ticks=True, grid=True, labels=False),
            scale=alt.Scale(),
        ),
        y=alt.Y('price:Q'), # cat lvl 2: N
        color=alt.Color('shipping_from:N'),
        tooltip=[alt.Tooltip('price in $', title='Listed price'),
                 alt.Tooltip('product', title='Number of offers'),
                 alt.Tooltip('category_level_2', title='Category lvl 2'),
                 alt.Tooltip('category_level_3', title='Category lvl 3'),
                 alt.Tooltip('shipping_from', title='Ships from')
                 ],
        size='price:Q',
        column=alt.Column(
            'category_level_2:N',
            #title='shipping_from',
            header=alt.Header(
                labelAngle=-15,
                titleOrient='top',
                labelOrient='bottom',
                labelAlign='center',
                labelPadding=350,
                labelFontSize=16,
                labelColor='white'
            ),
        ),
      ).transform_calculate(
        # Generate Gaussian jitter with a Box-Muller transform
        jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
    )
    st.altair_chart(stripplot_by_category, use_container_width=False)


    stripplot_by_country = alt.Chart(df_country, width=min(1440/len(select_country), 200)).mark_point().encode(
        x=alt.X(
            'jitter:Q',
            title=None,
            axis=alt.Axis(values=[0], ticks=True, grid=True, labels=False),
            scale=alt.Scale(),
        ),
        y=alt.Y('price:Q'), # cat lvl 2: N
        color=alt.Color('shipping_from:N'),
        tooltip=[alt.Tooltip('price in $', title='Listed price'),
                 alt.Tooltip('product', title='Number of offers'),
                 alt.Tooltip('category_level_2', title='Category lvl 2'),
                 alt.Tooltip('category_level_3', title='Category lvl 3'),
                 alt.Tooltip('shipping_from', title='Ships from'),
                 alt.Tooltip('shipping_to', title='Ships to')
                 ],
        size='price:Q',
        column=alt.Column(
            'shipping_from',
            title='Listed offers by country of origin',
            header=alt.Header(
                titleFontSize=32,
                labelFontSize=24,
                #labelAngle=-15,
                titleOrient='top',
                labelOrient='bottom',
                labelAnchor='middle',
                labelAlign='center',
                labelPadding=330,
            ),
        ),
      ).transform_calculate(
        # Generate Gaussian jitter with a Box-Muller transform
        jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
    ).configure_axisY(
    titleFontSize=16,
).configure_header(
    titleColor='white',
    titleFontSize=32,
    labelColor='white',
    labelFontSize=16
).interactive()

    st.altair_chart(stripplot_by_country, use_container_width=False)





    stripplot_by_receiving_country = alt.Chart(df_country, width=1440/len(df_country['shipping_to'].unique())).mark_point().encode(
        x=alt.X(
            'jitter:Q',
            title=None,
            axis=alt.Axis(values=[0], ticks=True, grid=True, labels=False),
            scale=alt.Scale(),
        ),
        y=alt.Y('price:Q'), # cat lvl 2: N
        color=alt.Color('shipping_from:N'),
        tooltip=[alt.Tooltip('price in $', title='Listed price'),
                 alt.Tooltip('product', title='Number of offers'),
                 alt.Tooltip('category_level_2', title='Category lvl 2'),
                 alt.Tooltip('category_level_3', title='Category lvl 3'),
                 alt.Tooltip('shipping_from', title='Ships from'),
                 alt.Tooltip('shipping_to', title='Ships to')
                 ],
        size='price:Q',
        column=alt.Column(
            'shipping_to',
            title='Listed offers by receiving country',
            header=alt.Header(
                labelAngle=-15,
                titleOrient='top',
                labelOrient='bottom',
                labelAnchor='middle',
                labelAlign='right',
                labelPadding=350,
            ),
        ),
      ).transform_calculate(
        # Generate Gaussian jitter with a Box-Muller transform
        jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
    ).configure_axisY(
        titleFontSize=16,
    ).configure_header(
    titleColor='white',
    titleFontSize=32,
    labelColor='white',
    labelFontSize=16
).interactive()


    st.altair_chart(stripplot_by_receiving_country, use_container_width=False)

    st.write("___")
    st.header("To what extent does trust play a role?")
    st.write("Trust plays a key role in any transaction. Especially on the dark web where vendors are anonymous. "
             "In order for vendors to run a successful business, they need to gain the consumers' trust. "
             "TorreZ awards vendors several indicators of their experience and trustworthiness: the rank, the verificaiton level and the feedbacks. "
             "The rank of the vendors shows how many sales a vendor has on the TorreZ market. A higher rank indicates a more experienced vendor. "
             "The verification level indicates the vendors activity on other markets. The higher the level, the more markets the vendor is active on. "
             "Finally, TorreZ allows consumers to leave feedback of the vendor after a transaction has taken place. "
             "We were wondering if these trust indicators could lead to a difference in consumer behavior. ")

    st.subheader("Do vendors with a higher verification level have more transactions?")

    df_vendors['date'] = pd.to_datetime(df_vendors['since'])
    now = pd.to_datetime('Apr 18, 2021')
    df_vendors['num_months'] = (now.year - df_vendors.date.dt.year) * 12 + (now.month - df_vendors.date.dt.month)
    df_vendors['transactions_month'] = df_vendors['transactions']/df_vendors['num_months']

    verification_order = ["Verification Level 1", "Verification Level 2", "Verification Level 3", "Verification Level 4",
                          "Verification Level 5", "Verification Level 6", "Verification Level 7", "Verification Level 8",
                          'Verification Level 9', 'Verification Level 10', 'Verification Level 11', 'Verification Level 12',
                          'Verification Level 13', 'Verification Level 14', 'Verification Level 15', 'Verification Level 16',
                          'Verification Level 19']


    fig = px.box(df_vendors, x='verification',
                   y="transactions_month", title='Boxplot', category_orders={'verification':verification_order})
    st.plotly_chart(fig, use_container_width=True)


    st.markdown("""
                ####  Higher verified vendors do not have more transactions on average.
                
                The chart indicates that the verification level is not correlated with the number of transactions per month.
             Apparently, level 8 and 11 had the most transactions per month on average.
             Looking at the median, it even seems that higher level vendors have a lower number of sales per month.
             This could potentially be explained by different products offerings or products with higher prices on average. """)

    st.subheader("Do vendors with a higher verification level have more different product offerings?")

    nr_offers = pd.DataFrame(df_drugs.groupby(['vendor', 'category_level_2']).vendor.count())
    nr_offers.columns = ['nr_offers']
    nr_offers.reset_index(inplace=True)
    # df_vendors = df_vendors.merge(nr_offers, on='vendor', how='left')
    # df_combined = df_vendors.merge(df_drugs, on='vendor')
    df_verification = nr_offers.merge(df_vendors, on='vendor')
    df_verification.category_level_2.fillna("Not provided", inplace=True)
    df_combined_grouped = df_verification.groupby(['verification', 'category_level_2']).mean().reset_index()


    df_plot_data = df_combined_grouped.groupby(['verification', 'category_level_2']).mean().reset_index()[
        ['verification', 'category_level_2', 'nr_offers']]
    df_not_provided_2 = df_plot_data[df_plot_data['category_level_2'] == 'Not provided']
    df_rest_2 = df_plot_data[~df_plot_data.isin(df_not_provided_2)].dropna(axis=0)

    level_2_order = ['Cannabis & Hash', 'Dissociatives', 'Ecstasy', 'Opiates', 'Stimulants',
                     'Psychedelics', 'Benzos', 'Prescriptions Drugs', 'Steroids', 'Weight Loss',
                     'Accessories', 'Tobacco', 'Not provided']


    vendor_top = alt.Chart(df_combined_grouped).mark_circle().encode(
        alt.Y('category_level_2:O', sort=level_2_order, title='Categories'),
        alt.X('verification:N', sort=verification_order, title='Verification level'),
        alt.Size('nr_offers:Q', legend=None),
        alt.Color('nr_offers:Q', legend=None),  # sort='descending'),

        opacity=alt.value(1),
        tooltip=[alt.Tooltip('verification', title='Level'),
                 alt.Tooltip('category_level_2', title='Category'),
                 alt.Tooltip('nr_offers', title='Number of offers')
                 ]
    )

    vendor_top_missing = alt.Chart(
        df_not_provided_2
    ).mark_circle(
        color='gray'
    ).encode(
        alt.Y('category_level_2:N', sort=level_2_order),
        alt.X('verification:N', sort=verification_order),
        alt.Size('nr_offers:Q', legend=None),
        tooltip=[alt.Tooltip('verification', title='Level'),
                 alt.Tooltip('category_level_2', title='Category'),
                 alt.Tooltip('nr_offers', title='Number of offers')
                 ]
    )

    st.altair_chart(
        (vendor_top + vendor_top_missing).configure_axis(
            labelFontSize=12,
            titleFontSize=20,
            labelAngle=-30,
        ).configure_title(
            fontSize=32
        ).properties(
            height=500, title="What categories of drugs are sold in conjunction?"
        ), use_container_width=True
    )

    st.markdown("""
                ####  Higher verified vendors have different product offerings

                From the "Vendor insights" page we already observed a low number of vendors having a high verification level. 
                Looking at their product offerings in more detail, we see that they deviate from the lower verified vendors. 
                To make a fair comparison we computed the mean number of offers per category per verification level. 
                Again, the size as well as the color map the (mean) number of offers. 
                Although higher levels are scarce, we observe a difference in their product offerings. 
                The lower level vendors sell wide range of drugs while higher level vendors focus on specific categories. 
                Especially the vendors in level 15 stand out with their extreme offer in Steroids.
                Let's look at these vendors in more detail. 
                """)

    st.write("We see that there are just 3 vendors in level 15 and SteroidWarehouse explains the great offer in steroids.")

    # df_combined_level_15 = df_combined[df_combined.verification == 'Verification Level 15']
    df_verification = df_verification[['vendor', 'verification', 'category_level_2', 'nr_offers']]
    st.write(df_verification[df_verification.verification == 'Verification Level 15'].reset_index(drop=True))


    # fig = px.box(df_combined, x='verification',
    #                y="price in $", title='Boxplot', category_orders={'verification':verification_order})
    # st.plotly_chart(fig, use_container_width=True)

    st.subheader("Do vendors with positive feedback have more transactions?")
    st.write("Finally, we also want to find out if the consumers can be convinced to buy products from vendors that have earned positive feedback.")

    df_vendors.verification.fillna('No verification level', inplace=True)

    # df_vendors['feedback_positive'] = df_vendors['feedback_positive'].apply(lambda x: x.split('%')[0])
    # df_vendors['feedback_positive'] = df_vendors.feedback_positive.apply(pd.to_numeric)
    fig = px.scatter(df_vendors, x='feedback_positive',
                   y="transactions_month", title='Boxplot', color='verification')
    st.plotly_chart(fig, use_container_width=True)

    st.write(np.corrcoef(df_vendors['feedback_positive'], df_vendors['transactions_month']))
    st.write(df_vendors)