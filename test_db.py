from database import users_collection

data = {
    "name": "Test User",
    "role": "developer"
}

users_collection.insert_one(data)

print("Data inserted successfully")
