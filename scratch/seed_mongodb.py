import os
import random
from datetime import datetime, timedelta
from faker import Faker
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI or "<username>" in MONGODB_URI:
    print("ERROR: Please update MONGODB_URI in your .env file with your actual connection string.")
    print("Example: mongodb+srv://admin:password123@cluster0.mongodb.net/?retryWrites=true&w=majority")
    exit(1)

print("Connecting to MongoDB Atlas...")
client = MongoClient(MONGODB_URI)
db = client["startup_ai"]

fake = Faker()

def generate_olist_data(num_records=50):
    print("Generating Olist E-Commerce Data...")
    
    # Customers
    customers = []
    for _ in range(num_records):
        customers.append({
            "customer_id": fake.uuid4(),
            "customer_zip_code_prefix": fake.zipcode(),
            "customer_city": fake.city(),
            "customer_state": fake.state_abbr()
        })
    if customers: db.customers.insert_many(customers)
    
    # Sellers
    sellers = []
    for _ in range(10):
        sellers.append({
            "seller_id": fake.uuid4(),
            "seller_zip_code_prefix": fake.zipcode(),
            "seller_city": fake.city(),
            "seller_state": fake.state_abbr()
        })
    if sellers: db.sellers.insert_many(sellers)
    
    # Products
    products = []
    categories = ['health_beauty', 'computers_accessories', 'auto', 'bed_bath_table', 'furniture_decor']
    for _ in range(20):
        products.append({
            "product_id": fake.uuid4(),
            "product_category_name": random.choice(categories),
            "product_weight_g": random.randint(100, 5000),
            "product_length_cm": random.randint(10, 100),
            "product_height_cm": random.randint(10, 100),
            "product_width_cm": random.randint(10, 100)
        })
    if products: db.products.insert_many(products)
    
    # Orders & Payments & Reviews
    orders = []
    payments = []
    reviews = []
    order_items = []
    
    statuses = ['delivered', 'shipped', 'canceled', 'invoiced', 'processing']
    for customer in customers:
        order_id = fake.uuid4()
        purchase_date = fake.date_time_between(start_date='-1y', end_date='now')
        
        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_status": random.choices(statuses, weights=[80, 10, 5, 3, 2])[0],
            "order_purchase_timestamp": purchase_date,
            "order_delivered_customer_date": purchase_date + timedelta(days=random.randint(2, 14))
        })
        
        payments.append({
            "order_id": order_id,
            "payment_type": random.choice(['credit_card', 'boleto', 'voucher', 'debit_card']),
            "payment_installments": random.randint(1, 12),
            "payment_value": round(random.uniform(20.0, 1500.0), 2)
        })
        
        reviews.append({
            "review_id": fake.uuid4(),
            "order_id": order_id,
            "review_score": random.randint(1, 5),
            "review_comment_message": fake.sentence() if random.random() > 0.5 else "",
            "review_creation_date": purchase_date + timedelta(days=15)
        })
        
        # Order items
        for _ in range(random.randint(1, 3)):
            order_items.append({
                "order_id": order_id,
                "order_item_id": fake.uuid4(),
                "product_id": random.choice(products)["product_id"],
                "seller_id": random.choice(sellers)["seller_id"],
                "price": round(random.uniform(10.0, 500.0), 2),
                "freight_value": round(random.uniform(5.0, 50.0), 2)
            })
            
    if orders: db.orders.insert_many(orders)
    if payments: db.payments.insert_many(payments)
    if reviews: db.reviews.insert_many(reviews)
    if order_items: db.order_items.insert_many(order_items)

def generate_enterprise_data(num_records=20):
    print("Generating Enterprise Synthetic Data...")
    
    # Employees
    employees = []
    departments = ['Sales', 'Support', 'Engineering', 'Finance', 'HR', 'Operations']
    for _ in range(15):
        employees.append({
            "employee_id": fake.uuid4(),
            "name": fake.name(),
            "email": fake.company_email(),
            "department": random.choice(departments),
            "salary": random.randint(50000, 150000),
            "hire_date": fake.date_time_between(start_date='-3y', end_date='now')
        })
    if employees: db.employees.insert_many(employees)
    
    # Vendors
    vendors = []
    for _ in range(10):
        vendors.append({
            "vendor_id": fake.uuid4(),
            "company_name": fake.company(),
            "contact_email": fake.company_email(),
            "service_provided": fake.bs()
        })
    if vendors: db.vendors.insert_many(vendors)
    
    # Expenses
    expenses = []
    for _ in range(30):
        expenses.append({
            "expense_id": fake.uuid4(),
            "employee_id": random.choice(employees)["employee_id"],
            "amount": round(random.uniform(10.0, 2000.0), 2),
            "category": random.choice(['Travel', 'Software', 'Office Supplies', 'Meals']),
            "date": fake.date_time_between(start_date='-6m', end_date='now'),
            "status": random.choice(['Approved', 'Pending', 'Rejected'])
        })
    if expenses: db.expenses.insert_many(expenses)
    
    # Invoices (B2B)
    invoices = []
    for _ in range(20):
        invoices.append({
            "invoice_id": fake.uuid4(),
            "client_name": fake.company(),
            "amount_due": round(random.uniform(1000.0, 50000.0), 2),
            "issue_date": fake.date_time_between(start_date='-3m', end_date='now'),
            "due_date": fake.date_time_between(start_date='now', end_date='+2m'),
            "status": random.choice(['Paid', 'Unpaid', 'Overdue'])
        })
    if invoices: db.invoices.insert_many(invoices)
    
    # Tasks
    tasks = []
    for _ in range(40):
        tasks.append({
            "task_id": fake.uuid4(),
            "assigned_to": random.choice(employees)["employee_id"],
            "title": fake.catch_phrase(),
            "priority": random.choice(['P0', 'P1', 'P2', 'P3']),
            "status": random.choice(['To Do', 'In Progress', 'Done', 'Blocked']),
            "created_at": fake.date_time_between(start_date='-1m', end_date='now')
        })
    if tasks: db.tasks.insert_many(tasks)

# ==================================================
# DEMO ORGANIZATION + USERS (for Auth/RBAC testing)
# ==================================================

DEMO_ORG_ID = "demo-org-001"

def generate_demo_users():
    """
    Creates the demo organization and 9 demo users (one per role).
    All users have the password 'demo123' for development testing.
    """
    import bcrypt
    from datetime import datetime, timezone

    print("Generating Demo Organization & Users...")

    # Create the demo organization
    org = {
        "_id": DEMO_ORG_ID,
        "name": "Demo Startup",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    db.organizations.insert_one(org)

    # Hash the demo password once (all demo users share the same password)
    demo_password_hash = bcrypt.hashpw("demo123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    demo_users = [
        {"_id": "user-ceo-001",       "name": "Raj Patel (CEO)",        "email": "ceo@demo.com",        "role": "CEO"},
        {"_id": "user-manager-001",   "name": "Priya Sharma (Manager)", "email": "manager@demo.com",    "role": "MANAGER"},
        {"_id": "user-finance-001",   "name": "Amit Verma (Finance)",   "email": "finance@demo.com",    "role": "FINANCE"},
        {"_id": "user-sales-001",     "name": "Neha Gupta (Sales)",     "email": "sales@demo.com",      "role": "SALES"},
        {"_id": "user-support-001",   "name": "Vikram Singh (Support)", "email": "support@demo.com",    "role": "SUPPORT"},
        {"_id": "user-ops-001",       "name": "Anita Rao (Operations)", "email": "ops@demo.com",        "role": "OPERATIONS"},
        {"_id": "user-hr-001",        "name": "Suresh Kumar (HR)",      "email": "hr@demo.com",         "role": "HR"},
        {"_id": "user-analyst-001",   "name": "Kavita Desai (Analyst)", "email": "analyst@demo.com",    "role": "BUSINESS_ANALYST"},
        {"_id": "user-employee-001",  "name": "Rohan Mehta (Employee)", "email": "employee@demo.com",   "role": "EMPLOYEE"},
    ]

    for user in demo_users:
        user["password_hash"] = demo_password_hash
        user["organization_id"] = DEMO_ORG_ID
        user["created_at"] = datetime.now(timezone.utc)
        user["updated_at"] = datetime.now(timezone.utc)

    db.users.insert_many(demo_users)
    print(f"  Created {len(demo_users)} demo users (password: demo123)")


def tag_org_id():
    """
    Tags all existing business data with the demo organization ID
    so multi-tenant queries work correctly.
    """
    print("Tagging all business data with demo organizationId...")
    collections_to_tag = [
        "customers", "orders", "products", "sellers", "payments",
        "reviews", "order_items", "employees", "vendors", "expenses",
        "invoices", "tasks"
    ]
    for coll_name in collections_to_tag:
        result = db[coll_name].update_many(
            {"organization_id": {"$exists": False}},
            {"$set": {"organization_id": DEMO_ORG_ID}}
        )
        print(f"  {coll_name}: tagged {result.modified_count} documents")


if __name__ == "__main__":
    # Clear existing data so we can re-run safely
    print("Clearing existing collections...")
    for coll in db.list_collection_names():
        db[coll].drop()

    generate_olist_data()
    generate_enterprise_data()
    generate_demo_users()
    tag_org_id()
    print("\n[OK] Successfully seeded startup_ai database!")
    print("\n[DEMO ACCOUNTS] (password: demo123):")
    print("  ceo@demo.com       — CEO (full access)")
    print("  manager@demo.com   — Manager")
    print("  finance@demo.com   — Finance")
    print("  sales@demo.com     — Sales")
    print("  support@demo.com   — Support")
    print("  ops@demo.com       — Operations")
    print("  hr@demo.com        — HR")
    print("  analyst@demo.com   — Business Analyst")
    print("  employee@demo.com  — Employee")
