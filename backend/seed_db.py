from app.services.vector_store import ProductVectorDB

db = ProductVectorDB()

products = [
    # CABLES
    {
        "sku": "CABLE-HV-001",
        "name": "11kV XLPE Power Cable 3C x 300sqmm",
        "details": "High Tension aluminum cable, XLPE insulation, galvanized steel strip armour. Voltage: 11kV.",
        "category": "Cable",
        "price": 4500,
        "specs": {
            "voltage": "11kV",
            "insulation": "XLPE",
            "cores": "3",
            "armouring": "Strip"
        }
    },
    {
        "sku": "CABLE-LV-002",
        "name": "1.1kV PVC Control Cable 12C x 1.5sqmm",
        "details": "Low Voltage copper control cable, PVC insulated, unarmoured. Voltage: 1.1kV.",
        "category": "Cable",
        "price": 850,
        "specs": {
            "voltage": "1.1kV",
            "insulation": "PVC",
            "cores": "12",
            "armouring": "Unarmoured"
        }
    },
    # SERVICES / SOFTWARE (New Items)
    {
        "sku": "SVC-CLOUD-001",
        "name": "Enterprise Cloud Hosting & Managed Services",
        "details": "Secure cloud hosting on AWS/Azure, inclusive of 24/7 monitoring, OS patching, and uptime SLA 99.9%.",
        "category": "Service",
        "price": 12000,
        "specs": {
            "type": "Cloud",
            "sla": "99.9%",
            "platform": "AWS/Azure"
        }
    },
    {
        "sku": "SVC-DEV-002",
        "name": "Custom Portal Development",
        "details": "Software development services for web portals, e-RCS systems, and dashboard customization.",
        "category": "Service",
        "price": 25000,
        "specs": {
            "type": "Development",
            "domain": "Web Portal",
            "customization": "Yes"
        }
    },
    {
        "sku": "SVC-AMC-003",
        "name": "Annual Maintenance Contract (AMC) - Software",
        "details": "Post-deployment maintenance, bug fixes, and minor enhancements for 1 year.",
        "category": "Service",
        "price": 5000,
        "specs": {
            "type": "Support",
            "duration": "1 Year",
            "coverage": "Bug Fixes"
        }
    }
]

print("Seeding database with products...")
db.add_products(products)
print("Seeding Complete!")

# Test Search
# Test Search
print("\nTesting Search for 'Hosting':")
match = db.search("We need cloud hosting servers")
if match:
    print(f"Found: {match[0]['name']} (SKU: {match[0]['sku']})")
else:
    print("No matches found.")
