# Coupon Management System - Backend API

## Overview
A RESTful API built with FastAPI to manage and apply different types of discount coupons (cart-wise, product-wise, and BxGy) for an e-commerce platform. The system is designed for extensibility to easily add new coupon types in the future.

## Technology Stack
- **Framework**: FastAPI
- **Database**: SQLite (easily replaceable with PostgreSQL/MySQL)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Testing**: pytest

## Installation & Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd coupon-management-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation
Once running, visit:
- **Swagger UI**: http://localhost:8000/docs

## API Endpoints

### Coupon Management
- `POST /api/v1/coupons` - Create a new coupon
- `GET /api/v1/coupons` - Retrieve all active coupons
- `GET /api/v1/coupons/{id}` - Retrieve specific coupon
- `PUT /api/v1/coupons/{id}` - Update specific coupon
- `DELETE /api/v1/coupons/{id}` - Soft delete coupon

### Coupon Application
- `POST /api/v1/applicable-coupons` - Get all applicable coupons for a cart
- `POST /api/v1/apply-coupon/{id}` - Apply specific coupon to cart

## Coupon Types Implemented

### 1. Cart-wise Coupons
Applies discount to entire cart when total exceeds threshold.

**Example**:
```json
{
  "type": "cart-wise",
  "details": {
    "threshold": 100,
    "discount": 10,
    "max_discount": 50
  }
}
```

### 2. Product-wise Coupons
Applies discount to specific products in cart.

**Example**:
```json
{
  "type": "product-wise",
  "details": {
    "product_id": 1,
    "discount": 20,
    "max_discount": 100
  }
}
```

### 3. BxGy (Buy X Get Y) Coupons
Complex offer where buying specified quantities from one set gets items from another set free.

**Example**:
```json
{
  "type": "bxgy",
  "details": {
    "buy_products": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ],
    "get_products": [
      {"product_id": 3, "quantity": 1}
    ],
    "repition_limit": 3
  }
}
```

## Comprehensive Test Cases

### Test Category 1: Cart-wise Coupon Scenarios

#### TC-CW-001: Basic Threshold Test
**Objective**: Verify cart-wise coupon applies when threshold is met
```json
// Create Coupon
POST /api/v1/coupons
{
  "type": "cart-wise",
  "details": {
    "threshold": 100,
    "discount": 10
  }
}

// Test Cart (Total: 150)
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 3, "price": 50}
    ]
  }
}
// Expected: Coupon should be applicable with 15 discount (10% of 150)
```

#### TC-CW-002: Below Threshold Test
**Objective**: Verify coupon doesn't apply when cart total below threshold
```json
// Test Cart (Total: 75)
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 1, "price": 25},
      {"product_id": 2, "quantity": 2, "price": 25}
    ]
  }
}
// Expected: Coupon should NOT be applicable
```

#### TC-CW-003: Maximum Discount Cap Test
**Objective**: Verify maximum discount limit is respected
```json
// Create Coupon with max discount
POST /api/v1/coupons
{
  "type": "cart-wise",
  "details": {
    "threshold": 100,
    "discount": 20,
    "max_discount": 50
  }
}

// Test Cart (Total: 500)
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 10, "price": 50}
    ]
  }
}
// Expected: Discount should be capped at 50 (not 100)
```

#### TC-CW-004: Decimal Price Handling
**Objective**: Test discount calculation with decimal prices
```json
// Test Cart with decimal prices
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 3, "price": 33.33},
      {"product_id": 2, "quantity": 2, "price": 16.67}
    ]
  }
}
// Expected: Proper decimal handling and rounding
```

### Test Category 2: Product-wise Coupon Scenarios

#### TC-PW-001: Target Product in Cart
**Objective**: Verify product-wise discount applies to target product
```json
// Create Product-wise Coupon
POST /api/v1/coupons
{
  "type": "product-wise",
  "details": {
    "product_id": 1,
    "discount": 25
  }
}

// Test Cart
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 2, "price": 100},
      {"product_id": 2, "quantity": 1, "price": 50}
    ]
  }
}
// Expected: 25% discount on product 1 only (50 discount)
```

#### TC-PW-002: Target Product Not in Cart
**Objective**: Verify coupon doesn't apply when target product absent
```json
// Test Cart without target product
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 2, "quantity": 3, "price": 40},
      {"product_id": 3, "quantity": 1, "price": 80}
    ]
  }
}
// Expected: Coupon should NOT be applicable
```

#### TC-PW-003: Multiple Quantities of Target Product
**Objective**: Test discount on multiple quantities
```json
// Test Cart with multiple target product quantities
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 5, "price": 60}
    ]
  }
}
// Expected: 25% discount on all 5 quantities (75 discount)
```

#### TC-PW-004: Maximum Discount Limit
**Objective**: Test product-wise maximum discount cap
```json
// Create Coupon with max discount
POST /api/v1/coupons
{
  "type": "product-wise",
  "details": {
    "product_id": 1,
    "discount": 30,
    "max_discount": 80
  }
}

// Test Cart (Product 1 total: 400)
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 4, "price": 100}
    ]
  }
}
// Expected: Discount capped at 80 (not 120)
```

### Test Category 3: BxGy Coupon Scenarios

#### TC-BG-001: Simple B2G1 Scenario
**Objective**: Test basic Buy 2 Get 1 offer
```json
// Create BxGy Coupon
POST /api/v1/coupons
{
  "type": "bxgy",
  "details": {
    "buy_products": [
      {"product_id": 1, "quantity": 2}
    ],
    "get_products": [
      {"product_id": 2, "quantity": 1}
    ],
    "repition_limit": 1
  }
}

// Test Cart
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 2, "price": 50},
      {"product_id": 2, "quantity": 1, "price": 30}
    ]
  }
}
// Expected: Product 2 becomes free (30 discount)
```

#### TC-BG-002: Multiple Repetitions
**Objective**: Test BxGy with multiple repetition cycles
```json
// Test Cart allowing 2 repetitions
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 6, "price": 40},
      {"product_id": 2, "quantity": 3, "price": 25}
    ]
  }
}
// Expected: 3 units of product 2 become free (75 discount)
```

#### TC-BG-003: Insufficient Buy Products
**Objective**: Test when cart doesn't have enough buy products
```json
// Test Cart with insufficient buy products
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 1, "price": 50},
      {"product_id": 2, "quantity": 2, "price": 30}
    ]
  }
}
// Expected: Coupon should NOT be applicable
```

#### TC-BG-004: Insufficient Get Products
**Objective**: Test when cart has fewer get products than offered
```json
// Test Cart with limited get products
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 4, "price": 50},
      {"product_id": 2, "quantity": 1, "price": 30}
    ]
  }
}
// Expected: Only 1 unit becomes free (partial fulfillment)
```

#### TC-BG-005: Complex Multi-Product BxGy
**Objective**: Test complex buy/get combinations
```json
// Create Complex BxGy Coupon
POST /api/v1/coupons
{
  "type": "bxgy",
  "details": {
    "buy_products": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ],
    "get_products": [
      {"product_id": 3, "quantity": 1},
      {"product_id": 4, "quantity": 2}
    ],
    "repition_limit": 2
  }
}

// Test Cart
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 4, "price": 60},
      {"product_id": 2, "quantity": 2, "price": 40},
      {"product_id": 3, "quantity": 2, "price": 25},
      {"product_id": 4, "quantity": 4, "price": 20}
    ]
  }
}
// Expected: Complex calculation with multiple free products
```

#### TC-BG-006: Zero Repetition Limit
**Objective**: Test BxGy with no repetition limit
```json
// Create Unlimited BxGy Coupon
POST /api/v1/coupons
{
  "type": "bxgy",
  "details": {
    "buy_products": [
      {"product_id": 1, "quantity": 1}
    ],
    "get_products": [
      {"product_id": 2, "quantity": 1}
    ]
    // No repetition_limit specified (unlimited)
  }
}

// Test Cart
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 10, "price": 30},
      {"product_id": 2, "quantity": 8, "price": 20}
    ]
  }
}
// Expected: 8 units of product 2 become free (limited by availability)
```

### Test Category 4: Coupon Management Tests

#### TC-CM-001: Create Coupon Validation
**Objective**: Test coupon creation with invalid data
```json
// Invalid coupon type
POST /api/v1/coupons
{
  "type": "invalid-type",
  "details": {}
}
// Expected: 400 Bad Request

// Missing required fields
POST /api/v1/coupons
{
  "type": "cart-wise",
  "details": {}
}
// Expected: 400 Bad Request - Missing threshold/discount
```

#### TC-CM-002: Coupon Expiration Test
**Objective**: Test expired coupon handling
```json
// Create Expired Coupon
POST /api/v1/coupons
{
  "type": "cart-wise",
  "details": {
    "threshold": 50,
    "discount": 15
  },
  "expires_at": "2024-01-01T00:00:00"
}

// Test with valid cart
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 2, "price": 50}
    ]
  }
}
// Expected: Expired coupon should NOT be applicable
```

#### TC-CM-003: Usage Limit Test
**Objective**: Test coupon usage limit enforcement
```json
// Create Limited Usage Coupon
POST /api/v1/coupons
{
  "type": "cart-wise",
  "details": {
    "threshold": 100,
    "discount": 10
  },
  "usage_limit": 1
}

// Apply coupon first time
POST /api/v1/apply-coupon/1
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 3, "price": 40}
    ]
  }
}
// Expected: Should work

// Try to apply again
POST /api/v1/apply-coupon/1
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 2, "price": 60}
    ]
  }
}
// Expected: Should fail - usage limit exceeded
```

#### TC-CM-004: Update Coupon Test
**Objective**: Test coupon modification
```json
// Update existing coupon
PUT /api/v1/coupons/1
{
  "type": "cart-wise",
  "details": {
    "threshold": 150,
    "discount": 12,
    "max_discount": 75
  },
  "expires_at": "2025-12-31T23:59:59"
}
// Expected: Coupon should be updated successfully
```

#### TC-CM-005: Soft Delete Test
**Objective**: Test coupon soft deletion
```json
// Delete coupon
DELETE /api/v1/coupons/1
// Expected: Coupon marked as inactive, not physically deleted

// Try to apply deleted coupon
POST /api/v1/apply-coupon/1
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 2, "price": 75}
    ]
  }
}
// Expected: Should fail - coupon not active
```

### Test Category 5: Edge Cases and Error Scenarios

#### TC-EC-001: Empty Cart Test
**Objective**: Test system behavior with empty cart
```json
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": []
  }
}
// Expected: No coupons applicable, graceful handling
```

#### TC-EC-002: Zero Price Items
**Objective**: Test handling of zero-price items
```json
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 2, "price": 0},
      {"product_id": 2, "quantity": 1, "price": 100}
    ]
  }
}
// Expected: Proper handling without division by zero
```

#### TC-EC-003: Negative Values Test
**Objective**: Test validation of negative values
```json
// Negative discount
POST /api/v1/coupons
{
  "type": "cart-wise",
  "details": {
    "threshold": 100,
    "discount": -10
  }
}
// Expected: 400 Bad Request

// Negative quantity in cart
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": -2, "price": 50}
    ]
  }
}
// Expected: 400 Bad Request
```

#### TC-EC-004: Large Numbers Test
**Objective**: Test system with very large values
```json
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 1000000, "price": 999999.99}
    ]
  }
}
// Expected: System handles large calculations without overflow
```

#### TC-EC-005: Invalid Product IDs
**Objective**: Test handling of non-existent product references
```json
// BxGy with invalid product ID
POST /api/v1/coupons
{
  "type": "bxgy",
  "details": {
    "buy_products": [
      {"product_id": 99999, "quantity": 2}
    ],
    "get_products": [
      {"product_id": 88888, "quantity": 1}
    ],
    "repition_limit": 1
  }
}
// Expected: Should create but handle gracefully when applied
```

### Test Category 6: Performance and Stress Tests

#### TC-PS-001: Large Cart Test
**Objective**: Test performance with large cart
```json
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      // Generate 100+ items
      {"product_id": 1, "quantity": 50, "price": 25},
      {"product_id": 2, "quantity": 30, "price": 40},
      // ... continue for 100 different products
    ]
  }
}
// Expected: Response within acceptable time limits
```

#### TC-PS-002: Multiple Coupons Test
**Objective**: Test system with many active coupons
```json
// Create 50+ different coupons of various types
// Then test applicable coupons
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 3, "price": 100}
    ]
  }
}
// Expected: Efficient filtering and response
```

### Test Category 7: Concurrent Access Tests

#### TC-CA-001: Concurrent Coupon Application
**Objective**: Test simultaneous coupon applications
```bash
# Simulate multiple users applying same limited coupon simultaneously
# Use tools like Apache Bench or custom script
# Expected: Proper handling of race conditions
```

#### TC-CA-002: Concurrent Coupon Updates
**Objective**: Test simultaneous coupon modifications
```bash
# Multiple PUT requests to same coupon
# Expected: Data consistency maintained
```

### Test Category 8: Integration Tests

#### TC-IT-001: Complete Workflow Test
**Objective**: Test entire coupon lifecycle
```json
// 1. Create coupon
POST /api/v1/coupons
{
  "type": "cart-wise",
  "details": {
    "threshold": 100,
    "discount": 15
  },
  "usage_limit": 5
}

// 2. Get applicable coupons
POST /api/v1/applicable-coupons
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 3, "price": 50}
    ]
  }
}

// 3. Apply coupon
POST /api/v1/apply-coupon/{coupon_id}
{
  "cart": {
    "items": [
      {"product_id": 1, "quantity": 3, "price": 50}
    ]
  }
}

// 4. Verify usage count updated
GET /api/v1/coupons/{coupon_id}

// 5. Update coupon
PUT /api/v1/coupons/{coupon_id}
{
  "type": "cart-wise",
  "details": {
    "threshold": 120,
    "discount": 20
  }
}

// 6. Delete coupon
DELETE /api/v1/coupons/{coupon_id}
```

## Test Execution Guidelines

### Manual Testing Steps
1. **Setup**: Create test database and start server
2. **Data Preparation**: Create various coupon types using provided examples
3. **Systematic Testing**: Execute test cases in order
4. **Verification**: Check responses match expected outcomes
5. **Cleanup**: Clear test data between test suites

### Automated Testing
```bash
# Run specific test categories
pytest tests/test_cart_wise.py -v
pytest tests/test_product_wise.py -v
pytest tests/test_bxgy.py -v
pytest tests/test_edge_cases.py -v

# Run all tests with coverage
pytest --cov=app --cov-report=html tests/
```

### Test Data Management
- Use consistent product IDs across tests
- Maintain separate test database
- Reset coupon usage counts between test runs
- Use meaningful test data that represents real scenarios

## Use Cases Analysis

### IMPLEMENTED CASES

#### Cart-wise Coupons
1. **Basic threshold discount**: 10% off on carts over Rs. 100
2. **Maximum discount cap**: Discount limited to maximum amount
3. **Multiple threshold levels**: Different discounts for different cart values
4. **Percentage vs fixed amount**: Both percentage and fixed discounts

#### Product-wise Coupons
1. **Single product discount**: 20% off on Product A
2. **Multiple quantity handling**: Discount applies to all quantities of target product
3. **Maximum discount limits**: Cap on total discount per product
4. **Product not in cart**: Graceful handling when target product absent

#### BxGy Coupons
1. **Simple B2G1**: Buy 2 products from [X,Y], get 1 from [A,B] free
2. **Multiple buy products**: Buy from array of products [X,Y,Z]
3. **Multiple get products**: Get multiple different products free [A,B,C]
4. **Repetition limits**: Maximum number of times offer can be applied
5. **Insufficient buy products**: Handle cases where not enough buy products
6. **Insufficient get products**: Handle when fewer get products available than offered
7. **Complex combinations**: Buy 3 of [X,Y] + 2 of [Z], get 1 of [A] + 2 of [B]

#### General Features
1. **Coupon expiration**: Time-based validity
2. **Usage limits**: Maximum number of times coupon can be used
3. **Soft deletion**: Coupons marked inactive instead of deleted
4. **Concurrent safety**: Database transactions prevent race conditions

### 📄 PARTIALLY IMPLEMENTED CASES

#### Advanced BxGy Scenarios
1. **Mixed product requirements**: Implemented but limited testing
2. **Fractional repetitions**: Handled with floor division
3. **Priority ordering**: Basic implementation, could be enhanced

### UNIMPLEMENTED CASES (Future Enhancements)

#### Complex Business Logic
1. **Coupon stacking**: Multiple coupons on same cart
   - **Reason**: Complex business rules needed for stacking priority
   - **Implementation**: Would require coupon precedence system

2. **User-specific coupons**: Personalized offers
   - **Reason**: Requires user authentication and profiling
   - **Implementation**: Add user_id field and user validation

3. **Category-wise coupons**: Discounts on product categories
   - **Reason**: Requires product category information
   - **Implementation**: Need product catalog with category mapping

4. **Time-bound flash sales**: Limited time offers
   - **Reason**: Requires real-time countdown and auto-deactivation
   - **Implementation**: Background jobs for time-based activation/deactivation

5. **Minimum quantity requirements**: Buy at least N items to qualify
   - **Reason**: Time constraint for implementation
   - **Implementation**: Add quantity validation in applicable coupons logic

6. **Geographic restrictions**: Location-based coupon validity
   - **Reason**: Requires user location and geo-mapping
   - **Implementation**: Add location fields and validation

7. **First-time user coupons**: Special offers for new users
   - **Reason**: Requires user history tracking
   - **Implementation**: User service integration needed

8. **Seasonal/Holiday coupons**: Auto-activate during specific periods
   - **Reason**: Complex scheduling logic required
   - **Implementation**: Cron jobs or background schedulers

9. **Dynamic pricing integration**: Coupons that work with surge pricing
   - **Reason**: Requires real-time pricing service
   - **Implementation**: Integration with pricing microservice

10. **Referral-based coupons**: Discounts for referrals
    - **Reason**: Requires referral tracking system
    - **Implementation**: Referral service and reward calculation

#### Advanced BxGy Cases
1. **Cross-category BxGy**: Buy electronics, get fashion items
   - **Reason**: Requires product categorization
   - **Implementation**: Category-based product grouping

2. **Tiered BxGy**: Different rewards based on spend levels
   - **Reason**: Complex multi-tier logic needed
   - **Implementation**: Nested condition evaluation

3. **Progressive BxGy**: Better rewards for higher quantities
   - **Reason**: Multi-level reward calculation
   - **Implementation**: Sliding scale discount calculator

#### Performance & Scale Cases
1. **Bulk coupon application**: Apply multiple coupons simultaneously
   - **Reason**: Complex optimization problem
   - **Implementation**: Advanced algorithm for optimal coupon combination

2. **Real-time inventory sync**: Ensure product availability
   - **Reason**: Requires inventory management system
   - **Implementation**: Integration with inventory microservice

3. **High-frequency updates**: Handle thousands of concurrent applications
   - **Reason**: Requires advanced caching and queuing
   - **Implementation**: Redis caching, message queues

## Edge Cases Handled

### Data Validation
- Invalid coupon types rejected
- Negative discounts prevented
- Missing required fields validation
- Invalid product IDs handled gracefully
- Zero or negative quantities in cart
- Empty cart scenarios

### Business Logic Edge Cases
- Expired coupons automatically excluded
- Usage limit exceeded prevents application
- Insufficient products for BxGy offers
- Products not in cart for product-wise coupons
- Cart total below threshold for cart-wise coupons
- Maximum discount caps respected
- Floating point precision in calculations

### System Edge Cases
- Database connection failures handled
- Concurrent coupon usage tracked
- Invalid coupon IDs return appropriate errors
- Malformed request data validation

## Assumptions Made

### Business Rules
1. **No coupon stacking**: Only one coupon can be applied per transaction
2. **Price precedence**: Original product prices used for discount calculation
3. **Rounding**: Discounts rounded to 2 decimal places
4. **Free items**: BxGy free items come from existing cart inventory
5. **Partial fulfillment**: BxGy offers applied for maximum possible repetitions

### Technical Assumptions
1. **Product catalog**: Product IDs are managed externally
2. **Currency**: All prices in single currency (no conversion)
3. **Time zones**: UTC used for all timestamps
4. **User context**: No user authentication required for basic functionality
5. **Inventory**: Unlimited inventory assumed (no stock validation)

### Data Assumptions
1. **Product prices**: Always positive numbers
2. **Quantities**: Always positive integers
3. **Discount percentages**: Between 0-100%
4. **Cart persistence**: Carts exist only during request lifecycle

## Limitations

### Current Implementation
1. **Single coupon application**: Cannot apply multiple coupons together
2. **No user tracking**: Cannot track individual user usage patterns
3. **Limited analytics**: Basic usage counting only
4. **No A/B testing**: Cannot test different coupon variants
5. **Static pricing**: No integration with dynamic pricing systems

### Performance Limitations
1. **In-memory calculations**: All discount calculations done in application layer
2. **No caching**: Coupon data fetched from database each time
3. **Synchronous processing**: No async processing for complex calculations
4. **Single database**: No read replicas or sharding support

### Business Logic Limitations
1. **Fixed repetition logic**: BxGy repetition is simple floor division
2. **No priority rules**: Cannot define coupon application priority
3. **Limited date handling**: Basic expiration checking only
4. **No rollback mechanism**: Applied coupons cannot be easily reversed

## Future Improvements

### Short Term (1-2 sprints)
1. **Caching layer**: Redis for frequently accessed coupons
2. **Audit logging**: Track all coupon applications
3. **Better error messages**: More descriptive validation errors
4. **Batch operations**: Bulk coupon creation and updates

### Medium Term (1-2 months)
1. **User management**: Authentication and user-specific coupons
2. **Analytics dashboard**: Coupon usage statistics and insights
3. **Advanced BxGy**: More complex buy/get combinations
4. **Category support**: Product category-based coupons

### Long Term (3-6 months)
1. **Microservices**: Split into separate coupon, cart, and pricing services
2. **Event-driven architecture**: Async processing with message queues
3. **Machine learning**: Personalized coupon recommendations
4. **Multi-tenant support**: Support for multiple e-commerce stores

## Testing

### Unit Tests
- Coupon CRUD operations
- Discount calculation algorithms
- Edge case handling
- Validation logic

### Integration Tests
- API endpoint testing
- Database integration
- End-to-end coupon application

### Test Coverage
- Target: 90%+ code coverage
- Current: ~85% (estimated)

```bash
# Run tests
pytest tests/ -v --cov=app --cov-report=html
```

## Database Schema

### Coupons Table
```sql
CREATE TABLE coupons (
    id INTEGER PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    details JSON NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    usage_limit INTEGER NULL,
    used_count INTEGER DEFAULT 0
);
```
## License
MIT License

---

**Note**: This implementation prioritizes extensibility
