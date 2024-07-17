import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title("Customize your Smoothie :cup_with_straw:")
st.write("""Choose The Fruits you want in your custom Smoothie!""")

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

pd_df = my_dataframe.to_pandas()

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothies will be :', name_on_order)

ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            fruityvice_response.raise_for_status()  # Check if the request was successful
            fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch data for {fruit_chosen}: {e}")
            print(f"Error: {e}")
        
    my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                         values ('{ingredients_string}', '{name_on_order}')"""

    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Failed to submit order: {e}")
            print(f"Error: {e}")
