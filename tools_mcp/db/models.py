from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ---------------------------------------------------------------------------
# Declarative base — ecommerce domain only
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """Shared declarative base for all ecommerce ORM models."""


# ---------------------------------------------------------------------------
# User & identity tables
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_uuid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    full_name: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    city: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_email_verified: Mapped[bool | None] = mapped_column(Boolean, default=False)
    status: Mapped[str | None] = mapped_column(String(20), default="active")

    # Relationships
    addresses: Mapped[list[Address]] = relationship(
        "Address", back_populates="user", lazy="raise"
    )
    orders: Mapped[list[Order]] = relationship(
        "Order", back_populates="user", lazy="raise"
    )
    reviews: Mapped[list[Review]] = relationship(
        "Review", back_populates="user", lazy="raise"
    )
    review_votes: Mapped[list[ReviewVote]] = relationship(
        "ReviewVote", back_populates="user", lazy="raise"
    )
    role_mappings: Mapped[list[UserRoleMapping]] = relationship(
        "UserRoleMapping", back_populates="user", lazy="raise"
    )
    sessions: Mapped[list[UserSession]] = relationship(
        "UserSession", back_populates="user", lazy="raise"
    )


class Address(Base):
    __tablename__ = "addresses"

    address_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    type: Mapped[str | None] = mapped_column(String(20))
    street_line1: Mapped[str | None] = mapped_column(String(200))
    landmark: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(50))
    state: Mapped[str | None] = mapped_column(String(50))
    country: Mapped[str | None] = mapped_column(String(50), default="India")
    pincode: Mapped[str | None] = mapped_column(String(10))
    is_default: Mapped[bool | None] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped[User] = relationship("User", back_populates="addresses", lazy="raise")
    orders: Mapped[list[Order]] = relationship(
        "Order", back_populates="address", lazy="raise"
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200))
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)

    role_mappings: Mapped[list[UserRoleMapping]] = relationship(
        "UserRoleMapping", back_populates="role", lazy="raise"
    )


class UserRoleMapping(Base):
    __tablename__ = "user_role_mapping"

    mapping_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_roles.role_id"), nullable=False
    )
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped[User] = relationship(
        "User", back_populates="role_mappings", lazy="raise"
    )
    role: Mapped[UserRole] = relationship(
        "UserRole", back_populates="role_mappings", lazy="raise"
    )


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)
    device: Mapped[str | None] = mapped_column(String(100))
    ip_address: Mapped[str | None] = mapped_column(String(45))

    user: Mapped[User] = relationship("User", back_populates="sessions", lazy="raise")


# ---------------------------------------------------------------------------
# Catalogue tables (products, categories, brands, attributes)
# ---------------------------------------------------------------------------

class Brand(Base):
    __tablename__ = "brands"

    brand_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(50))
    segment: Mapped[str | None] = mapped_column(String(50))
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    products: Mapped[list[Product]] = relationship(
        "Product", back_populates="brand", lazy="raise"
    )


class Category(Base):
    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.category_id")
    )
    slug: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Self-referential: remote_side references this table's PK column
    parent: Mapped[Category | None] = relationship(
        "Category",
        back_populates="children",
        remote_side=[category_id],
        foreign_keys=[parent_category_id],
        lazy="raise",
    )
    children: Mapped[list[Category]] = relationship(
        "Category",
        back_populates="parent",
        foreign_keys=[parent_category_id],
        lazy="raise",
    )
    products: Mapped[list[Product]] = relationship(
        "Product", back_populates="category", lazy="raise"
    )


class Attribute(Base):
    __tablename__ = "attributes"

    attribute_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200))

    values: Mapped[list[AttributeValue]] = relationship(
        "AttributeValue", back_populates="attribute", lazy="raise"
    )


class AttributeValue(Base):
    __tablename__ = "attribute_values"

    value_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attribute_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attributes.attribute_id"), nullable=False
    )
    value: Mapped[str] = mapped_column(String(100), nullable=False)

    attribute: Mapped[Attribute] = relationship(
        "Attribute", back_populates="values", lazy="raise"
    )
    variant_attributes: Mapped[list[VariantAttribute]] = relationship(
        "VariantAttribute", back_populates="attribute_value", lazy="raise"
    )


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    brand_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("brands.brand_id")
    )
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.category_id")
    )
    base_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    slug: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str | None] = mapped_column(String(20), default="active")

    brand: Mapped[Brand | None] = relationship(
        "Brand", back_populates="products", lazy="raise"
    )
    category: Mapped[Category | None] = relationship(
        "Category", back_populates="products", lazy="raise"
    )
    variants: Mapped[list[ProductVariant]] = relationship(
        "ProductVariant", back_populates="product", lazy="raise"
    )
    images: Mapped[list[ProductImage]] = relationship(
        "ProductImage", back_populates="product", lazy="raise"
    )
    reviews: Mapped[list[Review]] = relationship(
        "Review", back_populates="product", lazy="raise"
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"

    variant_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.product_id"), nullable=False
    )
    sku: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    stock_qty: Mapped[int | None] = mapped_column(Integer, default=0)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    status: Mapped[str | None] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    product: Mapped[Product] = relationship(
        "Product", back_populates="variants", lazy="raise"
    )
    images: Mapped[list[ProductImage]] = relationship(
        "ProductImage", back_populates="variant", lazy="raise"
    )
    order_items: Mapped[list[OrderItem]] = relationship(
        "OrderItem", back_populates="variant", lazy="raise"
    )
    inventory_logs: Mapped[list[InventoryLog]] = relationship(
        "InventoryLog", back_populates="variant", lazy="raise"
    )
    variant_attributes: Mapped[list[VariantAttribute]] = relationship(
        "VariantAttribute", back_populates="variant", lazy="raise"
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    image_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.product_id"), nullable=False
    )
    variant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("product_variants.variant_id")
    )
    url: Mapped[str | None] = mapped_column(String(500))
    is_primary: Mapped[bool | None] = mapped_column(Boolean, default=False)

    product: Mapped[Product] = relationship(
        "Product", back_populates="images", lazy="raise"
    )
    variant: Mapped[ProductVariant | None] = relationship(
        "ProductVariant", back_populates="images", lazy="raise"
    )


class VariantAttribute(Base):
    """Junction table linking product_variants ↔ attributes ↔ attribute_values."""

    __tablename__ = "variant_attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    variant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("product_variants.variant_id"), nullable=False
    )
    attribute_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attributes.attribute_id"), nullable=False
    )
    value_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attribute_values.value_id"), nullable=False
    )

    variant: Mapped[ProductVariant] = relationship(
        "ProductVariant", back_populates="variant_attributes", lazy="raise"
    )
    attribute: Mapped[Attribute] = relationship("Attribute", lazy="raise")
    attribute_value: Mapped[AttributeValue] = relationship(
        "AttributeValue", back_populates="variant_attributes", lazy="raise"
    )


class InventoryLog(Base):
    __tablename__ = "inventory_log"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    variant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("product_variants.variant_id"), nullable=False
    )
    change_qty: Mapped[int | None] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    variant: Mapped[ProductVariant] = relationship(
        "ProductVariant", back_populates="inventory_logs", lazy="raise"
    )


# ---------------------------------------------------------------------------
# Order tables
# ---------------------------------------------------------------------------

class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    address_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("addresses.address_id")
    )
    # coupon_id has no FK constraint in the DB schema
    coupon_id: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String(20))
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), default=0)
    tax: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), default=0)
    shipping_fee: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), default=0)
    grand_total: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped[User] = relationship("User", back_populates="orders", lazy="raise")
    address: Mapped[Address | None] = relationship(
        "Address", back_populates="orders", lazy="raise"
    )
    items: Mapped[list[OrderItem]] = relationship(
        "OrderItem", back_populates="order", lazy="raise"
    )
    status_history: Mapped[list[OrderStatusHistory]] = relationship(
        "OrderStatusHistory",
        back_populates="order",
        order_by="OrderStatusHistory.changed_at",
        lazy="raise",
    )
    payments: Mapped[list[Payment]] = relationship(
        "Payment", back_populates="order", lazy="raise"
    )
    shipments: Mapped[list[Shipment]] = relationship(
        "Shipment", back_populates="order", lazy="raise"
    )
    refunds: Mapped[list[Refund]] = relationship(
        "Refund", back_populates="order", lazy="raise"
    )
    reviews: Mapped[list[Review]] = relationship(
        "Review", back_populates="order", lazy="raise"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.order_id"), nullable=False
    )
    variant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("product_variants.variant_id"), nullable=False
    )
    quantity: Mapped[int | None] = mapped_column(Integer)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    total_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    order: Mapped[Order] = relationship("Order", back_populates="items", lazy="raise")
    variant: Mapped[ProductVariant] = relationship(
        "ProductVariant", back_populates="order_items", lazy="raise"
    )


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    history_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.order_id"), nullable=False
    )
    status: Mapped[str | None] = mapped_column(String(20))
    note: Mapped[str | None] = mapped_column(String(200))
    changed_at: Mapped[datetime | None] = mapped_column(DateTime)

    order: Mapped[Order] = relationship(
        "Order", back_populates="status_history", lazy="raise"
    )


# ---------------------------------------------------------------------------
# Payment & refund tables
# ---------------------------------------------------------------------------

class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.order_id"), nullable=False
    )
    method: Mapped[str | None] = mapped_column(String(30))
    gateway: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str | None] = mapped_column(String(20))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    gateway_txn_id: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)

    order: Mapped[Order] = relationship(
        "Order", back_populates="payments", lazy="raise"
    )
    refunds: Mapped[list[Refund]] = relationship(
        "Refund", back_populates="payment", lazy="raise"
    )


class Refund(Base):
    __tablename__ = "refunds"

    refund_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("payments.payment_id"), nullable=False
    )
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.order_id"), nullable=False
    )
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    reason: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    payment: Mapped[Payment] = relationship(
        "Payment", back_populates="refunds", lazy="raise"
    )
    order: Mapped[Order] = relationship(
        "Order", back_populates="refunds", lazy="raise"
    )


# ---------------------------------------------------------------------------
# Shipment tables
# ---------------------------------------------------------------------------

class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.order_id"), nullable=False
    )
    carrier: Mapped[str | None] = mapped_column(String(50))
    tracking_number: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str | None] = mapped_column(String(20))
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    shipping_charge: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime)

    order: Mapped[Order] = relationship(
        "Order", back_populates="shipments", lazy="raise"
    )
    tracking_events: Mapped[list[ShipmentTracking]] = relationship(
        "ShipmentTracking",
        back_populates="shipment",
        order_by="ShipmentTracking.event_time",
        lazy="raise",
    )


class ShipmentTracking(Base):
    __tablename__ = "shipment_tracking"

    tracking_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shipment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shipments.shipment_id"), nullable=False
    )
    event_description: Mapped[str | None] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(100))
    event_time: Mapped[datetime | None] = mapped_column(DateTime)

    shipment: Mapped[Shipment] = relationship(
        "Shipment", back_populates="tracking_events", lazy="raise"
    )


# ---------------------------------------------------------------------------
# Review tables
# ---------------------------------------------------------------------------

class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="reviews_rating_check"),
    )

    review_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.product_id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    order_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("orders.order_id")
    )
    rating: Mapped[int | None] = mapped_column(SmallInteger)
    title: Mapped[str | None] = mapped_column(String(200))
    body: Mapped[str | None] = mapped_column(Text)
    is_verified_purchase: Mapped[bool | None] = mapped_column(Boolean, default=False)
    helpful_count: Mapped[int | None] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    product: Mapped[Product] = relationship(
        "Product", back_populates="reviews", lazy="raise"
    )
    user: Mapped[User] = relationship(
        "User", back_populates="reviews", lazy="raise"
    )
    order: Mapped[Order | None] = relationship(
        "Order", back_populates="reviews", lazy="raise"
    )
    images: Mapped[list[ReviewImage]] = relationship(
        "ReviewImage",
        back_populates="review",
        order_by="ReviewImage.sort_order",
        lazy="raise",
    )
    votes: Mapped[list[ReviewVote]] = relationship(
        "ReviewVote", back_populates="review", lazy="raise"
    )


class ReviewImage(Base):
    __tablename__ = "review_images"

    image_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reviews.review_id"), nullable=False
    )
    url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int | None] = mapped_column(Integer, default=1)

    review: Mapped[Review] = relationship(
        "Review", back_populates="images", lazy="raise"
    )


class ReviewVote(Base):
    __tablename__ = "review_votes"

    vote_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reviews.review_id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    is_helpful: Mapped[bool | None] = mapped_column(Boolean)
    voted_at: Mapped[datetime | None] = mapped_column(DateTime)

    review: Mapped[Review] = relationship(
        "Review", back_populates="votes", lazy="raise"
    )
    user: Mapped[User] = relationship(
        "User", back_populates="review_votes", lazy="raise"
    )
