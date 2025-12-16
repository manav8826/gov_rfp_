from typing import List, Dict

class PricingAgent:
    def __init__(self):
        # Mock Service Rate Card
        self.service_rates = {
            "testing": 5000,
            "logistics": 2000,
            "tax_rate": 0.18
        }

    def calculate_pricing(self, technical_output: Dict) -> Dict:
        """
        Augments the technical output with pricing.
        """
        line_items = technical_output.get("line_items", [])
        total_project_value = 0
        
        priced_items = []
        for item in line_items:
            recommendation = item.get("recommendation", {})
            sku = recommendation.get("sku")
            
            # Base Price
            base_price = recommendation.get("price")
            if not base_price:
                base_price = self._get_price_for_sku(sku)
            
            # Quantity (Default to 1 if missing)
            qty = item.get("requirement", {}).get("quantity", 1.0)
            
            # Service Costs (Mock logic: if 'Test' in text, add cost)
            service_cost = self.service_rates["testing"]
            
            # Line Total = (Unit Price * Qty) + Service Cost
            line_total = (base_price * qty) + service_cost
            
            total_project_value += line_total
            
            # Add pricing info to the item
            item["pricing"] = {
                "unit_price": base_price,
                "quantity": qty,
                "service_add_ons": service_cost,
                "total_price": line_total
            }
            priced_items.append(item)
            
        return {
            "line_items": priced_items,
            "commercial_summary": {
                "subtotal": total_project_value,
                "tax": total_project_value * self.service_rates["tax_rate"],
                "grand_total": total_project_value * (1 + self.service_rates["tax_rate"])
            },
            "technical_summary": technical_output.get("summary"),
            "strategic_analysis": technical_output.get("strategic_analysis")
        }

    def _get_price_for_sku(self, sku: str) -> float:
        """
        Mock DB lookup
        """
        price_db = {
            "CABLE-A1": 4500.0,
            "CABLE-B2": 850.0
        }
        return price_db.get(sku, 0.0)
