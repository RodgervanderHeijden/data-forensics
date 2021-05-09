import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry
import altair as alt
from PIL import Image

# BASE SETUP
st.set_page_config(page_title='Group 17: Data Forensics Dashboard', page_icon=None, layout='wide', initial_sidebar_state='expanded')
st.title('Shining a Light on the Dark Web')


# LOAD THE DATA
@st.cache(allow_output_mutation=True)
def get_all_data():
    drugs = pd.read_csv(r'Product_dataset_new.csv')
    drugs.drop(drugs.columns[0], axis=1, inplace=True)
    # The price in $s is captured as a string, containing both decimal points and commas. Here we clean that to a float
    drugs['price'] = [round(float(x)) if len(x) <= 6 else float(x[:-3].replace(",", "")) for x in drugs['price in $']]
    # to do: add country of origin to the vendor dataset. Can be extracted from drugs dataset.
    # vendor can have multiple shipping from locations --> unable to trace exact country of origin
    vendors = pd.read_csv(r'Vendor_dataset_new.csv')
    vendors.drop(vendors.columns[0], axis=1, inplace=True)
    # rename misspelled column
    vendors.rename(columns={'verifcation': 'verification'}, inplace=True)
    return drugs, vendors


df_drugs, df_vendors = get_all_data()


# Given the countries the user inputs in the sidebar, select the relevant data.
@st.cache(allow_output_mutation=True)
def return_specified_data(countries):
    drugs, vendors = get_all_data()
    df_country_offers = drugs.loc[drugs['shipping_from'].isin(countries)]
    unique_vendors = df_country_offers['vendor'].unique().tolist()
    df_unique_vendors = vendors.loc[vendors['vendor'].isin(unique_vendors)]
    return df_country_offers, df_unique_vendors


# Create function to filter on countries
def country_multiselect():
    global st_country_select
    shipping_from_countries = list(df_drugs.shipping_from.unique())
    shipping_from_countries_copy = ['All countries'] + shipping_from_countries
    st_country_select = st.multiselect('Select what country/countries you want to see the data of.',
                                       options=shipping_from_countries_copy, default=['All countries'])
    # load data for all countries when requested
    if 'All countries' in st_country_select:
        st_country_select = shipping_from_countries
    return st_country_select


# SIDEBAR
with st.sidebar:
    st.header("A dashboard for Data Forensics")

    chapter = st.radio("Navigate to:", ("0. Preface",
                                        "1. Data Description",
                                        "2. Product Insights",
                                        "3. Vendor Insights",
                                        "4. Advanced Insights",))

# CHAPTER 0
if chapter == "0. Preface":
    col_left, col_right = st.beta_columns((3, 1))
    with col_left, col_right:
        col_left.subheader("A dashboard highlighting insights into dark web drug selling")
        col_left.write("""
        In the context of the course Data Forensics of their master's degree Data Science & Entrepreneurship, two 
        students - Thaibinh Luu and Rodger van der Heijden - were tasked to develop insights into criminal behaviour on 
        the web. Drawn by the interesting nature of the assignment, they shared an extreme motivation to not only finish
        this assignment, but to make something truly special of it. 

        This project is heavily focused on counterfeit/falsified medicine, drugs and NPS.
        We saw the most potential in this ANITA scenario and believe it has the most information available on the internet. 
        Furthermore, as these illicit goods may negatively impact public health, it is of great essence to monitor and analyse the flow of these products.
        As a lot of illegal trafficking is facilitated by marketplaces on the dark web, we were motivated to analyse the supply and demand on this specific level of the internet. 
        
        The ultimate goal of this project is to gain valuable insights in one of the largest dark web marketplaces for drugs: ToRReZ.
        By thoroughly analysing this market, we hope to get a sense of the popular types of drugs, the drug flow, supply, demand and so on. 
        Better understanding the market may help in identifying key players and keeping track of illegal drug flows so law 
        enforcement agencies can proactively take action. 

        Data was collected by crawling and scraping the dark web marketplace ToRReZ. To do so, and to be able to extract
        exactly the desired data, we wrote our own crawler and scraper. Data collection occurred on the 5th of 
        March. Be aware that any offers, vendors and pricing therefore may already be outdated.

        Insights derived from the retrieved data were diligently analysed, with the key takeaways shared in the 
        dashboard in front of you. The side panel on the left contains a table of contents, which allows for navigation.
        The first pages contain a more introductory approach to the data with insights of descriptive nature. The last
        one specifically goes into some hypotheses we defined in advance and were able to answer over the past weeks. 
        During this research several (related) insights where also found, which we highlight there as well. 
        
        Where possible (and where logical) we have included the option for interactivity, which presents itself in the 
        ability to hover of data, zoom, pan and select subsets. We strongly encourage the reader to use the sandbox to 
        their own liking; we merely provide the tools that allow you to discover additional insights. 

        In case any question remains, some confusion arises or additional information is desired, please do contact us. 
        Wishing you the best reading experience possible, 

        Thaibinh Luu and Rodger van der Heijden
        """)
        col_right.subheader("The authors")
        col_right.write("""
            Group 17, consisting of Thaibinh Luu and Rodger van der Heijden, has chosen to tackle online drug selling. 
            Both students are close to finishing the master's degree Data Science & Entrepreneurship at the Jheronimus
            Academy of Data Science (JADS). 
        """)

# CHAPTER 1
if chapter == "1. Data Description":
    st.header("Architecture overview")
    st.write("""To obtain data of the ToRReZ market we had to visit the dark web. To achieve this, the following 
                environment is implemented. First, a virtual machine is downloaded to create a safe place to 
                experiment in. Then, to add another layer of protection, we connected to a VPN within the virtual machine. 
                Finally, we downloaded the Tor browser which allowed us to visit the dark web 
                and ToRReZ. The image below clearly indicates the architecture used. 
             """)
    col_left, col_right = st.beta_columns((3, 1))
    with col_left, col_right:
        # show image architecture
        image = Image.open(r'Architecture.png')
        col_left.image(image)

    st.write("___")
    st.header("Data collection")
    st.write("""
             By accessing the market, we were exposed to a lot of interesting data. We found that the marketplace 
             offers all kinds of illicit goods. Besides drugs and chemicals, also software & malware, fraud and many more 
             products are offered. Our category of interest, however, is 'Drugs and Chemicals'. 
             This section contains all drug and chemical related products offered on the market. 
             At the time of scraping, this section had 14.013 product offerings. Besides all these products, 
             the vendor pages also contain a lot of valuable information.
             
             To capture all this relevant information required for analysis, we built our own crawler and scraper 
             from scratch. Scraping is done using the BeautifulSoup package in Python. This package allowed us to 
             pick the relevant information from the HTML we were interested in. For the product pages we scraped the 
             vendor name, category levels, product name, price and shipping locations. The same approach is used for 
             the vendor pages. However, this time we scraped the vendor name, rank, verification, number of 
             transactions, feedback, and disputes. The crawler that we made allowed us to go through pages to scrape 
             all the information. For the product pages, the crawler goes through all of the 721 pages. For the 
             vendors, it goes through all vendor pages that have at least one offer in the category 
             ‘Drugs and Chemicals’. More specific information can be found in the code, where comments are also 
             provided for better understanding the workflow. 
             """)

    st.write("___")
    st.header("Data description")
    st.write("""
    Crawling and scraping eventually led to a dataset that can be used for analysis. 
    We ended up with two different datasets, one that contains the product information and one that contains 
    the vendor information. We wanted specific insights on the ToRReZ market and hence only this market is scraped. 
    The type of data scraped is textual data. Images were not scraped as they were not useful for the analysis we intended to do. 
    Below you can find the data description; the variable name, the data type and the explanation.
    """)

    # load the tables containing the data descriptions
    data_description_product = pd.read_excel(r'Data description.xlsx', sheet_name='Blad1')
    data_description_vendor = pd.read_excel(r'Data description.xlsx', sheet_name='Blad2')

    st.subheader("Product data")
    st.table(data_description_product)
    st.subheader("Vendor data")
    st.table(data_description_vendor)

    st.write("___")
    st.header("Raw data")
    st.write("""
            Have a look at the raw data that we scraped. Two datasets are provided, the product dataset and the vendor dataset.
            """)
    st.subheader("Product data")
    st.write(""" At the moment of scraping 14.013 offers were posted on ToRReZ in the Drugs and Chemicals-category. We 
    scraped all of those; below you can find an overview of the raw data. If desired, you can (de)select columns, you can pick 
    how many observations are shown and/or you can order any column by clicking on the column name.""")
    st_ms = st.multiselect("Select which columns you want to display.", df_drugs.columns.tolist(),
                           default=df_drugs.columns.tolist())
    st_slider = st.slider("Number of observations to display.", 0, len(df_drugs), 10)
    st.dataframe(df_drugs[st_ms].head(st_slider))

    st.subheader("Vendor data")
    st.write(""" At the moment of scraping 668 vendors had active offers on ToRReZ in the Drugs and Chemicals-category. We 
    scraped their profiles; below you can find an overview of the data. Again, if desired, you can (de)select columns, you 
    can pick how many observations are shown and/or you can order any column by clicking on the column name.""")
    st_ms_vendor = st.multiselect("Select which columns you want to display.", df_vendors.columns.tolist(),
                                  default=df_vendors.columns.tolist())
    st_slider_vendor = st.slider("Number of observations to display.", 0, len(df_vendors), 10)
    st.dataframe(df_vendors[st_ms_vendor].head(st_slider_vendor))

# CHAPTER 2
if chapter == "2. Product Insights":
    st.header("Product insights")

    country_multiselect()
    df_drugs, df_vendors = return_specified_data(st_country_select)

    st.write(
        "Here we describe the data about the individual offers and showcase some interesting aspects we have found. "
        "In essence the figures on this page cover all countries, but the option to select specific countries within "
        "the data set exists. The tool below provides all options in both a dropdown menu and a search box; the figures"
        " will then automatically update with the relevant data."
    )
    st.write("___")
    st.header("Shipping locations")

    st.markdown(
        "Vendors have possibility for each individual offer to state what country the drugs are shipped from, and what "
        "shipping destinations exists. In our dataset we see *4* primary countries from which the drugs are sold: "
        "the _United Kingdom_, the _United States, Germany_ and the _Netherlands_. Despite there being 33 countries in "
        "total, these four amount to 82.0% of all offers. "
    )

    st.write(
        "On the right we see the 'receiving' countries outlined: the locations which the drugs are possible to get "
        "shipped to. Here we see that nearly half of all drugs are sold worldwide, indicating that smuggling drugs "
        "across (potentially) multiple borders is not a large hurdle for quite some vendors. The United States hold "
        "second place, with the United Kingdom in fourth. Both countries have a sizable portion of drugs that are "
        "destined for the own market (US is the origin in 21.1% and the (only) destination in 17.2%, UK is the origin "
        "in 27% and the (only) destination in 11.4%). Notably, the shares for Australia do not change much (5.61% on "
        "the supply side and 5.42% on the demand side). "
    )

    st.write(
        "Though we do not have enough finegrained data to fully investigate this (for instance, we only see offers but "
        "not which offers get sold), we assume that the border patrol does take a part in it. The US and Australia have"
        " a large proportion for their own market, the UK has a significant (but lesser) percentage, and the highly "
        "frequently origin countries of Germany and the Netherlands play a very small part. Due to the Schengen "
        "agreement, or so we openly hypothesize, shipping drugs within the European Union is relatively convenient and "
        "risk free, so vendors can offer coverage for the entirety of Europe (as we see on the third place). "
    )

    st.write(
        "Another interesting finding is that we only see European and North American countries - along with Australia -"
        " but no Asian countries. However, when we look at the origin of the drugs, both China and India are present. "
        "Combined they represent 675 offers, yet nearly all of those are intended for the international market. China, "
        "India or Asia combined all have fewer than 100 offers that ship to these locations. "
    )

    col_left, col_right = st.beta_columns(2)
    with col_left, col_right:
        df_origin = pd.DataFrame(df_drugs.shipping_from.value_counts()).reset_index()
        df_origin.columns = ['country', 'shipping_from']
        # We select only the countries which occur over 100 times in the "shipping from" category
        df_origin.loc[df_origin[
                          'shipping_from'] < 100, 'country'] = 'Other countries'  # Represent only large countries
        # Then we create a pie chart (using Plotly) with these countries.
        fig_country_origin = px.pie(df_origin, values='shipping_from', names='country',
                                    title='Shipping origins (having at least 100 offers):', hole=.4)
        col_left.plotly_chart(fig_country_origin, use_container_width=True)

        df_destination = pd.DataFrame(df_drugs.shipping_to.value_counts())
        df_destination.reset_index(inplace=True)
        df_destination.columns = ['country', 'shipping_to']
        # We select only the regions which have over 100 occurances in the destination
        df_destination.loc[df_destination[
                               'shipping_to'] < 100, 'country'] = 'Other countries'  # Represent only large countries
        # And, just like above, we plot that in a pie chart.
        fig_country_destination = px.pie(df_destination, values='shipping_to', names='country',
                                         title='Shipping destinations (having at least 100 offers):', hole=.4)

        col_right.plotly_chart(fig_country_destination, use_container_width=True)

    st.write("___")
    st.header("Drug pricing")
    st.write(
        "Not all drugs are the same: the workings of LSD differ significantly from the workings of cocaine or weed. We "
        "wondered whether we could find some information in the prices that the offers note. The following quartet of "
        "graphs showcases this. The first pair of graphs contains the visualization that covers *all data* with the "
        "country selected above, while the second row covers only categories with *at least 100 offers*. The graphs are"
        " as interactive as possible, with information on hover, but also the ability to (de)select categories from the"
        " legend by clicking. As the legends have been ordered alphabetically, the colors and ordering of every level "
        "two category is the same on each pair. The ordering of the level 3 categories - the categories on the y-axis -"
        " are based on the highest average value of offers within that category. "
    )

    st.write(
        "What we can deduce from the first pair of plots is that the costs vary wildly. We see some average prices that"
        " exceed $3000, while the tail end has 9 categories with an average offer below $200. The left graph shows that"
        " some outliers are present, such as an offer for close to $400k in the Speed category and two around the $200k"
        " range for Speed and Heroin. Despite these very high peaks (which unfortunately also partially obfuscate the "
        "results for the other categories) the categories of Speed and Heroin are not even the top 5 most expensive "
        "ones. We also noticed that the subcategory does have a significant effect on the (average) price of the "
        "listing, so we pose that this is quite important for vendors."
    )

    st.write(
        "Though clicking on categories in the legend allows for (de)selection in the graph, we wanted to look "
        "into the categories a bit more, and decided to only include categories with at least 100 offers for the next "
        "two graphs. "
    )

    category_prices, category_avg_prices = st.beta_columns(2)
    with category_prices, category_avg_prices:
        # These lists will be used later: they are set as the order in which the categories will appear.
        lvl_2_cats = ['Accessories', 'Benzos', 'Cannabis & Hash', 'Dissociatives', 'Ecstasy', 'Opiates',
                      'Prescriptions Drugs', 'Psychedelics', 'Steroids', 'Stimulants', 'Weight Loss', 'Tobacco']

        order_list = ['Dissociatives', 'GBL', 'Ketamine', 'GHB', 'RC', 'Powder', 'Benzos', 'Pills', 'Heroin',
                      'Oxycodone', 'Opiates', 'Codeine', 'Buprenorphine', 'Speed', 'Meth', 'Cocaine', 'Stimulants',
                      'Vyvanse', 'Adderal', '4-FA', 'Crack', 'Ecstasy', 'MDMA', '2C-B', 'LSD', 'Mushrooms', 'DMT',
                      'Mescaline', 'Psychedelics', 'Vaping', 'Cannabis & Hash', 'Synthetic', 'Buds & Flowers', 'Hash',
                      'Shake', 'Topical', 'Edibles', 'Seeds', 'Prerolls', 'Prescriptions Drugs', 'Steroids', 'Tobacco',
                      'Weight Loss', 'Accessories']
        frequent_values = df_drugs['highest_category'].unique()
        order_list_country_specific = [category for category in order_list if category in frequent_values]
        plot_order = {'category_level_3': order_list_country_specific,
                      'highest_category': order_list_country_specific,
                      'category_level_2': lvl_2_cats}
        df_plot_data = df_drugs[df_drugs['highest_category'].isin(order_list)]

        # We drop data with missing fields in these essential columns
        df_plot_data.dropna(subset=['highest_category', 'price', 'category_level_2'], how='any', inplace=True, axis=0)

        category_prices.subheader("Drug prices for all categories")
        # Create a strip plot using Plotly and the dataframe + order we have just defined.
        fig_category_prices = px.strip(df_plot_data,
                                       x="price",
                                       y="highest_category",
                                       color="category_level_2",
                                       category_orders=plot_order,
                                       labels = {"highest_category": "category",
                                        "price": "price in $"}
                                       )
        fig_category_prices.update_layout(height=800)
        category_prices.plotly_chart(fig_category_prices, use_container_width=True)

        category_avg_prices.subheader("Average prices for each category")
        # We group by the highest category and category level 2 to calculate the mean price.
        df_data_ordered_by_price = df_plot_data.groupby(
            ['highest_category', 'category_level_2']).mean().reset_index().sort_values(
            by='price', ascending=False)

        # Those mean prices are then plotted with a strip plot, with the earlier defined order.
        fig_category_avg_prices = px.strip(df_data_ordered_by_price,
                                           x="price",
                                           y="highest_category",
                                           color="category_level_2",
                                           category_orders=plot_order,
                                       labels = {"highest_category": "category",
                                        "price": "price in $"}
                                           )
        fig_category_avg_prices.update_layout(height=800)
        category_avg_prices.plotly_chart(fig_category_avg_prices, use_container_width=True)

    category_prices, category_avg_prices = st.beta_columns(2)
    with category_prices, category_avg_prices:
        freq = df_plot_data['highest_category'].value_counts()
        # Select frequent values, so categories with a lot of offers. The value itself is in the index.
        frequent_values = freq[freq >= 100].index
        # Return only rows with at least 100 offers.
        df_temp = df_plot_data[df_plot_data['highest_category'].isin(frequent_values)]

        # A new order list comprehension: with the selected countries it may be possible that several categories do not
        # meet the 100 offers threshold. To prevent lack of data, we do not include those categories as labels.
        order_list_country_specific = [category for category in order_list if category in frequent_values]
        plot_order_country_specific = {'category_level_3': order_list_country_specific,
                                       'highest_category': order_list_country_specific,
                                       'category_level_2': lvl_2_cats}
        # As before, we plot the new subset of data on a stripplot.
        fig_category_prices_threshold = px.strip(df_temp,
                                                 x="price",
                                                 y="highest_category",
                                                 color="category_level_2",
                                                 category_orders=plot_order_country_specific,
                                       labels = {"highest_category": "category",
                                        "price": "price in $"}
                                                 )
        category_prices.subheader("Drug prices for categories with at least 100 offers")
        # We define a certain height: lower than that and some labels on the y axis get hidden
        fig_category_prices_threshold.update_layout(height=800)
        category_prices.plotly_chart(fig_category_prices_threshold, use_container_width=True)

        # Same as before, group by highest category and category level two and calculate the mean scores.
        df_temp_avg = df_temp.groupby(
            ['highest_category', 'category_level_2']).mean().reset_index().sort_values(
            by='price', ascending=True)
        fig_category_avg_prices_threshold = px.strip(df_temp_avg,
                                                     x="price",
                                                     y="highest_category",
                                                     color="category_level_2",
                                                     category_orders=plot_order_country_specific,
                                       labels = {"highest_category": "category",
                                        "price": "price in $"}
                                                     )
        category_avg_prices.subheader("Average prices for each category with at least 100 offers")
        fig_category_avg_prices_threshold.update_layout(height=800)
        category_avg_prices.plotly_chart(fig_category_avg_prices_threshold, use_container_width=True)

    st.write(
        "When looking at the data for the selected country or countries and then taking only the (sub)categories with "
        "at least 100 offers, we see that some categories fall off. Accessories, Weight Loss and Tobacco all have fewer"
        " than 100 offers worldwide. As for the subcategories, several drop off. For instance, the only dissociative "
        "that is left is _ketamine_. Of the 5 subcategories with an average price above $3000, only two remain: _RC_ "
        "(_research chemical_). Curiously, this is both in the _benzos_ and _opiates_ main categories. Though a more "
        "in-depth research should be conducted to draw hard conclusions, with over 100 offers we can see clear "
        "differences, which we thought was quite interesting. "
    )

# CHAPTER 3
if chapter == "3. Vendor Insights":
    st.header("Vendor insights")
    st.write('Here we describe the data about the individual vendors and showcase some interesting aspects we have found. '
             'We will first take a look at the number vendors over time. '
             'Subsequently, we will delve into certain characteristics of vendors such as the rank and '
             'verification level. We will especially take a closer look at the top vendors on ToRReZ. '
             'Finally, we will go into the distributions of the transactions and offers per vendor to get a sense of the spread of the data.')

    # count rank
    ranks = pd.DataFrame(df_vendors['rank'].value_counts())
    ranks.reset_index(inplace=True)
    ranks.columns = ['rank', 'count']

    # verification rank
    verification = pd.DataFrame(df_vendors['verification'].value_counts())
    verification.reset_index(inplace=True)
    verification.columns = ['verification', 'count']

    st.subheader("Total number of vendors over time")
    st.write("ToRReZ launched in February 2020 and has become very popular. After a modest start we observe a "
             "rapid increase in the number of vendors with at least one listing in the category 'Drugs & Chemicals'. "
             "In the beginning it took 7 months to reach 100 vendors. But in the 7 months that followed, the number of "
             "vendors increased significantly to 668. We conclude ToRReZ is becoming more and more popular and we expect the number "
             "of vendors to keep rising.")

    df_vendors['date'] = pd.to_datetime(df_vendors['since'])
    df_vendor_month = df_vendors.groupby(df_vendors['date'].dt.strftime('%B %Y'))['vendor'].count().reset_index()
    df_vendor_month['date'] = pd.to_datetime(df_vendor_month["date"], format='%B %Y')
    df_vendor_month = df_vendor_month.sort_values('date')
    df_vendor_month['cumulative_sum_vendor'] = df_vendor_month['vendor'].cumsum()
    df_vendor_month.date = df_vendor_month.date.dt.strftime('%B %Y')

    # cumulative number of vendors over time
    fig11 = px.area(df_vendor_month, x="date", y="cumulative_sum_vendor", labels={
        "cumulative_sum_vendor": "number of vendors",
        "date": ""}, )
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
             "Rank 0 represents 0-9 items sold, Rank 1 represents 10-99 items sold, Rank 3 represents 100-199 items sold, "
             "and so on. A 'TOP' seller is a vendor that has over 1000 sales. Most vendors have either rank 0, 1 or 2 (83.7%). This indicates "
             "that most vendors on ToRReZ have relatively low sales so far. However, looking at the previous chart we see "
             "that a lot of vendors recently joined the market and these new vendors obviously may not have that many sales just yet. "
             "Higher ranks are rare, however, there are still 17 TOP vendors.")

    rank_order = ['Rank 0', 'Rank 1', 'Rank 2', 'Rank 3', 'Rank 4', 'Rank 5', 'Rank 6',
                  'Rank 7', 'Rank 8', 'Rank 9', 'Rank 10', 'TOP', ]
    col_vendor_1, col_vendor_2 = st.beta_columns(2)
    with col_vendor_1, col_vendor_2:
        # pie chart ranks

        fig12 = go.Figure(
            data=[go.Pie(labels=rank_order, values=ranks['count'], hole=.4, direction='clockwise', sort=False)])
        col_vendor_1.plotly_chart(fig12, use_container_width=True)

        # bar chart ranks
        fig21 = px.bar(ranks, x='rank', y='count', category_orders={'rank': rank_order}, labels={
            "rank": "", 'count': 'frequency'})
        col_vendor_2.plotly_chart(fig21, use_container_width=True)

    st.write("Let's take a more detailed look at these TOP vendors, the big players, to unveil certain characteristics. "
             "We observe that the TOP vendors joined ToRReZ between February 2020 and November 2020. "
             "This means that the number of months that TOP vendors have been operating ranges between 5 and 14 months."
             )
    df_vendors['verification'].fillna('Verification Level 0', inplace=True)
    df_vendors_TOP = df_vendors[df_vendors['rank']=='TOP']
    now = pd.to_datetime('Apr 1, 2021')
    df_vendors_TOP['num_months'] = (now.year - df_vendors_TOP.date.dt.year) * 12 + (now.month - df_vendors_TOP.date.dt.month)
    df_vendors_TOP['transactions_month'] = df_vendors_TOP['transactions'] / df_vendors_TOP['num_months']
    st.write(df_vendors_TOP)

    st.write(" ")
    st.write("Let's visualize this data to reveal more insights. First we will start by comparing these TOP vendors "
             "with respect to the number of sales per month to unveil the dominant key vendors of ToRReZ.")

    fig = px.bar(df_vendors_TOP, x='vendor',
                 y="transactions_month", title='Average sales per month per vendor',
                     hover_data=["num_months"],
                 labels={"transactions_month": "sales per month",
                         'num_months':'number of months'}
                 )
    fig.update_xaxes(categoryorder='total descending')
    st.plotly_chart(fig, use_container_width=True)

    st.write("The vendor with the most sales per month is Tripwirewiki2. This vendor has on average a whopping 354 "
             "sales per month which is significantly higher than the other vendors. Tripwirewiki2 has been on the market "
             "for 7 months and has rapidly managed to become one of the key players on the market. The vendor espn "
             "is in second place with 1420 sales while only being 5 months on the market. These numbers once again show that "
             "there is a lot of traffic on ToRReZ. It has become one of the popular dark web markets that facilitates "
             "drug trafficking.")
    st.write(" ")
    st.write("To get more insights in the TOP vendors, we will now investigate some more details and statistics of these vendors. "
             "We will look at the verification levels, the number of offers and the transactions.")

    col_vendor_1, col_vendor_2, col_vendor_3 = st.beta_columns(3)
    with col_vendor_1, col_vendor_2, col_vendor_3:

        df_vendors_TOP_2 = pd.DataFrame(df_vendors_TOP['verification'].value_counts())
        df_vendors_TOP_2.reset_index(inplace=True)
        df_vendors_TOP_2.columns = ['verification', 'count']

        verification_order = ["Level 0", "Level 1", "Level 2", "Level 3", "Level 4",
                              "Level 5", "Level 6", "Level 7", "Level 8",
                              'Level 9', 'Level 10', 'Level 11', 'Level 12',
                              'Level 13', 'Level 14', 'Level 15', 'Level 16',
                              'Level 19']

        fig12 = go.Figure(
            data=[go.Pie(labels=verification_order, values=df_vendors_TOP_2['count'], hole=.4, direction='clockwise', sort=False)])
        fig12.update_layout(
            title={
                'text': "Verification levels",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
        col_vendor_1.plotly_chart(fig12, use_container_width=True)


        fig = px.box(df_vendors_TOP, y="nr_offers", points="all",
                             labels={"nr_offers": "number of offers"})
        fig.update_layout(
            title={
                'text': "Number of offers",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
        col_vendor_2.plotly_chart(fig, use_container_width=True)

        fig = px.scatter(df_vendors_TOP, x="nr_offers", y="transactions",
                             labels={"nr_offers": "number of offers"})
        fig.update_layout(
            title={
                'text': "Number of offers vs transactions",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
        col_vendor_3.plotly_chart(fig, use_container_width=True)


    st.write("For the TOP vendors the majority either has verification level 0, 1 or 2 (52.9%). "
             "Interesting here is that no TOP vendor has a verification level above 10. "
             "The number of offers differs greatly and ranges from 1 to 158 offers per vendor. We observe that 75% of all "
             "TOP vendors offer between 1 and 56 products and just a small number of vendors have a very wide assortment. "
             "Finally, we do not necessarily see a relationship between the number of offers and the number of transactions. "
             "The vendor PilotElon, for instance, has significantly more transactions while having only 10 offers.")

    st.subheader("Verification level")
    st.write("Every vendor on ToRReZ that has a positive history from other markets can get a verification badge. "
             "The level indicates the number of other markets the vendor is active on (with good reputation). Level 1 means that the vendor is "
             "active on one other market, level 2 indicates activity on two other markets and so on. Most of the vendors "
             "have verification level 0 (38.6 %). Verification levels 1, 2 and 3 account for 30.98%. "
             "Only a very small number of vendors is active on 10 or more other markets (37 vendors; 5.5%).")

    verification_order = ["Level 0", "Level 1", "Level 2", "Level 3", "Level 4",
                          "Level 5", "Level 6", "Level 7", "Level 8",
                          'Level 9', 'Level 10', 'Level 11', 'Level 12',
                          'Level 13', 'Level 14', 'Level 15', 'Level 16',
                          'Level 19']

    col_vendor_1, col_vendor_2 = st.beta_columns(2)
    with col_vendor_1, col_vendor_2:
        verification['verification'] = verification['verification'].str.replace('Verification ', "").str.replace(
            'No verification level', 'Level 0')

        # pie chart verification
        fig13 = go.Figure(
            data=[go.Pie(labels=verification_order, values=verification['count'], hole=.4, direction='clockwise')])
        col_vendor_1.plotly_chart(fig13, use_container_width=True)

        # bar chart verification
        fig13 = px.bar(verification, x='verification', y='count', category_orders={'verification': verification_order},
                       labels={"verification": "", 'count': 'frequency'})
        col_vendor_2.plotly_chart(fig13, use_container_width=True)

    st.subheader("Transactions")
    st.write(
        'The number of sales a vendor has made so far. We observe a skewed distribution when taking all vendors into account. '
        'You can adjust the verification levels to see specific distributions.')

    # verification levels filter
    df_vendors['verification'].fillna("Level 0", inplace=True)
    all_verifications = df_vendors['verification'].unique().tolist()
    all_verifications.append('All levels')
    st_ms_ver = st.multiselect("Select which verification level(s) you want to display.", all_verifications,
                               default=['All levels'])
    if 'All levels' in st_ms_ver:
        st_ms_ver = df_vendors['verification'].unique().tolist()

    col_vendor_3, col_vendor_4 = st.beta_columns([2.5, 1])
    with col_vendor_3, col_vendor_4:

        fig12 = px.histogram(df_vendors[df_vendors['verification'].isin(st_ms_ver)],
                             x="transactions", title='Distribution of Transactions', nbins=50,
                             labels={"transactions": "number of transactions", 'count': 'frequency'})
        col_vendor_3.plotly_chart(fig12, use_container_width=True)

        fig12 = px.box(df_vendors[df_vendors['verification'].isin(st_ms_ver)],
                       y="transactions", title='Boxplot',
                       labels={'transactions': 'number of transactions'})
        col_vendor_4.plotly_chart(fig12, use_container_width=True)

    st.subheader("Number of offers")
    st.write(
        'The number of offers a vendor has in the category "Drugs & Chemicals". We again observe a skewed distribution when taking all vendors into account. '
        'You can adjust the ranks to see specific distributions.')
    # rank filter
    all_ranks = df_vendors['rank'].unique().tolist()
    all_ranks.append('All ranks')
    st_ms_rank = st.multiselect("Select which rank(s) you want to display.", all_ranks,
                                default=['All ranks'])
    if 'All ranks' in st_ms_rank:
        st_ms_rank = df_vendors['rank'].unique().tolist()

    col_vendor_3, col_vendor_4 = st.beta_columns([2.5, 1])
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


# CHAPTER 4
elif chapter == '4. Advanced Insights':
    st.header("Advanced insights")
    st.write("""
        In the previous sections we have provided some interesting descriptive insights regarding the product offerings 
        (page 2) and vendors (page 3) on ToRReZ. In this section we will go a step further and analyse the market in 
        more detail. We have defined two main areas of interest: the supply side (_"Can we deduce relationships between 
        drug offerings, drug prices, top vendors, countries of origin and shipping destinations?"_) and the 
        vendor side (_"To what extent does trust play a role on ToRReZ in drug offerings and drug sales?"_)
        """)

    st.write("___")
    st.header("1. Can we deduce relationships between drug offerings, drug prices, top vendors, countries of origin and"
              " shipping destinations?")
    st.write(
        "We wondered whether the vendors on the dark web are well-versed in the entire criminal circuit or might just "
        "have a connection with one kind of drugs and are experts in that. Additionally, it would be possible that "
        "several drugs are often sold in conjunction. For instance, cocaine and psychedelics have vastly different "
        "effects, and one could imagine that expertise in one category would not necessarily translate into knowledge "
        "of the other.")

    st.write("ToRReZ works with a hierarchy that can be selected by the vendor. However, this is optional, and vendors "
             "can decide not to further specify their offers. Our dataset is specifically selected within the first "
             "level, 'Drugs & Chemicals'. The chart beneath showcases the spread of the second level categories. We "
             "have selected the 50 vendors with the highest amount of active offers at the time of the scraping. This "
             "results in a cut-off of 63 offers. The categories are sorted on the quantity of the offers (descending), "
             "similarly, the vendors are sorted as well (descending). The size of the markers refers to the amount of "
             "offers for that specific category and vendor combination; specific numbers are visible in the tooltip "
             "when hovering. The color is based on the same metric, with more blue indicating more offers. As not all "
             "offers had a specified category assigned, we assigned those offers an 'Not provided' label, plotted them "
             "on the bottom and colored them gray.")

    st.write(
        "The resulting figure, as shown below, is very information dense. We will cover some interesting insights, "
        "but have left some others to be discovered by the reader. ")
    st.subheader("Main categories")

    # Quite a chained operation, so explanation:
    # Groupby vendor, then show count. Sort values by product (the column here doesn't matter too much, as long as these no missings)
    # Show the top 50 highest # of offers and take the index (the account names) to convert that to a list for further selection
    top_vendors = df_drugs.groupby("vendor").count().sort_values('product', ascending=False).head(50).index.tolist()
    top_vendors_offers = df_drugs[df_drugs['vendor'].isin(top_vendors)]
    top_vendors_offers.fillna("Not provided", inplace=True)

    # A new groupby such that the index is (vendor, category) and the resulting value is frequency ("count").
    df_plot_data = top_vendors_offers.groupby(['vendor', 'category_level_2']).count().reset_index()[
        ['vendor', 'category_level_2', 'product']]
    df_not_provided_2 = df_plot_data[df_plot_data['category_level_2'] == 'Not provided']
    df_rest_2 = df_plot_data[~df_plot_data.isin(df_not_provided_2)].dropna(axis=0)

    # Used to color code in order
    level_2_order = ['Cannabis & Hash', 'Dissociatives', 'Ecstasy', 'Opiates', 'Stimulants',
                     'Psychedelics', 'Benzos', 'Prescriptions Drugs', 'Steroids', 'Weight Loss',
                     'Accessories', 'Tobacco', 'Not provided']

    # Altair - the library used for the next 5 plots - uses a quite descriptive API
    # On first look it's very puzzling, with every single aspect explicitly defined
    # More barebones graphs are very possible, but as we had limited room to work with
    # we decided to incorporate multiple insights into each graph.
    vendor_top = alt.Chart(df_rest_2).mark_circle().encode(
        alt.Y('category_level_2:O', sort=level_2_order, title='Categories'),
        alt.X('vendor:N', sort=top_vendors, title='Vendors'),
        alt.Size('product:Q', legend=None),
        alt.Color('product:Q', legend=None),  # sort='descending'),
        opacity=alt.value(1),
        tooltip=[alt.Tooltip('vendor', title='Vendor'),
                 alt.Tooltip('category_level_2', title='Category'),
                 alt.Tooltip('product', title='Number of offers')
                 ]
    )

    # We create a new chart for the missing data ("Not provided"), which we later stack.
    vendor_top_missing = alt.Chart(
        df_not_provided_2
    ).mark_circle(
        color='gray'
    ).encode(
        alt.Y('category_level_2:N', sort=level_2_order),
        alt.X('vendor',
              sort=top_vendors),
        alt.Size('product:Q', legend=None),
        tooltip=[alt.Tooltip('vendor', title='Vendor'),
                 alt.Tooltip('category_level_2', title='Category'),
                 alt.Tooltip('product', title='Number of offers')
                 ]
    )

    # Here we stack the two charts and configure the axes
    st.altair_chart(
        (vendor_top + vendor_top_missing).configure_axis(
            labelFontSize=12,
            titleFontSize=15,
        ).configure_axisX(
            labelAngle=-30,
        ).configure_title(
            fontSize=24
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
        #### &ensp;&ensp;&ensp;&ensp; 3. _Benzos, Prescriptions Drugs, Steroids, Weight Loss, Accessories_""")

    st.markdown("""After noting the peculiarities of the weed sales, the remaining categories can very distinctively be separated "
             "into two separate groups: drugs sold by almost all vendors and drugs sold by a select few vendors. Drugs in the"
             "second group have vendors which also basically sell all drugs in that group, while the drugs in the last group
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
             "order of the graph above. Notably, one exception is in place: _benzos_ (red). ToRReZ uses the subcategory "
             "_pills_ for _Ecstacy_ as well, and thus these are plotted together. The color coding is correct, for a "
             "more convenient interpretation the other _benzos_ category is plotted next to the _pills_. ")
    st.write("")

    # A new groupby such that the index is (vendor, category) and the resulting value is frequency ("count").
    df_plot_data = top_vendors_offers.groupby(['vendor', 'category_level_3', 'category_level_2']).count().reset_index()[
        ['vendor', 'category_level_2', 'category_level_3', 'product']]
    df_not_provided = df_plot_data[df_plot_data['category_level_3'] == 'Not provided']
    df_rest = df_plot_data[~df_plot_data.isin(df_not_provided)].dropna(axis=0)

    st.subheader("Subcategories")

    level_3_order = [
        'Buds & Flowers', 'Edibles', 'Hash', 'Prerolls', 'Seeds', 'Shake', 'Synthetic', 'Topical', 'Vaping',
        # Cannabis & Hash
        'GBL', 'Ketamine',  # Dissociatives
        'MDMA', 'Pills',  # Ecstacy
        'Powder',  # Benzos
        'Codeine', 'Heroin', 'Oxycodone', 'RC',  # Opiates
        '4-FA', 'Adderal', 'Crack', 'Cocaine', 'Meth', 'Speed', 'TMA',  # Stimulants
        '2C-B', '5-MeO-DMT', 'DMT', 'LSD', 'Mescaline', 'Mushrooms',  # Psychedelics
        'Not provided']

    vendors_top = alt.Chart(df_rest).mark_circle().encode(
        alt.Y('category_level_3:O', title='Categories', sort=level_3_order),
        alt.X('vendor:N', sort=top_vendors, title='Vendors'),
        alt.Size('product:Q', legend=None),
        alt.Color('category_level_2:N', legend=None, sort=level_2_order,
                  scale=alt.Scale(scheme='category20'),
                  ),
        opacity=alt.value(1),
        tooltip=[alt.Tooltip('vendor', title='Vendor'),
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
        tooltip=[alt.Tooltip('vendor', title='Vendor'),
                 alt.Tooltip('category_level_2', title='Category lvl 2'),
                 alt.Tooltip('category_level_3', title='Category lvl 3'),
                 alt.Tooltip('product', title='Number of offers'),
                 ]
    )

    st.altair_chart(
        (vendors_top + vendor_top_missing).configure_axis(
            labelFontSize=12,
            titleFontSize=15,
        ).configure_axisX(
            labelAngle=-30,
        ).configure_title(
            fontSize=24
        ).properties(
            height=700, title="What subcategories of drugs are sold in conjunction?"
        ), use_container_width=True
    )

    st.markdown("""
        ### 5. _Buds & Flowers_ explains popularity _Cannabis & Hash_
        
        With the noted presence of _Cannabis & Hash_, we see that _Buds & Flowers_ are mainly responsible for this 
        effect. Most subcategories however are barely sold, not in quantity in offers nor in quantity of vendors. A 
        possible explanation would be that there are a lot of strains for cannabis, and logically the type of flower
        matters to prospective buyers. For other types of drugs, say cocaine, only purity matters, and individual 
        vendors do not have dozens of types of cocaine. 
        
        ### 6. _Ketamine_, _MDMA_ and _Cocaine_ are popular
        
        On the other hand, _Ketamine_, _MDMA_ and _Cocaine_ are sold by a lot of different vendors (and often the same 
        vendors), but a single vendor has at most 28 offers of one category. We can hypothesize about the underlying 
        reasons, partly already explained in the previous finding, but it's peculiar nonetheless. 
    """)

    st.markdown("""
        ### 7. Several subcategories are only sold by one or a few vendors
        
        For instance, the subcategories as _Seeds_, _Synthetic_, _GBL_, _Powder_, _Codeine_, _4-FA_, _TMA_, _DMT_ and 
        _Mescaline_ are only offered by at most two vendors out of the top 50. In a similar vain, vendors that offer 
        drugs in the _Cannabis & Hash_ (blue), _Ecstacy_ (orange) or _Stimulants_ (green) categories generally offer 
        multiple subcategories if not all. On the flipside, vendors that sell drugs within the _Benzos_ (red) or 
        _Opiates_ (beige) categories only sell one specific subcategory. Due to our limited expertise we cannot 
        formulate a hypothesis that could potentially explain this.
        
        ### 8. _Prescription drugs_, _Steroids_ and _Weight Loss_ drugs do not have subcategories
 
        With a total of 1158 offers within these categories, one could propose that further specification is in place. 
        ToRReZ however does not allow any subcategories within these categories. Scrolling through the offers here show
        a wide variety of drugs in each one, though we're unaware whether a proper (categorical) distinction could 
        possibly be created. For your discovery, we have included a view of the offers within these categories.
    """)

    st.write(
        df_drugs[df_drugs['category_level_2'].isin(['Weight Loss', 'Prescriptions Drugs', 'Steroids'])].reset_index(
            drop=True)[['vendor', 'category_level_2', 'product', 'price in $', 'shipping_from', 'shipping_to']])

    st.markdown("""        
        Furthermore, the accessories category does not have subcategories as well. However, with only 10 offers this 
        would not benefit anyone. Additionally, several listings should not have been placed in the _Drugs & Chemicals_
        main category of ToRReZ at all, such as a "Facebook hack", tasers or a Netflix gift card. Also, for just $3.99 
        you can buy the knowledge on how to get free Amazon gift card!          
    """)

    st.write(
        df_drugs[df_drugs['category_level_2'].isin(['Accessories'])].reset_index(drop=True)[
            ['vendor', 'category_level_2', 'category_level_3', 'product', 'price in $', 'shipping_from',
             'shipping_to']])

    st.write("___")
    st.subheader("Vendors")
    st.write(
        "These insights are quite interesting, but now let's shift the focus to the vendors themselves. The x-axis "
        "contains the categories of drugs, and the y-axis shows the top 50 vendors. They are - in both cases - ordered "
        "by the country of origin (shipping from), and then by number of offers. The left figure shows the number of"
        " offers as the size, while the right figure shows the mean product price as size.  "
    )

    st.markdown("""
        ### 9. Vendors with a lot of offers are cheaper on average 
        
        When looking at the vendors that offer a wide variety of drugs within a category, for instance RoyalMailer with
        310 offers within the Cannabis & Hash category, we see that their mean product price is quite low. Or look at 
        vendors LucySkyDiamonds (a reference to the Beatles hit song about LSD) and Hofmanncrew: despite being the most
        active vendors on ToRReZ, their average price is a lot less pronounced. 
        
        ### 10. Drug offer prices are more dependent on the vendor than the actual drugs
        
        When looking per category, we see that the larger dots do correlate with the category. Of course, we also saw
        this effect on the _Product Insights_ page. Stimulants and Dissociatives for example contain sizable markers.
        However, quite to our surprise, the differences in offer price between sellers within a category is larger than 
        the differences in offer price between categories. 
        
        ### 11. Vendors that specialize in certain categories are cheaper on average than vendors that sell everything.
        
        The specialists, such as RoyalMailer, kandykones, California420Service, StrainPirate or PSteroids, are notable 
        within their drug category and primarily sell (a lot of) one specific group of drugs. However, they do not 
        appear in the right graph, which shows the average listing price. This seems counter-intuitive to us, as one
        could pose that expertise could translate into more specified listings and also more expensive. A pedigree of 
        quality, if you will. However, since the inverse seems true, we suggest that it's maybe a question of scale: if
        you can sell large quantities of drugs, then the production and sale of drugs per unit decrease, and 
        undercutting your competitors can in turn ensure that your sales increase even more. This theory is given some 
        credence by the two vendors that sell exclusively from Australia (and as we have seen earlier, exclusively to 
        Australia): though _inc_ has more offers overall, _auspride_ is (significantly) more expensive.
        
        ### 12. The top vendors have several shipping locations
        
        Vendors like drkend, akgeneric, TheBodyShop and NarcoticsWorldwide post their offers with several locations 
        where they ship from. For drkend it's mainly China with a bit of Canada, for akgeneric it's primarily India
        with 28 offers from the United States, TheBodyShop also ships from India primarily but offers other drugs from
        the Netherlands, and NarcoticsWorldwide it's between Germany and Australia. With the opportunity to offer 
        multiple types of drugs getting shipped from multiple countries, we are confident that these vendors are part 
        of a large organisation. 
    """)
    # Not required but used for a bit of padding
    st.write("")

    # A new groupby such that the index is (vendor, category) and the resulting value is frequency ("count").
    plot_df = top_vendors_offers.groupby(['vendor', 'category_level_2', 'shipping_from']).agg(
        ['mean', 'count'])
    plot_df.columns = ['Mean product price', 'Count']
    plot_df['Mean product price'].astype(int)
    plot_df.reset_index(inplace=True)

    df_not_provided = plot_df[plot_df['shipping_from'] == 'Not provided']
    df_rest = plot_df[~plot_df.isin(df_not_provided)].dropna(axis=0)

    for seller in df_rest['vendor']:
        country_of_origin = df_vendors[df_vendors['vendor'] == seller]

    top_vendors_country_order = [
        'RoyalMailer', 'PitStopUK', 'Everylittlehalps', 'LucySkyDiamonds', 'DrSeuss', 'kandykones',
        'jnenfrancis', 'cerberusuk', 'exclusivepharma', 'maurelius', 'MedicineMan420', 'BritishStandard',
        'Pygmalion',  # UK

        'drkend', 'MicroDroper',  # China

        'California420Service', 'StrainPirate', 'RXChemist', 'topmoneymaker', 'CanadianSmoker12', 'TheRxPharma',
        'vessel', 'Worldtime',  # US

        'inc', 'auspride',  # Aus

        'akgeneric', 'TheBodyShop', 'bestgroup',  # India

        # Netherlands
        'NextLevel', 'SteroidWarehouse', 'donalddrugs', 'RoleXx17', 'DutchGlory', 'Hofmanncrew', 'tomandjerry',
        'ScotchAndCoca', 'StreetLegend', 'maxverstappen', 'EUROSHOPPER', 'DoctorXXL', 'Coffeshop', 'DutchPharmacy',
        'NarcoticsWorldwide', 'MisterX', 'DrugAmazon', 'loveloyalty', 'FGWL', 'Mont-Blanc', 'Island_Paradise',

        # Lithuania
        'PSteroids']

    # We plot the top vendors - ordered by the country of _shipping_from_ primarily and _number of offers_ secondly -
    # with the size being also the number of offers.
    vendors_top_number_offers = alt.Chart(df_rest).mark_circle().encode(
        alt.X('category_level_2:O', title='Categories', sort=level_2_order),
        alt.Y('vendor:N', sort=top_vendors_country_order, title='Vendors'),
        alt.Size('Count:Q', legend=None),
        alt.Color('shipping_from',
                  scale=alt.Scale(scheme='category20'),
                  ),
        opacity=alt.value(1),
        tooltip=[alt.Tooltip('vendor', title='Vendor'),
                 alt.Tooltip('category_level_2', title='Category lvl 2'),
                 alt.Tooltip('Count', title='Number of offers'),
                 alt.Tooltip('Mean product price', title='Average price of listing'),
                 alt.Tooltip('shipping_from', title='Country of origin')
                 ]
    )

    # We separately plot the data where the category is Not Provided, and then later add it to the same graph
    vendors_top_number_offers_missing = alt.Chart(
        df_not_provided
    ).mark_circle(
        color='gray'
    ).encode(
        alt.X('category_level_2:N', sort=level_2_order
              ),
        alt.Y('vendor',
              sort=top_vendors_country_order),
        alt.Size('Count:Q', legend=None),
        tooltip=[alt.Tooltip('vendor', title='Vendor'),
                 alt.Tooltip('category_level_2', title='Category lvl 2'),
                 alt.Tooltip('Count', title='Number of offers'),
                 alt.Tooltip('Mean product price', title='Average price of listing'),
                 alt.Tooltip('shipping_from', title='Country of origin')
                 ]
    )

    col_left, col_right = st.beta_columns(2)
    with col_left, col_right:
        col_left.altair_chart(
            (vendors_top_number_offers + vendors_top_number_offers_missing).configure_axis(
                labelFontSize=12,
                titleFontSize=20,
            ).configure_axisX(
                labelAngle=-30,
            ).configure_title(
                fontSize=32
            ).properties(
                height=1000, width=800, title="Number of offers"
            ),
        )

        # Similar to above, we plot the top 50 vendors, ordered by country and number of offers. Key difference: size now
        # is the mean of the product price (in that category). Everything else is identical.
        vendors_top_mean_price = alt.Chart(df_rest).mark_circle().encode(
            alt.X('category_level_2:O', title='Categories', sort=level_2_order),
            alt.Y('vendor:N', sort=top_vendors_country_order, title='Vendors'),
            alt.Size('Mean product price:Q', legend=None),
            alt.Color('shipping_from',
                      scale=alt.Scale(scheme='category20'),
                      ),
            opacity=alt.value(1),
            tooltip=[alt.Tooltip('vendor', title='Vendor'),
                     alt.Tooltip('category_level_2', title='Category lvl 2'),
                     alt.Tooltip('Count', title='Number of offers'),
                     alt.Tooltip('Mean product price', title='Average price of listing'),
                     alt.Tooltip('shipping_from', title='Country of origin')
                     ]
        )

        vendors_top_mean_price_missing = alt.Chart(
            df_not_provided
        ).mark_circle(
            color='gray'
        ).encode(
            alt.X('category_level_2:N', sort=level_2_order
                  ),
            alt.Y('vendor',
                  sort=top_vendors_country_order),
            alt.Size('Mean product price:Q', legend=None),
            tooltip=[alt.Tooltip('vendor', title='Vendor'),
                     alt.Tooltip('category_level_2', title='Category lvl 2'),
                     alt.Tooltip('Count', title='Number of offers'),
                     alt.Tooltip('Mean product price', title='Average price of listing'),
                     alt.Tooltip('shipping_from', title='Country of origin')
                     ]
        )

        col_right.altair_chart(
            (vendors_top_mean_price + vendors_top_mean_price_missing).configure_axis(
                labelFontSize=12,
                titleFontSize=20,
            ).configure_axisX(
                labelAngle=-30,
                labelFontSize=12,
            ).configure_title(
                fontSize=32
            ).properties(
                height=1000, width=800, title="Mean product price"
            ),
        )

    st.write("___")
    st.subheader("Drug availability")

    st.write(
        "In the previous graphs we have already seen that the offer of different categories of drugs differs between "
        "countries. But, to what extend? These following graphs delve deeper into that aspect. The first graph shows "
        "the categories on the y-axis, with the countries of origin on the x-axis. The color coding is done by country "
        "of origin, with the opacity (intensity of the color) being the number of vendors active in that category. So, "
        "the United Kingdom and the United States have a priority on Cannabis & Hash and Stimulants but score high in "
        "a lot of categories while German drug dealers most frequently target the Stimulant market."
    )

    # For the next graph, we want to set out the country of origin along with the category, but have the intensity (opacity)
    # be the number of vendors within tht (country:drug category) combination. This requires some ugly data engineering
    # First: fill all missing data, then group by shipping_from, cat_lvl2 and the vendor and count the offers.
    # Next, we reset the index again to group by shipping_from and cat_lvl_2 (omitting the vendor).
    # Now we can count again, which will give us the number of vendors (as opposed to number of offers earlier)
    df_country_drugs = df_drugs.fillna('Not provided').groupby(by=['shipping_from', 'category_level_2', 'vendor']).count().reset_index().groupby(by=['shipping_from', 'category_level_2']).count()

    strip = alt.Chart(df_country_drugs.reset_index()).mark_square(size=625).encode(
        x=alt.X('shipping_from', title='Shipping from'),
        y=alt.Y('category_level_2', title='Category (level 2)'),
        color=alt.Color('shipping_from:N', legend=None),
        opacity=alt.Opacity('vendor:Q', scale=alt.Scale(type='linear', clamp=True,
                                                        domain=[25, 70]),
                            legend=None),
        tooltip=[alt.Tooltip('vendor', title='Number of vendors'),
                 alt.Tooltip('category_level_2', title='Category lvl 2'),
                 alt.Tooltip('shipping_from', title='Country of origin')
                 ]
    )

    st.altair_chart(strip.configure_axisX(
        labelAngle=-30,
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=20,
    ).configure_title(
        fontSize=32
    ).properties(
        title='Does country x sell drug y?',
        height=550
    ), use_container_width=True)

    st.markdown("""### 13. The most popular countries sell (nearly) everything""")

    st.write(
        "Basically every category of drugs gets shipped from Australia, Canada, China, France, Germany, Netherlands, "
        "United Kingdom and United States, which are the most popular countries as seen before. No surprises there. "
        "However, the converse is quite interesting: countries as Colombia, Latvia, Lithuania, Mexico and Peru sell "
        "just one drug category, all of which match common sense/stereotypes: Colombia and Peru sell coke (Stimulants),"
        " Latvia and Lithuania sell steroids and Mexico sells psychedelics.")

    st.markdown("""
    ### 14. Tobacco is only being offered from Germany and Spain
    
    Though tobacco in itself is legal, the counterfeit variant of course is not legal. This 'new' category - it did not
    show up in the top 50 vendors - is only being shipped from Germany and Spain, which we thought was quite 
    interesting, as the smoking populace is quite heavily on the decline. Given the relative unpopularity of the 
    category (a total of 15 offers), we wonder why ToRReZ has tobacco as separate category.
    """)

    st.write("___")

    st.write("The next plots look at the price per category, country and destination. First of all, we select the "
             "subset of offers that are less than $10.000, as the few offers above distort the remaining data too "
             "much. The opportunity for a second subset exists at the hands of the reader: using the dropdown menu "
             "one can (de)select countries to their choosing. For these points, we've selected the three countries of "
             "Australia, the Netherlands and the United States, but one can imagine that there are countless yet "
             "undescribed insights hidden in the data.")

    st.write("Then, we convey the price in two factors: the y axis position and the size of the circle. The "
             "country of origin in all three figures is color-coded. ")

    shipping_from_countries = list(df_drugs.shipping_from.unique())
    shipping_from_countries_copy = ['All countries'] + shipping_from_countries
    select_country = st.multiselect('Select what country/countries you want to see the data of.',
                                    options=shipping_from_countries_copy,
                                    default=['Netherlands', 'Australia', 'United States'])
    if 'All countries' in select_country:
        select_country = shipping_from_countries

    df_under_50 = df_drugs[df_drugs['price'] <= 10000]
    df_country = df_under_50[df_under_50['shipping_from'].isin(select_country)]  # 1000/len(select_country)

    df_category = df_country[~df_country['category_level_2'].isin(['Accessories', 'Weight Loss', 'Tobacco'])]
    stripplot_by_category = alt.Chart(df_category, width=120).mark_point().encode(
        x=alt.X(
            'jitter:Q',
            title=None,
            axis=alt.Axis(values=[0], ticks=True, grid=True, labels=False),
            scale=alt.Scale(),
        ),
        y=alt.Y('price:Q'),  # cat lvl 2: N
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
            # title='shipping_from',
            header=alt.Header(
                labelAngle=-15,
                titleOrient='top',
                labelOrient='bottom',
                labelAlign='center',
                labelPadding=350,
                labelFontSize=20,
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
    ).interactive()
    st.altair_chart(stripplot_by_category, use_container_width=False)

    st.write("Above graph looks at the category by country of origin and by price. With our default selection, we note"
             " that:")

    st.markdown("""
            ### 15. Certain categories are clearly dominated by a specific country.
            
            For instance, benzos and cannabis & hash are very U.S. focused, while dissociatives, steriods and 
            stimulants (between these three) are the Dutch specialty.  
    """)

    stripplot_by_country = alt.Chart(df_country, width=min(1200 / len(select_country), 250)).mark_point().encode(
        x=alt.X(
            'jitter:Q',
            title=None,
            axis=alt.Axis(values=[0], ticks=True, grid=True, labels=False),
            scale=alt.Scale(),
        ),
        y=alt.Y('price:Q'),  # cat lvl 2: N
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
                # labelAngle=-15,
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

    st.write("Above graph looks at the price distribution (sub $10.000) between the selected countries, so between "
             "Australia, the Netherlands and the US by default. Though not interesting enough to deserve its own "
             "insight-header, we do notice that the US has way more offers just under $10.000 than the other two "
             "countries. The real meat of this subject however can be found in the next figure. We see the location of "
             "destination, color coded for country of origin. We see that there are no Australian or American drugs "
             "being sold exclusively to Europe or the Netherlands, and that there are no Australian or Dutch drugs "
             "being sold exclusively to the US or North America. Of course, that makes sense: if you ship to those "
             "countries, it makes sense to just ship worldwide. ")

    st.markdown("""
        ### 16. Australia exclusively ships to Australia
        
        This is peculiar: no Australian offer (below $10.000) ships worldwide. We thought this effect was very strange,
        but could not come up with an explanation for it. 
    """)

    shipping_to_value_counts = df_country['shipping_to'].value_counts()
    countries_with_50_min = shipping_to_value_counts[shipping_to_value_counts > 50].index

    stripplot_by_receiving_country = alt.Chart(df_country[df_country['shipping_to'].isin(countries_with_50_min)],
                                               width=1200 / len(countries_with_50_min)).mark_point().encode(
        x=alt.X(
            'jitter:Q',
            title=None,
            axis=alt.Axis(values=[0], ticks=True, grid=True, labels=False),
            scale=alt.Scale(),
        ),
        y=alt.Y('price:Q'),  # cat lvl 2: N
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
                labelAlign='center',
                labelPadding=350,
                labelFontSize=20,
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
    st.header("2. To what extent does trust play a role on ToRReZ in drug offerings and drug sales?")
    st.write(
        "We assume that trust plays a key role in any transaction. Especially on the dark web where vendors are "
        "anonymous. ToRReZ awards vendors several labels that indicate their trustworthiness: the verification level "
        "and the percentage of positive feedback. The verification level indicates the vendor's activity on other markets. The higher the level, the more "
        "other markets the vendor is also active on. Feedback can be given to vendors by consumers after they have made a purchase. "
        "We were wondering if these labels lead to a difference in consumer behavior and benefit the vendors. "
    )

    st.subheader("Do vendors with a higher verification level have more sales?")
    st.write(
        "Verification level, to a certain extent, indicates the trustworthiness of the vendors. Vendors that have a "
        "positive history from other markets (and can prove that!) can get a higher verification level. So, the higher "
        "the level, the more other markets the vendor is active on (with good reputations). We were interested to find "
        "out if the verification level is actually a factor in the number of sales a vendor has. Some vendors have been"
        " active on ToRReZ for a longer period than others. Therefore, to make a fair comparison we will look at the "
        "number of transactions per month for each vendor."
    )

    df_vendors['date'] = pd.to_datetime(df_vendors['since'])
    now = pd.to_datetime('Apr 1, 2021')
    df_vendors['num_months'] = (now.year - df_vendors.date.dt.year) * 12 + (now.month - df_vendors.date.dt.month)
    df_vendors['transactions_month'] = df_vendors['transactions'] / df_vendors['num_months']

    verification_order = ["Level 0", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7",
                          "Level 8", 'Level 9', 'Level 10', 'Level 11', 'Level 12', 'Level 13', 'Level 14', 'Level 15',
                          'Level 16', 'Level 19']

    df_vendors['verification'] = df_vendors.verification.str.replace('Verification ', "").str.replace(
        "No verification level", "Level 0")
    fig = px.box(df_vendors, x='verification',
                 y="transactions_month", title='Boxplots of the sales per month per verification level'
                 , category_orders={'verification': verification_order},
                 labels={"transactions_month": "sales per month",
                         "verification": "verification level"})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""The boxplots showcase the distributions of the sales per month for the different verification levels.
                    Some distributions, for instance of level 8, are more spread.
                    The medians of the boxplots indicate that the verification level are not necessarily correlated with the sales per month.
                  That is, we do not see an increase in the number of sales per month for a higher verification level.
                  Let's have a look at the average sales per month per verification level to get a clearer idea. """)

    df_vendors_grouped = df_vendors.groupby('verification')['transactions_month'].mean().reset_index()
    fig = px.bar(df_vendors_grouped, x='verification',
                 y="transactions_month", title='Average sales per month per verification level'
                 , category_orders={'verification': verification_order},
                 labels={"transactions_month": "sales per month",
                         "verification": "verification level"}
                 )
    st.plotly_chart(fig, use_container_width=True)

    st.write(
        "The average sales per month does not indicate a positive relation with the verification level. Vendors with "
        "higher levels do not necessarily have more sales per month. It even seems that higher level vendors have less sales per month."
        " This could potentially be explained by different products offerings or products with higher prices on average.")

    st.write("___")
    st.subheader("Do vendors with a higher verification level have different product offerings?")
    st.write("We just saw that the highest level vendors have on average less sales per month. "
             "We wondered to what extent this could be related to different product offerings."
             " So, to what extent do higher level vendors differentiate in their product offerings?")
    st.write("")

    df_drugs.category_level_2.fillna("Not provided", inplace=True)
    nr_offers = pd.DataFrame(df_drugs.groupby(['vendor', 'category_level_2']).vendor.count())
    nr_offers.columns = ['nr_offers']
    nr_offers.reset_index(inplace=True)
    df_verification = nr_offers.merge(df_vendors, on='vendor')
    df_combined_grouped = df_verification.groupby(['verification', 'category_level_2']).sum().reset_index()

    df_temp = df_vendors.groupby(['verification']).vendor.count().reset_index()
    df_temp.rename({'vendor': 'vendor_count'}, axis=1, inplace=True)
    df_combined_grouped_new = df_combined_grouped.merge(df_temp, on='verification')
    df_combined_grouped_new[
        'offer_verification_level'] = df_combined_grouped_new.nr_offers / df_combined_grouped_new.vendor_count
    df_not_provided_2 = df_combined_grouped_new[df_combined_grouped_new['category_level_2'] == 'Not provided']
    df_rest_2 = df_combined_grouped_new[~df_combined_grouped_new.isin(df_not_provided_2)].dropna(axis=0)


    level_2_order = ['Cannabis & Hash', 'Dissociatives', 'Ecstasy', 'Opiates', 'Stimulants',
                     'Psychedelics', 'Benzos', 'Prescriptions Drugs', 'Steroids', 'Weight Loss',
                     'Accessories', 'Tobacco', 'Not provided']

    vendor_top = alt.Chart(df_rest_2).mark_circle().encode(
        alt.Y('category_level_2:O', sort=level_2_order, title='Categories'),
        alt.X('verification:N', sort=verification_order, title='Verification level'),
        alt.Size('offer_verification_level:Q', legend=None),
        alt.Color('offer_verification_level:Q', legend=None),  # sort='descending'),

        opacity=alt.value(1),
        tooltip=[alt.Tooltip('verification', title='Level'),
                 alt.Tooltip('category_level_2', title='Category'),
                 alt.Tooltip('offer_verification_level', title='Number of offers')
                 ]
    )

    vendor_top_missing = alt.Chart(
        df_not_provided_2
    ).mark_circle(
        color='gray'
    ).encode(
        alt.Y('category_level_2:N', sort=level_2_order),
        alt.X('verification:N', sort=verification_order),
        alt.Size('offer_verification_level:Q', legend=None),
        tooltip=[alt.Tooltip('verification', title='Level'),
                 alt.Tooltip('category_level_2', title='Category'),
                 alt.Tooltip('offer_verification_level', title='Number of offers')
                 ]
    )

    st.altair_chart(
        (vendor_top + vendor_top_missing).configure_axis(
            labelFontSize=12,
            titleFontSize=15,
        ).configure_axisX(
            labelAngle=-30,
        ).configure_title(
            fontSize=24
        ).properties(
            height=500, title="Product offerings per verification level"
        ), use_container_width=True
    )

    st.markdown("""
                    From the "Vendor Insights" page we already observed a low number of vendors having a high verification level. 
                    Looking at their product offerings in more detail, we see that they deviate from the lower verified vendors. 
                    To make a fair comparison we computed the mean number of offers per category per verification level. 
                    The mean number of offers is mapped to the size as well as the color.
                    Although higher levels are scarce, we observe a difference in their product offerings. 
                    The lower level vendors sell all kind of drugs while higher level vendors focus on specific categories. 
                    Furthermore, all low level vendors seem to focus on the popular categories (Cannabis & Hash) which is 
                    consistent with our findings in the previous chapter. Higher level vendors have different product offerings.
                    Especially the vendors in level 15 stand out with their extreme offer in Steroids.
                    Looking at this group in more detail we observe that level 15 contains 3 different vendors and that
                    SteroidWarehouse explains the great offer in steroids.
                    """)

    df_verification_2 = df_verification[['vendor', 'verification', 'category_level_2', 'nr_offers']]
    st.write(df_verification_2[df_verification_2.verification == 'Level 15'].reset_index(drop=True))

    st.write("___")
    st.subheader("Do vendors with positive feedback have more transactions?")
    st.write("ToRReZ provides the consumers the possibility to give feedback on their experience with vendors. "
             "The percentage of positive feedback is a great indicator of the trustworthiness of the vendor and its products."
             " We were wondering if these two variables have a clearer relationship. To make a fair conclusion, we only "
             "consider vendors with at least one feedback received.")

    df_vendors.verification.fillna('No verification level', inplace=True)
    df_verification['feedback_positive_percentage'] = df_verification['feedback_positive'].apply(
        lambda x: x.split('%')[0])
    df_verification['feedback_positive_percentage'] = df_verification['feedback_positive_percentage'].astype("float")
    df_verification = df_verification[df_verification['feedback_total'] != 0]

    fig = px.scatter(df_verification, x='feedback_positive_percentage',
                     y="transactions_month", title='Sales per month vs feedback', color='verification',
                     hover_data=["feedback_total"],
                     labels={"transactions_month": "sales per month",
                             "feedback_positive_percentage": "percentage of positive feedback"},
                     category_orders={'verification':verification_order})
    st.plotly_chart(fig, use_container_width=True)

    st.write(
        "The great majority of the data is scattered densely between 80 and 100% positive feedback. It looks like there is some "
        "positive relationship. However, because the of the density this is difficult to ensure. Let's take some more "
        "advanced statistics to determine the relationship. The pearson correlation coefficient is a statistical "
        "measure of the strength of a linear association between two variables. A value greater than 0 indicates "
        "a positive association; if the value of one variables increases, so does the value of the other variable. "
        "The pearson correlation coefficient for the sales per month and the percentage of positive "
        "feedback gives 0.0140. This indicates that there is a positive correlation but the correlation is very low. ")
    st.write(
        "We can conclude that trust is not as important on ToRReZ as we expected it to be. There are no clear "
        "indications that the verification levels and feedback affect the consumers in their behavior. These "
        "indicators of trustworthiness do not significantly benefit the vendors in terms of more sales per month.")

#     st.write('Pearson correlation matrix')
#     st.write(np.corrcoef(df_verification['feedback_positive_percentage'], df_verification['transactions_month']))


