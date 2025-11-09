#!/usr/bin/env python
"""
Simple test script to verify service prices are being populated correctly
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YourPlanner.settings')
sys.path.insert(0, '/Users/chrys/Projects/YourPlanner')
django.setup()

from services.models import Service, Price

# Find a service with no items but with service-level prices
print("=" * 70)
print("CHECKING SERVICES FOR ONES WITH NO ITEMS BUT WITH SERVICE PRICES")
print("=" * 70)

services = Service.objects.all()
for service in services:
    item_count = service.items.count()
    price_count = service.get_service_prices().count()
    
    if item_count == 0 and price_count > 0:
        print(f"\n✓ FOUND: Service '{service.title}' (ID: {service.pk})")
        print(f"  Items: {item_count}")
        print(f"  Service-Level Prices: {price_count}")
        
        prices = service.get_service_prices()
        for price in prices:
            labels = [l.name for l in price.labels.all()]
            print(f"    - {price.amount} {price.currency} | {price.get_frequency_display()} | Labels: {labels}")
            print(f"      Description: {price.description}")

print("\n" + "=" * 70)
print("TESTING JSON SERIALIZATION")
print("=" * 70)

# Test the JSON serialization like the view does
test_service = Service.objects.filter(items__isnull=True).first()
if test_service:
    print(f"\nUsing service: {test_service.title}")
    
    service_dict = {
        'id': test_service.pk,
        'title': test_service.title,
        'professional_name': test_service.professional.title or test_service.professional.user.get_full_name(),
        'items': []
    }
    
    # Get service prices
    service_prices = test_service.get_service_prices()
    service_dict['service_prices'] = []
    for price in service_prices:
        service_dict['service_prices'].append({
            'id': price.pk,
            'amount': str(price.amount),
            'currency': price.currency,
            'frequency': price.get_frequency_display(),
            'description': price.description,
        })
    
    print(f"\nService dict structure:")
    print(json.dumps(service_dict, indent=2))
else:
    print("\nNo service without items found")

print("\n" + "=" * 70)
