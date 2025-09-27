# Orders App Test Suite

This directory contains comprehensive test cases for the Orders app, covering models, forms, and views.

## Test Structure

The test suite is organized into multiple files to maintain readability and manageability:

1. `test_orders.py` - Tests for the Order model (test cases #001-#005)
2. `test_orders_part2.py` - Tests for OrderItem model, OrderStatusHistory, OrderForm, and OrderStatusUpdateForm (test cases #006-#010)
3. `test_orders_part3.py` - Tests for OrderItemForm and Order views (test cases #011-#017)
4. `test_orders_part4.py` - Tests for OrderItem views (test cases #018-#020)
5. `test_orders_main.py` - Imports all test cases from the separate files for easy running

## Running Tests

To run all tests:

```bash
python manage.py test orders.tests.test_orders_main
```

To run a specific test file:

```bash
python manage.py test orders.tests.test_orders
```

To run a specific test case:

```bash
python manage.py test orders.tests.test_orders.OrderModelTestCase
```

To run a specific test method:

```bash
python manage.py test orders.tests.test_orders.OrderModelTestCase.test_create_new_order
```

## Test Coverage

The test suite covers the following functionality:

### Order Model Tests
- Creating a new order
- Calculating the total amount of an order
- Checking if an order can be cancelled
- Changing the status of an order
- Changing the payment status of an order

### OrderItem Model Tests
- Creating a new order item
- Calculating the final price of an order item

### OrderStatusHistory Tests
- Creating an order status history entry

### Form Tests
- Creating a new order using OrderForm
- Updating order status using OrderStatusUpdateForm
- Adding an item to an order using OrderItemForm
- Updating an item in an order using OrderItemForm

### View Tests
- Creating an order
- Listing orders
- Viewing order details
- Updating order status
- Cancelling an order
- Adding an item to an order
- Updating an item in an order
- Deleting an item from an order



