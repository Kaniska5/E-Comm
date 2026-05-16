"""
Database seeding for mock e-commerce data.
"""
import uuid
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from backend.database.session import AsyncSessionLocal
from backend.database.models import Customer, Order, FAQDocument

logger = logging.getLogger(__name__)

def utcnow():
    return datetime.now(timezone.utc)

async def seed_database():
    """Seed initial mock data if the database is empty."""
    async with AsyncSessionLocal() as session:
        # Check if we already have customers
        result = await session.execute(select(Customer).limit(1))
        if result.scalar_one_or_none() is not None:
            logger.info("Database already seeded. Skipping.")
            return

        logger.info("Seeding database with mock data...")

        # 1. Seed Customers
        c1 = Customer(
            id="CUST-001",
            name="Alice Smith",
            email="alice@example.com",
            phone="+91-9876543210"
        )
        c2 = Customer(
            id="CUST-002",
            name="Bob Johnson",
            email="bob@example.com",
            phone="+91-9123456789"
        )
        session.add_all([c1, c2])

        # 2. Seed Orders
        o1 = Order(
            id="ORD-1001",
            customer_id="CUST-001",
            status="shipped",
            total_amount=1500.0,
            items=[{"name": "Wireless Headphones", "price": 1500.0, "quantity": 1}],
            tracking_number="TRK987654321",
            estimated_delivery=utcnow() + timedelta(days=2),
            created_at=utcnow() - timedelta(days=1)
        )
        o2 = Order(
            id="ORD-1002",
            customer_id="CUST-001",
            status="delivered",
            total_amount=850.0,
            items=[{"name": "Bluetooth Mouse", "price": 850.0, "quantity": 1}],
            tracking_number="TRK123456789",
            estimated_delivery=utcnow() - timedelta(days=1),
            created_at=utcnow() - timedelta(days=5)
        )
        o3 = Order(
            id="ORD-1003",
            customer_id="CUST-002",
            status="processing",
            total_amount=4500.0,
            items=[{"name": "Mechanical Keyboard", "price": 4500.0, "quantity": 1}],
            tracking_number=None,
            estimated_delivery=utcnow() + timedelta(days=5),
            created_at=utcnow()
        )
        session.add_all([o1, o2, o3])

        # 3. Seed FAQ Snippets (Optional, since we use markdown mostly, but good to have)
        f1 = FAQDocument(
            category="Shipping",
            question="How long does shipping take?",
            answer="Standard delivery takes 3-5 business days. Express takes 1-2 business days."
        )
        f2 = FAQDocument(
            category="Refunds",
            question="What is the refund limit for auto-approval?",
            answer="Refunds up to Rs 1000 are processed automatically. Larger amounts require human approval."
        )
        session.add_all([f1, f2])

        await session.commit()
        logger.info("Database seeding complete!")
