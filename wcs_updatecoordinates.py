#%%
#packages
import pwd
import time
import tqdm
import requests
from pandas import read_sql
from sqlalchemy import create_engine

# create variable with base url of the API
base_url = 'https://nominatim.openstreetmap.org/search'

# define function to call API and check status code of the response for a given address 
def fetch(address):
    # define query parameters
    params = {
        'q': address,
        'format': 'json'
        # ,'countrycode': 'fr' # Limit results to a sepcific country if needed
    }

    # Check if request has succeeded or not and return accordingly
    res = requests.get(url=base_url, params=params)
    if res.status_code == 200:
        return res
    else:
        return None

# define function to add columns and update coordinates
def update_coordinates(engine, tablename):
     
    # Set connection string and targeted table name
    # engine = create_engine(f'mysql+pymysql://root:{pwd.db_password}@localhost/dataengineer')
    # tablename = 'address'

    # Connect to db using 'with' statement
    with engine.connect() as cnn:
        
        # Check if columns latitude and longitude exist or not in targeted table
        checkcolumns = f"""
                    SELECT 
                        COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA='dataengineer' 
                        AND TABLE_NAME='{tablename}' 
                        AND COLUMN_NAME IN ('longitude', 'latitude');
                    """
        # Execute above sql query and store results in a variable
        check = cnn.execute(checkcolumns).fetchall()
        
        # Add columns if not exist
        if check[0][0] == 0:
            addcolumns = f"""
                    ALTER TABLE {tablename} 
                        ADD COLUMN latitude DECIMAL(8,6) NULL DEFAULT NULL
                        , ADD COLUMN longitude DECIMAL(9,6) NULL DEFAULT NULL;
                    """
            cnn.execute(addcolumns)
            print('Added longitude and latitude columns.')
        else:
            print('The longitude and latitude columns already exist.')

        # Create variable with list of address_id and concatenation of fields 'address' + 'postal code' from targeted table
        # NB : More successful responses when not using 'city' field in API queries
        q_addresses = f"""
                    SELECT 
                        address_id, CONCAT(address,', ', postal_code) AS 'full_address' 
                    FROM {tablename}
                        WHERE latitude IS NULL OR longitude IS NULL;
                    """ 
        addresses = cnn.execute(q_addresses).fetchall()

        print(f'starting update for {len(addresses)} row(s).')
        
        # Get latitude and longitude for each address in addresses using fetch function
        # tqdm displays progress bar and stats of for loop
        for address in tqdm.tqdm(addresses):
            res = fetch(address[1]).json()

            if len(res) > 0:
            # Update table accordingly if API's response is not empty

                address_id = address[0]
                latitude = res[0]['lat']
                longitude = res[0]['lon']

                updaterow = f"""
                UPDATE {tablename} SET latitude = {latitude}, longitude = {longitude} WHERE address_id = {address_id}
                """
                cnn.execute(updaterow)
    
            # respect nominatim's requirements : https://operations.osmfoundation.org/policies/nominatim/
            time.sleep(1)
        
        # get list of rows that could not be updated and print number and proportion
        missing_addresses = cnn.execute(q_addresses).fetchall()
        print(f'{len(missing_addresses)} missing coordinate(s) out of {len(addresses)} : {len(missing_addresses)/len(addresses)*100} % of the dataset.\n')

        # 86 missing coordinates out of 562 : 15.302491103202847 % of the dataset.

#%%
if __name__ == '__main__':
   
    # Set connection string and targeted table name
    engine = create_engine(f'mysql+pymysql://root:{pwd.db_password}@localhost/dataengineer')
    tablename = 'address'

    # call function
    update_coordinates(engine, tablename)
    
    # Bernardo's additional query, customer with highest number of rentals:
    with engine.connect() as cnn:
        query = """ 
            SELECT
                c.first_name
                , c.last_name
                , COUNT(rental_id) AS "num_rentals"
                , a.address
                , a.city
                , a.postal_code
                , a.latitude
                , a.longitude
            FROM customer c
                LEFT JOIN address a ON c.address_id = a.address_id
                LEFT JOIN rental r ON c.customer_id = r.customer_id
                GROUP BY c.first_name, c.last_name, a.address, a.city, a.postal_code, a.latitude, a.longitude
                ORDER BY COUNT(rental_id) DESC
                LIMIT 1 
                ;
            """
        
        print('Result of the query for customer with highest number of rentals :')
        display(read_sql(query, cnn))

#  +-------------+-----------+---------------+--------------------+------------------+-------------+-----------+-----------+
#  | first_name  | last_name |  num_rentals  |      address       |       city       | postal_code | latitude  | longitude |
#  +-------------+-----------+---------------+--------------------+------------------+-------------+-----------+-----------+
#  |   ELEANOR   |    HUNT   |      46       | 17 IMP DES JARDINS |     VALLEIRY     |     74520   | 46.106851 |  5.966339 | 
#  +-------------+-----------+---------------+--------------------+------------------+-------------+-----------+-----------+


# %%
