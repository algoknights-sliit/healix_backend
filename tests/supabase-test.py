from app.db.supabase import supabase

def test_connection():
    response = supabase.table("patients").select("*").limit(1).execute()
    print("Connected successfully!")
    print(response)

if __name__ == "__main__":
    test_connection()
