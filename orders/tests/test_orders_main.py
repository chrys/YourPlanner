"""
Main test file that imports all test cases from the separate test files.
This allows running all tests with a single command.
"""

from .test_orders import OrderModelTestCase
from .test_orders_part2 import OrderItemModelTestCase, OrderStatusHistoryTestCase, OrderFormTestCase, OrderStatusUpdateFormTestCase
from .test_orders_part3 import OrderItemFormTestCase, OrderViewTestCase
from .test_orders_part4 import OrderItemViewTestCase

# This file doesn't contain any test cases itself, it just imports them from other files.
# This allows running all tests with a single command: python manage.py test orders.tests.test_orders_main

