import random
from datetime import datetime
import json

class EcommerceDataGenerator:
    def __init__(self):
        self.product_categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Beauty']
        self.payment_methods = ['Credit Card', 'PayPal', 'Apple Pay', 'Google Pay']
        self.shipping_methods = ['Standard', 'Express', 'Next Day', 'International']
        self.countries = ['US', 'UK', 'CA', 'AU', 'DE', 'FR']
        
    def generate_product(self):
        category = random.choice(self.product_categories)
        return {
            "product_id": random.randint(1, 1000),
            "name": f"{category}-{random.randint(1000,9999)}",
            "category": category,
            "price": round(random.uniform(10.0, 1000.0), 2),
            "in_stock": random.choice([True, False]),
            "vendor": f"Vendor-{random.randint(1,50)}"
        }
    
    def generate_customer(self):
        country = random.choice(self.countries)
        return {
            "customer_id": random.randint(1, 10000),
            "email": f"customer{random.randint(1,10000)}@example.com",
            "country": country,
            "is_premium": random.choice([True, False]),
            "account_age_days": random.randint(1, 1000)
        }
    
    def generate_order(self):
        products = [self.generate_product() for _ in range(random.randint(1,5))]
        customer = self.generate_customer()
        
        total_amount = sum(p["price"] * random.randint(1,3) for p in products)
        shipping_cost = round(random.uniform(5.0, 25.0), 2)
        
        return {
            "order_id": f"ORD-{random.randint(10000,99999)}",
            "timestamp": datetime.now().isoformat(),
            "customer": customer,
            "products": products,
            "payment_method": random.choice(self.payment_methods),
            "shipping_method": random.choice(self.shipping_methods),
            "subtotal": round(total_amount, 2),
            "shipping_cost": shipping_cost,
            "tax": round(total_amount * 0.1, 2),
            "total_amount": round(total_amount + shipping_cost, 2),
            "currency": "USD",
            "status": random.choice(['Pending', 'Confirmed', 'Shipped', 'Delivered'])
        }

    def generate_batch(self, batch_size=100):
        return [self.generate_order() for _ in range(batch_size)]