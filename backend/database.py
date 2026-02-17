import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# get the connection
def get_connection():
    return mysql.connector.connect(
        host= os.getenv("DB_HOST"),
        user= os.getenv("DB_USER"),
        password= os.getenv("DB_PASSWORD"),
        database= os.getenv("DB_NAME")
    )

def init_db():
    # initializing tables and database
    temp_conn= mysql.connector.connect(
        host= os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password= os.getenv("DB_PASSWORD")
    )

    cursor= temp_conn.cursor()

    # create the db if it does not exist
    db_name= os.getenv("DB_NAME")
    cursor.execute(f"create database if not exists {db_name}")
    cursor.close()
    temp_conn.close()

    # connect to specific db to create tables, if not exists
    conn= get_connection()
    cursor= conn.cursor()

    # creating tables
    # create table brands like deluxe, berger etc
    cursor.execute(
        """
        create table if not exists brand(
            brand_id int auto_increment primary key,
            brand_name varchar(100) not null unique
        )
        """
    )

    # create table category like enamel, putty etc
    cursor.execute(
        """
        create table if not exists category(
            category_id int auto_increment primary key,
            category_name varchar(50) not null
        )
        """
    )

    # create table products like royalEmulsion, silk glamour etc..
    cursor.execute(
        """
        create table if not exists products(
            product_id int auto_increment primary key,
            brand_id int not null,
            category_id int not null,

            series_name varchar(250) not null,
            finish_type varchar(100) default 'Standard',
            quality_grade varchar(100) default 'Standard',

            foreign key(brand_id) references brand(brand_id),
            foreign key(category_id) references category(category_id),

            unique key unique_product(brand_id, series_name, quality_grade, finish_type)
        )
        """
    )

    # create table for inventory-> to account for the number of items in each product
    cursor.execute(
        """
        create table if not exists inventory(
        sku_id int auto_increment primary key,
        product_id int not null,
        
        base_color varchar(150) not null,

        pack_size_label varchar(50),
        pack_size_vol decimal(20,3),

        quantity int default 0,

        price_cp decimal(20,3),
        price_sell_sp decimal(20,3),
        min_stock_alert int default 3,

        unique(product_id, base_color, pack_size_label),

        foreign key (product_id) references products(product_id)
        )
        """
    ) 

    categories= ['Enamel', 'Emulsion', 'Putty', 'Primer']
    for cat in categories:
        try:
            cursor.execute('insert into category (category_name) values (%s)', (cat,))
        except mysql.connector.errors.IntegrityError:
            print("integrity error while entering category_name in category")
            
    
    brands= ['Deluxe Paints', 'Luxor Piants', 'Berger Paints', 'Asian Paints']
    for brand in brands:
        try:
            cursor.execute('insert into brand (brand_name) values (%s)', (brand,))
        except mysql.connector.errors.IntegrityErrors:
            print("integrity error while entering brand name in brand")     
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

