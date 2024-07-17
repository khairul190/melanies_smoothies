# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title("Pending Smoothie Order :cup_with_straw:")
st.write("""Orders that need to filled!"""
    
)

cnx= st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED")==0).collect()

if my_dataframe:
    editable_df = st.data_editor(my_dataframe)
    submitted = st.button('Submit')
    
    if submitted:
        og_dataset = session.table("smoothies.public.orders") 
        edited_dataset = session.create_dataframe(editable_df)
        try:
            og_dataset.merge(edited_dataset
                             , (og_dataset['order_uid'] == edited_dataset['order_uid'])
                             , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                            )
            st.success("Someone Clicked the button.", icon="👍")
        except:
            st.write("Something went Wrong.")

else:
    st.success("There are no pending orders right now.", icon="👍")

# name_on_order = st.text_input('Name on Smoothie:')
# st.write('The name on your Smoothies will be :', name_on_order)

# ingredients_list = st.multiselect(
#     'Choose up to 5 Ingridients:'
#     , my_dataframe
# )

# if ingredients_list:
#     ingredients_string = ''
    
#     for fruit_chosen in ingredients_list:
#         ingredients_string += fruit_chosen + ' '

#     my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
#             values ('""" + ingredients_string + """','"""+name_on_order+"""')"""

#     # st.write(my_insert_stmt)
#     # st.stop

#     time_to_insert = st.button('Submit Order')
    
#     if time_to_insert:
#         session.sql(my_insert_stmt).collect()
#         st.success('Your Smoothie is ordered, '+name_on_order+'!', icon="✅")

    
# else:
#     st.write('No Fruits Selected')
