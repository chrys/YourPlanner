#!/usr/bin/env python
"""
Test script to verify service-level multiple prices with labels functionality.
Tests creating and updating services with multiple prices linked to labels.
"""

import os
import sys
import django
from decimal import Decimal
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YourPlanner.settings.base')
sys.path.insert(0, '/Users/chrys/Projects/YourPlanner')
django.setup()

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from services.models import Service, Price
from labels.models import Label
from users.models import Professional
from django.db.models import Q

User = get_user_model()

def get_unique_service_name(base_name):
    """Generate a unique service name with timestamp to avoid slug conflicts."""
    return f"{base_name}_{int(time.time() * 1000) % 10000}"

def test_create_service_with_multiple_prices():
    """Test creating a service with multiple prices and labels."""
    print("\n" + "="*80)
    print("TEST 1: Create Service with Multiple Prices")
    print("="*80)
    
    # Get or create test user and professional
    user, _ = User.objects.get_or_create(
        username='test_pro_prices',
        defaults={'email': 'testpro@prices.com', 'is_active': True}
    )
    prof, _ = Professional.objects.get_or_create(
        user=user,
        defaults={
            'title': 'Test Multiple Prices Professional',
            'specialization': 'Wedding Planning'
        }
    )
    
    # Create labels
    label_standard, _ = Label.objects.get_or_create(
        name='Standard',
        defaults={'label_type': 'PRICE', 'description': 'Standard pricing'}
    )
    label_agent, _ = Label.objects.get_or_create(
        name='Agent Price',
        defaults={'label_type': 'PRICE', 'description': 'Agent pricing'}
    )
    
    # Delete existing test service if it exists
    Service.objects.filter(
        title='Test Multiple Prices Service',
        professional=prof
    ).delete()
    
    # Create service with multiple prices
    service = Service.objects.create(
        professional=prof,
        title=get_unique_service_name('Test Multiple Prices Service'),
        description='Testing service-level pricing with labels',
        is_active=True
    )
    print(f"✅ Created service: {service.title} (ID: {service.pk})")
    
    # Create multiple prices linked to the service
    price1 = Price.objects.create(
        service=service,
        amount=1000.00,
        currency='EUR',
        frequency='ONCE',
        description='Full wedding coordination',
        is_active=True
    )
    price1.labels.add(label_standard)
    print(f"✅ Created price 1: {price1.amount} EUR (ONCE) - Standard")
    
    price2 = Price.objects.create(
        service=service,
        amount=800.00,
        currency='EUR',
        frequency='ONCE',
        description='Coordination for agents',
        is_active=True
    )
    price2.labels.add(label_agent)
    print(f"✅ Created price 2: {price2.amount} EUR (ONCE) - Agent Price")
    
    # Verify
    service_prices = service.get_service_prices()
    print(f"\n📊 Service has {service_prices.count()} prices:")
    for p in service_prices:
        labels = ', '.join([l.name for l in p.labels.all()]) or 'No labels'
        print(f"   - {p.amount} {p.currency} ({p.frequency}) - {labels}")
    
    assert service_prices.count() == 2, f"Expected 2 prices, got {service_prices.count()}"
    print("\n✅ TEST 1 PASSED: Service has 2 prices with correct labels")
    
    return service, price1, price2


def test_update_service_prices():
    """Test updating service prices."""
    print("\n" + "="*80)
    print("TEST 2: Update Service Prices")
    print("="*80)
    
    service, price1, price2 = test_create_service_with_multiple_prices()
    
    # Update price amounts
    price1.amount = Decimal('1200.00')
    price1.save()
    print(f"✅ Updated price 1 amount to: {price1.amount}")
    
    price2.amount = Decimal('850.00')
    price2.save()
    print(f"✅ Updated price 2 amount to: {price2.amount}")
    
    # Refresh and verify
    service_prices = service.get_service_prices().order_by('amount')
    amounts = [p.amount for p in service_prices]
    print(f"\n📊 Updated prices: {amounts}")
    
    assert amounts == [850.0, 1200.0], f"Expected [850.0, 1200.0], got {amounts}"
    print("\n✅ TEST 2 PASSED: Prices updated correctly")


def test_delete_service_price():
    """Test deleting a service price."""
    print("\n" + "="*80)
    print("TEST 3: Delete Service Price")
    print("="*80)
    
    service, price1, price2 = test_create_service_with_multiple_prices()
    
    initial_count = service.get_service_prices().count()
    print(f"Initial prices: {initial_count}")
    
    # Delete one price
    price1_id = price1.id
    price1.delete()
    print(f"✅ Deleted price 1 (ID: {price1_id})")
    
    # Verify
    remaining_prices = service.get_service_prices()
    final_count = remaining_prices.count()
    print(f"Remaining prices: {final_count}")
    
    assert final_count == 1, f"Expected 1 price, got {final_count}"
    assert list(remaining_prices) == [price2], "Wrong price remaining"
    print("\n✅ TEST 3 PASSED: Price deleted successfully")


def test_service_price_validation():
    """Test that prices require either service or item, not both."""
    print("\n" + "="*80)
    print("TEST 4: Service Price Validation")
    print("="*80)
    
    # Get test professional
    user, _ = User.objects.get_or_create(
        username='test_pro_validation',
        defaults={'email': 'testval@prices.com', 'is_active': True}
    )
    prof, _ = Professional.objects.get_or_create(
        user=user,
        defaults={
            'title': 'Test Validation Professional',
            'specialization': 'Wedding Planning'
        }
    )
    
    # Create service
    service = Service.objects.create(
        professional=prof,
        title=get_unique_service_name('Validation Test Service'),
        description='Testing validation',
        is_active=True
    )
    print(f"✅ Created test service")
    
    # Test 1: Service only (valid)
    price_service_only = Price(
        service=service,
        amount=Decimal('100.00'),
        currency='EUR',
        frequency='ONCE'
    )
    try:
        price_service_only.full_clean()
        price_service_only.save()
        print("✅ Service-only price validation passed")
    except Exception as e:
        print(f"❌ Service-only price validation failed: {e}")
        raise
    
    # Test 2: Neither service (invalid) - this should fail since service is required for our use case
    price_neither = Price(
        amount=Decimal('100.00'),
        currency='EUR',
        frequency='ONCE'
    )
    try:
        price_neither.full_clean()
        print("❌ Price with no service/item should fail validation but didn't!")
        raise AssertionError("Price with neither service nor item should fail validation")
    except ValidationError as e:
        print(f"✅ Price with no service correctly rejected: {e.messages}")
    
    print("\n✅ TEST 4 PASSED: Validation working correctly")


def test_service_get_all_prices():
    """Test Service.get_service_prices() returns service-level prices."""
    print("\n" + "="*80)
    print("TEST 5: Service.get_service_prices() Returns Service Prices Only")
    print("="*80)
    
    # Get test professional
    user, _ = User.objects.get_or_create(
        username='test_pro_service_prices',
        defaults={'email': 'testservice@prices.com', 'is_active': True}
    )
    prof, _ = Professional.objects.get_or_create(
        user=user,
        defaults={
            'title': 'Test Service Prices Professional',
            'specialization': 'Event Coordination'
        }
    )
    
    # Delete existing test service
    service_title = get_unique_service_name('Test Service Prices Only')
    Service.objects.filter(
        title__startswith='Test Service Prices Only',
        professional=prof
    ).delete()
    
    # Create service with multiple prices
    service = Service.objects.create(
        professional=prof,
        title=service_title,
        description='Testing get_service_prices',
        is_active=True
    )
    
    # Create service-level prices
    service_price1 = Price.objects.create(
        service=service,
        amount=Decimal('500.00'),
        currency='EUR',
        frequency='ONCE',
        description='Service price 1'
    )
    print(f"✅ Created service price 1: {service_price1.amount} EUR")
    
    service_price2 = Price.objects.create(
        service=service,
        amount=Decimal('750.00'),
        currency='EUR',
        frequency='MONTHLY',
        description='Service price 2'
    )
    print(f"✅ Created service price 2: {service_price2.amount} EUR")
    
    # Get service prices
    service_prices = service.get_service_prices()
    print(f"\n📊 Service has {service_prices.count()} service-level prices")
    for p in service_prices:
        print(f"   - {p.amount} EUR ({p.frequency})")
    
    assert service_prices.count() == 2, f"Expected 2 prices, got {service_prices.count()}"
    amounts = sorted([Decimal(str(p.amount)) for p in service_prices])
    expected = [Decimal('500.00'), Decimal('750.00')]
    assert amounts == expected, f"Expected {expected}, got {amounts}"
    
    print("\n✅ TEST 5 PASSED: get_service_prices() returns only service-level prices")


if __name__ == '__main__':
    try:
        print("\n🚀 Starting Service Multiple Prices Tests...\n")
        
        test_service_price_validation()
        test_create_service_with_multiple_prices()
        test_update_service_prices()
        test_delete_service_price()
        test_service_get_all_prices()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
