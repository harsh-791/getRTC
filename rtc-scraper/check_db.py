import psycopg2
from psycopg2.extras import RealDictCursor

def check_database():
    # Database connection parameters
    conn_params = {
        "dbname": "rtc_documents",
        "user": "rtc_user",
        "password": "rtc_password",
        "host": "localhost",
        "port": "5432"
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check total number of properties
        print("\n1. Total number of properties:")
        cur.execute("SELECT COUNT(*) as count FROM properties;")
        result = cur.fetchone()
        print(f"Total properties: {result['count']}")
        
        # 2. Check total number of documents
        print("\n2. Total number of documents:")
        cur.execute("SELECT COUNT(*) as count FROM rtc_documents;")
        result = cur.fetchone()
        print(f"Total documents: {result['count']}")
        
        # 3. List all properties with their details
        print("\n3. Property details:")
        cur.execute("""
            SELECT id, survey_number, surnoc, hissa, village, hobli, taluk, district 
            FROM properties;
        """)
        properties = cur.fetchall()
        for prop in properties:
            print("\nProperty ID:", prop['id'])
            print(f"Survey Number: {prop['survey_number']}")
            print(f"Surnoc: {prop['surnoc']}")
            print(f"Hissa: {prop['hissa']}")
            print(f"Village: {prop['village']}")
            print(f"Hobli: {prop['hobli']}")
            print(f"Taluk: {prop['taluk']}")
            print(f"District: {prop['district']}")
            
        # 4. List documents for each property with their periods
        print("\n4. Documents by property:")
        cur.execute("""
            SELECT 
                p.id as property_id,
                p.survey_number,
                p.hissa,
                d.id as document_id,
                d.period_text,
                d.year_text,
                d.created_at
            FROM properties p
            JOIN rtc_documents d ON p.id = d.property_id
            ORDER BY p.id, d.year_text;
        """)
        documents = cur.fetchall()
        current_property = None
        for doc in documents:
            if current_property != doc['property_id']:
                print(f"\nProperty ID: {doc['property_id']}")
                print(f"Survey Number: {doc['survey_number']}")
                print(f"Hissa: {doc['hissa']}")
                print("Documents:")
                current_property = doc['property_id']
            print(f"  - ID: {doc['document_id']}, Year: {doc['year_text']}")
            print(f"    Period: {doc['period_text']}")
            print(f"    Created: {doc['created_at']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database()