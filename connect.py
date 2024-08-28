import psycopg2


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host='localhost', 
            database='business_owners_db', 
            user='postgres', 
            password='postgres'
            )
        print("Successfully connected to database!")
        return conn
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    return None
get_db_connection()


def create_tables():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            
            # Create the tables if it doesn't exist SQL COMMANDS                       
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_registration_requests (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE
                );
            """)
            cur.execute("""ALTER TABLE user_registration_requests ADD COLUMN IF NOT EXISTS name VARCHAR(250);""")           
            cur.execute("""ALTER TABLE user_registration_requests ADD COLUMN IF NOT EXISTS phone VARCHAR(250);""")           
                        
            
            cur.execute("""         
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    is_approved BOOLEAN DEFAULT FALSE,
                    profile_image TEXT  -- Adding profile_image column directly

            );
            """)
            cur.execute("""ALTER TABLE users ADD COLUMN IF NOT EXISTS suspended BOOLEAN DEFAULT FALSE;""")
            cur.execute("""ALTER TABLE users ADD COLUMN IF NOT EXISTS activation_token TEXT;""")
            cur.execute("""ALTER TABLE users ADD COLUMN IF NOT EXISTS is_activated BOOLEAN DEFAULT FALSE;""")
            cur.execute("""
                        ALTER TABLE users ADD COLUMN IF NOT EXISTS registration_request_id INTEGER REFERENCES user_registration_requests(id) ON DELETE CASCADE;
                    """)
                                    
            cur.execute("""
                ALTER TABLE users
                DROP CONSTRAINT IF EXISTS fk_users_registration_request;
            """)
            cur.execute("""
                ALTER TABLE users
                ADD CONSTRAINT fk_users_registration_request
                FOREIGN KEY (registration_request_id) REFERENCES user_registration_requests(id) ON DELETE CASCADE;
            """) 

            
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS business_registration_requests (
                    id SERIAL PRIMARY KEY,
                    business_name VARCHAR(100) NOT NULL,
                    shop_no VARCHAR(100) NOT NULL,
                    phone_number VARCHAR(20),
                    description TEXT NOT NULL,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    category VARCHAR(50) NOT NULL,
                    block_num VARCHAR(50)
                );
            """)
            cur.execute("""ALTER TABLE business_registration_requests ADD COLUMN IF NOT EXISTS email VARCHAR(100);""")

           
            cur.execute("""
                CREATE TABLE IF NOT EXISTS businesses (
                    id SERIAL PRIMARY KEY,
                    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    business_name VARCHAR(100) NOT NULL,
                    shop_no VARCHAR(100) NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    description TEXT NOT NULL,
                    is_subscribed BOOLEAN DEFAULT FALSE,
                    media_type VARCHAR(10) CHECK (media_type IN ('image', 'video')),
                    media_url TEXT,
                    category VARCHAR(50) NOT NULL,
                    block_num VARCHAR(50)
                );
                """)
            cur.execute("""ALTER TABLE businesses ADD COLUMN IF NOT EXISTS email VARCHAR(100);""")
            # Add the category column to the businesses table
            cur.execute("""ALTER TABLE businesses ADD COLUMN IF NOT EXISTS category VARCHAR(100);""")

            # Populate the category column in the businesses table with data from business_registration_requests
            cur.execute("""
                UPDATE businesses b
                SET category = r.category
                FROM business_registration_requests r
                WHERE b.id = r.id;
            """)




            cur.execute("""
                CREATE TABLE IF NOT EXISTS images_videos (
                    id SERIAL PRIMARY KEY,
                    business_id INTEGER REFERENCES businesses(id),
                    media_type VARCHAR(10) CHECK (media_type IN ('image', 'video')),
                    media_url TEXT NOT NULL
                );
                """)


            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    category_name VARCHAR(255) UNIQUE NOT NULL
                );
                """)


            cur.execute("""
                CREATE TABLE IF NOT EXISTS business_categories (
                    id SERIAL PRIMARY KEY,
                    business_id INTEGER REFERENCES businesses(id),
                    category_id INTEGER REFERENCES categories(id)
                );
                """)           
            # cur.execute("""ALTER TABLE business_categories ADD CONSTRAINT unique_business_category UNIQUE (business_id, category_id);""")
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
            );
            """)
            cur.execute("""ALTER TABLE admin ADD COLUMN IF NOT EXISTS profile_pic VARCHAR(255);""")

            
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subscription_plans (
                    id SERIAL PRIMARY KEY,
                    plan_name VARCHAR(50) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL, -- Amount in Naira
                    duration INTEGER NOT NULL, -- Duration in months
                    UNIQUE (plan_name, duration) -- Multi-column unique constraint
                );
                """)   
             
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id SERIAL PRIMARY KEY,
                    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
                    subscription_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) CHECK (status IN ('pending', 'confirmed')),
                    plan_id INTEGER REFERENCES subscription_plans(id)
                    );
                """)    
            cur.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    subscription_id INTEGER REFERENCES subscriptions(id) ON DELETE CASCADE,
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    amount DECIMAL(10, 2) NOT NULL,
                    payment_status VARCHAR(20) CHECK (payment_status IN ('pending', 'completed')),
                    payment_method VARCHAR(50)
                );
                """)
            
            cur.execute("""INSERT INTO subscription_plans (plan_name, amount, duration) VALUES 
                        ('Monthly', 10000, 1), 
                        ('Yearly', 85000, 12)
                        ON CONFLICT (plan_name, duration) DO NOTHING;""")    
            
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS claim_requests (
                        id SERIAL PRIMARY KEY,
                        business_id INTEGER REFERENCES businesses(id),
                        user_id INTEGER REFERENCES users(id),
                        phone_number VARCHAR(255),
                        email VARCHAR(255),
                        category VARCHAR(255),
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        reviewed BOOLEAN DEFAULT FALSE
                    );                        
                    """)

            
            print("Database tables created successfully")
            conn.commit()

        except psycopg2.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cur.close()
            conn.close()
    else:
        print("Could not open connection to the database")

# Call the function to initialize the database
create_tables()


"""#SQL COMMAND TO DELETE A USER FROM TABLE and also to DELETE A TABLE THAT IS REFERENCE TO OTHERS TABLESBELOW:
DELETE FROM tablename WHERE id = 5;

DROP TABLE IF EXISTS subscription_plans CASCADE;

"""







