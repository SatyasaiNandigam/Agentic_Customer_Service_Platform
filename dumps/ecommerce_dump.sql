--
-- PostgreSQL database dump
--

\restrict 6BjLOgcBYzomTP7jigNI8p67Q8JLli31SvuFjSNd88bO8MHfANo9ku1YVkLOaTV

-- Dumped from database version 16.12
-- Dumped by pg_dump version 16.12

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: addresses; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.addresses (
    address_id integer NOT NULL,
    user_id integer NOT NULL,
    type character varying(20),
    street_line1 character varying(200),
    landmark character varying(200),
    city character varying(50),
    state character varying(50),
    country character varying(50) DEFAULT 'India'::character varying,
    pincode character varying(10),
    is_default boolean DEFAULT false,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.addresses OWNER TO dev_user;

--
-- Name: addresses_address_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.addresses_address_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.addresses_address_id_seq OWNER TO dev_user;

--
-- Name: addresses_address_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.addresses_address_id_seq OWNED BY public.addresses.address_id;


--
-- Name: attribute_values; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.attribute_values (
    value_id integer NOT NULL,
    attribute_id integer NOT NULL,
    value character varying(100) NOT NULL
);


ALTER TABLE public.attribute_values OWNER TO dev_user;

--
-- Name: attribute_values_value_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.attribute_values_value_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attribute_values_value_id_seq OWNER TO dev_user;

--
-- Name: attribute_values_value_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.attribute_values_value_id_seq OWNED BY public.attribute_values.value_id;


--
-- Name: attributes; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.attributes (
    attribute_id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(200)
);


ALTER TABLE public.attributes OWNER TO dev_user;

--
-- Name: attributes_attribute_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.attributes_attribute_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attributes_attribute_id_seq OWNER TO dev_user;

--
-- Name: attributes_attribute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.attributes_attribute_id_seq OWNED BY public.attributes.attribute_id;


--
-- Name: brands; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.brands (
    brand_id integer NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(100),
    country character varying(50),
    segment character varying(50),
    is_active boolean DEFAULT true,
    created_at timestamp without time zone
);


ALTER TABLE public.brands OWNER TO dev_user;

--
-- Name: brands_brand_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.brands_brand_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.brands_brand_id_seq OWNER TO dev_user;

--
-- Name: brands_brand_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.brands_brand_id_seq OWNED BY public.brands.brand_id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.categories (
    category_id integer NOT NULL,
    name character varying(100) NOT NULL,
    parent_category_id integer,
    slug character varying(100),
    is_active boolean DEFAULT true,
    created_at timestamp without time zone
);


ALTER TABLE public.categories OWNER TO dev_user;

--
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_category_id_seq OWNER TO dev_user;

--
-- Name: categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.categories_category_id_seq OWNED BY public.categories.category_id;


--
-- Name: inventory_log; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.inventory_log (
    log_id integer NOT NULL,
    variant_id integer NOT NULL,
    change_qty integer,
    reason character varying(50),
    created_at timestamp without time zone
);


ALTER TABLE public.inventory_log OWNER TO dev_user;

--
-- Name: inventory_log_log_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.inventory_log_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_log_log_id_seq OWNER TO dev_user;

--
-- Name: inventory_log_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.inventory_log_log_id_seq OWNED BY public.inventory_log.log_id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.order_items (
    item_id integer NOT NULL,
    order_id integer NOT NULL,
    variant_id integer NOT NULL,
    quantity integer,
    unit_price numeric(12,2),
    total_price numeric(12,2)
);


ALTER TABLE public.order_items OWNER TO dev_user;

--
-- Name: order_items_item_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.order_items_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_items_item_id_seq OWNER TO dev_user;

--
-- Name: order_items_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.order_items_item_id_seq OWNED BY public.order_items.item_id;


--
-- Name: order_status_history; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.order_status_history (
    history_id integer NOT NULL,
    order_id integer NOT NULL,
    status character varying(20),
    note character varying(200),
    changed_at timestamp without time zone
);


ALTER TABLE public.order_status_history OWNER TO dev_user;

--
-- Name: order_status_history_history_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.order_status_history_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_status_history_history_id_seq OWNER TO dev_user;

--
-- Name: order_status_history_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.order_status_history_history_id_seq OWNED BY public.order_status_history.history_id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    order_uuid uuid NOT NULL,
    user_id integer NOT NULL,
    address_id integer,
    coupon_id integer,
    status character varying(20),
    subtotal numeric(12,2),
    discount numeric(12,2) DEFAULT 0,
    tax numeric(12,2) DEFAULT 0,
    shipping_fee numeric(12,2) DEFAULT 0,
    grand_total numeric(12,2),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.orders OWNER TO dev_user;

--
-- Name: orders_order_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_order_id_seq OWNER TO dev_user;

--
-- Name: orders_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.orders_order_id_seq OWNED BY public.orders.order_id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.payments (
    payment_id integer NOT NULL,
    order_id integer NOT NULL,
    method character varying(30),
    gateway character varying(50),
    status character varying(20),
    amount numeric(12,2),
    gateway_txn_id character varying(50),
    created_at timestamp without time zone,
    paid_at timestamp without time zone
);


ALTER TABLE public.payments OWNER TO dev_user;

--
-- Name: payments_payment_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.payments_payment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payments_payment_id_seq OWNER TO dev_user;

--
-- Name: payments_payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.payments_payment_id_seq OWNED BY public.payments.payment_id;


--
-- Name: product_images; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.product_images (
    image_id integer NOT NULL,
    product_id integer NOT NULL,
    variant_id integer,
    url character varying(500),
    is_primary boolean DEFAULT false
);


ALTER TABLE public.product_images OWNER TO dev_user;

--
-- Name: product_images_image_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.product_images_image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_images_image_id_seq OWNER TO dev_user;

--
-- Name: product_images_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.product_images_image_id_seq OWNED BY public.product_images.image_id;


--
-- Name: product_variants; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.product_variants (
    variant_id integer NOT NULL,
    product_id integer NOT NULL,
    sku character varying(50) NOT NULL,
    price numeric(12,2),
    stock_qty integer DEFAULT 0,
    weight_kg numeric(6,2),
    status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp without time zone
);


ALTER TABLE public.product_variants OWNER TO dev_user;

--
-- Name: product_variants_variant_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.product_variants_variant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_variants_variant_id_seq OWNER TO dev_user;

--
-- Name: product_variants_variant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.product_variants_variant_id_seq OWNED BY public.product_variants.variant_id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    product_uuid uuid NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    brand_id integer,
    category_id integer,
    base_price numeric(12,2),
    slug character varying(200),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    status character varying(20) DEFAULT 'active'::character varying
);


ALTER TABLE public.products OWNER TO dev_user;

--
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.products_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_product_id_seq OWNER TO dev_user;

--
-- Name: products_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.product_id;


--
-- Name: refunds; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.refunds (
    refund_id integer NOT NULL,
    payment_id integer NOT NULL,
    order_id integer NOT NULL,
    amount numeric(12,2),
    reason character varying(200),
    status character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.refunds OWNER TO dev_user;

--
-- Name: refunds_refund_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.refunds_refund_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.refunds_refund_id_seq OWNER TO dev_user;

--
-- Name: refunds_refund_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.refunds_refund_id_seq OWNED BY public.refunds.refund_id;


--
-- Name: review_images; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.review_images (
    image_id integer NOT NULL,
    review_id integer NOT NULL,
    url character varying(500),
    sort_order integer DEFAULT 1
);


ALTER TABLE public.review_images OWNER TO dev_user;

--
-- Name: review_images_image_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.review_images_image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.review_images_image_id_seq OWNER TO dev_user;

--
-- Name: review_images_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.review_images_image_id_seq OWNED BY public.review_images.image_id;


--
-- Name: review_votes; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.review_votes (
    vote_id integer NOT NULL,
    review_id integer NOT NULL,
    user_id integer NOT NULL,
    is_helpful boolean,
    voted_at timestamp without time zone
);


ALTER TABLE public.review_votes OWNER TO dev_user;

--
-- Name: review_votes_vote_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.review_votes_vote_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.review_votes_vote_id_seq OWNER TO dev_user;

--
-- Name: review_votes_vote_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.review_votes_vote_id_seq OWNED BY public.review_votes.vote_id;


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.reviews (
    review_id integer NOT NULL,
    product_id integer NOT NULL,
    user_id integer NOT NULL,
    order_id integer,
    rating smallint,
    title character varying(200),
    body text,
    is_verified_purchase boolean DEFAULT false,
    helpful_count integer DEFAULT 0,
    created_at timestamp without time zone,
    CONSTRAINT reviews_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE public.reviews OWNER TO dev_user;

--
-- Name: reviews_review_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.reviews_review_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reviews_review_id_seq OWNER TO dev_user;

--
-- Name: reviews_review_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.reviews_review_id_seq OWNED BY public.reviews.review_id;


--
-- Name: shipment_tracking; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.shipment_tracking (
    tracking_id integer NOT NULL,
    shipment_id integer NOT NULL,
    event_description character varying(200),
    location character varying(100),
    event_time timestamp without time zone
);


ALTER TABLE public.shipment_tracking OWNER TO dev_user;

--
-- Name: shipment_tracking_tracking_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.shipment_tracking_tracking_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.shipment_tracking_tracking_id_seq OWNER TO dev_user;

--
-- Name: shipment_tracking_tracking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.shipment_tracking_tracking_id_seq OWNED BY public.shipment_tracking.tracking_id;


--
-- Name: shipments; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.shipments (
    shipment_id integer NOT NULL,
    order_id integer NOT NULL,
    carrier character varying(50),
    tracking_number character varying(50),
    status character varying(20),
    weight_kg numeric(6,2),
    shipping_charge numeric(8,2),
    shipped_at timestamp without time zone,
    delivered_at timestamp without time zone
);


ALTER TABLE public.shipments OWNER TO dev_user;

--
-- Name: shipments_shipment_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.shipments_shipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.shipments_shipment_id_seq OWNER TO dev_user;

--
-- Name: shipments_shipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.shipments_shipment_id_seq OWNED BY public.shipments.shipment_id;


--
-- Name: user_role_mapping; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.user_role_mapping (
    mapping_id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    assigned_at timestamp without time zone
);


ALTER TABLE public.user_role_mapping OWNER TO dev_user;

--
-- Name: user_role_mapping_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.user_role_mapping_mapping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_role_mapping_mapping_id_seq OWNER TO dev_user;

--
-- Name: user_role_mapping_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.user_role_mapping_mapping_id_seq OWNED BY public.user_role_mapping.mapping_id;


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.user_roles (
    role_id integer NOT NULL,
    role_name character varying(50) NOT NULL,
    description character varying(200),
    is_active boolean DEFAULT true
);


ALTER TABLE public.user_roles OWNER TO dev_user;

--
-- Name: user_roles_role_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.user_roles_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_roles_role_id_seq OWNER TO dev_user;

--
-- Name: user_roles_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.user_roles_role_id_seq OWNED BY public.user_roles.role_id;


--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.user_sessions (
    session_id integer NOT NULL,
    session_uuid uuid NOT NULL,
    user_id integer NOT NULL,
    token character varying(255) NOT NULL,
    created_at timestamp without time zone,
    expires_at timestamp without time zone,
    is_active boolean DEFAULT true,
    device character varying(100),
    ip_address character varying(45)
);


ALTER TABLE public.user_sessions OWNER TO dev_user;

--
-- Name: user_sessions_session_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.user_sessions_session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_sessions_session_id_seq OWNER TO dev_user;

--
-- Name: user_sessions_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.user_sessions_session_id_seq OWNED BY public.user_sessions.session_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    user_uuid uuid NOT NULL,
    first_name character varying(50),
    last_name character varying(50),
    full_name character varying(100),
    email character varying(150) NOT NULL,
    password_hash character varying(255),
    phone character varying(20),
    city character varying(50),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_email_verified boolean DEFAULT false,
    status character varying(20) DEFAULT 'active'::character varying
);


ALTER TABLE public.users OWNER TO dev_user;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO dev_user;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: variant_attributes; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.variant_attributes (
    id integer NOT NULL,
    variant_id integer NOT NULL,
    attribute_id integer NOT NULL,
    value_id integer NOT NULL
);


ALTER TABLE public.variant_attributes OWNER TO dev_user;

--
-- Name: variant_attributes_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.variant_attributes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.variant_attributes_id_seq OWNER TO dev_user;

--
-- Name: variant_attributes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.variant_attributes_id_seq OWNED BY public.variant_attributes.id;


--
-- Name: addresses address_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.addresses ALTER COLUMN address_id SET DEFAULT nextval('public.addresses_address_id_seq'::regclass);


--
-- Name: attribute_values value_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.attribute_values ALTER COLUMN value_id SET DEFAULT nextval('public.attribute_values_value_id_seq'::regclass);


--
-- Name: attributes attribute_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.attributes ALTER COLUMN attribute_id SET DEFAULT nextval('public.attributes_attribute_id_seq'::regclass);


--
-- Name: brands brand_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.brands ALTER COLUMN brand_id SET DEFAULT nextval('public.brands_brand_id_seq'::regclass);


--
-- Name: categories category_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.categories ALTER COLUMN category_id SET DEFAULT nextval('public.categories_category_id_seq'::regclass);


--
-- Name: inventory_log log_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.inventory_log ALTER COLUMN log_id SET DEFAULT nextval('public.inventory_log_log_id_seq'::regclass);


--
-- Name: order_items item_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.order_items ALTER COLUMN item_id SET DEFAULT nextval('public.order_items_item_id_seq'::regclass);


--
-- Name: order_status_history history_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.order_status_history ALTER COLUMN history_id SET DEFAULT nextval('public.order_status_history_history_id_seq'::regclass);


--
-- Name: orders order_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.orders ALTER COLUMN order_id SET DEFAULT nextval('public.orders_order_id_seq'::regclass);


--
-- Name: payments payment_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.payments ALTER COLUMN payment_id SET DEFAULT nextval('public.payments_payment_id_seq'::regclass);


--
-- Name: product_images image_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.product_images ALTER COLUMN image_id SET DEFAULT nextval('public.product_images_image_id_seq'::regclass);


--
-- Name: product_variants variant_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.product_variants ALTER COLUMN variant_id SET DEFAULT nextval('public.product_variants_variant_id_seq'::regclass);


--
-- Name: products product_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.products ALTER COLUMN product_id SET DEFAULT nextval('public.products_product_id_seq'::regclass);


--
-- Name: refunds refund_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.refunds ALTER COLUMN refund_id SET DEFAULT nextval('public.refunds_refund_id_seq'::regclass);


--
-- Name: review_images image_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.review_images ALTER COLUMN image_id SET DEFAULT nextval('public.review_images_image_id_seq'::regclass);


--
-- Name: review_votes vote_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.review_votes ALTER COLUMN vote_id SET DEFAULT nextval('public.review_votes_vote_id_seq'::regclass);


--
-- Name: reviews review_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.reviews ALTER COLUMN review_id SET DEFAULT nextval('public.reviews_review_id_seq'::regclass);


--
-- Name: shipment_tracking tracking_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.shipment_tracking ALTER COLUMN tracking_id SET DEFAULT nextval('public.shipment_tracking_tracking_id_seq'::regclass);


--
-- Name: shipments shipment_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.shipments ALTER COLUMN shipment_id SET DEFAULT nextval('public.shipments_shipment_id_seq'::regclass);


--
-- Name: user_role_mapping mapping_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_role_mapping ALTER COLUMN mapping_id SET DEFAULT nextval('public.user_role_mapping_mapping_id_seq'::regclass);


--
-- Name: user_roles role_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_roles ALTER COLUMN role_id SET DEFAULT nextval('public.user_roles_role_id_seq'::regclass);


--
-- Name: user_sessions session_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN session_id SET DEFAULT nextval('public.user_sessions_session_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Name: variant_attributes id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.variant_attributes ALTER COLUMN id SET DEFAULT nextval('public.variant_attributes_id_seq'::regclass);


--
-- Data for Name: addresses; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.addresses (address_id, user_id, type, street_line1, landmark, city, state, country, pincode, is_default, created_at, updated_at) FROM stdin;
1	1	home	Opp. City Mall, Station Road	Near Metro Station	Hyderabad	Telangana	India	500032	t	2025-06-23 12:39:59	2025-12-25 11:30:53
2	1	home	Old No 9 New No 21, TTK Road	NaN	Lucknow	Uttar Pradesh	India	226010	f	2025-11-01 22:05:22	2026-02-07 03:08:48
3	2	home	78 Park Street	Opp. Post Office	Mumbai	Maharashtra	India	400068	t	2025-09-15 00:31:03	2026-02-24 07:07:56
4	3	home	Opp. City Mall, Station Road	NaN	Kolkata	West Bengal	India	700001	t	2025-12-29 10:11:19	2026-01-23 16:51:26
5	4	home	No 34, Anna Salai	Near Metro Station	Hyderabad	Telangana	India	500032	t	2026-01-24 07:38:14	2026-02-03 00:48:28
6	4	other	23 Cantonment Road	NaN	Jaipur	Rajasthan	India	302020	f	2025-03-31 15:09:23	2025-05-09 09:46:30
7	5	other	23 Cantonment Road	Behind SBI Bank	Chandigarh	Punjab	India	160011	t	2026-01-26 00:11:27	2026-01-30 06:26:42
8	5	home	3rd Cross, Koramangala	NaN	Lucknow	Uttar Pradesh	India	226022	f	2025-04-12 08:26:00	2025-07-26 22:56:47
9	6	home	Plot 88, HITEC City	Behind SBI Bank	Coimbatore	Tamil Nadu	India	641045	t	2026-02-28 20:06:04	2026-03-01 15:23:15
10	7	other	Plot 88, HITEC City	NaN	Pune	Maharashtra	India	411057	t	2025-06-06 05:42:44	2025-08-30 08:25:26
11	8	work	Block C, DLF Phase 2	Near Metro Station	Chandigarh	Punjab	India	160011	t	2025-03-15 15:07:39	2025-04-04 21:58:12
12	8	other	Near Bus Stand, Civil Lines	Behind SBI Bank	Surat	Gujarat	India	395001	f	2025-12-22 05:10:49	2026-02-02 05:41:27
13	9	other	Tower 3, Prestige Enclave	Next to Park	Coimbatore	Tamil Nadu	India	641045	t	2025-03-23 17:32:55	2025-12-01 10:03:49
14	10	home	23 Cantonment Road	Behind SBI Bank	Surat	Gujarat	India	395001	t	2025-09-24 06:54:44	2025-10-12 02:50:51
15	11	work	Near Bus Stand, Civil Lines	NaN	Coimbatore	Tamil Nadu	India	641011	t	2025-03-02 06:37:34	2025-03-26 10:21:20
16	12	other	Flat 202, Sunshine Apts	Near Metro Station	Kochi	Kerala	India	682001	t	2025-06-03 04:05:05	2025-07-07 09:51:26
17	12	home	Flat 4B, Highland Park	Next to Park	Coimbatore	Tamil Nadu	India	641018	f	2025-09-02 19:43:13	2025-09-22 20:15:21
18	13	home	Flat 202, Sunshine Apts	Near Metro Station	Hyderabad	Telangana	India	500072	t	2025-05-03 17:30:43	2025-07-06 12:25:16
19	13	home	Flat 202, Sunshine Apts	NaN	Mumbai	Maharashtra	India	400001	f	2025-12-25 21:22:05	2026-01-31 16:53:08
20	13	work	6/2 Baner Road	Next to Park	Chandigarh	Punjab	India	160036	f	2025-09-14 15:54:01	2025-11-05 15:57:52
21	14	work	3rd Cross, Koramangala	Behind SBI Bank	Ahmedabad	Gujarat	India	380058	t	2025-09-28 02:03:42	2025-11-20 17:30:44
22	14	home	22, Linking Road	NaN	Ahmedabad	Gujarat	India	380009	f	2025-09-06 22:36:36	2025-09-20 16:19:46
23	15	home	Sector 62, Noida	Near Metro Station	Bangalore	Karnataka	India	560001	t	2025-09-16 05:13:29	2025-10-25 20:03:57
24	16	home	Plot 88, HITEC City	Next to Park	Pune	Maharashtra	India	411014	t	2025-06-20 05:12:03	2025-12-15 23:02:24
25	16	home	Near Bus Stand, Civil Lines	Next to Park	Jaipur	Rajasthan	India	302020	f	2026-01-24 08:07:06	2026-02-05 12:35:41
26	17	work	Plot 7, Sector 18	Behind SBI Bank	Nagpur	Maharashtra	India	440015	t	2026-02-19 21:57:54	2026-02-22 06:25:16
27	18	other	15 Sarojini Devi Road	NaN	Kochi	Kerala	India	682030	t	2025-08-01 23:12:52	2026-02-13 19:51:40
28	18	work	Old No 9 New No 21, TTK Road	NaN	Pune	Maharashtra	India	411028	f	2026-01-23 13:31:38	2026-02-26 21:08:43
29	19	home	Plot 7, Sector 18	Opp. Post Office	Chennai	Tamil Nadu	India	600001	t	2025-07-19 15:20:52	2025-08-07 16:01:24
30	19	other	No 34, Anna Salai	NaN	Coimbatore	Tamil Nadu	India	641045	f	2025-10-23 00:07:34	2026-02-12 13:59:28
31	20	home	12, MG Road	Opp. Post Office	Nagpur	Maharashtra	India	440015	t	2025-06-15 05:19:42	2025-08-16 17:27:39
32	21	other	Opp. City Mall, Station Road	NaN	Mumbai	Maharashtra	India	400093	t	2025-10-14 08:57:39	2025-12-26 13:28:38
33	21	home	Plot 7, Sector 18	Behind SBI Bank	Coimbatore	Tamil Nadu	India	641011	f	2025-08-25 05:45:44	2025-12-28 21:46:53
34	22	other	12, MG Road	Opp. Post Office	Mumbai	Maharashtra	India	400068	t	2025-09-10 10:36:31	2025-11-28 00:35:40
35	22	work	Old No 9 New No 21, TTK Road	Near Metro Station	Nagpur	Maharashtra	India	440001	f	2025-04-13 13:16:13	2025-04-25 18:33:01
36	23	other	Flat 202, Sunshine Apts	Behind SBI Bank	Mumbai	Maharashtra	India	400051	t	2025-11-02 21:35:29	2025-12-06 18:38:57
37	24	home	Flat 4B, Highland Park	NaN	Delhi	Delhi	India	110001	t	2025-12-10 09:00:49	2026-01-17 01:25:21
38	24	home	Tower 3, Prestige Enclave	Next to Park	Chandigarh	Punjab	India	160001	f	2025-05-20 05:21:56	2025-12-16 12:30:14
39	25	work	Sector 62, Noida	Opp. Post Office	Kolkata	West Bengal	India	700054	t	2025-05-14 17:53:58	2025-11-19 11:50:06
40	25	work	6/2 Baner Road	NaN	Pune	Maharashtra	India	411057	f	2025-12-31 08:07:21	2026-01-19 07:57:09
41	26	other	3rd Cross, Koramangala	Behind SBI Bank	Hyderabad	Telangana	India	500090	t	2025-11-06 21:22:00	2026-01-10 02:36:27
42	27	other	E-7 Arera Colony	NaN	Pune	Maharashtra	India	411014	t	2025-07-17 05:10:09	2025-10-08 00:13:41
43	28	other	B-12 Rajouri Garden	Opp. Post Office	Bangalore	Karnataka	India	560068	t	2026-01-18 20:18:43	2026-01-31 16:56:41
44	29	work	101 Residency Road	Opp. Post Office	Chennai	Tamil Nadu	India	600040	t	2025-11-27 07:08:15	2026-02-26 19:01:00
45	29	other	3rd Cross, Koramangala	Near Metro Station	Ahmedabad	Gujarat	India	380058	f	2025-06-18 09:02:27	2025-10-08 17:14:27
46	30	other	12, MG Road	Next to Park	Coimbatore	Tamil Nadu	India	641011	t	2025-08-16 18:28:49	2026-01-27 19:15:52
47	31	other	3rd Cross, Koramangala	Behind SBI Bank	Surat	Gujarat	India	395009	t	2025-09-01 14:15:11	2025-12-05 18:28:50
48	31	work	Block C, DLF Phase 2	Next to Park	Coimbatore	Tamil Nadu	India	641004	f	2026-02-01 20:20:11	2026-02-28 18:01:49
49	32	other	Plot 88, HITEC City	Behind SBI Bank	Chennai	Tamil Nadu	India	600001	t	2025-06-20 08:48:47	2025-12-07 17:20:57
50	33	home	101 Residency Road	NaN	Surat	Gujarat	India	395010	t	2025-03-31 16:57:18	2025-08-29 12:02:24
51	33	other	Opp. City Mall, Station Road	Behind SBI Bank	Coimbatore	Tamil Nadu	India	641011	f	2025-10-20 03:25:52	2025-11-10 12:14:38
52	34	other	Flat 202, Sunshine Apts	Opp. Post Office	Delhi	Delhi	India	110048	t	2025-05-05 06:36:03	2025-05-23 20:49:10
53	35	home	22, Linking Road	Behind SBI Bank	Kolkata	West Bengal	India	700054	t	2025-12-27 02:21:15	2026-01-09 09:17:36
54	36	work	Shop 5, Commercial Complex	NaN	Chandigarh	Punjab	India	160001	t	2025-04-10 03:50:59	2025-10-25 03:01:41
55	37	home	B-12 Rajouri Garden	Next to Park	Hyderabad	Telangana	India	500090	t	2025-04-12 14:50:41	2025-12-05 21:38:36
56	37	home	Shop 5, Commercial Complex	Near Metro Station	Coimbatore	Tamil Nadu	India	641001	f	2025-03-24 13:31:10	2025-12-31 09:00:28
57	38	other	101 Residency Road	Near Metro Station	Chennai	Tamil Nadu	India	600083	t	2026-02-03 06:57:00	2026-02-12 17:01:16
58	39	other	Tower 3, Prestige Enclave	Near Metro Station	Hyderabad	Telangana	India	500090	t	2025-11-14 10:01:31	2025-12-16 10:19:42
59	39	home	House No 8, Gandhi Colony	Behind SBI Bank	Nagpur	Maharashtra	India	440015	f	2025-07-16 04:37:19	2025-11-11 09:17:45
60	40	other	Old No 9 New No 21, TTK Road	Opp. Post Office	Jaipur	Rajasthan	India	302001	t	2025-07-22 04:16:33	2026-01-12 23:18:56
61	41	other	Near Bus Stand, Civil Lines	Next to Park	Hyderabad	Telangana	India	500001	t	2025-08-23 03:54:36	2026-01-12 08:16:27
62	41	other	Block C, DLF Phase 2	Next to Park	Chandigarh	Punjab	India	160022	f	2025-04-08 08:04:44	2025-08-29 22:27:54
63	42	work	E-7 Arera Colony	NaN	Ahmedabad	Gujarat	India	380009	t	2025-07-01 11:34:02	2025-10-11 18:03:11
64	43	home	Near Bus Stand, Civil Lines	Near Metro Station	Kolkata	West Bengal	India	700054	t	2025-03-19 02:59:18	2025-03-29 12:17:52
65	44	home	Old No 9 New No 21, TTK Road	Next to Park	Hyderabad	Telangana	India	500090	t	2026-01-30 20:46:05	2026-02-04 06:49:26
66	44	home	No 34, Anna Salai	NaN	Chandigarh	Punjab	India	160022	f	2025-09-07 01:36:59	2026-01-23 23:03:04
67	44	work	Plot 88, HITEC City	Opp. Post Office	Hyderabad	Telangana	India	500072	f	2026-02-24 04:11:01	2026-02-28 19:28:40
68	45	other	E-7 Arera Colony	NaN	Kolkata	West Bengal	India	700078	t	2025-09-10 22:22:42	2025-10-16 00:21:12
69	45	home	Block C, DLF Phase 2	Opp. Post Office	Ahmedabad	Gujarat	India	380054	f	2025-03-13 14:02:38	2026-01-24 15:14:54
70	45	home	45 Nehru Nagar	Behind SBI Bank	Mumbai	Maharashtra	India	400012	f	2026-01-08 13:10:01	2026-02-25 04:39:45
71	46	work	101 Residency Road	Next to Park	Jaipur	Rajasthan	India	302001	t	2026-03-01 21:27:31	2026-03-01 23:56:21
72	47	work	101 Residency Road	Next to Park	Mumbai	Maharashtra	India	400012	t	2026-02-04 16:46:40	2026-02-13 14:21:49
73	48	work	House No 8, Gandhi Colony	Behind SBI Bank	Coimbatore	Tamil Nadu	India	641045	t	2026-02-23 14:33:24	2026-02-24 23:57:16
74	49	work	15 Sarojini Devi Road	Near Metro Station	Nagpur	Maharashtra	India	440015	t	2025-05-02 13:02:14	2025-08-23 04:28:15
75	49	work	78 Park Street	Behind SBI Bank	Ahmedabad	Gujarat	India	380009	f	2025-12-08 06:15:18	2026-01-10 06:27:36
76	49	other	House No 8, Gandhi Colony	Next to Park	Surat	Gujarat	India	395001	f	2026-01-29 15:04:50	2026-02-07 16:14:36
77	50	other	Flat 4B, Highland Park	Next to Park	Mumbai	Maharashtra	India	400001	t	2025-11-06 12:22:20	2026-01-20 12:47:57
78	50	home	No 34, Anna Salai	Near Metro Station	Kochi	Kerala	India	682030	f	2026-02-22 09:53:08	2026-02-26 04:00:15
79	51	home	Opp. City Mall, Station Road	NaN	Coimbatore	Tamil Nadu	India	641011	t	2025-08-29 15:43:40	2026-02-21 07:14:46
80	51	other	B-12 Rajouri Garden	Next to Park	Jaipur	Rajasthan	India	302017	f	2025-04-11 14:45:50	2025-05-31 07:39:21
81	52	other	12, MG Road	Near Metro Station	Delhi	Delhi	India	110092	t	2025-04-24 09:30:21	2025-08-22 00:30:51
82	52	work	Shop 5, Commercial Complex	NaN	Delhi	Delhi	India	110048	f	2025-04-21 01:48:36	2025-07-23 07:21:04
83	53	home	Tower 3, Prestige Enclave	Behind SBI Bank	Bangalore	Karnataka	India	560095	t	2025-10-22 08:37:00	2026-01-31 17:15:03
84	53	work	B-12 Rajouri Garden	Next to Park	Kochi	Kerala	India	682030	f	2025-12-03 00:45:23	2026-01-10 14:50:14
85	54	other	No 34, Anna Salai	Opp. Post Office	Hyderabad	Telangana	India	500001	t	2025-08-01 11:41:05	2026-01-14 05:01:47
86	54	home	3rd Cross, Koramangala	NaN	Delhi	Delhi	India	110092	f	2026-02-04 17:58:54	2026-02-22 03:10:03
87	54	other	H No 55, Punjabi Bagh	NaN	Coimbatore	Tamil Nadu	India	641045	f	2025-12-17 18:15:30	2026-01-01 15:20:06
88	55	home	22, Linking Road	NaN	Ahmedabad	Gujarat	India	380009	t	2025-03-26 13:23:15	2025-04-23 09:40:48
89	56	work	Plot 88, HITEC City	Behind SBI Bank	Kochi	Kerala	India	682020	t	2025-04-27 14:01:48	2025-11-17 09:25:35
90	57	work	101 Residency Road	Next to Park	Nagpur	Maharashtra	India	440001	t	2025-08-06 20:13:53	2026-01-10 19:13:42
91	58	home	23 Cantonment Road	Opp. Post Office	Coimbatore	Tamil Nadu	India	641001	t	2025-06-29 22:36:55	2025-07-22 02:52:20
92	59	home	3rd Cross, Koramangala	Next to Park	Chennai	Tamil Nadu	India	600040	t	2025-12-23 05:42:33	2026-02-03 11:54:15
93	59	work	No 34, Anna Salai	Near Metro Station	Nagpur	Maharashtra	India	440034	f	2026-02-21 19:14:39	2026-02-22 03:13:03
94	60	work	Opp. City Mall, Station Road	Near Metro Station	Coimbatore	Tamil Nadu	India	641011	t	2025-06-28 08:34:50	2025-10-14 19:07:16
95	61	work	No 34, Anna Salai	NaN	Coimbatore	Tamil Nadu	India	641001	t	2025-09-02 20:02:53	2025-09-26 10:56:33
96	62	other	Opp. City Mall, Station Road	Near Metro Station	Nagpur	Maharashtra	India	440034	t	2026-02-09 18:23:47	2026-02-27 18:50:34
97	62	work	6/2 Baner Road	Opp. Post Office	Kochi	Kerala	India	682030	f	2025-11-17 06:21:33	2025-12-18 10:48:29
98	63	home	12, MG Road	Next to Park	Pune	Maharashtra	India	411045	t	2025-11-13 14:05:47	2026-01-30 20:05:12
99	63	home	15 Sarojini Devi Road	Near Metro Station	Lucknow	Uttar Pradesh	India	226016	f	2025-03-09 19:53:22	2025-10-02 04:27:33
100	64	work	B-12 Rajouri Garden	Near Metro Station	Pune	Maharashtra	India	411057	t	2025-06-06 20:53:12	2025-11-06 05:52:38
101	64	work	15 Sarojini Devi Road	Next to Park	Ahmedabad	Gujarat	India	380058	f	2025-12-22 00:44:59	2026-02-10 05:55:24
102	65	work	Shop 5, Commercial Complex	Next to Park	Coimbatore	Tamil Nadu	India	641045	t	2025-05-14 22:42:51	2025-05-18 05:22:00
103	65	home	H No 55, Punjabi Bagh	Near Metro Station	Nagpur	Maharashtra	India	440001	f	2025-12-28 10:11:22	2026-02-12 09:13:38
104	66	home	Opp. City Mall, Station Road	Next to Park	Kolkata	West Bengal	India	700054	t	2025-09-30 18:06:18	2025-11-04 07:04:57
105	67	work	Flat 202, Sunshine Apts	Behind SBI Bank	Kochi	Kerala	India	682040	t	2025-10-23 10:21:41	2025-11-04 13:17:30
106	68	work	Flat 202, Sunshine Apts	Opp. Post Office	Pune	Maharashtra	India	411045	t	2025-03-17 15:38:47	2026-01-18 15:41:56
107	69	other	3rd Cross, Koramangala	Next to Park	Nagpur	Maharashtra	India	440015	t	2025-04-23 10:48:21	2026-02-23 04:27:17
108	69	other	Plot 88, HITEC City	NaN	Chandigarh	Punjab	India	160011	f	2026-01-28 00:18:53	2026-02-05 01:49:04
109	70	other	Block C, DLF Phase 2	Near Metro Station	Delhi	Delhi	India	110011	t	2025-11-24 18:41:49	2026-01-31 09:37:52
110	71	home	Plot 88, HITEC City	Near Metro Station	Hyderabad	Telangana	India	500081	t	2026-02-27 03:25:34	2026-03-01 17:14:04
111	72	work	Plot 88, HITEC City	NaN	Chandigarh	Punjab	India	160022	t	2026-02-19 13:22:52	2026-02-25 12:29:25
112	72	other	Near Bus Stand, Civil Lines	Behind SBI Bank	Delhi	Delhi	India	110001	f	2025-05-03 04:37:18	2025-11-04 06:31:25
113	73	home	45 Nehru Nagar	Next to Park	Delhi	Delhi	India	110092	t	2025-04-17 20:53:57	2025-09-06 15:51:09
114	74	home	Plot 7, Sector 18	NaN	Chandigarh	Punjab	India	160022	t	2025-10-25 19:13:35	2025-12-09 00:45:53
115	75	other	3rd Cross, Koramangala	Near Metro Station	Ahmedabad	Gujarat	India	380024	t	2025-06-09 13:08:54	2025-09-15 07:57:51
116	76	other	Near Bus Stand, Civil Lines	Near Metro Station	Kolkata	West Bengal	India	700054	t	2025-11-12 03:17:07	2026-02-08 08:26:04
117	77	home	E-7 Arera Colony	Behind SBI Bank	Delhi	Delhi	India	110011	t	2025-04-12 00:44:53	2025-04-15 01:12:41
118	77	work	12, MG Road	Near Metro Station	Kolkata	West Bengal	India	700078	f	2025-09-29 00:16:24	2025-12-25 17:06:50
119	77	work	B-12 Rajouri Garden	Next to Park	Lucknow	Uttar Pradesh	India	226010	f	2025-09-15 23:54:17	2025-12-09 02:01:25
120	78	other	Tower 3, Prestige Enclave	NaN	Coimbatore	Tamil Nadu	India	641001	t	2025-04-29 19:21:37	2025-07-05 10:58:33
121	79	other	Flat 202, Sunshine Apts	Opp. Post Office	Jaipur	Rajasthan	India	302020	t	2025-10-08 07:20:26	2025-10-23 22:54:20
122	80	work	15 Sarojini Devi Road	NaN	Hyderabad	Telangana	India	500032	t	2025-06-25 19:21:14	2025-07-16 20:44:09
123	80	work	Shop 5, Commercial Complex	Behind SBI Bank	Mumbai	Maharashtra	India	400068	f	2025-05-10 07:36:50	2025-06-19 03:00:49
124	80	other	Flat 4B, Highland Park	NaN	Coimbatore	Tamil Nadu	India	641045	f	2025-05-31 01:35:34	2026-01-30 12:17:33
125	81	home	23 Cantonment Road	Behind SBI Bank	Kolkata	West Bengal	India	700078	t	2025-03-30 10:53:38	2025-08-21 14:40:18
126	82	other	Flat 4B, Highland Park	Near Metro Station	Mumbai	Maharashtra	India	400001	t	2025-03-19 19:23:07	2025-05-27 06:53:07
127	83	work	15 Sarojini Devi Road	Opp. Post Office	Mumbai	Maharashtra	India	400001	t	2025-07-28 13:43:36	2025-11-21 18:38:00
128	83	home	E-7 Arera Colony	Behind SBI Bank	Surat	Gujarat	India	395004	f	2025-12-08 03:45:14	2026-01-24 15:56:48
129	84	home	78 Park Street	Near Metro Station	Ahmedabad	Gujarat	India	380058	t	2026-01-26 09:33:36	2026-02-18 01:17:17
130	85	home	Sector 62, Noida	Next to Park	Surat	Gujarat	India	395001	t	2025-03-26 08:25:17	2026-02-21 03:05:07
131	86	other	Near Bus Stand, Civil Lines	Behind SBI Bank	Coimbatore	Tamil Nadu	India	641011	t	2025-07-21 01:32:14	2025-09-10 15:38:27
132	87	work	Block C, DLF Phase 2	NaN	Ahmedabad	Gujarat	India	380058	t	2025-09-21 18:44:26	2026-01-06 04:10:37
133	87	other	House No 8, Gandhi Colony	Behind SBI Bank	Pune	Maharashtra	India	411045	f	2026-02-16 09:49:50	2026-02-19 11:12:02
134	88	work	Opp. City Mall, Station Road	Opp. Post Office	Hyderabad	Telangana	India	500072	t	2025-09-06 18:40:18	2025-12-27 07:58:31
135	88	other	Tower 3, Prestige Enclave	Near Metro Station	Kolkata	West Bengal	India	700091	f	2025-04-08 20:48:57	2026-02-04 16:45:27
136	89	other	Tower 3, Prestige Enclave	Opp. Post Office	Pune	Maharashtra	India	411014	t	2026-02-26 09:25:31	2026-02-28 23:44:09
137	89	other	6/2 Baner Road	Near Metro Station	Surat	Gujarat	India	395010	f	2025-09-03 09:01:26	2025-10-05 05:33:15
138	90	home	23 Cantonment Road	Behind SBI Bank	Nagpur	Maharashtra	India	440010	t	2025-05-30 10:42:06	2025-11-27 17:44:37
139	91	home	Shop 5, Commercial Complex	NaN	Pune	Maharashtra	India	411028	t	2025-07-21 19:42:33	2025-09-17 00:54:08
140	91	work	101 Residency Road	Near Metro Station	Surat	Gujarat	India	395009	f	2025-11-09 00:52:39	2026-01-13 09:15:12
141	91	other	12, MG Road	Behind SBI Bank	Lucknow	Uttar Pradesh	India	226022	f	2025-12-26 04:55:56	2026-01-20 06:51:40
142	92	home	B-12 Rajouri Garden	Near Metro Station	Ahmedabad	Gujarat	India	380054	t	2025-05-19 01:03:15	2025-10-26 20:29:45
143	92	other	No 34, Anna Salai	Next to Park	Chandigarh	Punjab	India	160001	f	2026-01-30 10:18:11	2026-02-01 06:20:18
144	93	work	Flat 202, Sunshine Apts	Opp. Post Office	Mumbai	Maharashtra	India	400051	t	2025-04-01 12:44:15	2025-09-10 11:24:46
145	93	home	Old No 9 New No 21, TTK Road	Opp. Post Office	Delhi	Delhi	India	110048	f	2025-11-18 08:01:30	2026-01-11 00:33:12
146	93	work	Sector 62, Noida	Behind SBI Bank	Kolkata	West Bengal	India	700001	f	2026-01-20 21:22:25	2026-02-08 14:07:50
147	94	other	Flat 202, Sunshine Apts	Behind SBI Bank	Lucknow	Uttar Pradesh	India	226016	t	2026-02-18 22:20:25	2026-02-19 05:02:27
148	94	home	Shop 5, Commercial Complex	Behind SBI Bank	Lucknow	Uttar Pradesh	India	226022	f	2026-02-10 16:19:11	2026-02-20 20:17:57
149	94	other	Plot 7, Sector 18	Behind SBI Bank	Nagpur	Maharashtra	India	440022	f	2025-10-02 11:48:43	2026-01-07 21:21:12
150	95	home	23 Cantonment Road	Near Metro Station	Kolkata	West Bengal	India	700001	t	2025-09-15 16:06:51	2025-10-09 17:54:57
\.


--
-- Data for Name: attribute_values; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.attribute_values (value_id, attribute_id, value) FROM stdin;
1	1	Black
2	1	White
3	1	Blue
4	1	Red
5	1	Green
6	1	Grey
7	1	Navy
8	1	Brown
9	2	XS
10	2	S
11	2	M
12	2	L
13	2	XL
14	2	XXL
15	2	6
16	2	7
17	2	8
18	2	9
19	2	10
20	3	64GB
21	3	128GB
22	3	256GB
23	3	512GB
24	3	1TB
25	4	4GB
26	4	6GB
27	4	8GB
28	4	16GB
29	4	32GB
30	5	Cotton
31	5	Polyester
32	5	Leather
33	5	Metal
34	5	Plastic
35	5	Wood
36	6	Light
37	6	Medium
38	6	Heavy
\.


--
-- Data for Name: attributes; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.attributes (attribute_id, name, description) FROM stdin;
1	Color	Product color
2	Size	Clothing/shoe size
3	Storage	Storage capacity in GB
4	RAM	RAM in GB
5	Material	Primary material
6	Weight	Weight class
\.


--
-- Data for Name: brands; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.brands (brand_id, name, slug, country, segment, is_active, created_at) FROM stdin;
1	Samsung	samsung	South Korea	Electronics	t	2025-09-08 00:22:23
2	Apple	apple	USA	Electronics	t	2025-05-18 11:10:39
3	Sony	sony	Japan	Electronics	t	2025-08-12 17:57:46
4	OnePlus	oneplus	China	Electronics	t	2025-12-07 11:37:50
5	Boat	boat	India	Audio	t	2025-10-26 03:35:16
6	Noise	noise	India	Wearables	t	2025-10-16 12:21:08
7	Nike	nike	USA	Fashion	t	2025-05-25 03:43:07
8	Adidas	adidas	Germany	Fashion	t	2026-01-03 19:41:52
9	Puma	puma	Germany	Fashion	t	2026-02-15 07:14:34
10	Levi's	levis	USA	Fashion	t	2026-01-02 03:38:19
11	Philips	philips	Netherlands	Home & Kitchen	t	2025-07-25 05:44:39
12	Prestige	prestige	India	Kitchen	t	2026-01-15 08:37:42
13	Ikea	ikea	Sweden	Furniture	t	2025-07-30 17:27:52
14	Bajaj	bajaj	India	Appliances	t	2026-01-30 13:41:21
15	Himalaya	himalaya	India	Beauty	t	2025-11-22 00:08:18
16	Mamaearth	mamaearth	India	Beauty	t	2025-05-23 13:29:25
17	Decathlon	decathlon	France	Sports	t	2025-04-30 03:19:12
18	Cosco	cosco	India	Sports	t	2025-08-28 05:20:09
19	Wildcraft	wildcraft	India	Outdoor	t	2025-11-13 12:56:20
20	HP	hp	USA	Electronics	t	2025-05-10 12:24:35
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.categories (category_id, name, parent_category_id, slug, is_active, created_at) FROM stdin;
1	Electronics	\N	electronics	t	2025-08-05 21:20:54
2	Fashion	\N	fashion	t	2025-07-27 20:52:18
3	Home & Kitchen	\N	home---kitchen	t	2025-05-18 16:50:17
4	Beauty & Personal	\N	beauty---personal	t	2025-10-20 19:10:38
5	Sports & Fitness	\N	sports---fitness	t	2025-05-10 10:33:30
6	Mobile Phones	1	mobile-phones	t	2025-05-30 10:12:15
7	Laptops & Computers	1	laptops---computers	t	2025-06-06 11:32:51
8	Audio & Headphones	1	audio---headphones	t	2025-04-22 17:55:40
9	Cameras	1	cameras	t	2025-12-22 02:34:15
10	Men's Clothing	2	mens-clothing	t	2025-04-04 14:58:11
11	Women's Clothing	2	womens-clothing	t	2025-06-07 12:53:49
12	Footwear	2	footwear	t	2025-12-10 03:03:41
13	Watches	2	watches	t	2025-07-28 18:26:55
14	Kitchen Appliances	3	kitchen-appliances	t	2025-09-24 03:31:55
15	Furniture	3	furniture	t	2025-11-22 18:13:07
16	Bedding & Pillows	3	bedding---pillows	t	2025-11-29 01:01:23
17	Skincare	4	skincare	t	2025-09-27 04:23:14
18	Haircare	4	haircare	t	2025-04-05 21:20:05
19	Gym Equipment	5	gym-equipment	t	2026-03-01 10:18:22
20	Outdoor Sports	5	outdoor-sports	t	2025-10-30 07:21:09
\.


--
-- Data for Name: inventory_log; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.inventory_log (log_id, variant_id, change_qty, reason, created_at) FROM stdin;
1	22	-1	correction	2026-02-02 21:46:04
2	44	-13	sale	2025-07-26 10:18:16
3	35	198	return	2026-01-04 02:13:46
4	23	191	restock	2025-10-12 22:53:50
5	86	178	initial_stock	2025-03-26 00:00:06
6	20	88	initial_stock	2025-07-17 07:13:56
7	61	25	restock	2025-04-24 03:54:46
8	37	-23	correction	2025-10-12 14:15:03
9	34	90	restock	2026-02-24 12:54:26
10	31	73	initial_stock	2025-06-08 09:10:56
11	56	163	initial_stock	2025-04-03 14:09:01
12	72	10	restock	2025-11-04 10:08:58
13	76	-13	correction	2025-07-03 00:03:13
14	63	102	return	2025-04-25 06:24:16
15	79	64	restock	2026-02-26 01:32:42
16	55	-30	damage_write_off	2025-06-19 01:07:53
17	54	124	restock	2025-05-29 01:09:55
18	97	-34	sale	2025-03-16 12:47:25
19	92	97	restock	2025-08-30 09:28:05
20	95	35	restock	2025-10-03 00:54:24
21	91	-3	correction	2025-05-08 20:40:32
22	5	79	restock	2026-01-30 16:18:21
23	56	28	initial_stock	2025-04-04 19:37:48
24	22	73	initial_stock	2025-04-05 00:35:24
25	16	27	initial_stock	2025-04-01 16:03:54
26	3	-18	correction	2026-01-05 14:21:02
27	48	-12	sale	2025-08-21 20:37:39
28	50	-4	damage_write_off	2025-08-15 08:32:38
29	24	60	return	2025-09-17 01:34:09
30	60	-5	sale	2025-07-17 15:55:53
31	23	-20	correction	2025-11-13 01:44:54
32	40	-3	damage_write_off	2025-11-04 16:35:31
33	28	-13	correction	2025-03-19 07:07:20
34	66	-21	damage_write_off	2025-12-17 19:23:26
35	84	166	restock	2025-08-30 10:24:09
36	15	-36	sale	2025-08-10 16:24:57
37	96	41	restock	2025-03-15 02:04:20
38	21	40	return	2026-01-03 14:41:21
39	97	61	restock	2025-04-21 15:08:16
40	22	-28	correction	2026-01-23 10:55:58
41	10	-17	damage_write_off	2025-04-02 04:47:47
42	31	142	restock	2025-12-25 05:08:27
43	69	183	initial_stock	2025-10-27 15:08:35
44	57	-39	correction	2025-08-25 05:19:11
45	80	-48	sale	2025-10-12 05:24:12
46	33	-29	damage_write_off	2025-04-21 10:50:29
47	72	-30	correction	2025-09-26 15:45:45
48	45	72	return	2026-01-03 22:25:02
49	66	-7	damage_write_off	2026-02-06 07:15:31
50	18	174	initial_stock	2025-03-29 00:36:53
51	22	-16	damage_write_off	2026-02-08 04:12:38
52	68	144	restock	2025-10-15 09:53:15
53	54	-19	correction	2026-01-06 07:30:04
54	3	-25	sale	2025-05-13 03:39:38
55	86	-39	sale	2025-03-22 07:00:57
56	10	-13	damage_write_off	2025-12-19 15:46:28
57	66	-17	correction	2025-07-20 07:01:38
58	17	171	restock	2025-12-30 03:48:01
59	62	-37	sale	2026-01-26 18:17:53
60	60	97	restock	2025-07-24 16:35:32
61	87	63	restock	2025-11-16 10:44:00
62	36	-15	sale	2025-10-25 08:29:49
63	65	-7	damage_write_off	2025-12-11 02:51:14
64	62	-37	correction	2025-04-19 14:35:54
65	61	-42	sale	2025-06-09 20:39:02
66	59	65	restock	2026-02-24 07:36:17
67	80	-49	sale	2025-03-13 08:26:00
68	67	81	return	2025-03-08 20:04:29
69	47	106	initial_stock	2025-12-19 13:34:51
70	17	-35	damage_write_off	2025-06-15 16:47:52
71	72	45	initial_stock	2025-07-31 02:55:52
72	98	-37	damage_write_off	2025-10-23 05:34:48
73	24	-24	damage_write_off	2025-05-16 14:43:36
74	20	141	initial_stock	2025-04-10 23:38:27
75	62	165	initial_stock	2026-02-06 15:51:56
76	56	-43	sale	2025-09-14 09:15:21
77	52	-34	damage_write_off	2025-12-15 03:18:32
78	63	166	initial_stock	2025-04-03 13:23:57
79	59	-38	damage_write_off	2025-10-19 16:21:50
80	48	98	restock	2025-07-05 18:20:27
81	14	-44	correction	2025-03-11 14:53:31
82	83	51	initial_stock	2025-12-16 22:41:43
83	32	-19	correction	2026-02-13 04:29:39
84	73	68	restock	2025-10-07 21:32:11
85	62	89	initial_stock	2025-05-25 19:58:49
86	49	-30	correction	2026-01-21 18:40:56
87	33	-4	correction	2025-05-09 12:45:34
88	27	-6	damage_write_off	2025-04-03 11:10:51
89	49	146	restock	2025-08-18 16:40:57
90	89	-10	damage_write_off	2025-05-22 06:44:52
91	73	86	return	2026-01-10 10:45:06
92	14	27	initial_stock	2026-01-17 15:46:52
93	43	46	return	2025-05-31 02:47:42
94	65	27	initial_stock	2025-08-04 02:40:11
95	32	-19	damage_write_off	2025-09-01 18:34:27
96	26	-47	damage_write_off	2025-07-08 05:56:47
97	76	160	return	2025-10-22 14:30:39
98	42	-11	correction	2025-08-23 05:12:19
99	18	-15	correction	2025-04-26 01:08:18
100	53	133	return	2025-06-08 02:42:41
101	48	-25	correction	2025-07-16 04:16:51
102	10	-33	damage_write_off	2025-03-19 21:23:11
103	28	143	return	2025-11-20 07:10:55
104	69	123	initial_stock	2025-11-20 07:21:40
105	55	-4	damage_write_off	2025-11-18 22:38:08
106	28	123	initial_stock	2025-10-17 05:44:24
107	81	132	return	2025-03-09 04:11:10
108	25	29	restock	2025-06-06 09:06:02
109	69	-25	correction	2025-05-07 13:34:54
110	18	-15	correction	2025-07-01 14:26:59
111	50	-48	correction	2025-11-12 16:30:15
112	46	-5	correction	2025-10-15 03:23:12
113	99	-41	damage_write_off	2025-09-04 02:55:56
114	5	115	restock	2025-10-03 19:51:36
115	52	-9	correction	2025-03-05 22:21:07
116	41	-21	damage_write_off	2025-05-16 17:01:35
117	35	-8	sale	2025-06-05 18:17:49
118	61	-30	sale	2025-07-23 10:33:39
119	80	183	return	2025-12-14 16:15:21
120	21	28	initial_stock	2026-01-15 22:05:38
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.order_items (item_id, order_id, variant_id, quantity, unit_price, total_price) FROM stdin;
1	1	66	3	6999.00	20997.00
2	1	32	1	29999.00	29999.00
3	1	36	2	1999.00	3998.00
4	2	61	3	8999.00	26997.00
5	2	51	4	1799.00	7196.00
6	3	32	2	29999.00	59998.00
7	3	99	3	8999.00	26997.00
8	3	24	4	499.00	1996.00
9	3	64	1	74999.00	74999.00
10	4	24	4	499.00	1996.00
11	5	54	4	3499.00	13996.00
12	5	49	2	2499.00	4998.00
13	6	57	4	12999.00	51996.00
14	7	83	1	2999.00	2999.00
15	7	62	3	14999.00	44997.00
16	7	7	3	3499.00	10497.00
17	7	73	2	2999.00	5998.00
18	8	68	4	2999.00	11996.00
19	8	82	3	14999.00	44997.00
20	9	49	1	2499.00	2499.00
21	10	9	1	5499.00	5499.00
22	11	23	2	29999.00	59998.00
23	11	75	3	999.00	2997.00
24	11	84	4	42999.00	171996.00
25	12	58	4	1999.00	7996.00
26	12	44	1	3499.00	3499.00
27	13	72	3	3999.00	11997.00
28	13	9	2	5499.00	10998.00
29	14	42	3	1299.00	3897.00
30	15	94	1	1799.00	1799.00
31	15	24	4	499.00	1996.00
32	15	78	2	12999.00	25998.00
33	16	5	4	999.00	3996.00
34	17	15	3	6999.00	20997.00
35	17	64	4	74999.00	299996.00
36	17	76	1	74999.00	74999.00
37	17	44	4	3499.00	13996.00
38	18	88	3	2499.00	7497.00
39	19	31	2	999.00	1998.00
40	20	54	2	3499.00	6998.00
41	21	11	3	42999.00	128997.00
42	22	72	1	3999.00	3999.00
43	22	79	4	14999.00	59996.00
44	22	95	4	2999.00	11996.00
45	22	100	3	3999.00	11997.00
46	23	64	1	74999.00	74999.00
47	23	62	1	14999.00	14999.00
48	23	2	3	1999.00	5997.00
49	24	98	1	5499.00	5499.00
50	24	41	4	499.00	1996.00
51	24	21	4	799.00	3196.00
52	25	79	4	14999.00	59996.00
53	26	39	4	3499.00	13996.00
54	26	90	4	42999.00	171996.00
55	26	88	2	2499.00	4998.00
56	26	67	2	999.00	1998.00
57	27	4	2	3499.00	6998.00
58	27	98	2	5499.00	10998.00
59	28	2	3	1999.00	5997.00
60	29	86	3	1299.00	3897.00
61	30	18	2	42999.00	85998.00
62	30	59	1	3499.00	3499.00
63	30	61	2	8999.00	17998.00
64	31	91	3	8999.00	26997.00
65	32	28	2	799.00	1598.00
66	32	39	3	3499.00	10497.00
67	32	48	3	1999.00	5997.00
68	33	88	4	2499.00	9996.00
69	34	36	1	1999.00	1999.00
70	34	47	1	74999.00	74999.00
71	34	84	3	42999.00	128997.00
72	34	7	3	3499.00	10497.00
73	35	67	3	999.00	2997.00
74	35	40	3	3999.00	11997.00
75	36	60	3	1499.00	4497.00
76	36	64	3	74999.00	224997.00
77	36	88	4	2499.00	9996.00
78	37	52	2	1799.00	3598.00
79	38	66	4	6999.00	27996.00
80	39	39	1	3499.00	3499.00
81	40	24	2	499.00	998.00
82	40	35	2	2499.00	4998.00
83	41	26	4	12999.00	51996.00
84	42	10	3	14999.00	44997.00
85	43	66	1	6999.00	6999.00
86	44	88	1	2499.00	2499.00
87	45	24	2	499.00	998.00
88	45	60	3	1499.00	4497.00
89	46	62	4	14999.00	59996.00
90	46	21	1	799.00	799.00
91	47	34	2	1999.00	3998.00
92	47	72	1	3999.00	3999.00
93	48	19	1	799.00	799.00
94	48	27	4	2499.00	9996.00
95	49	59	4	3499.00	13996.00
96	49	70	4	2999.00	11996.00
97	49	85	4	5499.00	21996.00
98	50	14	2	29999.00	59998.00
99	51	100	2	3999.00	7998.00
100	51	26	2	12999.00	25998.00
101	52	53	1	2499.00	2499.00
102	52	94	3	1799.00	5397.00
103	53	37	1	8999.00	8999.00
104	53	31	3	999.00	2997.00
105	53	100	4	3999.00	15996.00
106	54	44	3	3499.00	10497.00
107	54	22	2	2499.00	4998.00
108	54	90	4	42999.00	171996.00
109	55	6	2	1799.00	3598.00
110	56	74	1	1499.00	1499.00
111	57	98	2	5499.00	10998.00
112	57	92	3	14999.00	44997.00
113	58	74	4	1499.00	5996.00
114	58	48	3	1999.00	5997.00
115	58	26	4	12999.00	51996.00
116	59	49	2	2499.00	4998.00
117	60	14	1	29999.00	29999.00
118	60	36	4	1999.00	7996.00
119	60	32	2	29999.00	59998.00
120	61	54	2	3499.00	6998.00
121	61	2	1	1999.00	1999.00
122	61	79	1	14999.00	14999.00
123	62	58	2	1999.00	3998.00
124	63	100	2	3999.00	7998.00
125	63	39	1	3499.00	3499.00
126	63	31	3	999.00	2997.00
127	64	46	1	5499.00	5499.00
128	65	12	1	6999.00	6999.00
129	65	34	2	1999.00	3998.00
130	66	4	3	3499.00	10497.00
131	67	49	3	2499.00	7497.00
132	67	34	2	1999.00	3998.00
133	67	35	4	2499.00	9996.00
134	68	1	1	999.00	999.00
135	68	62	1	14999.00	14999.00
136	69	46	2	5499.00	10998.00
137	70	78	1	12999.00	12999.00
138	71	88	4	2499.00	9996.00
139	72	59	2	3499.00	6998.00
140	73	94	2	1799.00	3598.00
141	74	4	1	3499.00	3499.00
142	75	7	3	3499.00	10497.00
143	76	82	3	14999.00	44997.00
144	76	32	1	29999.00	29999.00
145	77	50	2	12999.00	25998.00
146	77	62	1	14999.00	14999.00
147	78	6	1	1799.00	1799.00
148	78	25	3	55999.00	167997.00
149	79	90	2	42999.00	85998.00
150	79	15	4	6999.00	27996.00
151	79	17	4	8999.00	35996.00
152	80	14	2	29999.00	59998.00
153	80	18	4	42999.00	171996.00
154	80	62	4	14999.00	59996.00
155	80	42	2	1299.00	2598.00
156	81	23	4	29999.00	119996.00
157	81	74	2	1499.00	2998.00
158	81	21	1	799.00	799.00
159	81	50	4	12999.00	51996.00
160	82	74	1	1499.00	1499.00
161	83	93	1	55999.00	55999.00
162	83	33	1	8999.00	8999.00
163	84	49	2	2499.00	4998.00
164	85	24	4	499.00	1996.00
165	85	19	3	799.00	2397.00
166	86	60	1	1499.00	1499.00
167	86	41	1	499.00	499.00
168	86	64	3	74999.00	224997.00
169	86	51	4	1799.00	7196.00
170	87	100	2	3999.00	7998.00
171	87	44	2	3499.00	6998.00
172	87	69	3	799.00	2397.00
173	88	76	1	74999.00	74999.00
174	88	62	1	14999.00	14999.00
175	89	44	2	3499.00	6998.00
176	89	41	1	499.00	499.00
177	90	21	2	799.00	1598.00
178	91	31	1	999.00	999.00
179	92	34	3	1999.00	5997.00
180	92	1	4	999.00	3996.00
181	92	70	3	2999.00	8997.00
182	93	84	1	42999.00	42999.00
183	93	66	2	6999.00	13998.00
184	94	39	2	3499.00	6998.00
185	95	54	4	3499.00	13996.00
186	95	84	1	42999.00	42999.00
187	95	39	2	3499.00	6998.00
188	96	55	1	42999.00	42999.00
189	96	62	4	14999.00	59996.00
190	97	67	3	999.00	2997.00
191	97	43	4	8999.00	35996.00
192	98	63	3	55999.00	167997.00
193	98	92	4	14999.00	59996.00
194	99	16	1	3999.00	3999.00
195	99	70	2	2999.00	5998.00
196	100	37	1	8999.00	8999.00
197	100	32	3	29999.00	89997.00
198	100	74	2	1499.00	2998.00
199	100	61	1	8999.00	8999.00
200	101	72	1	3999.00	3999.00
201	101	87	3	2999.00	8997.00
202	102	99	4	8999.00	35996.00
203	103	62	3	14999.00	44997.00
204	103	72	4	3999.00	15996.00
205	104	43	4	8999.00	35996.00
206	104	59	1	3499.00	3499.00
207	105	59	3	3499.00	10497.00
208	106	90	3	42999.00	128997.00
209	107	30	2	2499.00	4998.00
210	107	95	3	2999.00	8997.00
211	108	30	2	2499.00	4998.00
212	109	55	1	42999.00	42999.00
213	109	49	1	2499.00	2499.00
214	109	5	3	999.00	2997.00
215	110	83	2	2999.00	5998.00
216	111	2	3	1999.00	5997.00
217	111	61	3	8999.00	26997.00
218	111	9	1	5499.00	5499.00
219	111	21	2	799.00	1598.00
220	112	97	1	2499.00	2499.00
221	112	30	4	2499.00	9996.00
222	112	27	3	2499.00	7497.00
223	113	75	2	999.00	1998.00
224	113	84	4	42999.00	171996.00
225	113	63	2	55999.00	111998.00
226	114	2	2	1999.00	3998.00
227	114	36	4	1999.00	7996.00
228	114	26	4	12999.00	51996.00
229	115	20	3	2999.00	8997.00
230	115	90	2	42999.00	85998.00
231	115	51	2	1799.00	3598.00
232	115	75	3	999.00	2997.00
233	116	6	4	1799.00	7196.00
234	116	49	1	2499.00	2499.00
235	116	87	2	2999.00	5998.00
236	117	62	1	14999.00	14999.00
237	117	31	2	999.00	1998.00
238	117	29	1	6999.00	6999.00
239	118	52	4	1799.00	7196.00
240	119	68	2	2999.00	5998.00
241	119	26	1	12999.00	12999.00
242	120	65	3	1299.00	3897.00
243	121	19	2	799.00	1598.00
244	122	15	4	6999.00	27996.00
245	122	18	4	42999.00	171996.00
246	122	22	3	2499.00	7497.00
247	122	70	3	2999.00	8997.00
248	123	75	3	999.00	2997.00
249	123	43	1	8999.00	8999.00
250	123	40	3	3999.00	11997.00
251	124	34	4	1999.00	7996.00
252	125	47	3	74999.00	224997.00
253	126	32	3	29999.00	89997.00
254	127	92	4	14999.00	59996.00
255	128	68	2	2999.00	5998.00
256	128	17	2	8999.00	17998.00
257	129	89	3	6999.00	20997.00
258	129	91	2	8999.00	17998.00
259	130	27	2	2499.00	4998.00
260	131	79	2	14999.00	29998.00
261	131	73	4	2999.00	11996.00
262	131	36	2	1999.00	3998.00
263	131	49	4	2499.00	9996.00
264	132	32	2	29999.00	59998.00
265	133	50	4	12999.00	51996.00
266	134	69	3	799.00	2397.00
267	134	36	3	1999.00	5997.00
268	135	91	4	8999.00	35996.00
269	135	65	4	1299.00	5196.00
270	136	61	2	8999.00	17998.00
271	137	34	4	1999.00	7996.00
272	138	15	2	6999.00	13998.00
273	138	34	4	1999.00	7996.00
274	139	54	4	3499.00	13996.00
275	140	77	1	8999.00	8999.00
276	140	27	4	2499.00	9996.00
277	140	85	2	5499.00	10998.00
278	141	91	2	8999.00	17998.00
279	142	28	1	799.00	799.00
280	143	4	3	3499.00	10497.00
281	143	74	1	1499.00	1499.00
282	144	66	1	6999.00	6999.00
283	145	93	2	55999.00	111998.00
284	146	73	3	2999.00	8997.00
285	146	78	1	12999.00	12999.00
286	146	62	2	14999.00	29998.00
287	147	71	4	3499.00	13996.00
288	148	93	1	55999.00	55999.00
289	148	86	1	1299.00	1299.00
290	148	44	1	3499.00	3499.00
291	149	21	2	799.00	1598.00
292	149	27	2	2499.00	4998.00
293	150	77	2	8999.00	17998.00
294	150	59	4	3499.00	13996.00
295	151	63	3	55999.00	167997.00
296	151	37	4	8999.00	35996.00
297	151	25	1	55999.00	55999.00
298	151	100	2	3999.00	7998.00
299	152	11	1	42999.00	42999.00
300	153	12	2	6999.00	13998.00
301	154	4	2	3499.00	6998.00
302	155	44	4	3499.00	13996.00
303	155	59	3	3499.00	10497.00
304	155	33	1	8999.00	8999.00
305	155	15	1	6999.00	6999.00
306	156	66	1	6999.00	6999.00
307	157	67	2	999.00	1998.00
308	158	58	2	1999.00	3998.00
309	158	29	4	6999.00	27996.00
310	158	95	1	2999.00	2999.00
311	159	67	4	999.00	3996.00
312	159	29	4	6999.00	27996.00
313	159	37	1	8999.00	8999.00
314	159	91	2	8999.00	17998.00
315	160	88	2	2499.00	4998.00
316	161	100	4	3999.00	15996.00
317	161	62	4	14999.00	59996.00
318	162	12	2	6999.00	13998.00
319	163	39	3	3499.00	10497.00
320	164	65	3	1299.00	3897.00
321	164	78	4	12999.00	51996.00
322	164	34	3	1999.00	5997.00
323	164	22	4	2499.00	9996.00
324	165	55	3	42999.00	128997.00
325	165	1	2	999.00	1998.00
326	165	5	3	999.00	2997.00
327	165	21	1	799.00	799.00
328	166	19	4	799.00	3196.00
329	166	92	4	14999.00	59996.00
330	167	58	3	1999.00	5997.00
331	167	90	4	42999.00	171996.00
332	168	1	2	999.00	1998.00
333	169	23	3	29999.00	89997.00
334	170	62	4	14999.00	59996.00
335	171	80	2	14999.00	29998.00
336	172	78	4	12999.00	51996.00
337	173	31	3	999.00	2997.00
338	173	97	4	2499.00	9996.00
339	173	4	1	3499.00	3499.00
340	174	51	1	1799.00	1799.00
341	175	76	3	74999.00	224997.00
342	176	73	1	2999.00	2999.00
343	177	66	1	6999.00	6999.00
344	178	40	3	3999.00	11997.00
345	178	17	3	8999.00	26997.00
346	179	34	3	1999.00	5997.00
347	179	97	1	2499.00	2499.00
348	179	65	4	1299.00	5196.00
349	180	29	2	6999.00	13998.00
350	180	32	4	29999.00	119996.00
351	181	71	2	3499.00	6998.00
352	182	97	4	2499.00	9996.00
353	182	7	2	3499.00	6998.00
354	182	59	1	3499.00	3499.00
355	183	46	4	5499.00	21996.00
356	183	51	4	1799.00	7196.00
357	183	73	2	2999.00	5998.00
358	184	23	3	29999.00	89997.00
359	185	22	1	2499.00	2499.00
360	186	76	3	74999.00	224997.00
361	186	58	1	1999.00	1999.00
362	187	33	2	8999.00	17998.00
363	187	66	1	6999.00	6999.00
364	187	9	1	5499.00	5499.00
365	188	87	4	2999.00	11996.00
366	188	72	4	3999.00	15996.00
367	189	12	4	6999.00	27996.00
368	190	2	4	1999.00	7996.00
369	191	62	4	14999.00	59996.00
370	191	76	4	74999.00	299996.00
371	191	31	3	999.00	2997.00
372	191	75	4	999.00	3996.00
373	192	74	2	1499.00	2998.00
374	192	5	1	999.00	999.00
375	192	40	1	3999.00	3999.00
376	193	77	4	8999.00	35996.00
377	193	7	3	3499.00	10497.00
378	194	75	4	999.00	3996.00
379	194	56	2	1799.00	3598.00
380	195	93	2	55999.00	111998.00
381	195	72	1	3999.00	3999.00
382	195	89	2	6999.00	13998.00
383	196	97	3	2499.00	7497.00
384	197	70	4	2999.00	11996.00
385	197	40	1	3999.00	3999.00
386	197	81	1	999.00	999.00
387	197	57	3	12999.00	38997.00
388	198	95	4	2999.00	11996.00
389	198	52	3	1799.00	5397.00
390	198	74	3	1499.00	4497.00
391	198	42	3	1299.00	3897.00
392	199	95	3	2999.00	8997.00
393	200	69	4	799.00	3196.00
394	68	21	1	799.00	799.00
395	57	65	2	1299.00	2598.00
396	197	76	2	74999.00	149998.00
397	97	76	1	74999.00	74999.00
398	164	89	2	6999.00	13998.00
399	39	37	2	8999.00	17998.00
400	195	97	2	2499.00	4998.00
\.


--
-- Data for Name: order_status_history; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.order_status_history (history_id, order_id, status, note, changed_at) FROM stdin;
1	1	pending	Order placed, awaiting confirmation	2025-12-04 08:42:10
2	2	pending	Order placed, awaiting confirmation	2025-08-06 18:13:45
3	2	cancelled	Order cancelled by customer	2025-08-07 08:13:45
4	3	pending	Order placed, awaiting confirmation	2025-11-28 16:54:47
5	3	confirmed	Payment confirmed	2025-11-29 06:54:47
6	3	processing	Preparing for shipment	2025-11-29 07:54:47
7	3	shipped	Handed over to courier	2025-11-29 17:54:47
8	3	delivered	Delivered to customer	2025-11-29 18:54:47
9	4	pending	Order placed, awaiting confirmation	2025-10-19 16:48:36
10	4	confirmed	Payment confirmed	2025-10-20 02:48:36
11	4	processing	Preparing for shipment	2025-10-20 23:48:36
12	4	shipped	Handed over to courier	2025-10-21 02:48:36
13	4	delivered	Delivered to customer	2025-10-21 11:48:36
14	5	pending	Order placed, awaiting confirmation	2025-08-13 11:34:59
15	5	confirmed	Payment confirmed	2025-08-14 06:34:59
16	5	processing	Preparing for shipment	2025-08-14 17:34:59
17	5	shipped	Handed over to courier	2025-08-15 01:34:59
18	5	delivered	Delivered to customer	2025-08-15 17:34:59
19	5	returned	Return request accepted	2025-08-16 02:34:59
20	6	pending	Order placed, awaiting confirmation	2025-09-03 17:20:49
21	6	confirmed	Payment confirmed	2025-09-04 12:20:49
22	6	processing	Preparing for shipment	2025-09-04 14:20:49
23	6	shipped	Handed over to courier	2025-09-05 00:20:49
24	6	delivered	Delivered to customer	2025-09-05 09:20:49
25	7	pending	Order placed, awaiting confirmation	2025-08-15 05:48:58
26	7	confirmed	Payment confirmed	2025-08-16 03:48:58
27	7	processing	Preparing for shipment	2025-08-16 11:48:58
28	7	shipped	Handed over to courier	2025-08-17 05:48:58
29	8	pending	Order placed, awaiting confirmation	2025-03-12 12:43:19
30	8	confirmed	Payment confirmed	2025-03-13 02:43:19
31	8	processing	Preparing for shipment	2025-03-13 10:43:19
32	8	shipped	Handed over to courier	2025-03-13 17:43:19
33	8	delivered	Delivered to customer	2025-03-14 14:43:19
34	9	pending	Order placed, awaiting confirmation	2025-11-08 06:28:24
35	10	pending	Order placed, awaiting confirmation	2025-04-03 04:18:56
36	10	confirmed	Payment confirmed	2025-04-03 19:18:56
37	10	processing	Preparing for shipment	2025-04-04 18:18:56
38	10	shipped	Handed over to courier	2025-04-05 06:18:56
39	10	delivered	Delivered to customer	2025-04-05 11:18:56
40	11	pending	Order placed, awaiting confirmation	2025-04-23 18:59:44
41	11	confirmed	Payment confirmed	2025-04-24 15:59:44
42	11	processing	Preparing for shipment	2025-04-25 10:59:44
43	11	shipped	Handed over to courier	2025-04-26 08:59:44
44	12	pending	Order placed, awaiting confirmation	2025-03-27 00:52:48
45	12	confirmed	Payment confirmed	2025-03-28 00:52:48
46	12	processing	Preparing for shipment	2025-03-28 03:52:48
47	12	shipped	Handed over to courier	2025-03-28 19:52:48
48	12	delivered	Delivered to customer	2025-03-29 06:52:48
49	13	pending	Order placed, awaiting confirmation	2025-10-21 10:31:11
50	13	confirmed	Payment confirmed	2025-10-22 08:31:11
51	13	processing	Preparing for shipment	2025-10-23 06:31:11
52	13	shipped	Handed over to courier	2025-10-23 21:31:11
53	13	delivered	Delivered to customer	2025-10-24 07:31:11
54	14	pending	Order placed, awaiting confirmation	2026-02-02 05:00:09
55	14	cancelled	Order cancelled by customer	2026-02-02 13:00:09
56	15	pending	Order placed, awaiting confirmation	2025-11-20 04:54:51
57	15	confirmed	Payment confirmed	2025-11-20 05:54:51
58	16	pending	Order placed, awaiting confirmation	2026-01-07 21:45:41
59	17	pending	Order placed, awaiting confirmation	2026-01-13 12:06:17
60	17	confirmed	Payment confirmed	2026-01-13 18:06:17
61	17	processing	Preparing for shipment	2026-01-13 21:06:17
62	17	shipped	Handed over to courier	2026-01-14 08:06:17
63	17	delivered	Delivered to customer	2026-01-14 11:06:17
64	18	pending	Order placed, awaiting confirmation	2025-07-10 19:50:25
65	18	confirmed	Payment confirmed	2025-07-11 15:50:25
66	19	pending	Order placed, awaiting confirmation	2025-10-17 10:44:19
67	19	confirmed	Payment confirmed	2025-10-18 02:44:19
68	19	processing	Preparing for shipment	2025-10-18 21:44:19
69	19	shipped	Handed over to courier	2025-10-19 00:44:19
70	19	delivered	Delivered to customer	2025-10-19 19:44:19
71	20	pending	Order placed, awaiting confirmation	2025-08-26 11:28:25
72	20	confirmed	Payment confirmed	2025-08-26 22:28:25
73	20	processing	Preparing for shipment	2025-08-27 02:28:25
74	20	shipped	Handed over to courier	2025-08-27 19:28:25
75	20	delivered	Delivered to customer	2025-08-28 09:28:25
76	21	pending	Order placed, awaiting confirmation	2026-01-28 02:22:09
77	21	confirmed	Payment confirmed	2026-01-28 17:22:09
78	21	processing	Preparing for shipment	2026-01-29 00:22:09
79	21	shipped	Handed over to courier	2026-01-29 10:22:09
80	21	delivered	Delivered to customer	2026-01-30 03:22:09
81	22	pending	Order placed, awaiting confirmation	2025-07-28 21:30:39
82	23	pending	Order placed, awaiting confirmation	2026-02-28 03:59:07
83	23	confirmed	Payment confirmed	2026-02-28 15:59:07
84	23	processing	Preparing for shipment	2026-03-01 15:59:07
85	23	shipped	Handed over to courier	2026-03-02 00:00:00
86	23	delivered	Delivered to customer	2026-03-02 00:00:00
87	24	pending	Order placed, awaiting confirmation	2025-10-17 02:33:49
88	25	pending	Order placed, awaiting confirmation	2025-07-22 21:45:06
89	25	confirmed	Payment confirmed	2025-07-23 01:45:06
90	25	processing	Preparing for shipment	2025-07-24 00:45:06
91	25	shipped	Handed over to courier	2025-07-24 12:45:06
92	25	delivered	Delivered to customer	2025-07-25 01:45:06
93	26	pending	Order placed, awaiting confirmation	2025-07-19 00:44:46
94	26	confirmed	Payment confirmed	2025-07-19 07:44:46
95	26	processing	Preparing for shipment	2025-07-19 15:44:46
96	26	shipped	Handed over to courier	2025-07-20 04:44:46
97	26	delivered	Delivered to customer	2025-07-20 15:44:46
98	27	pending	Order placed, awaiting confirmation	2025-06-26 09:34:37
99	27	confirmed	Payment confirmed	2025-06-27 01:34:37
100	27	processing	Preparing for shipment	2025-06-27 07:34:37
101	27	shipped	Handed over to courier	2025-06-27 23:34:37
102	28	pending	Order placed, awaiting confirmation	2025-07-14 16:32:00
103	28	confirmed	Payment confirmed	2025-07-15 11:32:00
104	28	processing	Preparing for shipment	2025-07-15 17:32:00
105	28	shipped	Handed over to courier	2025-07-15 19:32:00
106	29	pending	Order placed, awaiting confirmation	2025-09-20 02:00:57
107	29	confirmed	Payment confirmed	2025-09-20 12:00:57
108	30	pending	Order placed, awaiting confirmation	2025-08-13 00:39:44
109	30	confirmed	Payment confirmed	2025-08-13 09:39:44
110	30	processing	Preparing for shipment	2025-08-13 19:39:44
111	30	shipped	Handed over to courier	2025-08-14 07:39:44
112	31	pending	Order placed, awaiting confirmation	2025-04-16 19:39:07
113	31	confirmed	Payment confirmed	2025-04-17 07:39:07
114	31	processing	Preparing for shipment	2025-04-18 06:39:07
115	31	shipped	Handed over to courier	2025-04-18 19:39:07
116	32	pending	Order placed, awaiting confirmation	2025-12-07 22:40:18
117	32	confirmed	Payment confirmed	2025-12-08 19:40:18
118	32	processing	Preparing for shipment	2025-12-09 09:40:18
119	32	shipped	Handed over to courier	2025-12-10 07:40:18
120	32	delivered	Delivered to customer	2025-12-10 18:40:18
121	33	pending	Order placed, awaiting confirmation	2025-12-22 13:08:12
122	33	confirmed	Payment confirmed	2025-12-23 00:08:12
123	33	processing	Preparing for shipment	2025-12-23 15:08:12
124	34	pending	Order placed, awaiting confirmation	2026-02-21 02:16:32
125	34	confirmed	Payment confirmed	2026-02-21 21:16:32
126	34	processing	Preparing for shipment	2026-02-22 20:16:32
127	34	shipped	Handed over to courier	2026-02-23 04:16:32
128	34	delivered	Delivered to customer	2026-02-23 09:16:32
129	35	pending	Order placed, awaiting confirmation	2025-10-18 06:19:02
130	35	confirmed	Payment confirmed	2025-10-18 09:19:02
131	35	processing	Preparing for shipment	2025-10-19 04:19:02
132	35	shipped	Handed over to courier	2025-10-19 20:19:02
133	36	pending	Order placed, awaiting confirmation	2025-12-25 08:46:18
134	36	confirmed	Payment confirmed	2025-12-25 22:46:18
135	36	processing	Preparing for shipment	2025-12-26 07:46:18
136	36	shipped	Handed over to courier	2025-12-26 08:46:18
137	37	pending	Order placed, awaiting confirmation	2025-08-26 21:12:42
138	37	confirmed	Payment confirmed	2025-08-26 23:12:42
139	37	processing	Preparing for shipment	2025-08-27 06:12:42
140	37	shipped	Handed over to courier	2025-08-28 03:12:42
141	37	delivered	Delivered to customer	2025-08-28 23:12:42
142	38	pending	Order placed, awaiting confirmation	2025-05-18 10:27:44
143	38	confirmed	Payment confirmed	2025-05-18 21:27:44
144	39	pending	Order placed, awaiting confirmation	2026-01-03 21:46:15
145	39	confirmed	Payment confirmed	2026-01-04 09:46:15
146	39	processing	Preparing for shipment	2026-01-05 06:46:15
147	39	shipped	Handed over to courier	2026-01-05 22:46:15
148	39	delivered	Delivered to customer	2026-01-06 20:46:15
149	40	pending	Order placed, awaiting confirmation	2025-05-22 10:39:01
150	40	confirmed	Payment confirmed	2025-05-23 01:39:01
151	40	processing	Preparing for shipment	2025-05-23 06:39:01
152	40	shipped	Handed over to courier	2025-05-24 00:39:01
153	40	delivered	Delivered to customer	2025-05-24 09:39:01
154	41	pending	Order placed, awaiting confirmation	2025-07-07 16:55:15
155	41	confirmed	Payment confirmed	2025-07-08 01:55:15
156	41	processing	Preparing for shipment	2025-07-08 11:55:15
157	42	pending	Order placed, awaiting confirmation	2025-10-31 01:34:45
158	42	confirmed	Payment confirmed	2025-10-31 23:34:45
159	42	processing	Preparing for shipment	2025-11-01 12:34:45
160	43	pending	Order placed, awaiting confirmation	2025-08-08 15:49:51
161	43	confirmed	Payment confirmed	2025-08-09 01:49:51
162	43	processing	Preparing for shipment	2025-08-09 08:49:51
163	43	shipped	Handed over to courier	2025-08-09 17:49:51
164	43	delivered	Delivered to customer	2025-08-09 18:49:51
165	44	pending	Order placed, awaiting confirmation	2025-05-02 17:08:04
166	44	confirmed	Payment confirmed	2025-05-03 08:08:04
167	44	processing	Preparing for shipment	2025-05-03 17:08:04
168	44	shipped	Handed over to courier	2025-05-04 09:08:04
169	45	pending	Order placed, awaiting confirmation	2025-08-22 15:22:03
170	45	confirmed	Payment confirmed	2025-08-22 20:22:03
171	45	processing	Preparing for shipment	2025-08-23 17:22:03
172	46	pending	Order placed, awaiting confirmation	2025-05-18 12:32:35
173	46	confirmed	Payment confirmed	2025-05-19 05:32:35
174	46	processing	Preparing for shipment	2025-05-19 22:32:35
175	46	shipped	Handed over to courier	2025-05-20 07:32:35
176	46	delivered	Delivered to customer	2025-05-20 08:32:35
177	47	pending	Order placed, awaiting confirmation	2025-05-22 09:05:55
178	47	confirmed	Payment confirmed	2025-05-22 14:05:55
179	47	processing	Preparing for shipment	2025-05-23 14:05:55
180	47	shipped	Handed over to courier	2025-05-24 02:05:55
181	47	delivered	Delivered to customer	2025-05-25 01:05:55
182	48	pending	Order placed, awaiting confirmation	2025-04-13 01:07:38
183	48	confirmed	Payment confirmed	2025-04-13 18:07:38
184	48	processing	Preparing for shipment	2025-04-14 09:07:38
185	48	shipped	Handed over to courier	2025-04-14 12:07:38
186	48	delivered	Delivered to customer	2025-04-14 22:07:38
187	49	pending	Order placed, awaiting confirmation	2026-01-02 04:04:01
188	49	confirmed	Payment confirmed	2026-01-03 04:04:01
189	49	processing	Preparing for shipment	2026-01-03 19:04:01
190	50	pending	Order placed, awaiting confirmation	2025-06-01 09:27:46
191	50	confirmed	Payment confirmed	2025-06-01 21:27:46
192	50	processing	Preparing for shipment	2025-06-02 01:27:46
193	50	shipped	Handed over to courier	2025-06-02 07:27:46
194	50	delivered	Delivered to customer	2025-06-02 11:27:46
195	51	pending	Order placed, awaiting confirmation	2026-01-01 10:10:31
196	51	confirmed	Payment confirmed	2026-01-01 11:10:31
197	51	processing	Preparing for shipment	2026-01-01 13:10:31
198	51	shipped	Handed over to courier	2026-01-02 01:10:31
199	51	delivered	Delivered to customer	2026-01-02 18:10:31
200	51	returned	Return request accepted	2026-01-03 16:10:31
201	52	pending	Order placed, awaiting confirmation	2025-12-03 09:01:00
202	52	confirmed	Payment confirmed	2025-12-04 05:01:00
203	52	processing	Preparing for shipment	2025-12-04 10:01:00
204	52	shipped	Handed over to courier	2025-12-05 07:01:00
205	52	delivered	Delivered to customer	2025-12-05 19:01:00
206	53	pending	Order placed, awaiting confirmation	2025-08-26 07:42:59
207	53	confirmed	Payment confirmed	2025-08-26 12:42:59
208	53	processing	Preparing for shipment	2025-08-27 11:42:59
209	53	shipped	Handed over to courier	2025-08-28 01:42:59
210	54	pending	Order placed, awaiting confirmation	2025-05-02 05:19:38
211	54	confirmed	Payment confirmed	2025-05-03 00:19:38
212	55	pending	Order placed, awaiting confirmation	2025-11-22 06:03:37
213	55	confirmed	Payment confirmed	2025-11-23 00:03:37
214	55	processing	Preparing for shipment	2025-11-23 04:03:37
215	56	pending	Order placed, awaiting confirmation	2025-07-20 02:29:53
216	56	confirmed	Payment confirmed	2025-07-20 04:29:53
217	56	processing	Preparing for shipment	2025-07-20 09:29:53
218	56	shipped	Handed over to courier	2025-07-21 09:29:53
219	56	delivered	Delivered to customer	2025-07-22 08:29:53
220	57	pending	Order placed, awaiting confirmation	2026-01-01 05:38:57
221	57	confirmed	Payment confirmed	2026-01-01 07:38:57
222	57	processing	Preparing for shipment	2026-01-02 06:38:57
223	57	shipped	Handed over to courier	2026-01-02 10:38:57
224	58	pending	Order placed, awaiting confirmation	2025-04-26 00:45:29
225	58	confirmed	Payment confirmed	2025-04-26 03:45:29
226	58	processing	Preparing for shipment	2025-04-26 08:45:29
227	58	shipped	Handed over to courier	2025-04-26 11:45:29
228	58	delivered	Delivered to customer	2025-04-27 07:45:29
229	59	pending	Order placed, awaiting confirmation	2025-05-04 06:43:35
230	59	confirmed	Payment confirmed	2025-05-04 07:43:35
231	59	processing	Preparing for shipment	2025-05-05 07:43:35
232	59	shipped	Handed over to courier	2025-05-06 05:43:35
233	59	delivered	Delivered to customer	2025-05-07 04:43:35
234	60	pending	Order placed, awaiting confirmation	2025-04-28 13:25:18
235	60	confirmed	Payment confirmed	2025-04-29 10:25:18
236	60	processing	Preparing for shipment	2025-04-29 22:25:18
237	60	shipped	Handed over to courier	2025-04-30 01:25:18
238	60	delivered	Delivered to customer	2025-04-30 08:25:18
239	61	pending	Order placed, awaiting confirmation	2026-02-05 14:02:17
240	61	confirmed	Payment confirmed	2026-02-05 20:02:17
241	61	processing	Preparing for shipment	2026-02-06 06:02:17
242	61	shipped	Handed over to courier	2026-02-06 14:02:17
243	61	delivered	Delivered to customer	2026-02-07 06:02:17
244	62	pending	Order placed, awaiting confirmation	2025-07-04 19:56:11
245	62	confirmed	Payment confirmed	2025-07-05 00:56:11
246	62	processing	Preparing for shipment	2025-07-05 10:56:11
247	63	pending	Order placed, awaiting confirmation	2025-10-03 21:43:36
248	63	cancelled	Order cancelled by customer	2025-10-04 06:43:36
249	64	pending	Order placed, awaiting confirmation	2025-09-19 04:16:09
250	64	confirmed	Payment confirmed	2025-09-20 02:16:09
251	64	processing	Preparing for shipment	2025-09-20 05:16:09
252	64	shipped	Handed over to courier	2025-09-20 08:16:09
253	64	delivered	Delivered to customer	2025-09-20 15:16:09
254	65	pending	Order placed, awaiting confirmation	2025-10-02 00:42:36
255	65	confirmed	Payment confirmed	2025-10-02 08:42:36
256	65	processing	Preparing for shipment	2025-10-02 12:42:36
257	65	shipped	Handed over to courier	2025-10-02 23:42:36
258	65	delivered	Delivered to customer	2025-10-03 07:42:36
259	66	pending	Order placed, awaiting confirmation	2025-12-31 12:17:46
260	66	confirmed	Payment confirmed	2025-12-31 14:17:46
261	66	processing	Preparing for shipment	2026-01-01 07:17:46
262	66	shipped	Handed over to courier	2026-01-02 02:17:46
263	67	pending	Order placed, awaiting confirmation	2025-11-07 16:11:03
264	67	confirmed	Payment confirmed	2025-11-08 01:11:03
265	67	processing	Preparing for shipment	2025-11-08 11:11:03
266	68	pending	Order placed, awaiting confirmation	2025-10-10 09:32:28
267	68	confirmed	Payment confirmed	2025-10-11 00:32:28
268	68	processing	Preparing for shipment	2025-10-11 14:32:28
269	69	pending	Order placed, awaiting confirmation	2025-11-11 19:43:27
270	69	confirmed	Payment confirmed	2025-11-12 16:43:27
271	69	processing	Preparing for shipment	2025-11-13 12:43:27
272	70	pending	Order placed, awaiting confirmation	2025-06-17 18:18:39
273	70	confirmed	Payment confirmed	2025-06-18 01:18:39
274	70	processing	Preparing for shipment	2025-06-18 21:18:39
275	70	shipped	Handed over to courier	2025-06-19 06:18:39
276	70	delivered	Delivered to customer	2025-06-19 10:18:39
277	71	pending	Order placed, awaiting confirmation	2025-03-18 22:16:45
278	71	confirmed	Payment confirmed	2025-03-19 14:16:45
279	72	pending	Order placed, awaiting confirmation	2025-03-12 12:25:53
280	72	cancelled	Order cancelled by customer	2025-03-12 17:25:53
281	73	pending	Order placed, awaiting confirmation	2026-01-03 15:43:33
282	73	confirmed	Payment confirmed	2026-01-03 20:43:33
283	74	pending	Order placed, awaiting confirmation	2025-09-15 17:41:50
284	74	cancelled	Order cancelled by customer	2025-09-16 12:41:50
285	75	pending	Order placed, awaiting confirmation	2025-10-29 07:55:15
286	75	cancelled	Order cancelled by customer	2025-10-29 14:55:15
287	76	pending	Order placed, awaiting confirmation	2025-03-19 21:05:45
288	76	cancelled	Order cancelled by customer	2025-03-20 06:05:45
289	77	pending	Order placed, awaiting confirmation	2025-04-25 18:26:01
290	77	confirmed	Payment confirmed	2025-04-26 08:26:01
291	77	processing	Preparing for shipment	2025-04-26 16:26:01
292	77	shipped	Handed over to courier	2025-04-26 21:26:01
293	77	delivered	Delivered to customer	2025-04-27 05:26:01
294	78	pending	Order placed, awaiting confirmation	2025-06-13 03:55:36
295	78	confirmed	Payment confirmed	2025-06-13 08:55:36
296	78	processing	Preparing for shipment	2025-06-14 07:55:36
297	78	shipped	Handed over to courier	2025-06-14 15:55:36
298	78	delivered	Delivered to customer	2025-06-15 10:55:36
299	79	pending	Order placed, awaiting confirmation	2025-06-03 21:01:01
300	79	confirmed	Payment confirmed	2025-06-04 13:01:01
301	79	processing	Preparing for shipment	2025-06-05 09:01:01
302	80	pending	Order placed, awaiting confirmation	2025-07-20 15:29:08
303	81	pending	Order placed, awaiting confirmation	2025-08-07 17:58:04
304	81	cancelled	Order cancelled by customer	2025-08-08 17:58:04
305	82	pending	Order placed, awaiting confirmation	2025-05-29 17:43:24
306	82	confirmed	Payment confirmed	2025-05-30 08:43:24
307	82	processing	Preparing for shipment	2025-05-31 04:43:24
308	82	shipped	Handed over to courier	2025-05-31 15:43:24
309	82	delivered	Delivered to customer	2025-05-31 20:43:24
310	83	pending	Order placed, awaiting confirmation	2025-11-05 12:43:08
311	83	confirmed	Payment confirmed	2025-11-06 06:43:08
312	83	processing	Preparing for shipment	2025-11-07 00:43:08
313	84	pending	Order placed, awaiting confirmation	2025-09-12 06:21:23
314	84	confirmed	Payment confirmed	2025-09-13 00:21:23
315	84	processing	Preparing for shipment	2025-09-13 18:21:23
316	84	shipped	Handed over to courier	2025-09-13 23:21:23
317	84	delivered	Delivered to customer	2025-09-14 12:21:23
318	85	pending	Order placed, awaiting confirmation	2025-09-04 13:20:07
319	85	confirmed	Payment confirmed	2025-09-05 07:20:07
320	85	processing	Preparing for shipment	2025-09-06 04:20:07
321	85	shipped	Handed over to courier	2025-09-06 16:20:07
322	85	delivered	Delivered to customer	2025-09-07 14:20:07
323	86	pending	Order placed, awaiting confirmation	2025-06-01 14:49:13
324	86	confirmed	Payment confirmed	2025-06-02 00:49:13
325	86	processing	Preparing for shipment	2025-06-02 16:49:13
326	86	shipped	Handed over to courier	2025-06-02 23:49:13
327	86	delivered	Delivered to customer	2025-06-03 13:49:13
328	87	pending	Order placed, awaiting confirmation	2026-02-25 07:20:53
329	87	cancelled	Order cancelled by customer	2026-02-26 01:20:53
330	88	pending	Order placed, awaiting confirmation	2025-04-30 03:40:40
331	88	confirmed	Payment confirmed	2025-04-30 08:40:40
332	88	processing	Preparing for shipment	2025-05-01 06:40:40
333	88	shipped	Handed over to courier	2025-05-01 16:40:40
334	89	pending	Order placed, awaiting confirmation	2025-10-24 01:09:29
335	89	confirmed	Payment confirmed	2025-10-24 16:09:29
336	89	processing	Preparing for shipment	2025-10-25 01:09:29
337	89	shipped	Handed over to courier	2025-10-25 08:09:29
338	89	delivered	Delivered to customer	2025-10-26 01:09:29
339	90	pending	Order placed, awaiting confirmation	2025-12-06 11:53:41
340	90	cancelled	Order cancelled by customer	2025-12-07 02:53:41
341	91	pending	Order placed, awaiting confirmation	2025-11-28 17:47:10
342	91	confirmed	Payment confirmed	2025-11-29 04:47:10
343	91	processing	Preparing for shipment	2025-11-29 16:47:10
344	91	shipped	Handed over to courier	2025-11-29 21:47:10
345	91	delivered	Delivered to customer	2025-11-30 14:47:10
346	92	pending	Order placed, awaiting confirmation	2025-07-10 09:42:24
347	92	confirmed	Payment confirmed	2025-07-11 02:42:24
348	92	processing	Preparing for shipment	2025-07-11 17:42:24
349	92	shipped	Handed over to courier	2025-07-12 09:42:24
350	92	delivered	Delivered to customer	2025-07-12 23:42:24
351	93	pending	Order placed, awaiting confirmation	2025-12-14 19:26:42
352	93	confirmed	Payment confirmed	2025-12-14 21:26:42
353	93	processing	Preparing for shipment	2025-12-15 20:26:42
354	93	shipped	Handed over to courier	2025-12-16 06:26:42
355	93	delivered	Delivered to customer	2025-12-17 00:26:42
356	93	returned	Return request accepted	2025-12-17 13:26:42
357	94	pending	Order placed, awaiting confirmation	2025-03-18 18:11:58
358	94	confirmed	Payment confirmed	2025-03-18 23:11:58
359	94	processing	Preparing for shipment	2025-03-19 07:11:58
360	95	pending	Order placed, awaiting confirmation	2025-07-03 15:48:56
361	95	confirmed	Payment confirmed	2025-07-03 19:48:56
362	95	processing	Preparing for shipment	2025-07-03 23:48:56
363	95	shipped	Handed over to courier	2025-07-04 01:48:56
364	95	delivered	Delivered to customer	2025-07-04 05:48:56
365	96	pending	Order placed, awaiting confirmation	2025-09-21 19:17:22
366	96	confirmed	Payment confirmed	2025-09-22 04:17:22
367	96	processing	Preparing for shipment	2025-09-22 05:17:22
368	96	shipped	Handed over to courier	2025-09-22 16:17:22
369	97	pending	Order placed, awaiting confirmation	2026-01-09 00:18:56
370	98	pending	Order placed, awaiting confirmation	2025-08-10 13:35:44
371	98	cancelled	Order cancelled by customer	2025-08-11 08:35:44
372	99	pending	Order placed, awaiting confirmation	2025-08-09 03:53:39
373	99	confirmed	Payment confirmed	2025-08-09 08:53:39
374	99	processing	Preparing for shipment	2025-08-10 08:53:39
375	100	pending	Order placed, awaiting confirmation	2025-05-25 22:50:04
376	100	confirmed	Payment confirmed	2025-05-26 18:50:04
377	100	processing	Preparing for shipment	2025-05-27 12:50:04
378	100	shipped	Handed over to courier	2025-05-28 11:50:04
379	100	delivered	Delivered to customer	2025-05-29 11:50:04
380	101	pending	Order placed, awaiting confirmation	2025-08-06 04:18:21
381	101	confirmed	Payment confirmed	2025-08-06 05:18:21
382	101	processing	Preparing for shipment	2025-08-06 14:18:21
383	101	shipped	Handed over to courier	2025-08-07 14:18:21
384	102	pending	Order placed, awaiting confirmation	2025-06-24 20:10:39
385	102	confirmed	Payment confirmed	2025-06-25 16:10:39
386	102	processing	Preparing for shipment	2025-06-26 01:10:39
387	102	shipped	Handed over to courier	2025-06-26 08:10:39
388	102	delivered	Delivered to customer	2025-06-26 21:10:39
389	103	pending	Order placed, awaiting confirmation	2025-05-17 02:39:34
390	103	confirmed	Payment confirmed	2025-05-17 03:39:34
391	104	pending	Order placed, awaiting confirmation	2025-10-28 09:07:37
392	104	confirmed	Payment confirmed	2025-10-28 12:07:37
393	104	processing	Preparing for shipment	2025-10-29 05:07:37
394	104	shipped	Handed over to courier	2025-10-29 12:07:37
395	104	delivered	Delivered to customer	2025-10-29 20:07:37
396	105	pending	Order placed, awaiting confirmation	2025-10-15 15:04:39
397	105	confirmed	Payment confirmed	2025-10-16 12:04:39
398	105	processing	Preparing for shipment	2025-10-16 18:04:39
399	105	shipped	Handed over to courier	2025-10-16 22:04:39
400	105	delivered	Delivered to customer	2025-10-17 06:04:39
401	106	pending	Order placed, awaiting confirmation	2026-01-20 18:08:04
402	106	confirmed	Payment confirmed	2026-01-20 21:08:04
403	106	processing	Preparing for shipment	2026-01-21 01:08:04
404	107	pending	Order placed, awaiting confirmation	2025-06-25 19:36:59
405	107	confirmed	Payment confirmed	2025-06-25 22:36:59
406	108	pending	Order placed, awaiting confirmation	2025-10-29 12:56:08
407	108	confirmed	Payment confirmed	2025-10-30 03:56:08
408	108	processing	Preparing for shipment	2025-10-31 00:56:08
409	108	shipped	Handed over to courier	2025-10-31 11:56:08
410	109	pending	Order placed, awaiting confirmation	2026-01-10 23:36:08
411	110	pending	Order placed, awaiting confirmation	2026-01-06 13:08:16
412	110	cancelled	Order cancelled by customer	2026-01-06 14:08:16
413	111	pending	Order placed, awaiting confirmation	2025-11-11 23:33:29
414	111	confirmed	Payment confirmed	2025-11-12 22:33:29
415	111	processing	Preparing for shipment	2025-11-13 15:33:29
416	111	shipped	Handed over to courier	2025-11-14 04:33:29
417	111	delivered	Delivered to customer	2025-11-14 07:33:29
418	112	pending	Order placed, awaiting confirmation	2025-05-23 12:11:42
419	112	confirmed	Payment confirmed	2025-05-23 18:11:42
420	112	processing	Preparing for shipment	2025-05-24 12:11:42
421	112	shipped	Handed over to courier	2025-05-24 21:11:42
422	113	pending	Order placed, awaiting confirmation	2026-01-26 03:38:10
423	113	confirmed	Payment confirmed	2026-01-26 13:38:10
424	113	processing	Preparing for shipment	2026-01-27 06:38:10
425	113	shipped	Handed over to courier	2026-01-27 09:38:10
426	113	delivered	Delivered to customer	2026-01-27 14:38:10
427	114	pending	Order placed, awaiting confirmation	2025-07-22 09:04:47
428	114	confirmed	Payment confirmed	2025-07-22 14:04:47
429	114	processing	Preparing for shipment	2025-07-23 02:04:47
430	114	shipped	Handed over to courier	2025-07-23 03:04:47
431	114	delivered	Delivered to customer	2025-07-23 12:04:47
432	115	pending	Order placed, awaiting confirmation	2025-09-08 20:38:45
433	115	confirmed	Payment confirmed	2025-09-09 09:38:45
434	115	processing	Preparing for shipment	2025-09-09 15:38:45
435	115	shipped	Handed over to courier	2025-09-10 06:38:45
436	115	delivered	Delivered to customer	2025-09-11 03:38:45
437	116	pending	Order placed, awaiting confirmation	2026-02-08 07:39:04
438	116	confirmed	Payment confirmed	2026-02-09 05:39:04
439	116	processing	Preparing for shipment	2026-02-09 13:39:04
440	117	pending	Order placed, awaiting confirmation	2025-11-09 03:23:28
441	117	confirmed	Payment confirmed	2025-11-09 09:23:28
442	117	processing	Preparing for shipment	2025-11-09 14:23:28
443	118	pending	Order placed, awaiting confirmation	2025-09-24 09:34:11
444	118	cancelled	Order cancelled by customer	2025-09-25 09:34:11
445	119	pending	Order placed, awaiting confirmation	2026-01-08 19:32:41
446	119	confirmed	Payment confirmed	2026-01-09 13:32:41
447	119	processing	Preparing for shipment	2026-01-10 08:32:41
448	119	shipped	Handed over to courier	2026-01-11 03:32:41
449	120	pending	Order placed, awaiting confirmation	2025-07-19 06:09:45
450	120	confirmed	Payment confirmed	2025-07-19 13:09:45
451	120	processing	Preparing for shipment	2025-07-19 19:09:45
452	120	shipped	Handed over to courier	2025-07-19 20:09:45
453	120	delivered	Delivered to customer	2025-07-20 10:09:45
454	121	pending	Order placed, awaiting confirmation	2026-01-09 22:00:40
455	121	confirmed	Payment confirmed	2026-01-10 13:00:40
456	121	processing	Preparing for shipment	2026-01-11 12:00:40
457	122	pending	Order placed, awaiting confirmation	2025-03-18 00:24:49
458	122	cancelled	Order cancelled by customer	2025-03-18 23:24:49
459	123	pending	Order placed, awaiting confirmation	2025-07-17 16:43:28
460	123	confirmed	Payment confirmed	2025-07-18 10:43:28
461	123	processing	Preparing for shipment	2025-07-18 17:43:28
462	123	shipped	Handed over to courier	2025-07-19 02:43:28
463	124	pending	Order placed, awaiting confirmation	2025-12-19 03:42:26
464	124	confirmed	Payment confirmed	2025-12-19 07:42:26
465	124	processing	Preparing for shipment	2025-12-19 23:42:26
466	125	pending	Order placed, awaiting confirmation	2025-07-30 22:36:45
467	125	confirmed	Payment confirmed	2025-07-31 10:36:45
468	125	processing	Preparing for shipment	2025-07-31 12:36:45
469	125	shipped	Handed over to courier	2025-07-31 13:36:45
470	126	pending	Order placed, awaiting confirmation	2025-12-26 06:30:42
471	126	confirmed	Payment confirmed	2025-12-26 17:30:42
472	126	processing	Preparing for shipment	2025-12-27 12:30:42
473	127	pending	Order placed, awaiting confirmation	2025-07-26 15:03:18
474	127	confirmed	Payment confirmed	2025-07-26 18:03:18
475	127	processing	Preparing for shipment	2025-07-27 14:03:18
476	127	shipped	Handed over to courier	2025-07-27 17:03:18
477	128	pending	Order placed, awaiting confirmation	2025-05-12 23:48:08
478	128	confirmed	Payment confirmed	2025-05-13 09:48:08
479	128	processing	Preparing for shipment	2025-05-13 16:48:08
480	128	shipped	Handed over to courier	2025-05-14 12:48:08
481	128	delivered	Delivered to customer	2025-05-14 14:48:08
482	129	pending	Order placed, awaiting confirmation	2025-04-05 14:09:44
483	129	confirmed	Payment confirmed	2025-04-05 23:09:44
484	129	processing	Preparing for shipment	2025-04-06 03:09:44
485	129	shipped	Handed over to courier	2025-04-06 06:09:44
486	129	delivered	Delivered to customer	2025-04-07 06:09:44
487	130	pending	Order placed, awaiting confirmation	2025-03-06 15:30:31
488	130	confirmed	Payment confirmed	2025-03-06 23:30:31
489	130	processing	Preparing for shipment	2025-03-07 10:30:31
490	130	shipped	Handed over to courier	2025-03-07 18:30:31
491	130	delivered	Delivered to customer	2025-03-08 01:30:31
492	131	pending	Order placed, awaiting confirmation	2025-05-05 16:59:31
493	131	confirmed	Payment confirmed	2025-05-06 08:59:31
494	132	pending	Order placed, awaiting confirmation	2025-09-18 08:11:50
495	132	confirmed	Payment confirmed	2025-09-18 22:11:50
496	132	processing	Preparing for shipment	2025-09-19 13:11:50
497	132	shipped	Handed over to courier	2025-09-20 00:11:50
498	133	pending	Order placed, awaiting confirmation	2025-08-19 00:04:07
499	133	confirmed	Payment confirmed	2025-08-19 18:04:07
500	133	processing	Preparing for shipment	2025-08-20 08:04:07
501	133	shipped	Handed over to courier	2025-08-20 09:04:07
502	134	pending	Order placed, awaiting confirmation	2025-11-23 11:32:53
503	134	confirmed	Payment confirmed	2025-11-23 18:32:53
504	135	pending	Order placed, awaiting confirmation	2025-05-23 12:42:15
505	135	confirmed	Payment confirmed	2025-05-24 03:42:15
506	135	processing	Preparing for shipment	2025-05-25 00:42:15
507	136	pending	Order placed, awaiting confirmation	2025-05-01 01:15:21
508	136	confirmed	Payment confirmed	2025-05-01 21:15:21
509	136	processing	Preparing for shipment	2025-05-02 09:15:21
510	136	shipped	Handed over to courier	2025-05-02 16:15:21
511	136	delivered	Delivered to customer	2025-05-03 02:15:21
512	137	pending	Order placed, awaiting confirmation	2026-02-28 15:36:24
513	137	confirmed	Payment confirmed	2026-03-01 13:36:24
514	137	processing	Preparing for shipment	2026-03-02 00:00:00
515	137	shipped	Handed over to courier	2026-03-02 00:00:00
516	138	pending	Order placed, awaiting confirmation	2025-12-01 23:43:46
517	138	confirmed	Payment confirmed	2025-12-02 10:43:46
518	138	processing	Preparing for shipment	2025-12-02 13:43:46
519	138	shipped	Handed over to courier	2025-12-02 18:43:46
520	138	delivered	Delivered to customer	2025-12-03 16:43:46
521	139	pending	Order placed, awaiting confirmation	2026-01-31 15:50:26
522	139	confirmed	Payment confirmed	2026-01-31 17:50:26
523	139	processing	Preparing for shipment	2026-02-01 02:50:26
524	139	shipped	Handed over to courier	2026-02-01 04:50:26
525	139	delivered	Delivered to customer	2026-02-01 11:50:26
526	140	pending	Order placed, awaiting confirmation	2025-06-09 19:25:26
527	140	confirmed	Payment confirmed	2025-06-10 04:25:26
528	140	processing	Preparing for shipment	2025-06-10 11:25:26
529	140	shipped	Handed over to courier	2025-06-11 04:25:26
530	141	pending	Order placed, awaiting confirmation	2026-01-07 03:15:01
531	141	confirmed	Payment confirmed	2026-01-08 00:15:01
532	142	pending	Order placed, awaiting confirmation	2025-07-18 21:33:49
533	142	confirmed	Payment confirmed	2025-07-19 15:33:49
534	142	processing	Preparing for shipment	2025-07-20 04:33:49
535	142	shipped	Handed over to courier	2025-07-20 18:33:49
536	143	pending	Order placed, awaiting confirmation	2026-02-23 13:39:56
537	144	pending	Order placed, awaiting confirmation	2025-08-15 07:44:59
538	144	confirmed	Payment confirmed	2025-08-15 20:44:59
539	144	processing	Preparing for shipment	2025-08-16 00:44:59
540	144	shipped	Handed over to courier	2025-08-16 23:44:59
541	145	pending	Order placed, awaiting confirmation	2025-04-23 17:16:45
542	145	cancelled	Order cancelled by customer	2025-04-24 12:16:45
543	146	pending	Order placed, awaiting confirmation	2026-02-09 04:17:15
544	146	confirmed	Payment confirmed	2026-02-09 05:17:15
545	146	processing	Preparing for shipment	2026-02-10 00:17:15
546	146	shipped	Handed over to courier	2026-02-10 11:17:15
547	146	delivered	Delivered to customer	2026-02-11 03:17:15
548	147	pending	Order placed, awaiting confirmation	2025-03-07 07:55:22
549	147	confirmed	Payment confirmed	2025-03-07 23:55:22
550	147	processing	Preparing for shipment	2025-03-08 20:55:22
551	148	pending	Order placed, awaiting confirmation	2026-02-16 05:34:45
552	148	confirmed	Payment confirmed	2026-02-16 06:34:45
553	148	processing	Preparing for shipment	2026-02-17 02:34:45
554	148	shipped	Handed over to courier	2026-02-17 13:34:45
555	148	delivered	Delivered to customer	2026-02-18 04:34:45
556	149	pending	Order placed, awaiting confirmation	2025-09-05 19:30:21
557	149	confirmed	Payment confirmed	2025-09-06 00:30:21
558	150	pending	Order placed, awaiting confirmation	2025-11-25 11:14:54
559	150	cancelled	Order cancelled by customer	2025-11-26 00:14:54
560	151	pending	Order placed, awaiting confirmation	2025-07-12 08:42:27
561	151	confirmed	Payment confirmed	2025-07-13 03:42:27
562	151	processing	Preparing for shipment	2025-07-13 16:42:27
563	151	shipped	Handed over to courier	2025-07-13 20:42:27
564	152	pending	Order placed, awaiting confirmation	2025-09-16 17:28:42
565	152	confirmed	Payment confirmed	2025-09-17 03:28:42
566	152	processing	Preparing for shipment	2025-09-17 11:28:42
567	153	pending	Order placed, awaiting confirmation	2025-03-25 15:35:19
568	153	confirmed	Payment confirmed	2025-03-26 03:35:19
569	154	pending	Order placed, awaiting confirmation	2025-06-24 18:14:17
570	154	confirmed	Payment confirmed	2025-06-25 06:14:17
571	154	processing	Preparing for shipment	2025-06-26 04:14:17
572	154	shipped	Handed over to courier	2025-06-26 18:14:17
573	154	delivered	Delivered to customer	2025-06-26 19:14:17
574	155	pending	Order placed, awaiting confirmation	2025-08-06 23:16:02
575	155	confirmed	Payment confirmed	2025-08-07 20:16:02
576	155	processing	Preparing for shipment	2025-08-07 22:16:02
577	155	shipped	Handed over to courier	2025-08-08 07:16:02
578	155	delivered	Delivered to customer	2025-08-08 08:16:02
579	156	pending	Order placed, awaiting confirmation	2025-10-20 02:40:27
580	156	confirmed	Payment confirmed	2025-10-20 07:40:27
581	156	processing	Preparing for shipment	2025-10-20 09:40:27
582	157	pending	Order placed, awaiting confirmation	2026-01-10 09:55:56
583	157	confirmed	Payment confirmed	2026-01-10 14:55:56
584	157	processing	Preparing for shipment	2026-01-11 01:55:56
585	157	shipped	Handed over to courier	2026-01-11 14:55:56
586	157	delivered	Delivered to customer	2026-01-12 11:55:56
587	158	pending	Order placed, awaiting confirmation	2025-06-29 00:04:27
588	158	confirmed	Payment confirmed	2025-06-29 12:04:27
589	158	processing	Preparing for shipment	2025-06-29 15:04:27
590	158	shipped	Handed over to courier	2025-06-30 13:04:27
591	158	delivered	Delivered to customer	2025-06-30 16:04:27
592	159	pending	Order placed, awaiting confirmation	2026-01-16 03:27:10
593	159	confirmed	Payment confirmed	2026-01-16 15:27:10
594	159	processing	Preparing for shipment	2026-01-17 15:27:10
595	159	shipped	Handed over to courier	2026-01-18 04:27:10
596	159	delivered	Delivered to customer	2026-01-18 19:27:10
597	160	pending	Order placed, awaiting confirmation	2025-10-01 14:40:23
598	160	cancelled	Order cancelled by customer	2025-10-02 01:40:23
599	161	pending	Order placed, awaiting confirmation	2025-06-28 15:55:40
600	161	confirmed	Payment confirmed	2025-06-29 06:55:40
601	161	processing	Preparing for shipment	2025-06-30 05:55:40
602	161	shipped	Handed over to courier	2025-06-30 11:55:40
603	162	pending	Order placed, awaiting confirmation	2025-08-03 06:45:29
604	162	confirmed	Payment confirmed	2025-08-03 16:45:29
605	162	processing	Preparing for shipment	2025-08-04 12:45:29
606	162	shipped	Handed over to courier	2025-08-04 23:45:29
607	162	delivered	Delivered to customer	2025-08-05 05:45:29
608	163	pending	Order placed, awaiting confirmation	2025-09-22 07:59:37
609	163	confirmed	Payment confirmed	2025-09-22 17:59:37
610	163	processing	Preparing for shipment	2025-09-22 19:59:37
611	163	shipped	Handed over to courier	2025-09-23 13:59:37
612	163	delivered	Delivered to customer	2025-09-24 05:59:37
613	164	pending	Order placed, awaiting confirmation	2025-12-04 23:55:29
614	164	confirmed	Payment confirmed	2025-12-05 15:55:29
615	165	pending	Order placed, awaiting confirmation	2025-08-10 15:42:53
616	165	confirmed	Payment confirmed	2025-08-10 17:42:53
617	165	processing	Preparing for shipment	2025-08-11 05:42:53
618	165	shipped	Handed over to courier	2025-08-11 12:42:53
619	165	delivered	Delivered to customer	2025-08-11 13:42:53
620	166	pending	Order placed, awaiting confirmation	2025-12-27 11:29:29
621	166	cancelled	Order cancelled by customer	2025-12-28 03:29:29
622	167	pending	Order placed, awaiting confirmation	2025-11-01 12:32:03
623	167	confirmed	Payment confirmed	2025-11-02 11:32:03
624	167	processing	Preparing for shipment	2025-11-03 06:32:03
625	167	shipped	Handed over to courier	2025-11-03 11:32:03
626	168	pending	Order placed, awaiting confirmation	2025-06-16 06:26:55
627	168	cancelled	Order cancelled by customer	2025-06-16 16:26:55
628	169	pending	Order placed, awaiting confirmation	2025-09-22 09:16:58
629	169	confirmed	Payment confirmed	2025-09-22 17:16:58
630	169	processing	Preparing for shipment	2025-09-23 00:16:58
631	170	pending	Order placed, awaiting confirmation	2025-10-10 13:14:33
632	170	confirmed	Payment confirmed	2025-10-10 17:14:33
633	170	processing	Preparing for shipment	2025-10-11 06:14:33
634	171	pending	Order placed, awaiting confirmation	2025-12-31 03:38:24
635	171	confirmed	Payment confirmed	2025-12-31 17:38:24
636	171	processing	Preparing for shipment	2026-01-01 05:38:24
637	171	shipped	Handed over to courier	2026-01-01 08:38:24
638	171	delivered	Delivered to customer	2026-01-02 07:38:24
639	172	pending	Order placed, awaiting confirmation	2025-09-10 05:13:22
640	172	confirmed	Payment confirmed	2025-09-10 15:13:22
641	172	processing	Preparing for shipment	2025-09-11 14:13:22
642	172	shipped	Handed over to courier	2025-09-11 17:13:22
643	172	delivered	Delivered to customer	2025-09-11 23:13:22
644	173	pending	Order placed, awaiting confirmation	2025-05-27 06:04:17
645	173	confirmed	Payment confirmed	2025-05-28 01:04:17
646	173	processing	Preparing for shipment	2025-05-28 13:04:17
647	173	shipped	Handed over to courier	2025-05-28 18:04:17
648	173	delivered	Delivered to customer	2025-05-29 12:04:17
649	174	pending	Order placed, awaiting confirmation	2026-02-07 21:44:05
650	174	confirmed	Payment confirmed	2026-02-08 13:44:05
651	174	processing	Preparing for shipment	2026-02-08 17:44:05
652	174	shipped	Handed over to courier	2026-02-09 11:44:05
653	174	delivered	Delivered to customer	2026-02-10 11:44:05
654	175	pending	Order placed, awaiting confirmation	2026-02-26 21:17:51
655	175	confirmed	Payment confirmed	2026-02-27 12:17:51
656	176	pending	Order placed, awaiting confirmation	2025-08-11 18:56:10
657	176	confirmed	Payment confirmed	2025-08-12 01:56:10
658	176	processing	Preparing for shipment	2025-08-12 05:56:10
659	176	shipped	Handed over to courier	2025-08-12 06:56:10
660	176	delivered	Delivered to customer	2025-08-13 05:56:10
661	176	returned	Return request accepted	2025-08-13 13:56:10
662	177	pending	Order placed, awaiting confirmation	2025-12-10 02:59:53
663	177	cancelled	Order cancelled by customer	2025-12-10 22:59:53
664	178	pending	Order placed, awaiting confirmation	2025-09-08 23:07:03
665	178	confirmed	Payment confirmed	2025-09-09 15:07:03
666	178	processing	Preparing for shipment	2025-09-09 23:07:03
667	178	shipped	Handed over to courier	2025-09-10 05:07:03
668	178	delivered	Delivered to customer	2025-09-10 08:07:03
669	179	pending	Order placed, awaiting confirmation	2025-03-09 13:59:46
670	179	confirmed	Payment confirmed	2025-03-10 07:59:46
671	179	processing	Preparing for shipment	2025-03-10 23:59:46
672	179	shipped	Handed over to courier	2025-03-11 08:59:46
673	180	pending	Order placed, awaiting confirmation	2025-11-10 03:22:23
674	180	confirmed	Payment confirmed	2025-11-11 01:22:23
675	180	processing	Preparing for shipment	2025-11-11 06:22:23
676	180	shipped	Handed over to courier	2025-11-11 19:22:23
677	181	pending	Order placed, awaiting confirmation	2026-01-29 05:46:18
678	181	confirmed	Payment confirmed	2026-01-29 09:46:18
679	181	processing	Preparing for shipment	2026-01-29 10:46:18
680	181	shipped	Handed over to courier	2026-01-30 05:46:18
681	181	delivered	Delivered to customer	2026-01-30 09:46:18
682	182	pending	Order placed, awaiting confirmation	2025-06-27 17:04:02
683	182	cancelled	Order cancelled by customer	2025-06-28 04:04:02
684	183	pending	Order placed, awaiting confirmation	2025-09-25 06:40:20
685	183	confirmed	Payment confirmed	2025-09-25 23:40:20
686	184	pending	Order placed, awaiting confirmation	2025-12-27 22:41:50
687	184	confirmed	Payment confirmed	2025-12-28 00:41:50
688	184	processing	Preparing for shipment	2025-12-28 06:41:50
689	184	shipped	Handed over to courier	2025-12-28 08:41:50
690	184	delivered	Delivered to customer	2025-12-28 21:41:50
691	185	pending	Order placed, awaiting confirmation	2026-01-18 09:17:55
692	185	confirmed	Payment confirmed	2026-01-18 22:17:55
693	185	processing	Preparing for shipment	2026-01-19 02:17:55
694	186	pending	Order placed, awaiting confirmation	2025-07-29 05:50:43
695	186	confirmed	Payment confirmed	2025-07-29 17:50:43
696	186	processing	Preparing for shipment	2025-07-30 09:50:43
697	187	pending	Order placed, awaiting confirmation	2025-10-20 07:46:04
698	187	confirmed	Payment confirmed	2025-10-20 10:46:04
699	187	processing	Preparing for shipment	2025-10-21 02:46:04
700	187	shipped	Handed over to courier	2025-10-21 16:46:04
701	187	delivered	Delivered to customer	2025-10-21 18:46:04
702	187	returned	Return request accepted	2025-10-21 19:46:04
703	188	pending	Order placed, awaiting confirmation	2025-12-09 00:15:28
704	188	confirmed	Payment confirmed	2025-12-09 23:15:28
705	188	processing	Preparing for shipment	2025-12-10 02:15:28
706	188	shipped	Handed over to courier	2025-12-10 11:15:28
707	188	delivered	Delivered to customer	2025-12-11 01:15:28
708	189	pending	Order placed, awaiting confirmation	2025-06-24 10:34:32
709	189	confirmed	Payment confirmed	2025-06-24 11:34:32
710	189	processing	Preparing for shipment	2025-06-24 22:34:32
711	189	shipped	Handed over to courier	2025-06-25 13:34:32
712	189	delivered	Delivered to customer	2025-06-25 23:34:32
713	190	pending	Order placed, awaiting confirmation	2025-11-27 04:44:59
714	190	confirmed	Payment confirmed	2025-11-28 02:44:59
715	190	processing	Preparing for shipment	2025-11-28 23:44:59
716	190	shipped	Handed over to courier	2025-11-29 22:44:59
717	190	delivered	Delivered to customer	2025-11-30 21:44:59
718	191	pending	Order placed, awaiting confirmation	2025-11-30 00:08:09
719	191	confirmed	Payment confirmed	2025-11-30 04:08:09
720	191	processing	Preparing for shipment	2025-12-01 01:08:09
721	191	shipped	Handed over to courier	2025-12-01 08:08:09
722	191	delivered	Delivered to customer	2025-12-01 20:08:09
723	192	pending	Order placed, awaiting confirmation	2025-11-14 22:09:56
724	192	confirmed	Payment confirmed	2025-11-15 09:09:56
725	192	processing	Preparing for shipment	2025-11-16 01:09:56
726	193	pending	Order placed, awaiting confirmation	2026-01-14 16:32:02
727	193	confirmed	Payment confirmed	2026-01-14 20:32:02
728	193	processing	Preparing for shipment	2026-01-15 07:32:02
729	193	shipped	Handed over to courier	2026-01-15 18:32:02
730	193	delivered	Delivered to customer	2026-01-15 20:32:02
731	194	pending	Order placed, awaiting confirmation	2025-07-21 07:30:05
732	194	confirmed	Payment confirmed	2025-07-21 10:30:05
733	194	processing	Preparing for shipment	2025-07-21 16:30:05
734	194	shipped	Handed over to courier	2025-07-22 11:30:05
735	194	delivered	Delivered to customer	2025-07-22 19:30:05
736	195	pending	Order placed, awaiting confirmation	2026-01-18 21:20:01
737	195	confirmed	Payment confirmed	2026-01-18 23:20:01
738	195	processing	Preparing for shipment	2026-01-19 02:20:01
739	196	pending	Order placed, awaiting confirmation	2026-01-18 01:35:24
740	196	confirmed	Payment confirmed	2026-01-18 22:35:24
741	196	processing	Preparing for shipment	2026-01-18 23:35:24
742	196	shipped	Handed over to courier	2026-01-19 01:35:24
743	196	delivered	Delivered to customer	2026-01-19 12:35:24
744	197	pending	Order placed, awaiting confirmation	2025-10-17 14:24:01
745	197	confirmed	Payment confirmed	2025-10-18 03:24:01
746	197	processing	Preparing for shipment	2025-10-18 13:24:01
747	197	shipped	Handed over to courier	2025-10-19 05:24:01
748	197	delivered	Delivered to customer	2025-10-19 08:24:01
749	198	pending	Order placed, awaiting confirmation	2026-02-21 01:55:30
750	199	pending	Order placed, awaiting confirmation	2026-01-18 20:28:50
751	199	confirmed	Payment confirmed	2026-01-19 00:28:50
752	199	processing	Preparing for shipment	2026-01-19 15:28:50
753	199	shipped	Handed over to courier	2026-01-20 13:28:50
754	200	pending	Order placed, awaiting confirmation	2025-11-14 00:09:09
755	200	confirmed	Payment confirmed	2025-11-14 08:09:09
756	200	processing	Preparing for shipment	2025-11-15 03:09:09
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.orders (order_id, order_uuid, user_id, address_id, coupon_id, status, subtotal, discount, tax, shipping_fee, grand_total, created_at, updated_at) FROM stdin;
1	6c01de43-f132-42cd-b069-1c3c75854450	91	91	\N	pending	54994.00	0.00	9898.92	0.00	64892.92	2025-12-03 17:42:10	2026-02-06 13:46:04
2	4447bf29-23bf-41c6-b849-3233162bf722	63	84	\N	cancelled	34193.00	0.00	6154.74	99.00	40446.74	2025-08-06 12:13:45	2025-11-18 11:24:19
3	bcad65e7-2a81-4305-95e5-fdbeac0266bf	27	64	\N	delivered	163990.00	0.00	29518.20	99.00	193607.20	2025-11-28 11:54:47	2026-01-01 02:19:32
4	f2574bcf-03d5-4cd4-a859-b607ae062649	75	126	\N	delivered	1996.00	0.00	359.28	49.00	2404.28	2025-10-19 02:48:36	2026-01-25 03:11:02
5	e97cc378-6547-43d8-8cd3-a6096e1fc475	24	123	7	returned	18994.00	140.93	3393.55	0.00	22246.62	2025-08-13 03:34:59	2025-10-28 10:10:21
6	c92cf6e4-7f4f-4e11-ae67-d72e21632c8c	66	8	8	delivered	51996.00	473.54	9274.04	0.00	60796.50	2025-09-02 19:20:49	2025-12-30 21:27:13
7	21930b5d-f653-4210-9131-477275b9fb3a	55	7	12	shipped	64491.00	213.54	11569.94	99.00	75946.40	2025-08-14 12:48:58	2025-12-30 05:58:10
8	5ef36e19-d5cb-485a-a5bc-746c6a64e558	42	20	\N	delivered	56993.00	0.00	10258.74	149.00	67400.74	2025-03-11 17:43:19	2025-04-15 22:10:37
9	4f83eb71-ca56-48d9-b46b-e37fa0eeef4b	93	15	\N	pending	2499.00	0.00	449.82	0.00	2948.82	2025-11-07 16:28:24	2026-02-23 07:17:32
10	2efbfafd-ae4c-40a6-889d-a4546556771b	54	139	\N	delivered	5499.00	0.00	989.82	49.00	6537.82	2025-04-02 14:18:56	2025-04-17 00:40:29
11	39c2623c-05e3-430f-998b-dc33d8480888	55	4	\N	shipped	234991.00	0.00	42298.38	149.00	277438.38	2025-04-23 17:59:44	2025-12-01 16:19:50
12	6c1d6ae8-0be3-4f37-bee8-6447c16263de	90	74	\N	delivered	11495.00	0.00	2069.10	99.00	13663.10	2025-03-26 06:52:48	2025-08-27 14:31:43
13	f3d67e23-a0d1-43f2-ba6b-6195bd1f39a5	71	6	\N	delivered	22995.00	0.00	4139.10	149.00	27283.10	2025-10-21 09:31:11	2025-11-10 22:25:08
14	8bbfc66d-b8c9-4df2-96cb-bb9d10e8fb24	6	78	\N	cancelled	3897.00	0.00	701.46	99.00	4697.46	2026-02-01 08:00:09	2026-02-05 19:51:16
15	0100f0c3-9d9b-4dd4-9c35-74ea7ba239a2	91	115	\N	confirmed	29793.00	0.00	5362.74	0.00	35155.74	2025-11-19 17:54:51	2026-02-01 20:23:41
16	6d2ceb4b-c378-4c6b-b220-26874b850237	71	37	16	pending	3996.00	371.75	652.37	0.00	4276.62	2026-01-07 10:45:41	2026-02-16 22:39:19
17	7153a891-a252-48e9-a413-4952529dff18	8	17	\N	delivered	409988.00	0.00	73797.84	49.00	483834.84	2026-01-13 08:06:17	2026-02-18 02:33:28
18	5025fe55-610b-4592-9a22-240bd8650a6a	28	102	\N	confirmed	7497.00	0.00	1349.46	49.00	8895.46	2025-07-10 17:50:25	2026-01-14 08:50:29
19	04cec75e-0e33-470f-9ca2-8341383d50b2	62	8	\N	delivered	1998.00	0.00	359.64	49.00	2406.64	2025-10-17 02:44:19	2026-01-27 21:50:21
20	b37de3a7-e5d6-403d-a1c6-538d6fc81c87	87	26	\N	delivered	6998.00	0.00	1259.64	49.00	8306.64	2025-08-26 05:28:25	2025-10-23 15:00:41
21	a353326f-a5b4-48b2-9d45-df6168d295fe	76	68	\N	delivered	128997.00	0.00	23219.46	0.00	152216.46	2026-01-27 21:22:09	2026-02-08 02:01:25
22	fb76ad2c-7f35-4217-a547-736a272f6cac	93	25	\N	pending	87988.00	0.00	15837.84	149.00	103974.84	2025-07-28 11:30:39	2026-02-16 17:13:56
23	e2555877-26cd-41d3-9e5c-7d43557b3f65	22	105	\N	delivered	95995.00	0.00	17279.10	149.00	113423.10	2026-02-28 00:59:07	2026-02-28 07:38:03
24	42ce1a71-a15c-47b5-ac9a-00e2a8a644e1	30	5	\N	pending	10691.00	0.00	1924.38	0.00	12615.38	2025-10-16 23:33:49	2026-01-16 17:29:18
25	49567f26-3b2a-4055-9a46-60a3d36e95d7	43	53	\N	delivered	59996.00	0.00	10799.28	149.00	70944.28	2025-07-22 10:45:06	2026-01-22 01:03:15
26	ef23e013-71ed-4ab0-bce0-f3900287b7d7	66	85	\N	delivered	192988.00	0.00	34737.84	149.00	227874.84	2025-07-18 13:44:46	2025-12-18 13:46:53
27	8186531f-fbd6-4388-8be3-cb3a2aa55c36	80	64	\N	shipped	17996.00	0.00	3239.28	99.00	21334.28	2025-06-25 12:34:37	2025-06-25 14:51:37
28	236b5767-012d-430f-ab77-5cb54f89d213	36	23	\N	shipped	5997.00	0.00	1079.46	49.00	7125.46	2025-07-13 19:32:00	2025-11-05 03:20:44
29	b3dbfcc2-bcd4-4f75-ab65-062b216211ae	19	20	\N	confirmed	3897.00	0.00	701.46	99.00	4697.46	2025-09-19 23:00:57	2025-10-15 19:56:37
30	b2aa6c9e-330d-4df9-a0d3-9d7af39e25ff	40	35	12	shipped	107495.00	265.42	19301.32	49.00	126579.90	2025-08-12 00:39:44	2026-01-08 11:59:31
31	c11dae46-7464-4d4c-8fc5-6d4b8fa66a09	35	121	\N	shipped	26997.00	0.00	4859.46	49.00	31905.46	2025-04-16 04:39:07	2025-11-01 00:17:06
32	e7917286-f1aa-411a-8ade-1be44fd50c31	33	25	\N	delivered	18092.00	0.00	3256.56	0.00	21348.56	2025-12-07 13:40:18	2026-01-10 13:50:58
33	6a4cedb2-554e-494f-b66b-cfceaede5710	86	75	\N	processing	9996.00	0.00	1799.28	49.00	11844.28	2025-12-22 05:08:12	2026-01-21 10:36:31
34	86af8f3d-5f8a-4d87-93e1-9319a0d9d477	68	18	\N	delivered	216492.00	0.00	38968.56	99.00	255559.56	2026-02-20 20:16:32	2026-02-23 09:51:27
35	b8c1617a-78af-4bd1-a15b-1ad09114a0f0	18	65	\N	shipped	14994.00	0.00	2698.92	99.00	17791.92	2025-10-17 20:19:02	2026-01-07 15:00:13
36	b7940bf0-cf7d-419f-8019-8e77d1979664	46	109	\N	shipped	239490.00	0.00	43108.20	49.00	282647.20	2025-12-24 10:46:18	2026-02-21 07:53:51
37	883e66e6-415a-4469-9f9a-3a71e88c5a43	10	134	7	delivered	3598.00	145.39	621.47	99.00	4173.08	2025-08-26 08:12:42	2026-02-06 07:13:36
38	440ce7db-dbbf-47b1-bebc-f33c2b93e064	76	148	\N	confirmed	27996.00	0.00	5039.28	149.00	33184.28	2025-05-18 05:27:44	2025-06-25 07:04:09
39	8729339e-1c16-4862-9fd6-406c61b95ba1	82	20	\N	delivered	21497.00	0.00	3869.46	49.00	25415.46	2026-01-03 02:46:15	2026-01-24 07:39:07
40	9bfbf6e4-053c-4064-9854-78cfbcbd5199	67	138	\N	delivered	5996.00	0.00	1079.28	49.00	7124.28	2025-05-21 11:39:01	2025-10-24 13:09:21
41	ad3ed207-5135-4225-a964-690dc2067ee7	40	26	\N	processing	51996.00	0.00	9359.28	49.00	61404.28	2025-07-06 23:55:15	2026-02-10 18:49:00
42	2826d747-c32b-4e4f-be8b-90cba3d8d822	31	150	\N	processing	44997.00	0.00	8099.46	149.00	53245.46	2025-10-30 19:34:45	2026-01-21 07:37:19
43	0f6fafe2-22b8-4ff5-be28-c60693ddc72f	2	52	\N	delivered	6999.00	0.00	1259.82	99.00	8357.82	2025-08-08 13:49:51	2025-11-24 06:37:14
44	7897fdf8-e961-4aab-be8b-497960010aa6	43	71	7	shipped	2499.00	252.86	404.31	49.00	2699.45	2025-05-02 14:08:04	2026-01-25 23:21:47
45	684468df-abde-4cd1-807c-f8c0abae1e6c	43	90	\N	processing	5495.00	0.00	989.10	99.00	6583.10	2025-08-22 11:22:03	2025-12-05 21:23:32
46	29396af1-3d24-46ea-9671-b2b4862287ce	89	137	\N	delivered	60795.00	0.00	10943.10	49.00	71787.10	2025-05-17 21:32:35	2025-09-20 18:04:03
47	df82b243-34e6-464b-a082-ad8e9fe0e014	18	66	\N	delivered	7997.00	0.00	1439.46	0.00	9436.46	2025-05-22 06:05:55	2025-07-21 08:12:43
48	40c9cd47-1af2-4fd7-9e57-aab2d0f7ede0	36	48	4	delivered	10795.00	19.27	1939.63	149.00	12864.36	2025-04-12 11:07:38	2026-01-06 14:14:26
49	f0f6c2e2-948d-45e3-b472-6bab47e84e93	32	11	\N	processing	47988.00	0.00	8637.84	49.00	56674.84	2026-01-02 03:04:01	2026-03-01 16:05:02
50	46e884ca-15d6-41a6-a99d-acb7f284db3f	61	120	3	delivered	59998.00	219.46	10760.14	0.00	70538.68	2025-05-31 16:27:46	2025-08-07 20:58:54
51	39792fcf-4a57-494b-a8a8-364b0b5148ad	64	90	\N	returned	33996.00	0.00	6119.28	0.00	40115.28	2026-01-01 03:10:31	2026-01-21 04:59:51
52	687904af-050a-4bd7-8e23-93bef3c191e4	4	14	\N	delivered	7896.00	0.00	1421.28	0.00	9317.28	2025-12-02 10:01:00	2026-02-16 12:46:44
53	50008006-843d-4ef5-bc70-c546dd14e340	6	80	\N	shipped	27992.00	0.00	5038.56	0.00	33030.56	2025-08-26 05:42:59	2025-11-02 00:13:18
54	872f8be0-df5c-4718-b5ca-85999e771107	62	50	10	confirmed	187491.00	21.27	33744.55	0.00	221214.28	2025-05-01 22:19:38	2025-10-08 11:14:23
55	3a3ee8f3-4cd7-49cd-8434-87c2fb922444	5	139	\N	processing	3598.00	0.00	647.64	0.00	4245.64	2025-11-22 01:03:37	2026-02-24 10:58:43
56	f843b511-81ac-493b-a2eb-a2b24b172922	30	67	\N	delivered	1499.00	0.00	269.82	0.00	1768.82	2025-07-19 11:29:53	2025-08-14 01:45:55
57	98e52cd8-246d-4a53-b0dc-fe78673bc735	64	7	16	shipped	58593.00	424.20	10470.38	0.00	68639.18	2025-12-31 09:38:57	2026-01-21 22:57:47
58	5430293a-1c98-419f-bb8f-e7d289d4f5de	90	98	\N	delivered	63989.00	0.00	11518.02	0.00	75507.02	2025-04-25 05:45:29	2025-09-19 16:49:30
59	629eea1d-8aaf-4616-a5ae-50b6f809c9f0	34	91	\N	delivered	4998.00	0.00	899.64	99.00	5996.64	2025-05-04 03:43:35	2025-07-25 00:33:02
60	0de140ef-3273-4ef6-b751-c5054d26fdd7	42	79	\N	delivered	97993.00	0.00	17638.74	149.00	115780.74	2025-04-28 10:25:18	2026-02-09 20:10:17
61	43637e66-badb-43fa-a7c5-f97c90b959a2	26	16	1	delivered	23996.00	173.20	4288.10	0.00	28110.90	2026-02-05 04:02:17	2026-02-13 11:40:30
62	9900d7fa-44a4-48f5-b0db-0ab1adf58b42	46	130	\N	processing	3998.00	0.00	719.64	49.00	4766.64	2025-07-03 22:56:11	2025-07-06 08:38:58
63	0530a7e7-f9cb-4fda-b12b-82ca3b465e5b	75	6	\N	cancelled	14494.00	0.00	2608.92	0.00	17102.92	2025-10-03 08:43:36	2025-12-12 13:29:00
64	31e476cf-f75c-40c8-9d10-f56c0090a2f1	51	61	18	delivered	5499.00	405.22	916.88	49.00	6059.66	2025-09-18 12:16:09	2025-10-09 02:32:55
65	5f14e8e4-1a09-4355-bd06-365b35b483a0	8	121	\N	delivered	10997.00	0.00	1979.46	149.00	13125.46	2025-10-01 09:42:36	2025-12-24 00:26:29
66	e762ab84-fcf3-41f3-bc36-3616e3be535f	98	134	\N	shipped	10497.00	0.00	1889.46	149.00	12535.46	2025-12-30 16:17:46	2026-01-04 19:40:41
67	5162c87d-a4bc-44b7-ab46-c3fcb82f26af	74	139	\N	processing	21491.00	0.00	3868.38	0.00	25359.38	2025-11-07 14:11:03	2025-12-26 22:26:57
68	059592c2-b211-461b-b261-26e821a1023f	61	106	\N	processing	16797.00	0.00	3023.46	49.00	19869.46	2025-10-09 16:32:28	2026-01-05 23:45:44
69	0c2a4783-c0c0-4353-988c-78613207d47b	84	131	\N	processing	10998.00	0.00	1979.64	149.00	13126.64	2025-11-11 14:43:27	2026-01-15 22:13:21
70	c5c6e8f2-b8a2-4bf4-b4f8-834025fb6686	76	50	9	delivered	12999.00	86.37	2324.27	0.00	15236.90	2025-06-17 07:18:39	2026-02-04 00:02:54
71	34274ab2-c069-4779-956b-cd4b4ae01619	18	98	\N	confirmed	9996.00	0.00	1799.28	0.00	11795.28	2025-03-18 08:16:45	2025-07-02 02:18:56
72	583e07f9-82c0-462e-bf0d-06886ec69b75	71	44	\N	cancelled	6998.00	0.00	1259.64	0.00	8257.64	2025-03-12 03:25:53	2025-07-28 17:06:36
73	e4375914-8d12-4e7c-84c7-b1943533010b	87	58	\N	confirmed	3598.00	0.00	647.64	0.00	4245.64	2026-01-02 17:43:33	2026-02-14 11:22:44
74	acd0d9f4-4a46-4dec-82e2-21fb91446a99	78	22	\N	cancelled	3499.00	0.00	629.82	0.00	4128.82	2025-09-15 14:41:50	2025-11-13 23:09:45
75	ceaa6eee-cb86-4d77-a4d3-cb93d9561a7b	66	84	18	cancelled	10497.00	285.36	1838.10	0.00	12049.74	2025-10-28 07:55:15	2025-12-09 21:36:51
76	4920627c-4698-4556-bdf0-48bbb7c776e1	27	68	17	cancelled	74996.00	183.25	13466.30	99.00	88378.05	2025-03-19 20:05:45	2025-10-09 03:24:56
77	f5ca525b-55cb-46ac-801c-4b0cf88748c3	10	22	19	delivered	40997.00	48.42	7370.74	49.00	48368.32	2025-04-25 01:26:01	2025-05-17 14:26:34
78	2588fdb0-a685-4ece-b6bc-54aff0d9849f	45	121	\N	delivered	169796.00	0.00	30563.28	99.00	200458.28	2025-06-12 20:55:36	2025-08-27 20:53:40
79	cc2ce2e4-8eb7-48f5-9002-26ee786c6418	8	55	\N	processing	149990.00	0.00	26998.20	49.00	177037.20	2025-06-03 16:01:01	2025-10-31 09:24:25
80	7fa9d976-13c6-490b-a5f6-a8ab092558e7	23	95	\N	pending	294588.00	0.00	53025.84	149.00	347762.84	2025-07-20 14:29:08	2025-10-04 08:53:09
81	0727e3a7-e890-4994-a49e-65d4ddd09067	31	52	\N	cancelled	175789.00	0.00	31642.02	149.00	207580.02	2025-08-07 05:58:04	2025-09-24 15:25:27
82	36719d36-3707-4c64-a692-2514595051d7	36	145	\N	delivered	1499.00	0.00	269.82	99.00	1867.82	2025-05-29 03:43:24	2025-12-29 08:36:06
83	e5c12edc-5446-4e3f-ad27-1260ba526ec7	55	50	19	processing	64998.00	216.28	11660.71	149.00	76591.43	2025-11-05 00:43:08	2025-12-25 00:04:40
84	0cde3373-c07f-49e2-9639-a0d338aca61e	17	30	6	delivered	4998.00	62.20	888.44	0.00	5824.24	2025-09-11 09:21:23	2025-12-03 12:53:01
85	0ede3c51-0864-4dcb-b956-95eceaedb136	70	110	\N	delivered	4393.00	0.00	790.74	0.00	5183.74	2025-09-03 23:20:07	2025-09-22 08:19:35
86	a60c5440-5d00-4389-be91-d539cf9fc33a	44	36	\N	delivered	234191.00	0.00	42154.38	149.00	276494.38	2025-06-01 04:49:13	2025-11-17 21:00:31
87	8eb34964-66b5-47af-a694-6513d2e2b8bf	8	100	\N	cancelled	17393.00	0.00	3130.74	99.00	20622.74	2026-02-24 10:20:53	2026-03-01 06:48:45
88	77e58f5c-1ca5-4f64-ad4f-99c2f9e22be6	10	129	8	shipped	89998.00	79.80	16185.28	149.00	106252.48	2025-04-30 01:40:40	2025-06-25 05:35:16
89	8943398f-ffea-4f68-8efa-83eea7f35046	52	148	\N	delivered	7497.00	0.00	1349.46	149.00	8995.46	2025-10-23 23:09:29	2026-01-02 16:47:15
90	d3574ec1-4993-437e-8e7c-51df77cc39bc	10	148	\N	cancelled	1598.00	0.00	287.64	99.00	1984.64	2025-12-05 14:53:41	2026-03-01 10:51:06
91	56e50f77-5f24-470c-adb2-a53c4cdbd4f8	13	104	19	delivered	999.00	471.51	94.95	149.00	771.44	2025-11-27 17:47:10	2025-12-11 16:37:58
92	eed1b5ec-6276-42a7-9167-63d4290a148d	7	77	18	delivered	18990.00	419.81	3342.63	149.00	22061.82	2025-07-09 20:42:24	2025-07-13 13:53:47
93	9c7d443a-6011-49f5-8c79-f60b777f9fe2	31	77	3	returned	56997.00	382.48	10190.61	0.00	66805.13	2025-12-14 13:26:42	2026-01-18 23:31:38
94	b527d670-5464-48bb-8223-b2e876954ae8	84	127	\N	processing	6998.00	0.00	1259.64	0.00	8257.64	2025-03-18 10:11:58	2025-05-25 15:28:19
95	6ab1a01e-e21f-4a65-8e77-552d2ad742b6	65	118	\N	delivered	63993.00	0.00	11518.74	99.00	75610.74	2025-07-03 06:48:56	2025-11-21 17:50:23
96	21630bfc-4942-406f-b8ff-3299c7dc117e	60	46	\N	shipped	102995.00	0.00	18539.10	0.00	121534.10	2025-09-21 15:17:22	2025-12-28 07:40:42
97	4279cf99-e780-43ae-aceb-65c2ae0faa72	31	65	4	pending	113992.00	227.70	20477.57	0.00	134241.87	2026-01-08 03:18:56	2026-01-29 04:08:14
98	fd96430f-311f-48e2-a58f-8a13a2e335b6	2	14	8	cancelled	227993.00	356.01	40974.66	49.00	268660.65	2025-08-10 00:35:44	2025-10-28 20:12:50
99	868dd772-d105-4d0f-a4ce-4e3a4e8d4ffe	7	142	\N	processing	9997.00	0.00	1799.46	149.00	11945.46	2025-08-08 13:53:39	2026-02-11 04:27:05
100	4894ddbf-5aa8-4b3c-9667-f35efb88fdcc	58	109	\N	delivered	110993.00	0.00	19978.74	49.00	131020.74	2025-05-25 14:50:04	2025-08-31 13:31:24
101	5443124d-1ec6-471b-b5b5-9ee18462fac9	94	44	\N	shipped	12996.00	0.00	2339.28	0.00	15335.28	2025-08-05 22:18:21	2025-11-12 12:40:32
102	c884d195-52d1-42bc-acd9-344e12b88810	65	128	\N	delivered	35996.00	0.00	6479.28	0.00	42475.28	2025-06-24 06:10:39	2025-12-19 16:28:27
103	4a3bbb50-6053-4096-93e7-c45984332eba	58	119	\N	confirmed	60993.00	0.00	10978.74	0.00	71971.74	2025-05-16 17:39:34	2025-06-24 23:06:41
104	5ec40a29-39d6-4ee1-af12-97d3522a2090	46	48	1	delivered	39495.00	56.06	7099.01	149.00	46686.95	2025-10-28 00:07:37	2026-01-10 16:45:30
105	8cc08a81-8ad5-40b8-abee-84e5df73fe0a	73	15	\N	delivered	10497.00	0.00	1889.46	0.00	12386.46	2025-10-15 09:04:39	2025-10-16 01:53:47
106	9b5241c4-0150-474a-873c-0abef83d5038	16	149	4	processing	128997.00	394.62	23148.43	0.00	151750.81	2026-01-19 21:08:04	2026-01-30 07:39:21
107	8944ce7f-85f7-46dc-9bd5-107b00b100f4	91	2	\N	confirmed	13995.00	0.00	2519.10	0.00	16514.10	2025-06-25 01:36:59	2025-10-14 15:21:09
108	7301e7bd-dc9e-4e49-8224-f0be6ed30145	62	143	16	shipped	4998.00	103.20	881.06	99.00	5874.86	2025-10-29 00:56:08	2026-01-01 15:45:02
109	4019d1df-55cf-4cd5-b05b-d5d3dd4dc60d	57	25	10	pending	48495.00	189.11	8695.06	0.00	57000.95	2026-01-10 05:36:08	2026-01-29 03:34:30
110	b4290210-915d-4207-b328-e1a08f6e2e3c	81	145	\N	cancelled	5998.00	0.00	1079.64	0.00	7077.64	2026-01-05 23:08:16	2026-02-07 07:49:03
111	5bc529a2-68d2-49be-b908-79678263276e	62	80	10	delivered	40091.00	373.00	7149.24	0.00	46867.24	2025-11-11 18:33:29	2026-01-24 09:55:01
112	62afbbfc-dd06-486a-a6b9-d0fb1e61cd21	8	27	7	shipped	19992.00	198.86	3562.77	49.00	23404.91	2025-05-23 02:11:42	2026-02-01 19:50:08
113	4331dd79-4078-4638-b5fa-c9b369db1687	67	15	\N	delivered	285992.00	0.00	51478.56	0.00	337470.56	2026-01-25 23:38:10	2026-02-27 09:36:32
114	dd357e5e-e706-4f64-8ef0-d1640252ac63	27	70	\N	delivered	63990.00	0.00	11518.20	0.00	75508.20	2025-07-22 00:04:47	2026-02-02 18:32:57
115	18a3539a-e1cb-4c67-b3b2-b0c1c7d3607c	1	97	\N	delivered	101590.00	0.00	18286.20	99.00	119975.20	2025-09-08 05:38:45	2025-09-26 05:28:57
116	5ba11353-6563-4ef2-8c8a-ee0d5168fe56	70	128	\N	processing	15693.00	0.00	2824.74	99.00	18616.74	2026-02-07 22:39:04	2026-02-23 02:06:05
117	e6135dd1-6239-4606-9d5f-2abaed139af9	93	20	7	processing	23996.00	192.22	4284.68	99.00	28187.46	2025-11-08 21:23:28	2026-01-31 07:48:08
118	e532af88-92f4-4d1c-aec3-baeb0f8c993a	77	114	7	cancelled	7196.00	424.65	1218.84	0.00	7990.19	2025-09-24 04:34:11	2026-01-16 04:57:19
119	b3793be3-b6a0-4686-84b5-4da71d198465	21	3	\N	shipped	18997.00	0.00	3419.46	49.00	22465.46	2026-01-08 15:32:41	2026-02-25 23:42:26
120	0157d6d6-af9b-4e0e-99bf-02b80a3c6f8a	35	3	\N	delivered	3897.00	0.00	701.46	149.00	4747.46	2025-07-18 14:09:45	2025-09-02 16:51:48
121	68e422f1-2295-4c86-8478-92b51c57cfef	79	29	\N	processing	1598.00	0.00	287.64	49.00	1934.64	2026-01-09 00:00:40	2026-01-15 08:59:32
122	f61d747b-3250-48ec-8a74-bb89073d4fb5	35	101	3	cancelled	216486.00	402.88	38894.96	0.00	254978.08	2025-03-17 11:24:49	2025-11-11 21:29:33
123	d7cc287e-cd46-437b-b5f1-4db0d77002b7	37	49	\N	shipped	23993.00	0.00	4318.74	149.00	28460.74	2025-07-17 00:43:28	2026-01-20 07:38:25
124	ce4289d0-ada2-41dd-a18e-53554b2a982f	36	15	\N	processing	7996.00	0.00	1439.28	49.00	9484.28	2025-12-18 12:42:26	2026-01-14 06:38:10
125	9aef6971-ecdf-4ea6-95a6-aa67148f1a89	52	42	\N	shipped	224997.00	0.00	40499.46	0.00	265496.46	2025-07-30 00:36:45	2025-12-03 03:31:37
126	161bf3bf-a505-4c46-80b1-253b4f394602	4	22	3	processing	89997.00	260.72	16152.53	99.00	105987.81	2025-12-25 19:30:42	2026-02-27 11:43:10
127	4bf3a02e-889a-4b5b-811a-89eccc71dd0c	24	81	19	shipped	59996.00	75.56	10785.68	149.00	70855.12	2025-07-26 01:03:18	2025-08-21 20:06:01
128	e3bd76c3-2ba4-438e-9286-7a50c3b6ed53	84	62	\N	delivered	23996.00	0.00	4319.28	0.00	28315.28	2025-05-12 21:48:08	2025-09-22 14:38:43
129	968c4f6b-d0c2-417e-80d6-fe3d9c2e3dad	21	89	3	delivered	38995.00	456.32	6936.96	149.00	45624.64	2025-04-05 04:09:44	2025-12-13 22:21:24
130	69894e6a-48f6-4472-94ae-99789ad331c1	79	101	\N	delivered	4998.00	0.00	899.64	99.00	5996.64	2025-03-06 04:30:31	2025-04-07 08:28:20
131	baa32d4b-a999-4bc3-bbac-a04cb25cb02b	86	48	\N	confirmed	55988.00	0.00	10077.84	49.00	66114.84	2025-05-05 00:59:31	2025-12-10 02:15:10
132	8df41000-89b6-4b76-b9e0-8311c44d7a9c	88	92	\N	shipped	59998.00	0.00	10799.64	0.00	70797.64	2025-09-17 21:11:50	2025-11-06 08:54:12
133	e1c7a4a8-0335-42ae-be0a-3e01a44c3d12	27	8	\N	shipped	51996.00	0.00	9359.28	49.00	61404.28	2025-08-18 22:04:07	2025-11-01 17:51:41
134	4fc6e936-c1a3-464e-a654-36eb7d510c41	60	104	12	confirmed	8394.00	129.43	1487.62	99.00	9851.19	2025-11-22 15:32:53	2025-12-28 18:36:17
135	9ce7cca8-d8f3-4aa8-ab0f-dfe8b59572ed	29	76	\N	processing	41192.00	0.00	7414.56	149.00	48755.56	2025-05-23 07:42:15	2025-09-02 20:01:45
136	e002c428-6a8f-445d-8d3e-4f43209b3924	83	136	\N	delivered	17998.00	0.00	3239.64	49.00	21286.64	2025-04-30 13:15:21	2025-08-11 19:36:34
137	f4a06547-ac70-4e87-abeb-40f75e5c30d6	59	79	\N	shipped	7996.00	0.00	1439.28	0.00	9435.28	2026-02-27 16:36:24	2026-03-01 21:58:25
138	81c6abc6-57f6-45f9-bb44-f8c84a042067	94	94	\N	delivered	21994.00	0.00	3958.92	149.00	26101.92	2025-12-01 02:43:46	2025-12-18 23:32:14
139	ec494096-aebb-4b04-bab0-e9c037b7dbdb	55	73	4	delivered	13996.00	345.24	2457.14	0.00	16107.90	2026-01-31 11:50:26	2026-02-02 16:25:03
140	594ca4a1-d42a-4b17-a5d6-bbda8c105d9a	30	149	\N	shipped	29993.00	0.00	5398.74	149.00	35540.74	2025-06-08 22:25:26	2025-07-25 12:30:49
141	450b6c04-af09-4f3b-bc51-b8150b16e27e	47	133	\N	confirmed	17998.00	0.00	3239.64	149.00	21386.64	2026-01-06 17:15:01	2026-02-10 18:19:13
142	0419950b-bc22-4642-b4d5-e3b2882447b0	18	134	12	shipped	799.00	342.53	82.16	0.00	538.63	2025-07-18 06:33:49	2025-10-22 18:40:01
143	a173e388-aee2-46d2-83e2-4829fd828692	56	14	\N	pending	11996.00	0.00	2159.28	149.00	14304.28	2026-02-23 01:39:56	2026-02-28 02:01:47
144	b87b8949-cea8-4520-bdf3-cfcd3f5d7901	100	59	15	shipped	6999.00	103.01	1241.28	149.00	8286.27	2025-08-14 15:44:59	2026-01-29 12:51:17
145	5a6a0624-7587-460e-b4b3-2c157bf64c34	65	84	\N	cancelled	111998.00	0.00	20159.64	0.00	132157.64	2025-04-23 10:16:45	2026-02-26 09:52:42
146	2ba3aa67-6a59-4209-b164-19d05f6a35b5	8	57	13	delivered	51994.00	3.61	9358.27	49.00	61397.66	2026-02-08 16:17:15	2026-02-25 04:48:12
147	1541b47d-0ec5-4ef6-b8ec-9643074104a1	3	88	\N	processing	13996.00	0.00	2519.28	49.00	16564.28	2025-03-06 16:55:22	2025-04-14 03:37:19
148	e15de80b-6035-4b87-b8d3-063be064387c	96	34	\N	delivered	60797.00	0.00	10943.46	49.00	71789.46	2026-02-15 05:34:45	2026-02-16 22:09:16
149	502ee5d2-bf02-415a-abf5-1823de65d274	14	86	\N	confirmed	6596.00	0.00	1187.28	0.00	7783.28	2025-09-05 18:30:21	2026-01-09 17:14:40
150	22fb3097-4d96-45a5-b7b4-741324ea7f03	26	115	\N	cancelled	31994.00	0.00	5758.92	0.00	37752.92	2025-11-24 13:14:54	2026-02-24 18:55:19
151	db0287ed-33ae-47f4-9dbf-9e52311bf1ea	26	78	\N	shipped	267990.00	0.00	48238.20	0.00	316228.20	2025-07-12 07:42:27	2025-09-22 01:33:03
152	a18ec971-3ccd-4fe3-8112-1e1fbbcbff34	96	23	\N	processing	42999.00	0.00	7739.82	0.00	50738.82	2025-09-16 15:28:42	2026-02-23 02:45:53
153	ccec6058-9e7a-4811-a4a7-c40fef64a125	91	81	\N	confirmed	13998.00	0.00	2519.64	99.00	16616.64	2025-03-24 17:35:19	2026-01-07 03:34:36
154	b4d98caf-2014-419b-93d2-e38a914cd9db	44	33	\N	delivered	6998.00	0.00	1259.64	49.00	8306.64	2025-06-23 21:14:17	2026-01-22 12:25:50
155	533af8d1-b1f9-4285-85b7-6f2c7ed521e3	95	85	8	delivered	40491.00	0.02	7288.38	99.00	47878.36	2025-08-06 09:16:02	2025-10-05 11:50:07
156	ac3dd352-d8aa-49d5-bac9-e10411f0345e	15	86	\N	processing	6999.00	0.00	1259.82	149.00	8407.82	2025-10-19 12:40:27	2026-01-29 07:39:30
157	9c742aeb-9aef-4caf-b0fd-d96dfff11ffe	86	17	\N	delivered	1998.00	0.00	359.64	0.00	2357.64	2026-01-10 06:55:56	2026-01-31 21:41:18
158	f360b393-a08c-41cc-b69b-a25881da7689	35	122	\N	delivered	34993.00	0.00	6298.74	99.00	41390.74	2025-06-28 01:04:27	2025-07-18 01:51:02
159	086885b1-c9c0-43f5-af70-2df9faaadfa2	82	150	\N	delivered	58989.00	0.00	10618.02	49.00	69656.02	2026-01-15 07:27:10	2026-02-12 16:21:23
160	305aa681-1a23-4300-a5ee-3594b8aed5cf	12	105	19	cancelled	4998.00	138.28	874.75	149.00	5883.47	2025-09-30 14:40:23	2025-12-18 23:24:29
161	da7ba7b6-ac6f-4dc6-8f3e-dd361cf98e47	100	24	15	shipped	75992.00	164.85	13648.89	49.00	89525.04	2025-06-28 14:55:40	2025-09-13 08:43:38
162	016fd178-22ac-46ba-b119-6a7f4bc02f72	13	136	\N	delivered	13998.00	0.00	2519.64	149.00	16666.64	2025-08-03 00:45:29	2025-09-03 23:05:28
163	b965a6cf-bf65-4679-afe8-fd26eec5bee6	5	103	\N	delivered	10497.00	0.00	1889.46	0.00	12386.46	2025-09-21 09:59:37	2026-02-12 13:12:15
164	aa1afc7f-46e5-4e73-8eaf-d6c847dbe187	76	130	\N	confirmed	85884.00	0.00	15459.12	0.00	101343.12	2025-12-04 05:55:29	2026-01-30 13:12:06
165	5b906317-3fa6-43d2-b8e9-186c0025f3a7	66	132	14	delivered	134791.00	305.93	24207.31	0.00	158692.38	2025-08-10 13:42:53	2025-12-26 17:27:11
166	2ed1e220-df08-4cd6-a010-4affdb60f886	45	115	\N	cancelled	63192.00	0.00	11374.56	149.00	74715.56	2025-12-27 07:29:29	2026-01-12 17:00:50
167	4b6f879f-917d-4ed5-88be-cfed4d862643	46	85	5	shipped	177993.00	421.69	31962.84	149.00	209683.15	2025-11-01 01:32:03	2026-02-10 20:05:12
168	070c2896-80c2-4ffd-981e-70d66a2e54e8	20	90	\N	cancelled	1998.00	0.00	359.64	49.00	2406.64	2025-06-15 08:26:55	2025-11-01 02:14:47
169	0b4c3df6-56c2-4de6-8caf-9abcf2a99105	16	105	7	processing	89997.00	289.56	16147.34	149.00	106003.78	2025-09-21 14:16:58	2025-12-24 05:19:50
170	b78ad2c6-45dc-4cb5-9f7f-d40d2fd30db1	8	53	\N	processing	59996.00	0.00	10799.28	0.00	70795.28	2025-10-09 14:14:33	2025-10-28 14:44:44
171	642df951-54c3-4aff-ad36-89fe1b236bee	93	103	\N	delivered	29998.00	0.00	5399.64	99.00	35496.64	2025-12-30 04:38:24	2026-02-25 00:26:42
172	5957cf06-1fed-45be-827d-39cddd6b3a1e	7	72	\N	delivered	51996.00	0.00	9359.28	149.00	61504.28	2025-09-10 01:13:22	2025-11-29 20:03:36
173	b2227236-62cf-445e-9d0d-151845538ddb	95	67	\N	delivered	16492.00	0.00	2968.56	0.00	19460.56	2025-05-26 12:04:17	2025-06-13 12:26:28
174	19d5f6fa-5dbc-4521-b8fb-76fcffd9cf72	87	5	\N	delivered	1799.00	0.00	323.82	149.00	2271.82	2026-02-06 23:44:05	2026-02-09 12:01:24
175	815622f7-ca57-468f-a294-e2b46fbb874b	97	137	\N	confirmed	224997.00	0.00	40499.46	0.00	265496.46	2026-02-26 09:17:51	2026-03-01 19:11:18
176	38841c32-d457-4468-8fdf-e1f648b65f3d	17	33	\N	returned	2999.00	0.00	539.82	49.00	3587.82	2025-08-11 15:56:10	2025-12-30 14:10:14
177	3bf98b22-6a1b-4b5d-bafa-664902c5cb73	99	22	\N	cancelled	6999.00	0.00	1259.82	149.00	8407.82	2025-12-09 03:59:53	2026-01-26 15:16:00
178	97c72b19-d677-4a0d-bcb8-9f7a93793cd2	42	102	17	delivered	38994.00	429.45	6941.62	99.00	45605.17	2025-09-08 10:07:03	2025-11-17 16:24:33
179	e1000c8b-2a3c-45f6-86f3-37afd7aff8d2	74	82	6	shipped	13692.00	322.39	2406.53	0.00	15776.14	2025-03-08 16:59:46	2025-10-11 09:08:27
180	d7514213-f6aa-4c4e-93aa-52d1f29092c7	52	124	\N	shipped	133994.00	0.00	24118.92	49.00	158161.92	2025-11-09 10:22:23	2026-02-05 20:25:44
181	ed06d56e-f4c5-4dbb-b8f9-513b331a927f	50	143	\N	delivered	6998.00	0.00	1259.64	99.00	8356.64	2026-01-28 05:46:18	2026-02-19 05:49:26
182	2fc746e2-d058-413f-a864-afae5b7f3cf3	42	51	\N	cancelled	20493.00	0.00	3688.74	99.00	24280.74	2025-06-26 22:04:02	2025-07-29 09:17:24
183	fd8ced56-a671-4e01-81ca-9c8bd97528d3	80	67	\N	confirmed	35190.00	0.00	6334.20	49.00	41573.20	2025-09-24 14:40:20	2026-01-31 22:04:00
184	e87e4e41-557a-4dac-9499-945b3a236a66	59	30	\N	delivered	89997.00	0.00	16199.46	0.00	106196.46	2025-12-27 04:41:50	2025-12-27 17:36:12
185	b08973d0-06bc-4805-a679-0b6e2fc0fe20	37	122	\N	processing	2499.00	0.00	449.82	149.00	3097.82	2026-01-18 07:17:55	2026-02-13 05:13:43
186	168071ff-6b6a-4ec6-80e9-57752891a511	69	57	\N	processing	226996.00	0.00	40859.28	0.00	267855.28	2025-07-28 05:50:43	2026-01-08 18:19:00
187	cd8d3bac-05c2-42ab-bc54-540662156da5	100	3	9	returned	30496.00	313.66	5432.82	49.00	35664.16	2025-10-20 05:46:04	2026-02-15 01:23:52
188	8dbae382-06b4-4ea7-a3ea-2e6d76bff71a	18	6	\N	delivered	27992.00	0.00	5038.56	0.00	33030.56	2025-12-08 06:15:28	2026-02-02 18:45:26
189	e5d36845-901e-4953-a680-f23a1e17ce23	11	99	\N	delivered	27996.00	0.00	5039.28	99.00	33134.28	2025-06-23 19:34:32	2026-01-07 01:15:56
190	499615cf-4dda-4a16-96e8-7c27fdf68baa	91	16	\N	delivered	7996.00	0.00	1439.28	49.00	9484.28	2025-11-27 03:44:59	2026-02-25 05:08:25
191	dc147e3b-6a80-43c2-8f82-f158e3d001d3	51	70	7	delivered	366985.00	145.47	66031.12	0.00	432870.65	2025-11-29 13:08:09	2025-12-16 14:49:58
192	1f202d4a-8261-44cf-bccf-2a7f1d98797e	30	57	\N	processing	7996.00	0.00	1439.28	149.00	9584.28	2025-11-14 07:09:56	2025-11-18 00:48:59
193	1472efa1-edc9-4af4-ba6d-e8a9f790d5b7	100	6	\N	delivered	46493.00	0.00	8368.74	49.00	54910.74	2026-01-13 23:32:02	2026-02-21 14:34:01
194	e1fbfd28-ee24-4371-b8ca-d296095736fe	33	125	\N	delivered	7594.00	0.00	1366.92	0.00	8960.92	2025-07-21 00:30:05	2026-01-15 15:18:32
195	f6e5fd85-894e-441a-9ffa-3bbdcc882d80	21	8	4	processing	134993.00	98.63	24280.99	49.00	159224.36	2026-01-18 13:20:01	2026-01-21 04:44:30
196	ec694345-a869-4345-95de-67dca1c2d62b	33	55	\N	delivered	7497.00	0.00	1349.46	149.00	8995.46	2026-01-17 22:35:24	2026-01-22 18:23:47
197	43e0702e-db70-4a7c-9e1d-8084a25858e6	58	12	\N	delivered	205989.00	0.00	37078.02	0.00	243067.02	2025-10-17 00:24:01	2025-12-06 04:02:05
198	82bdf38a-87d2-4cb5-85ea-2dfb5ad835ec	60	145	9	pending	25787.00	418.93	4566.25	0.00	29934.32	2026-02-20 17:55:30	2026-02-21 15:33:34
199	920beede-a2a6-4eb0-ab8a-98b791b83494	14	71	\N	shipped	8997.00	0.00	1619.46	99.00	10715.46	2026-01-18 07:28:50	2026-02-06 11:31:48
200	836a50f8-087b-4aab-b85e-d0be032aa3cb	17	26	19	processing	3196.00	451.03	494.09	0.00	3239.06	2025-11-13 23:09:09	2025-11-26 17:05:58
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.payments (payment_id, order_id, method, gateway, status, amount, gateway_txn_id, created_at, paid_at) FROM stdin;
1	1	Debit Card	CCAvenue	pending	30137.30	TXN535E27EA5F17	2025-12-03 18:12:10	\N
2	3	Net Banking	PayU	success	2924.91	TXNC3D9F6FC22EB	2025-11-28 12:04:47	2025-11-28 12:08:47
3	4	Debit Card	Razorpay	success	29537.30	TXN358A8AB59485	2025-10-19 02:59:36	2025-10-19 03:03:36
4	5	Debit Card	Razorpay	success	12784.50	TXNC099E4236D55	2025-08-13 04:04:59	2025-08-13 04:09:59
5	6	Wallet	MobiKwik	success	1970.54	TXN0A9F766E5BF3	2025-09-02 19:23:49	2025-09-02 19:28:49
6	7	Net Banking	Razorpay	success	176855.76	TXN7807B63CC1FA	2025-08-14 13:18:58	2025-08-14 13:23:58
7	8	UPI	BHIM	success	63533.71	TXN9A3E5FBF0B21	2025-03-11 18:02:19	2025-03-11 18:05:19
8	9	COD	COD	success	83435.88	TXN649C59245AD4	2025-11-07 16:29:24	2025-11-07 16:34:24
9	10	COD	COD	success	5947.14	TXN81D9956F82C6	2025-04-02 14:19:56	2025-04-02 14:20:56
10	11	Wallet	MobiKwik	success	386953.39	TXNFD2742F0DB30	2025-04-23 18:02:44	2025-04-23 18:07:44
11	12	Wallet	MobiKwik	success	202656.07	TXN7990AF3D45D4	2025-03-26 07:09:48	2025-03-26 07:13:48
12	13	Net Banking	PayU	success	3093.77	TXN302F2976016F	2025-10-21 09:43:11	2025-10-21 09:48:11
13	15	Credit Card	PayU	failed	45952.80	TXNBAFC2B19F7DD	2025-11-19 18:15:51	\N
14	16	Net Banking	Razorpay	failed	70527.54	TXNBB0CC6B400CB	2026-01-07 11:10:41	\N
15	17	Credit Card	CCAvenue	success	14149.24	TXN68E9D52845E0	2026-01-13 08:18:17	2026-01-13 08:23:17
16	18	Debit Card	Razorpay	success	34186.10	TXNC7EC1295C882	2025-07-10 17:54:25	2025-07-10 17:59:25
17	19	COD	COD	success	166243.48	TXN58029F3E4554	2025-10-17 02:56:19	2025-10-17 03:01:19
18	20	Wallet	MobiKwik	success	71811.55	TXN53A40230ACED	2025-08-26 05:35:25	2025-08-26 05:37:25
19	21	Debit Card	PayU	success	25680.30	TXN11BB8CADCA8E	2026-01-27 21:33:09	2026-01-27 21:34:09
20	22	Net Banking	Razorpay	success	5641.25	TXNA9CB1DAD9668	2025-07-28 12:00:39	2025-07-28 12:05:39
21	23	Net Banking	Razorpay	success	605.39	TXNC303A86A44BB	2026-02-28 01:26:07	2026-02-28 01:31:07
22	24	Credit Card	PayU	success	156096.42	TXNA03C7F8F3AD8	2025-10-16 23:41:49	2025-10-16 23:46:49
23	25	UPI	GPay	success	56660.25	TXN9DC31819B82E	2025-07-22 11:09:06	2025-07-22 11:13:06
24	26	UPI	Paytm	success	159830.52	TXND1B880D2BFBD	2025-07-18 14:00:46	2025-07-18 14:05:46
25	27	Net Banking	Razorpay	success	11753.95	TXN049AC62C1086	2025-06-25 12:43:37	2025-06-25 12:47:37
26	28	Debit Card	PayU	success	92082.08	TXN8FA643A6F466	2025-07-13 19:40:00	2025-07-13 19:44:00
27	29	Net Banking	PayU	pending	53146.18	TXN4F4A2EE461B9	2025-09-19 23:24:57	\N
28	30	UPI	GPay	success	7881.32	TXN8192A5C4C05B	2025-08-12 01:07:44	2025-08-12 01:08:44
29	31	Credit Card	CCAvenue	success	4086.25	TXNEDEDB7231F8C	2025-04-16 05:06:07	2025-04-16 05:07:07
30	32	UPI	GPay	success	32505.71	TXN377C10AA8C78	2025-12-07 14:03:18	2025-12-07 14:04:18
31	33	COD	COD	success	70365.50	TXN09C91F2CBE4E	2025-12-22 05:11:12	2025-12-22 05:16:12
32	34	Wallet	MobiKwik	success	16181.27	TXN94460350045E	2026-02-20 20:22:32	2026-02-20 20:24:32
33	35	Credit Card	PayU	success	31578.12	TXN14509B6DA05C	2025-10-17 20:25:02	2025-10-17 20:29:02
34	36	Wallet	Amazon Pay	success	11612.64	TXND92F41508F83	2025-12-24 10:55:18	2025-12-24 11:00:18
35	37	UPI	PhonePe	success	303422.19	TXNFA847285C896	2025-08-26 08:16:42	2025-08-26 08:20:42
36	38	COD	COD	success	29417.31	TXN268E9D1D7168	2025-05-18 05:45:44	2025-05-18 05:49:44
37	39	Net Banking	PayU	success	1985.96	TXN7C993B90E0DB	2026-01-03 03:14:15	2026-01-03 03:18:15
38	40	COD	COD	success	23879.86	TXN6A7AC630CEF9	2025-05-21 11:45:01	2025-05-21 11:50:01
39	41	Net Banking	PayU	success	2217.01	TXND2F23B191D92	2025-07-07 00:02:15	2025-07-07 00:03:15
40	42	COD	COD	success	5755.69	TXNF890327B86C6	2025-10-30 19:47:45	2025-10-30 19:51:45
41	43	Wallet	MobiKwik	success	12236.50	TXN809C0B4D32AA	2025-08-08 14:16:51	2025-08-08 14:18:51
42	44	Debit Card	CCAvenue	success	3619.29	TXN1D7893715927	2025-05-02 14:30:04	2025-05-02 14:34:04
43	45	Wallet	Amazon Pay	success	52968.74	TXN023B94E6C064	2025-08-22 11:48:03	2025-08-22 11:52:03
44	46	Wallet	MobiKwik	success	61076.24	TXNF53E96D19341	2025-05-17 21:38:35	2025-05-17 21:40:35
45	47	COD	COD	success	4487.17	TXN98F938575E8E	2025-05-22 06:20:55	2025-05-22 06:23:55
46	48	Wallet	Paytm	success	44562.82	TXNC6787DCACCC2	2025-04-12 11:29:38	2025-04-12 11:34:38
47	49	Debit Card	PayU	success	42551.65	TXN65B8E6C757DF	2026-01-02 03:14:01	2026-01-02 03:15:01
48	50	Net Banking	PayU	success	24625.63	TXN69636CB4D939	2025-05-31 16:40:46	2025-05-31 16:42:46
49	51	Credit Card	CCAvenue	success	218962.95	TXN7E49A248F2DC	2026-01-01 03:32:31	2026-01-01 03:35:31
50	52	Net Banking	Razorpay	success	31763.49	TXND74C627509F3	2025-12-02 10:16:00	2025-12-02 10:18:00
51	53	Net Banking	Razorpay	success	3019.36	TXN9CACF1B104D3	2025-08-26 06:07:59	2025-08-26 06:08:59
52	54	Wallet	Paytm	success	354182.42	TXN6B834E84C873	2025-05-01 22:35:38	2025-05-01 22:37:38
53	55	UPI	GPay	success	44046.03	TXN32B6C787081A	2025-11-22 01:16:37	2025-11-22 01:21:37
54	56	Wallet	MobiKwik	success	6240.06	TXN1C54DA09D199	2025-07-19 11:47:53	2025-07-19 11:49:53
55	57	Net Banking	PayU	success	34096.91	TXN2C333CB9D61B	2025-12-31 09:45:57	2025-12-31 09:47:57
56	58	Net Banking	PayU	success	29132.21	TXN5F4BBFB1B974	2025-04-25 05:46:29	2025-04-25 05:47:29
57	59	Debit Card	PayU	success	16125.17	TXN176221CC732C	2025-05-04 03:56:35	2025-05-04 04:01:35
58	60	COD	COD	success	6802.70	TXN287665E5598B	2025-04-28 10:36:18	2025-04-28 10:38:18
59	61	UPI	BHIM	success	215833.28	TXN79DBBC0258C6	2026-02-05 04:24:17	2026-02-05 04:26:17
60	62	COD	COD	success	14906.29	TXN67DAF7B15DC6	2025-07-03 22:59:11	2025-07-03 23:04:11
61	64	Net Banking	Razorpay	success	202773.73	TXNEC46C5D534E0	2025-09-18 12:45:09	2025-09-18 12:48:09
62	65	Net Banking	Razorpay	success	137762.31	TXNF39B2A1A22E7	2025-10-01 09:52:36	2025-10-01 09:57:36
63	66	Net Banking	Razorpay	success	9027.04	TXNB0C6642569D1	2025-12-30 16:37:46	2025-12-30 16:39:46
64	67	Wallet	Paytm	success	5388.09	TXNF83C2ADB7058	2025-11-07 14:34:03	2025-11-07 14:37:03
65	68	Net Banking	PayU	success	18921.81	TXN7DDCE2EC29A5	2025-10-09 16:39:28	2025-10-09 16:44:28
66	69	Net Banking	PayU	success	8472.49	TXN48DC3D43F41B	2025-11-11 14:56:27	2025-11-11 14:58:27
67	70	Debit Card	Razorpay	success	56274.17	TXN179EE6B6056B	2025-06-17 07:26:39	2025-06-17 07:28:39
68	71	Credit Card	CCAvenue	pending	12318.08	TXN2D08EA766379	2025-03-18 08:46:45	\N
69	73	Credit Card	Razorpay	success	32828.12	TXNFB8F65232EF9	2026-01-02 18:02:33	2026-01-02 18:03:33
70	77	COD	COD	success	42390.19	TXN38303B6BD4D5	2025-04-25 01:44:01	2025-04-25 01:46:01
71	78	Wallet	Amazon Pay	success	3746.18	TXN1B4C4BA6433F	2025-06-12 21:04:36	2025-06-12 21:08:36
72	79	Debit Card	CCAvenue	success	31820.14	TXN6DB66248F9E4	2025-06-03 16:29:01	2025-06-03 16:31:01
73	80	Net Banking	PayU	success	24912.67	TXND2171D998637	2025-07-20 14:51:08	2025-07-20 14:52:08
74	82	Credit Card	CCAvenue	success	33070.85	TXN9C3E8827A613	2025-05-29 03:44:24	2025-05-29 03:45:24
75	83	COD	COD	success	44515.70	TXN6C2AB13BA817	2025-11-05 00:49:08	2025-11-05 00:50:08
76	84	UPI	GPay	success	67756.68	TXNAEDA242DC18D	2025-09-11 09:25:23	2025-09-11 09:28:23
77	85	Debit Card	Razorpay	success	70361.02	TXN29DC81A674D9	2025-09-03 23:34:07	2025-09-03 23:39:07
78	86	Debit Card	Razorpay	success	7192.11	TXN29733FD61745	2025-06-01 05:11:13	2025-06-01 05:16:13
79	88	Net Banking	Razorpay	success	151484.78	TXNA16740DA391B	2025-04-30 02:05:40	2025-04-30 02:09:40
80	89	Debit Card	CCAvenue	success	44552.38	TXNB9219E70D62F	2025-10-23 23:12:29	2025-10-23 23:17:29
81	91	Debit Card	Razorpay	success	3599.14	TXNE208744D183E	2025-11-27 18:02:10	2025-11-27 18:07:10
82	92	Wallet	Amazon Pay	success	281748.64	TXN258D3D45B425	2025-07-09 20:58:24	2025-07-09 20:59:24
83	93	Net Banking	Razorpay	success	114521.64	TXNAE10C629E9D9	2025-12-14 13:53:42	2025-12-14 13:57:42
84	94	Credit Card	Razorpay	success	10603.10	TXN5A6E2EE7B616	2025-03-18 10:20:58	2025-03-18 10:25:58
85	95	Wallet	Paytm	success	60954.71	TXN28A563C6D10C	2025-07-03 07:01:56	2025-07-03 07:05:56
86	96	Net Banking	PayU	success	154838.96	TXN5562B0AB58A4	2025-09-21 15:22:22	2025-09-21 15:23:22
87	97	COD	COD	success	9016.80	TXN7F388280C3F4	2026-01-08 03:40:56	2026-01-08 03:41:56
88	99	Credit Card	Razorpay	success	13901.92	TXN975555262326	2025-08-08 14:21:39	2025-08-08 14:23:39
89	100	COD	COD	success	12628.35	TXNBB6C258ED038	2025-05-25 14:59:04	2025-05-25 15:02:04
90	101	UPI	GPay	success	42382.63	TXNCF352DB37EDB	2025-08-05 22:40:21	2025-08-05 22:44:21
91	102	Net Banking	PayU	success	12677.42	TXN8FAC91D857EC	2025-06-24 06:23:39	2025-06-24 06:28:39
92	103	Credit Card	Razorpay	failed	22312.20	TXNE8DC41FE59AA	2025-05-16 17:44:34	\N
93	104	Debit Card	PayU	success	8907.77	TXN9262C982A5B9	2025-10-28 00:34:37	2025-10-28 00:35:37
94	105	Debit Card	PayU	success	59978.63	TXN42A9E0F6E585	2025-10-15 09:10:39	2025-10-15 09:14:39
95	106	Wallet	Amazon Pay	success	30123.77	TXN93A44E72B513	2026-01-19 21:21:04	2026-01-19 21:25:04
96	107	COD	COD	success	18601.66	TXN99633CA20173	2025-06-25 01:51:59	2025-06-25 01:55:59
97	108	Wallet	Amazon Pay	success	8393.72	TXN0C1F1C318B34	2025-10-29 00:58:08	2025-10-29 00:59:08
98	109	COD	COD	pending	6938.47	TXNB36E4A48C053	2026-01-10 05:54:08	\N
99	111	COD	COD	success	176561.93	TXNAF67C0A4DCF6	2025-11-11 18:44:29	2025-11-11 18:46:29
100	112	COD	COD	success	4256.93	TXN2BB8430279A5	2025-05-23 02:41:42	2025-05-23 02:46:42
101	113	Wallet	Amazon Pay	success	1910.29	TXNF703CFB8D303	2026-01-25 23:47:10	2026-01-25 23:50:10
102	114	Net Banking	Razorpay	success	455390.73	TXN50E7606544DC	2025-07-22 00:17:47	2025-07-22 00:18:47
103	115	UPI	GPay	success	30610.06	TXN9ED94DFCF12F	2025-09-08 05:57:45	2025-09-08 05:59:45
104	116	COD	COD	success	84741.93	TXNBC3EBFF735D2	2026-02-07 23:09:04	2026-02-07 23:13:04
105	117	Wallet	Amazon Pay	success	28611.04	TXNC2F484BE1B74	2025-11-08 21:38:28	2025-11-08 21:41:28
106	119	Wallet	MobiKwik	success	32336.08	TXN8F6AEB3FBAB4	2026-01-08 15:45:41	2026-01-08 15:46:41
107	120	Net Banking	Razorpay	success	21963.73	TXN197669BECBC3	2025-07-18 14:26:45	2025-07-18 14:29:45
108	121	Credit Card	Razorpay	success	75554.31	TXN00E8AF0FC670	2026-01-09 00:05:40	2026-01-09 00:08:40
109	123	COD	COD	success	87383.67	TXN65D0FE24094E	2025-07-17 01:10:28	2025-07-17 01:12:28
110	124	COD	COD	success	48085.21	TXNA512CEA08D8D	2025-12-18 13:11:26	2025-12-18 13:16:26
111	125	Net Banking	Razorpay	success	16198.87	TXNEE5B9E38D2F9	2025-07-30 00:40:45	2025-07-30 00:41:45
112	126	Net Banking	Razorpay	success	48931.21	TXNB786044C8DA2	2025-12-25 19:46:42	2025-12-25 19:51:42
113	127	Debit Card	CCAvenue	success	12594.23	TXN4D2C0483814C	2025-07-26 01:32:18	2025-07-26 01:35:18
114	128	Net Banking	Razorpay	success	7994.12	TXNE3AE36DC9CEB	2025-05-12 22:10:08	2025-05-12 22:14:08
115	129	Credit Card	CCAvenue	success	70265.18	TXN2945B1EA22F0	2025-04-05 04:38:44	2025-04-05 04:41:44
116	130	UPI	GPay	success	18914.91	TXN68729AE61A2A	2025-03-06 04:47:31	2025-03-06 04:49:31
117	131	Credit Card	CCAvenue	pending	28480.70	TXND94518CD4D9C	2025-05-05 01:13:31	\N
118	132	COD	COD	success	15928.74	TXNF77975746886	2025-09-17 21:23:50	2025-09-17 21:24:50
119	133	COD	COD	success	6084.59	TXN018F97A58A88	2025-08-18 22:25:07	2025-08-18 22:30:07
120	134	COD	COD	success	4012.77	TXN09A202D6A845	2025-11-22 15:46:53	2025-11-22 15:49:53
121	135	Net Banking	PayU	success	2347.05	TXN7A5C11040481	2025-05-23 07:43:15	2025-05-23 07:44:15
122	136	Wallet	MobiKwik	success	102144.59	TXNFAFC78939910	2025-04-30 13:36:21	2025-04-30 13:37:21
123	137	Wallet	Amazon Pay	success	15906.65	TXN40B87618CD6A	2026-02-27 17:01:24	2026-02-27 17:04:24
124	138	Credit Card	Razorpay	success	108089.63	TXN59E145ACE1F9	2025-12-01 03:06:46	2025-12-01 03:10:46
125	139	Wallet	MobiKwik	success	15797.07	TXNB892E5AD85C9	2026-01-31 12:05:26	2026-01-31 12:06:26
126	140	Wallet	MobiKwik	success	13920.57	TXN7D08E1F46C17	2025-06-08 22:44:26	2025-06-08 22:48:26
127	141	UPI	Paytm	success	99234.53	TXNDC051B9F695E	2026-01-06 17:32:01	2026-01-06 17:36:01
128	142	Net Banking	Razorpay	success	309940.23	TXN16F45920B375	2025-07-18 06:51:49	2025-07-18 06:56:49
129	143	Credit Card	CCAvenue	failed	8245.98	TXN1AB87E373C5D	2026-02-23 02:04:56	\N
130	144	Credit Card	Razorpay	success	71773.58	TXN540DEEF32DDB	2025-08-14 15:51:59	2025-08-14 15:53:59
131	146	UPI	Paytm	success	5392.56	TXN115BB474D106	2026-02-08 16:19:15	2026-02-08 16:24:15
132	147	Wallet	Amazon Pay	success	38159.37	TXNCFECF7CC848D	2025-03-06 17:22:22	2025-03-06 17:24:22
133	148	Credit Card	PayU	success	129331.40	TXNA72A0199BA83	2026-02-15 05:50:45	2026-02-15 05:52:45
134	149	UPI	GPay	success	280874.37	TXN5134E9EAED15	2025-09-05 18:53:21	2025-09-05 18:56:21
135	151	Debit Card	Razorpay	success	16123.92	TXN7AEAA8860480	2025-07-12 07:52:27	2025-07-12 07:55:27
136	152	Credit Card	PayU	success	28999.32	TXN791525F95E46	2025-09-16 15:38:42	2025-09-16 15:39:42
137	153	Wallet	MobiKwik	success	267915.98	TXN69AA769B650A	2025-03-24 17:52:19	2025-03-24 17:55:19
138	154	Debit Card	CCAvenue	success	31935.40	TXNCADC72113D8E	2025-06-23 21:16:17	2025-06-23 21:17:17
139	155	UPI	Paytm	success	9057.66	TXN65AEB54EDF04	2025-08-06 09:27:02	2025-08-06 09:31:02
140	156	UPI	Paytm	success	1889.40	TXN3FA3F5043B2A	2025-10-19 12:52:27	2025-10-19 12:55:27
141	157	Net Banking	PayU	success	53086.16	TXN1EF5C8DAF2CE	2026-01-10 07:17:56	2026-01-10 07:20:56
142	158	Debit Card	PayU	success	6869.80	TXN77F81D660C63	2025-06-28 01:16:27	2025-06-28 01:20:27
143	159	Credit Card	Razorpay	success	5141.42	TXNC7C373A9493C	2026-01-15 07:29:10	2026-01-15 07:34:10
144	161	Net Banking	Razorpay	success	43351.26	TXNA623524A34E8	2025-06-28 15:17:40	2025-06-28 15:20:40
145	162	UPI	GPay	success	75091.25	TXNFE19CD30354B	2025-08-03 00:54:29	2025-08-03 00:56:29
146	163	Credit Card	PayU	success	8858.73	TXNF2DDFEC45EFA	2025-09-21 10:14:37	2025-09-21 10:16:37
147	164	Net Banking	PayU	pending	18858.81	TXNEB75F308B3C4	2025-12-04 06:13:29	\N
148	165	COD	COD	success	70945.72	TXNA22AFA43AB3C	2025-08-10 13:51:53	2025-08-10 13:56:53
149	167	UPI	Paytm	success	8494.32	TXNFE9D3C6213CB	2025-11-01 01:38:03	2025-11-01 01:39:03
150	169	COD	COD	success	2838.74	TXN72AF25BC4490	2025-09-21 14:31:58	2025-09-21 14:36:58
151	170	Credit Card	CCAvenue	success	11656.13	TXN343AE40475CB	2025-10-09 14:26:33	2025-10-09 14:31:33
152	171	Wallet	Amazon Pay	success	5843.91	TXN8EAC2BAF683D	2025-12-30 05:07:24	2025-12-30 05:09:24
153	172	Net Banking	Razorpay	success	6482.18	TXN574EAA924163	2025-09-10 01:29:22	2025-09-10 01:32:22
154	173	Debit Card	CCAvenue	success	6822.77	TXN39601739655A	2025-05-26 12:09:17	2025-05-26 12:10:17
155	174	COD	COD	success	12701.78	TXN5E6FEF1119A1	2026-02-06 23:49:05	2026-02-06 23:51:05
156	175	UPI	BHIM	pending	4403.54	TXNCB9DB01BEE45	2026-02-26 09:32:51	\N
157	176	COD	COD	success	20965.49	TXND13CFDE7B905	2025-08-11 16:11:10	2025-08-11 16:15:10
158	178	Debit Card	Razorpay	success	9434.96	TXN0163FFA438C0	2025-09-08 10:11:03	2025-09-08 10:16:03
159	179	Credit Card	CCAvenue	success	2958.35	TXN9019C4F4907E	2025-03-08 17:15:46	2025-03-08 17:17:46
160	180	Credit Card	CCAvenue	success	294224.01	TXN48BF2EEAF798	2025-11-09 10:47:23	2025-11-09 10:49:23
161	181	COD	COD	success	6820.72	TXN32E3DD41E997	2026-01-28 06:00:18	2026-01-28 06:05:18
162	183	Wallet	MobiKwik	failed	76771.53	TXN21DCDC554279	2025-09-24 14:41:20	\N
163	184	Debit Card	Razorpay	success	4378.73	TXN5EAD113A715B	2025-12-27 04:51:50	2025-12-27 04:53:50
164	185	UPI	Paytm	success	115230.63	TXN150E6D3CC888	2026-01-18 07:47:55	2026-01-18 07:51:55
165	186	COD	COD	success	6349.53	TXN725A84E14A16	2025-07-28 05:56:43	2025-07-28 05:59:43
166	187	COD	COD	success	12961.44	TXN9F7F4547AC4D	2025-10-20 06:04:04	2025-10-20 06:08:04
167	188	Credit Card	Razorpay	success	125204.18	TXN1F716F2D220F	2025-12-08 06:33:28	2025-12-08 06:38:28
168	189	Wallet	Paytm	success	35329.28	TXN85C8FFAF7D89	2025-06-23 19:39:32	2025-06-23 19:44:32
169	190	UPI	BHIM	success	208673.56	TXNCED30D845B7D	2025-11-27 04:14:59	2025-11-27 04:16:59
170	191	COD	COD	success	7793.14	TXNDB3817078D5B	2025-11-29 13:36:09	2025-11-29 13:39:09
171	192	COD	COD	success	10176.13	TXN7BDD2FF74AFC	2025-11-14 07:16:56	2025-11-14 07:20:56
172	193	Debit Card	CCAvenue	success	74399.74	TXN9BE80F725191	2026-01-13 23:51:02	2026-01-13 23:55:02
173	194	Debit Card	PayU	success	20848.05	TXNACE94BD5A5E3	2025-07-21 00:37:05	2025-07-21 00:38:05
174	195	Debit Card	Razorpay	success	44297.06	TXN6C32FE2CA130	2026-01-18 13:21:01	2026-01-18 13:26:01
175	196	Wallet	Amazon Pay	success	74995.71	TXN39A5E09C6D53	2026-01-17 23:04:24	2026-01-17 23:06:24
176	197	Net Banking	Razorpay	success	10173.05	TXNDB654F9FF3A9	2025-10-17 00:44:01	2025-10-17 00:46:01
177	198	COD	COD	success	44334.97	TXN0AECE9C3A2B1	2026-02-20 18:00:30	2026-02-20 18:04:30
178	199	Credit Card	Razorpay	success	8134.43	TXN768337135C1C	2026-01-18 07:54:50	2026-01-18 07:57:50
179	200	Credit Card	Razorpay	success	11402.31	TXN5B1F0558BCF1	2025-11-13 23:34:09	2025-11-13 23:35:09
\.


--
-- Data for Name: product_images; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.product_images (image_id, product_id, variant_id, url, is_primary) FROM stdin;
1	1	\N	https://cdn.store.com/products/1/img_1.jpg	t
2	1	1	https://cdn.store.com/products/1/img_2.jpg	f
3	1	1	https://cdn.store.com/products/1/img_3.jpg	f
4	2	\N	https://cdn.store.com/products/2/img_1.jpg	t
5	2	3	https://cdn.store.com/products/2/img_2.jpg	f
6	2	3	https://cdn.store.com/products/2/img_3.jpg	f
7	3	\N	https://cdn.store.com/products/3/img_1.jpg	t
8	4	\N	https://cdn.store.com/products/4/img_1.jpg	t
9	5	\N	https://cdn.store.com/products/5/img_1.jpg	t
10	5	6	https://cdn.store.com/products/5/img_2.jpg	f
11	6	\N	https://cdn.store.com/products/6/img_1.jpg	t
12	6	8	https://cdn.store.com/products/6/img_2.jpg	f
13	7	\N	https://cdn.store.com/products/7/img_1.jpg	t
14	7	9	https://cdn.store.com/products/7/img_2.jpg	f
15	8	\N	https://cdn.store.com/products/8/img_1.jpg	t
16	8	12	https://cdn.store.com/products/8/img_2.jpg	f
17	8	12	https://cdn.store.com/products/8/img_3.jpg	f
18	9	\N	https://cdn.store.com/products/9/img_1.jpg	t
19	9	14	https://cdn.store.com/products/9/img_2.jpg	f
20	10	\N	https://cdn.store.com/products/10/img_1.jpg	t
21	10	16	https://cdn.store.com/products/10/img_2.jpg	f
22	10	16	https://cdn.store.com/products/10/img_3.jpg	f
23	11	\N	https://cdn.store.com/products/11/img_1.jpg	t
24	11	18	https://cdn.store.com/products/11/img_2.jpg	f
25	12	\N	https://cdn.store.com/products/12/img_1.jpg	t
26	12	21	https://cdn.store.com/products/12/img_2.jpg	f
27	13	\N	https://cdn.store.com/products/13/img_1.jpg	t
28	13	22	https://cdn.store.com/products/13/img_2.jpg	f
29	13	22	https://cdn.store.com/products/13/img_3.jpg	f
30	14	\N	https://cdn.store.com/products/14/img_1.jpg	t
31	14	25	https://cdn.store.com/products/14/img_2.jpg	f
32	15	\N	https://cdn.store.com/products/15/img_1.jpg	t
33	15	26	https://cdn.store.com/products/15/img_2.jpg	f
34	16	\N	https://cdn.store.com/products/16/img_1.jpg	t
35	17	\N	https://cdn.store.com/products/17/img_1.jpg	t
36	17	31	https://cdn.store.com/products/17/img_2.jpg	f
37	17	31	https://cdn.store.com/products/17/img_3.jpg	f
38	18	\N	https://cdn.store.com/products/18/img_1.jpg	t
39	19	\N	https://cdn.store.com/products/19/img_1.jpg	t
40	19	34	https://cdn.store.com/products/19/img_2.jpg	f
41	19	34	https://cdn.store.com/products/19/img_3.jpg	f
42	20	\N	https://cdn.store.com/products/20/img_1.jpg	t
43	20	36	https://cdn.store.com/products/20/img_2.jpg	f
44	21	\N	https://cdn.store.com/products/21/img_1.jpg	t
45	21	37	https://cdn.store.com/products/21/img_2.jpg	f
46	21	37	https://cdn.store.com/products/21/img_3.jpg	f
47	22	\N	https://cdn.store.com/products/22/img_1.jpg	t
48	23	\N	https://cdn.store.com/products/23/img_1.jpg	t
49	24	\N	https://cdn.store.com/products/24/img_1.jpg	t
50	24	40	https://cdn.store.com/products/24/img_2.jpg	f
51	24	40	https://cdn.store.com/products/24/img_3.jpg	f
52	25	\N	https://cdn.store.com/products/25/img_1.jpg	t
53	25	41	https://cdn.store.com/products/25/img_2.jpg	f
54	26	\N	https://cdn.store.com/products/26/img_1.jpg	t
55	27	\N	https://cdn.store.com/products/27/img_1.jpg	t
56	28	\N	https://cdn.store.com/products/28/img_1.jpg	t
57	28	46	https://cdn.store.com/products/28/img_2.jpg	f
58	28	46	https://cdn.store.com/products/28/img_3.jpg	f
59	29	\N	https://cdn.store.com/products/29/img_1.jpg	t
60	30	\N	https://cdn.store.com/products/30/img_1.jpg	t
61	31	\N	https://cdn.store.com/products/31/img_1.jpg	t
62	31	53	https://cdn.store.com/products/31/img_2.jpg	f
63	32	\N	https://cdn.store.com/products/32/img_1.jpg	t
64	32	54	https://cdn.store.com/products/32/img_2.jpg	f
65	33	\N	https://cdn.store.com/products/33/img_1.jpg	t
66	33	55	https://cdn.store.com/products/33/img_2.jpg	f
67	34	\N	https://cdn.store.com/products/34/img_1.jpg	t
68	35	\N	https://cdn.store.com/products/35/img_1.jpg	t
69	36	\N	https://cdn.store.com/products/36/img_1.jpg	t
70	37	\N	https://cdn.store.com/products/37/img_1.jpg	t
71	38	\N	https://cdn.store.com/products/38/img_1.jpg	t
72	38	64	https://cdn.store.com/products/38/img_2.jpg	f
73	38	64	https://cdn.store.com/products/38/img_3.jpg	f
74	39	\N	https://cdn.store.com/products/39/img_1.jpg	t
75	39	66	https://cdn.store.com/products/39/img_2.jpg	f
76	40	\N	https://cdn.store.com/products/40/img_1.jpg	t
77	40	67	https://cdn.store.com/products/40/img_2.jpg	f
78	40	67	https://cdn.store.com/products/40/img_3.jpg	f
79	41	\N	https://cdn.store.com/products/41/img_1.jpg	t
80	41	69	https://cdn.store.com/products/41/img_2.jpg	f
\.


--
-- Data for Name: product_variants; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.product_variants (variant_id, product_id, sku, price, stock_qty, weight_kg, status, created_at) FROM stdin;
1	1	SKU-001-01	80520.00	49	4.47	active	2025-11-16 08:30:14
2	1	SKU-001-02	70720.00	163	1.38	active	2025-08-10 20:02:38
3	2	SKU-002-01	80160.00	88	3.32	active	2025-03-03 09:43:28
4	3	SKU-003-01	44090.00	51	0.11	active	2025-06-30 14:23:38
5	4	SKU-004-01	40080.00	113	4.67	active	2025-06-12 11:47:13
6	5	SKU-005-01	66100.00	135	3.17	active	2025-12-25 04:59:12
7	5	SKU-005-02	68760.00	195	3.07	active	2025-06-21 15:43:41
8	6	SKU-006-01	60750.00	26	4.05	active	2025-03-31 08:22:37
9	7	SKU-007-01	104420.00	14	2.14	active	2025-07-23 09:26:24
10	7	SKU-007-02	131410.00	160	4.75	active	2025-10-16 08:39:47
11	7	SKU-007-03	120030.00	49	3.81	active	2026-01-31 10:20:50
12	8	SKU-008-01	72970.00	44	1.40	active	2025-07-07 19:01:54
13	8	SKU-008-02	68040.00	33	4.52	active	2026-02-02 01:38:31
14	9	SKU-009-01	30140.00	183	0.98	active	2025-06-07 03:43:54
15	9	SKU-009-02	28560.00	118	2.91	active	2026-02-10 13:11:56
16	10	SKU-010-01	1420.00	122	2.91	active	2025-10-31 01:21:30
17	10	SKU-010-02	1680.00	121	3.36	active	2025-03-31 00:40:38
18	11	SKU-011-01	3360.00	117	2.66	active	2025-04-15 14:38:28
19	11	SKU-011-02	3440.00	126	0.45	active	2025-11-11 10:44:32
20	11	SKU-011-03	3790.00	145	3.44	active	2025-06-16 22:28:23
21	12	SKU-012-01	1040.00	105	1.38	active	2025-04-23 21:01:56
22	13	SKU-013-01	96050.00	101	0.28	active	2025-07-12 23:18:13
23	13	SKU-013-02	87360.00	142	3.80	active	2025-05-02 13:28:58
24	13	SKU-013-03	94300.00	14	3.51	active	2025-08-11 05:24:24
25	14	SKU-014-01	2200.00	29	2.47	active	2025-06-15 22:41:37
26	15	SKU-015-01	2660.00	18	2.84	active	2025-05-17 23:43:48
27	15	SKU-015-02	2730.00	44	3.54	active	2025-11-10 10:39:34
28	16	SKU-016-01	3040.00	173	0.66	active	2025-04-19 19:36:30
29	16	SKU-016-02	3650.00	38	2.77	active	2025-03-14 20:22:03
30	16	SKU-016-03	3600.00	165	1.96	active	2025-07-17 10:40:02
31	17	SKU-017-01	4210.00	194	4.85	active	2025-05-03 13:38:33
32	18	SKU-018-01	9840.00	87	4.07	active	2025-08-18 09:05:16
33	18	SKU-018-02	8520.00	45	3.72	active	2025-04-27 22:05:30
34	19	SKU-019-01	15910.00	133	3.68	active	2025-03-06 20:51:28
35	19	SKU-019-02	14370.00	174	3.99	active	2025-12-30 23:53:19
36	20	SKU-020-01	7290.00	187	3.99	active	2026-02-04 12:05:57
37	21	SKU-021-01	1010.00	41	4.39	active	2026-01-21 16:06:12
38	22	SKU-022-01	1420.00	95	1.34	active	2025-10-16 20:38:32
39	23	SKU-023-01	2400.00	5	1.57	active	2025-05-02 16:23:02
40	24	SKU-024-01	2040.00	73	4.07	active	2025-06-24 20:25:16
41	25	SKU-025-01	5120.00	109	4.03	active	2025-03-17 15:34:26
42	25	SKU-025-02	5440.00	155	3.45	active	2026-01-24 18:42:19
43	26	SKU-026-01	2340.00	8	1.95	active	2025-06-15 02:52:00
44	26	SKU-026-02	2310.00	140	0.84	active	2025-11-18 21:42:24
45	27	SKU-027-01	3270.00	73	3.72	active	2025-08-11 18:17:47
46	28	SKU-028-01	1620.00	198	1.22	active	2025-09-21 13:08:50
47	28	SKU-028-02	1500.00	13	1.14	active	2025-11-08 13:59:22
48	28	SKU-028-03	1450.00	145	0.56	active	2025-03-03 16:15:19
49	29	SKU-029-01	3410.00	51	0.75	active	2025-05-10 19:22:08
50	29	SKU-029-02	3170.00	15	4.95	active	2025-06-08 21:02:00
51	29	SKU-029-03	2840.00	195	2.21	active	2025-03-03 06:00:33
52	30	SKU-030-01	7180.00	114	0.46	active	2025-10-16 10:40:53
53	31	SKU-031-01	18720.00	33	2.44	active	2025-10-25 18:19:23
54	32	SKU-032-01	12900.00	40	1.24	active	2025-10-10 11:38:45
55	33	SKU-033-01	1240.00	25	2.24	active	2025-05-19 07:45:26
56	33	SKU-033-02	1460.00	44	0.76	active	2025-12-13 16:04:35
57	34	SKU-034-01	190.00	175	1.36	active	2025-11-10 00:10:07
58	35	SKU-035-01	640.00	129	4.59	active	2026-01-26 07:51:56
59	35	SKU-035-02	620.00	60	1.28	active	2025-05-29 01:41:49
60	35	SKU-035-03	640.00	107	2.04	active	2025-10-06 00:39:03
61	36	SKU-036-01	240.00	82	3.86	active	2025-07-09 18:52:04
62	37	SKU-037-01	330.00	160	0.25	active	2025-03-16 20:25:20
63	37	SKU-037-02	350.00	80	1.03	active	2025-03-21 09:46:38
64	38	SKU-038-01	240.00	171	1.35	active	2025-10-12 04:23:55
65	38	SKU-038-02	260.00	50	3.66	active	2025-04-15 07:16:02
66	39	SKU-039-01	790.00	36	3.51	active	2025-09-24 03:56:18
67	40	SKU-040-01	1230.00	14	4.72	active	2025-03-12 13:41:17
68	40	SKU-040-02	1280.00	36	3.08	active	2026-01-20 05:07:04
69	41	SKU-041-01	270.00	81	4.46	active	2025-06-05 03:10:01
70	41	SKU-041-02	310.00	199	0.46	active	2025-03-13 06:45:19
71	42	SKU-042-01	570.00	87	3.14	active	2025-12-22 08:44:01
72	43	SKU-043-01	3710.00	111	0.66	active	2025-08-18 06:23:32
73	44	SKU-044-01	6440.00	186	1.91	active	2025-08-13 13:37:50
74	45	SKU-045-01	1790.00	196	2.84	active	2025-11-07 08:18:19
75	45	SKU-045-02	1540.00	182	1.79	active	2025-04-16 07:36:52
76	45	SKU-045-03	1550.00	62	0.42	active	2025-03-14 21:43:52
77	46	SKU-046-01	680.00	158	0.60	active	2026-02-05 07:43:29
78	47	SKU-047-01	2640.00	62	1.14	active	2025-11-15 07:42:06
79	47	SKU-047-02	2530.00	4	3.05	active	2025-06-11 17:18:24
80	48	SKU-048-01	71120.00	31	3.71	active	2025-06-19 15:12:44
81	49	SKU-049-01	1960.00	180	2.26	active	2026-01-04 08:47:38
82	49	SKU-049-02	2040.00	82	2.60	active	2025-06-01 08:02:43
83	50	SKU-050-01	540.00	27	4.59	active	2025-08-03 17:08:06
84	50	SKU-050-02	550.00	17	3.00	active	2025-06-18 15:45:01
85	50	SKU-050-03	510.00	125	1.76	active	2025-10-19 05:07:42
86	6	SKU-006-X86	57100.00	17	2.30	active	2025-11-03 07:33:46
87	9	SKU-009-X87	31090.00	54	1.75	active	2025-11-14 11:41:52
88	43	SKU-043-X88	3530.00	9	0.18	active	2026-01-06 10:24:38
89	21	SKU-021-X89	870.00	32	0.15	active	2025-08-15 21:14:08
90	19	SKU-019-X90	14520.00	39	3.29	active	2025-11-25 05:57:27
91	19	SKU-019-X91	15750.00	111	0.51	active	2026-01-22 23:06:22
92	12	SKU-012-X92	1020.00	103	2.56	active	2025-04-01 04:06:11
93	18	SKU-018-X93	9400.00	82	1.08	active	2025-12-09 10:08:16
94	11	SKU-011-X94	3590.00	36	0.24	active	2025-10-22 22:05:55
95	5	SKU-005-X95	63380.00	105	0.60	active	2025-06-22 22:03:22
96	39	SKU-039-X96	800.00	133	1.30	active	2025-08-22 22:30:51
97	17	SKU-017-X97	4000.00	52	1.89	active	2025-04-28 20:56:16
98	13	SKU-013-X98	83550.00	37	3.23	active	2025-05-30 07:19:19
99	40	SKU-040-X99	1280.00	137	0.38	active	2025-10-03 20:17:46
100	28	SKU-028-X100	1540.00	5	1.42	active	2026-01-01 00:30:36
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.products (product_id, product_uuid, name, description, brand_id, category_id, base_price, slug, created_at, updated_at, status) FROM stdin;
1	6ce5d5f7-4f35-4203-a11e-8142339770e9	Samsung Galaxy S24	High quality Samsung Galaxy S24 from a trusted brand. Perfect for everyday use.	1	6	74999.00	samsung-galaxy-s24	2026-01-26 02:16:06	2026-02-22 14:46:19	active
2	06cfd46f-8c24-4876-93be-cb20b204b357	Apple iPhone 15	High quality Apple iPhone 15 from a trusted brand. Perfect for everyday use.	2	6	79999.00	apple-iphone-15	2025-12-05 07:56:30	2026-01-25 15:56:22	active
3	78f05bff-c0cd-4c71-890c-60f61638f8bc	OnePlus 12R	High quality OnePlus 12R from a trusted brand. Perfect for everyday use.	4	6	42999.00	oneplus-12r	2025-04-05 02:22:33	2025-10-04 06:08:11	active
4	e50ba8f8-50a4-44f0-bcfb-df3b573278eb	Samsung Galaxy A54	High quality Samsung Galaxy A54 from a trusted brand. Perfect for everyday use.	1	6	38999.00	samsung-galaxy-a54	2025-03-18 13:32:25	2025-07-01 04:31:22	active
5	4476644c-fcf6-4014-8a9f-68fc243884f8	Sony Xperia 5 V	High quality Sony Xperia 5 V from a trusted brand. Perfect for everyday use.	3	6	64999.00	sony-xperia-5-v	2025-08-14 03:12:25	2025-11-01 06:25:44	active
6	169b8ccb-77d0-4d24-9a8f-a491dfcd1783	HP Pavilion Laptop 15	High quality HP Pavilion Laptop 15 from a trusted brand. Perfect for everyday use.	20	7	55999.00	hp-pavilion-laptop-15	2026-02-27 09:27:00	2026-03-01 00:21:26	active
7	73a47d01-f0ed-4198-a1a7-172f8add4e43	Apple MacBook Air M2	High quality Apple MacBook Air M2 from a trusted brand. Perfect for everyday use.	2	7	114999.00	apple-macbook-air-m2	2025-09-19 10:12:53	2025-10-27 21:20:02	active
8	3daa4236-fab2-4d38-a196-b3e702c686ae	Samsung Galaxy Book3	High quality Samsung Galaxy Book3 from a trusted brand. Perfect for everyday use.	1	7	72999.00	samsung-galaxy-book3	2025-03-21 22:18:59	2025-08-07 18:41:24	active
9	135fd221-4873-44c8-8f23-374e29ebc371	Sony WH-1000XM5 Headphones	High quality Sony WH-1000XM5 Headphones from a trusted brand. Perfect for everyday use.	3	8	29999.00	sony-wh-1000xm5-headphones	2026-02-22 14:08:40	2026-02-24 12:59:03	active
10	3a410c1a-8959-4c43-ab1c-662efcbc5838	boAt Rockerz 450	High quality boAt Rockerz 450 from a trusted brand. Perfect for everyday use.	5	8	1499.00	boat-rockerz-450	2025-08-20 13:04:43	2025-12-14 03:55:31	draft
11	0af5dd9b-6293-4b35-9af6-c7470089ff6f	Noise Colorfit Pro 4	High quality Noise Colorfit Pro 4 from a trusted brand. Perfect for everyday use.	6	8	3499.00	noise-colorfit-pro-4	2025-05-09 23:35:20	2025-11-21 09:42:37	active
12	bb483ea9-1d67-413a-beb2-030825786304	boAt Airdopes 141	High quality boAt Airdopes 141 from a trusted brand. Perfect for everyday use.	5	8	999.00	boat-airdopes-141	2025-03-16 09:26:40	2025-04-28 00:47:02	active
13	aa0a141a-6342-4b63-a8a3-f410ba8eb53a	Sony Alpha A6400 Camera	High quality Sony Alpha A6400 Camera from a trusted brand. Perfect for everyday use.	3	9	84999.00	sony-alpha-a6400-camera	2025-09-01 23:27:16	2026-01-12 18:29:41	inactive
14	fc56bd8b-5a3c-4194-9658-7b8e09cd94a9	Nike Dri-FIT T-Shirt	High quality Nike Dri-FIT T-Shirt from a trusted brand. Perfect for everyday use.	7	10	1999.00	nike-dri-fit-t-shirt	2025-04-02 12:28:02	2025-09-14 17:40:16	active
15	04e653b8-98db-495c-bd34-955e3d93da15	Adidas Tiro Track Pants	High quality Adidas Tiro Track Pants from a trusted brand. Perfect for everyday use.	8	10	2499.00	adidas-tiro-track-pants	2025-04-26 12:01:56	2025-08-24 19:38:31	active
16	260e2692-2603-4ffc-83a7-154e970b758a	Puma Essential Hoodie	High quality Puma Essential Hoodie from a trusted brand. Perfect for everyday use.	9	10	3299.00	puma-essential-hoodie	2025-07-27 23:45:02	2025-12-03 00:45:20	active
17	8196b4dc-3f00-45f8-ac68-d21ff8a4a78b	Levi's 511 Slim Fit Jeans	High quality Levi's 511 Slim Fit Jeans from a trusted brand. Perfect for everyday use.	10	10	3999.00	levis-511-slim-fit-jeans	2025-08-06 09:57:07	2025-10-23 09:29:29	inactive
18	cff6f0e5-c66a-4e65-bf10-fe26d351ecd5	Nike Air Force 1	High quality Nike Air Force 1 from a trusted brand. Perfect for everyday use.	7	12	8999.00	nike-air-force-1	2025-03-23 12:21:52	2025-11-27 05:38:20	active
19	aa236888-9333-4b95-a5e3-5efa8df656ae	Adidas Ultraboost 22	High quality Adidas Ultraboost 22 from a trusted brand. Perfect for everyday use.	8	12	14999.00	adidas-ultraboost-22	2025-06-10 00:47:15	2026-01-07 20:56:42	active
20	2306f30c-5d95-4d81-8125-8ad660049b94	Puma Suede Classic	High quality Puma Suede Classic from a trusted brand. Perfect for everyday use.	9	12	6999.00	puma-suede-classic	2025-12-23 15:05:05	2026-01-04 21:30:13	active
21	5636f589-3c3b-41ac-b7dc-8cee52d8e198	Women's Floral Kurti	High quality Women's Floral Kurti from a trusted brand. Perfect for everyday use.	10	11	899.00	womens-floral-kurti	2025-11-26 21:51:33	2026-01-12 03:21:13	draft
22	1f0ac328-684a-4f6c-ad3e-c5d68f8219b2	Women's Palazzo Set	High quality Women's Palazzo Set from a trusted brand. Perfect for everyday use.	10	11	1299.00	womens-palazzo-set	2025-04-21 20:19:39	2026-02-02 16:09:01	inactive
23	74f0e7b3-50e8-4b8f-96ce-408af7e43af3	Casio Digital Watch	High quality Casio Digital Watch from a trusted brand. Perfect for everyday use.	3	13	2299.00	casio-digital-watch	2025-10-20 21:18:40	2025-11-19 02:24:44	active
24	49e912ed-9e51-49ff-8af3-98c8542e3ae9	Fastrack Analog Watch	High quality Fastrack Analog Watch from a trusted brand. Perfect for everyday use.	6	13	1799.00	fastrack-analog-watch	2025-08-07 13:37:36	2025-09-24 20:48:38	active
25	4ed48833-583d-4ff3-a945-431d69317e87	Philips Air Fryer	High quality Philips Air Fryer from a trusted brand. Perfect for everyday use.	11	14	5499.00	philips-air-fryer	2025-04-26 19:01:50	2025-08-19 17:42:23	active
26	dd3cf0b9-7ddd-4ea1-a4fe-690c11730178	Prestige Induction Cooktop	High quality Prestige Induction Cooktop from a trusted brand. Perfect for everyday use.	12	14	2199.00	prestige-induction-cooktop	2025-05-09 23:46:34	2025-10-16 04:05:02	active
27	b23f8b70-9ffb-47b4-af7c-2cd957907e74	Bajaj Mixer Grinder	High quality Bajaj Mixer Grinder from a trusted brand. Perfect for everyday use.	14	14	2999.00	bajaj-mixer-grinder	2025-05-21 14:46:46	2025-12-25 11:21:32	active
28	01403a1c-32da-45a6-bdce-4991c2025237	Philips Electric Kettle	High quality Philips Electric Kettle from a trusted brand. Perfect for everyday use.	11	14	1499.00	philips-electric-kettle	2025-09-11 20:15:42	2026-02-13 19:03:03	active
29	d8774805-4a4c-4b1d-bcbe-40a9ec4dd702	Ikea LACK Coffee Table	High quality Ikea LACK Coffee Table from a trusted brand. Perfect for everyday use.	13	15	2999.00	ikea-lack-coffee-table	2025-06-10 00:59:36	2025-07-25 13:30:00	inactive
30	e45d7cc0-c309-412c-be60-f91372b78c4b	Ikea KALLAX Shelf	High quality Ikea KALLAX Shelf from a trusted brand. Perfect for everyday use.	13	15	6999.00	ikea-kallax-shelf	2025-07-20 11:18:45	2025-09-30 16:30:36	active
31	af346cd3-cbb5-4735-85f4-f4b63ee25f1c	Ikea MALM Bed Frame	High quality Ikea MALM Bed Frame from a trusted brand. Perfect for everyday use.	13	15	18999.00	ikea-malm-bed-frame	2025-09-12 15:49:43	2025-11-07 12:40:27	active
32	2bc09092-43dd-492f-9440-eb89838ce5aa	Wakefit Orthopaedic Mattress	High quality Wakefit Orthopaedic Mattress from a trusted brand. Perfect for everyday use.	13	16	12999.00	wakefit-orthopaedic-mattress	2026-01-19 07:57:41	2026-01-21 15:30:35	active
33	0ad7ebcc-47a6-4f65-a29b-008e81a2debd	Bombay Dyeing Bedsheet Set	High quality Bombay Dyeing Bedsheet Set from a trusted brand. Perfect for everyday use.	15	16	1299.00	bombay-dyeing-bedsheet-set	2025-07-26 09:39:17	2025-12-28 09:32:38	active
34	8f7838c9-1eba-4387-aafe-1303f71e2fab	Himalaya Face Wash	High quality Himalaya Face Wash from a trusted brand. Perfect for everyday use.	15	17	199.00	himalaya-face-wash	2026-01-11 11:51:20	2026-02-19 06:32:54	active
35	9487e085-d0d1-44bd-bd03-4ab8817952a3	Mamaearth Vitamin C Serum	High quality Mamaearth Vitamin C Serum from a trusted brand. Perfect for everyday use.	16	17	599.00	mamaearth-vitamin-c-serum	2026-01-12 00:07:39	2026-02-17 00:33:56	active
36	b4cca5e3-845b-4ad0-a518-56d84d74272f	Himalaya Moisturizing Cream	High quality Himalaya Moisturizing Cream from a trusted brand. Perfect for everyday use.	15	17	249.00	himalaya-moisturizing-cream	2025-05-11 09:08:36	2025-05-25 23:31:51	draft
37	f022d483-20b2-4d5e-80b3-e1cac26d3e74	Mamaearth Onion Shampoo	High quality Mamaearth Onion Shampoo from a trusted brand. Perfect for everyday use.	16	18	349.00	mamaearth-onion-shampoo	2025-12-07 06:21:31	2026-02-28 11:38:34	active
38	3587b468-4b51-4a78-99df-22d033efffe7	Himalaya Anti-Dandruff Shampoo	High quality Himalaya Anti-Dandruff Shampoo from a trusted brand. Perfect for everyday use.	15	18	249.00	himalaya-anti-dandruff-shampoo	2025-08-21 10:08:08	2025-10-05 02:59:27	active
39	da9cc4bc-0b5f-49b1-9a25-5f3c2953614d	Decathlon Domyos Yoga Mat	High quality Decathlon Domyos Yoga Mat from a trusted brand. Perfect for everyday use.	17	19	799.00	decathlon-domyos-yoga-mat	2025-11-11 02:50:08	2025-12-25 00:17:07	active
40	5d0a7ae8-60fc-4184-8f1e-967e1912a992	Decathlon Dumbbells 5kg Pair	High quality Decathlon Dumbbells 5kg Pair from a trusted brand. Perfect for everyday use.	17	19	1299.00	decathlon-dumbbells-5kg-pair	2025-06-30 15:31:39	2025-08-10 17:10:37	inactive
41	41fe39f5-82b6-4e49-b288-7ec0e01ae0ac	Cosco Skipping Rope	High quality Cosco Skipping Rope from a trusted brand. Perfect for everyday use.	18	19	299.00	cosco-skipping-rope	2025-12-06 21:38:46	2026-01-06 09:09:45	active
42	3962dcd3-1c85-4699-884b-3c0c152f23d6	Decathlon Resistance Bands	High quality Decathlon Resistance Bands from a trusted brand. Perfect for everyday use.	17	19	599.00	decathlon-resistance-bands	2026-01-10 06:58:45	2026-02-03 12:52:13	active
43	2970daff-84db-402a-b3be-04d5f6f5b163	Wildcraft Backpack 45L	High quality Wildcraft Backpack 45L from a trusted brand. Perfect for everyday use.	19	20	3499.00	wildcraft-backpack-45l	2025-08-19 03:37:27	2025-09-19 06:27:45	inactive
44	f8157fa4-54d7-47a0-8211-7531ff353957	Decathlon Quechua Tent 2P	High quality Decathlon Quechua Tent 2P from a trusted brand. Perfect for everyday use.	17	20	5999.00	decathlon-quechua-tent-2p	2025-08-12 13:01:18	2025-11-20 01:05:44	active
45	f2f15b74-36cf-4337-a884-9821c78e2fd6	Nike Running Shorts	High quality Nike Running Shorts from a trusted brand. Perfect for everyday use.	7	10	1599.00	nike-running-shorts	2025-06-23 19:14:08	2025-10-26 07:24:16	active
46	9ba8a93e-a0ff-4626-ac8b-c6009c0d9876	Adidas Performance Socks 3pk	High quality Adidas Performance Socks 3pk from a trusted brand. Perfect for everyday use.	8	10	699.00	adidas-performance-socks-3pk	2025-09-25 02:11:43	2025-10-19 19:21:54	draft
47	0b8a8400-5dca-488d-baea-9f86edd7153b	boAt Stone 650 Bluetooth Speaker	High quality boAt Stone 650 Bluetooth Speaker from a trusted brand. Perfect for everyday use.	5	8	2499.00	boat-stone-650-bluetooth-speaker	2025-06-09 17:52:57	2025-11-24 02:21:57	inactive
48	e5c8263d-5e65-4f6c-933b-8d4ac409436d	Samsung 65" 4K Smart TV	High quality Samsung 65" 4K Smart TV from a trusted brand. Perfect for everyday use.	1	1	64999.00	samsung-65"-4k-smart-tv	2025-08-07 23:15:18	2025-10-08 21:09:19	active
49	3d31ddcb-b39a-4dd2-8fe7-fb8ebbefad87	Philips Hair Dryer	High quality Philips Hair Dryer from a trusted brand. Perfect for everyday use.	11	18	1799.00	philips-hair-dryer	2025-11-20 09:40:39	2026-02-13 20:28:31	active
50	de2e558f-6182-437b-94ed-8bc4a9ef8b46	Decathlon Swimming Goggles	High quality Decathlon Swimming Goggles from a trusted brand. Perfect for everyday use.	17	20	499.00	decathlon-swimming-goggles	2025-07-10 19:38:32	2025-09-25 13:56:19	active
\.


--
-- Data for Name: refunds; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.refunds (refund_id, payment_id, order_id, amount, reason, status, created_at, updated_at) FROM stdin;
1	4	5	12109.73	Customer changed mind	initiated	2025-08-19 03:34:59	2025-08-20 03:34:59
2	49	51	190766.67	Product damaged on delivery	completed	2026-01-02 03:10:31	2026-01-04 03:10:31
3	83	93	92527.57	Product damaged on delivery	processing	2025-12-18 13:26:42	2025-12-21 13:26:42
4	157	176	16394.69	Quality not satisfactory	completed	2025-08-13 15:56:10	2025-08-17 15:56:10
5	166	187	11588.97	Product damaged on delivery	completed	2025-10-27 05:46:04	2025-11-01 05:46:04
6	24	26	63034.56	Duplicate order	completed	2025-07-22 13:44:46	2025-07-23 13:44:46
7	167	188	58188.22	Quality not satisfactory	completed	2025-12-17 06:15:28	2025-12-20 06:15:28
8	5	6	664.92	Item not as described	processing	2025-09-07 19:20:49	2025-09-10 19:20:49
9	59	61	104304.18	Product damaged on delivery	initiated	2026-02-08 04:02:17	2026-02-11 04:02:17
10	141	157	19249.39	Quality not satisfactory	processing	2026-01-18 06:55:56	2026-01-19 06:55:56
11	93	104	3622.99	Customer changed mind	completed	2025-11-03 00:07:37	2025-11-04 00:07:37
12	57	59	6030.91	Product damaged on delivery	processing	2025-05-08 03:43:35	2025-05-11 03:43:35
13	30	32	15207.06	Quality not satisfactory	processing	2025-12-12 13:40:18	2025-12-16 13:40:18
\.


--
-- Data for Name: review_images; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.review_images (image_id, review_id, url, sort_order) FROM stdin;
1	1	https://cdn.store.com/reviews/1/img_1.jpg	1
2	6	https://cdn.store.com/reviews/6/img_1.jpg	1
3	7	https://cdn.store.com/reviews/7/img_1.jpg	1
4	9	https://cdn.store.com/reviews/9/img_1.jpg	1
5	9	https://cdn.store.com/reviews/9/img_2.jpg	2
6	11	https://cdn.store.com/reviews/11/img_1.jpg	1
7	12	https://cdn.store.com/reviews/12/img_1.jpg	1
8	14	https://cdn.store.com/reviews/14/img_1.jpg	1
9	16	https://cdn.store.com/reviews/16/img_1.jpg	1
10	21	https://cdn.store.com/reviews/21/img_1.jpg	1
11	22	https://cdn.store.com/reviews/22/img_1.jpg	1
12	22	https://cdn.store.com/reviews/22/img_2.jpg	2
13	24	https://cdn.store.com/reviews/24/img_1.jpg	1
14	24	https://cdn.store.com/reviews/24/img_2.jpg	2
15	27	https://cdn.store.com/reviews/27/img_1.jpg	1
16	27	https://cdn.store.com/reviews/27/img_2.jpg	2
17	32	https://cdn.store.com/reviews/32/img_1.jpg	1
18	32	https://cdn.store.com/reviews/32/img_2.jpg	2
19	34	https://cdn.store.com/reviews/34/img_1.jpg	1
20	34	https://cdn.store.com/reviews/34/img_2.jpg	2
21	37	https://cdn.store.com/reviews/37/img_1.jpg	1
22	37	https://cdn.store.com/reviews/37/img_2.jpg	2
23	39	https://cdn.store.com/reviews/39/img_1.jpg	1
24	39	https://cdn.store.com/reviews/39/img_2.jpg	2
25	42	https://cdn.store.com/reviews/42/img_1.jpg	1
26	42	https://cdn.store.com/reviews/42/img_2.jpg	2
27	45	https://cdn.store.com/reviews/45/img_1.jpg	1
28	45	https://cdn.store.com/reviews/45/img_2.jpg	2
29	49	https://cdn.store.com/reviews/49/img_1.jpg	1
30	50	https://cdn.store.com/reviews/50/img_1.jpg	1
31	51	https://cdn.store.com/reviews/51/img_1.jpg	1
32	51	https://cdn.store.com/reviews/51/img_2.jpg	2
33	56	https://cdn.store.com/reviews/56/img_1.jpg	1
34	57	https://cdn.store.com/reviews/57/img_1.jpg	1
35	58	https://cdn.store.com/reviews/58/img_1.jpg	1
36	58	https://cdn.store.com/reviews/58/img_2.jpg	2
37	65	https://cdn.store.com/reviews/65/img_1.jpg	1
38	67	https://cdn.store.com/reviews/67/img_1.jpg	1
39	67	https://cdn.store.com/reviews/67/img_2.jpg	2
40	69	https://cdn.store.com/reviews/69/img_1.jpg	1
41	69	https://cdn.store.com/reviews/69/img_2.jpg	2
42	71	https://cdn.store.com/reviews/71/img_1.jpg	1
43	75	https://cdn.store.com/reviews/75/img_1.jpg	1
44	75	https://cdn.store.com/reviews/75/img_2.jpg	2
45	78	https://cdn.store.com/reviews/78/img_1.jpg	1
46	79	https://cdn.store.com/reviews/79/img_1.jpg	1
47	85	https://cdn.store.com/reviews/85/img_1.jpg	1
48	87	https://cdn.store.com/reviews/87/img_1.jpg	1
49	87	https://cdn.store.com/reviews/87/img_2.jpg	2
50	89	https://cdn.store.com/reviews/89/img_1.jpg	1
51	89	https://cdn.store.com/reviews/89/img_2.jpg	2
52	90	https://cdn.store.com/reviews/90/img_1.jpg	1
53	90	https://cdn.store.com/reviews/90/img_2.jpg	2
54	94	https://cdn.store.com/reviews/94/img_1.jpg	1
55	111	https://cdn.store.com/reviews/111/img_1.jpg	1
56	114	https://cdn.store.com/reviews/114/img_1.jpg	1
57	115	https://cdn.store.com/reviews/115/img_1.jpg	1
58	115	https://cdn.store.com/reviews/115/img_2.jpg	2
59	125	https://cdn.store.com/reviews/125/img_1.jpg	1
60	125	https://cdn.store.com/reviews/125/img_2.jpg	2
61	126	https://cdn.store.com/reviews/126/img_1.jpg	1
62	126	https://cdn.store.com/reviews/126/img_2.jpg	2
63	130	https://cdn.store.com/reviews/130/img_1.jpg	1
64	131	https://cdn.store.com/reviews/131/img_1.jpg	1
65	131	https://cdn.store.com/reviews/131/img_2.jpg	2
66	132	https://cdn.store.com/reviews/132/img_1.jpg	1
67	133	https://cdn.store.com/reviews/133/img_1.jpg	1
68	135	https://cdn.store.com/reviews/135/img_1.jpg	1
69	137	https://cdn.store.com/reviews/137/img_1.jpg	1
70	137	https://cdn.store.com/reviews/137/img_2.jpg	2
\.


--
-- Data for Name: review_votes; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.review_votes (vote_id, review_id, user_id, is_helpful, voted_at) FROM stdin;
1	82	22	t	2026-02-14 10:39:11
2	141	75	f	2025-10-29 21:10:13
3	47	24	t	2025-09-04 03:07:27
4	89	41	f	2025-05-04 14:18:34
5	47	48	t	2025-04-02 22:08:17
6	14	43	t	2025-08-30 01:04:28
7	45	62	t	2026-02-26 15:03:44
8	62	46	t	2025-04-22 07:25:39
9	42	53	f	2026-01-10 20:23:22
10	17	51	f	2025-06-05 01:15:41
11	57	58	f	2025-08-21 20:37:39
12	17	71	t	2025-11-10 01:10:18
13	138	66	f	2025-03-17 01:27:33
14	38	16	t	2025-05-16 13:50:18
15	51	79	t	2025-08-26 16:56:19
16	60	90	t	2025-03-27 12:04:25
17	35	22	t	2025-08-04 16:12:51
18	105	31	t	2025-06-12 20:45:28
19	28	96	t	2025-06-30 06:42:09
20	117	92	t	2026-01-22 00:40:22
21	92	40	t	2025-04-28 22:30:33
22	21	24	t	2026-01-07 10:32:19
23	127	7	t	2025-11-29 21:52:44
24	6	14	f	2025-05-23 09:23:48
25	90	54	t	2025-09-18 14:49:12
26	141	91	t	2025-10-02 01:20:28
27	63	62	f	2025-12-01 05:21:48
28	75	37	t	2025-10-08 23:35:05
29	136	89	f	2025-08-24 22:21:11
30	83	27	f	2025-07-29 13:54:10
31	144	79	f	2025-12-03 10:14:43
32	77	33	f	2025-09-27 20:53:13
33	39	57	t	2025-08-01 03:03:40
34	98	96	f	2026-01-09 10:40:33
35	86	59	t	2026-01-24 09:06:33
36	32	70	t	2025-04-28 00:59:31
37	123	39	t	2025-03-03 04:10:55
38	13	24	t	2026-01-06 12:11:24
39	74	89	t	2025-04-12 10:27:46
40	61	13	t	2025-03-03 09:21:34
41	33	31	t	2025-03-09 16:32:46
42	120	33	f	2026-01-09 09:18:19
43	2	100	t	2025-08-14 11:24:45
44	102	37	t	2025-03-22 06:55:06
45	44	69	t	2025-12-13 23:44:18
46	7	67	t	2026-02-28 21:31:47
47	146	50	t	2025-06-30 03:59:02
48	91	81	t	2025-10-28 07:30:04
49	93	93	t	2025-07-29 22:22:46
50	42	19	t	2025-03-13 00:51:45
51	100	79	t	2025-09-21 09:55:51
52	15	84	t	2025-09-03 03:19:33
53	7	18	t	2025-05-11 13:31:58
54	94	51	t	2025-12-08 19:38:50
55	43	90	t	2025-04-02 10:59:57
56	134	32	f	2026-01-25 13:23:56
57	122	99	f	2026-01-24 09:31:24
58	95	59	t	2025-05-29 23:35:05
59	21	68	t	2025-07-01 02:02:16
60	5	78	f	2025-03-06 06:25:17
61	115	3	t	2025-12-01 17:08:41
62	3	95	t	2025-07-06 03:14:45
63	149	3	f	2026-02-08 20:06:32
64	12	81	t	2025-03-18 16:16:44
65	92	99	t	2025-05-19 02:24:09
66	145	78	f	2025-09-06 15:30:28
67	12	1	t	2025-12-01 01:57:12
68	55	41	f	2026-01-01 13:04:25
69	100	69	t	2026-01-26 10:32:59
70	97	93	t	2026-02-04 18:22:02
71	105	36	t	2025-07-20 18:38:06
72	120	31	t	2025-06-10 01:39:15
73	74	28	t	2025-08-15 15:17:22
74	104	91	t	2025-08-18 01:20:12
75	143	52	t	2026-01-31 17:19:32
76	148	31	t	2026-02-03 23:20:26
77	133	94	t	2025-09-28 02:06:14
78	126	62	t	2025-05-10 06:26:38
79	70	97	t	2025-10-06 21:15:23
80	133	22	t	2025-09-07 12:21:42
81	76	52	t	2025-03-17 10:31:11
82	86	38	t	2025-11-19 04:08:47
83	97	66	f	2026-02-09 04:57:28
84	8	6	t	2025-09-04 22:25:20
85	119	46	t	2025-09-18 09:40:47
86	109	75	t	2025-07-25 15:13:16
87	105	19	t	2025-11-07 23:22:43
88	98	83	t	2025-07-27 04:43:54
89	21	46	t	2025-12-31 17:56:11
90	4	55	f	2026-01-06 17:33:52
91	140	70	t	2025-10-18 12:07:29
92	79	77	t	2025-05-06 16:22:02
93	140	37	t	2025-05-18 05:19:38
94	4	49	t	2025-03-22 21:58:47
95	41	53	t	2025-08-06 20:45:09
96	117	85	f	2025-10-28 16:27:55
97	144	99	f	2025-10-13 15:48:53
98	18	11	t	2025-06-13 15:46:54
99	105	72	f	2026-01-20 00:43:45
100	49	35	f	2025-09-06 13:11:02
101	136	39	t	2025-07-04 17:05:30
102	30	85	f	2025-03-24 18:22:06
103	63	28	f	2025-06-07 11:25:44
104	124	35	t	2026-01-22 13:33:38
105	23	21	t	2025-08-08 13:04:13
106	126	79	t	2026-02-19 15:03:04
107	132	30	f	2025-12-06 17:13:56
108	70	15	f	2025-12-22 07:00:07
109	74	17	t	2026-02-24 07:52:13
110	47	95	t	2026-01-07 02:37:19
111	129	81	t	2026-01-08 06:46:57
112	132	21	t	2025-07-23 17:57:38
113	41	5	t	2025-04-19 18:08:16
114	91	57	t	2025-07-18 20:15:30
115	87	67	t	2026-01-29 01:48:30
116	88	60	t	2025-12-04 23:04:56
117	81	96	t	2025-12-21 20:15:01
118	94	7	f	2026-02-14 12:49:02
119	5	83	t	2025-12-15 22:00:15
120	2	46	t	2025-08-02 09:47:07
121	44	81	f	2025-12-27 20:50:41
122	71	77	f	2025-08-28 00:27:52
123	144	22	t	2025-06-03 22:05:58
124	47	80	f	2025-10-30 23:23:13
125	35	88	f	2025-11-14 07:27:40
126	141	67	t	2025-10-25 16:27:32
127	30	66	t	2025-09-18 21:50:46
128	97	42	f	2025-05-27 07:06:16
129	66	17	t	2025-07-27 05:03:55
130	38	6	t	2025-12-22 08:07:27
131	87	68	f	2025-08-14 12:25:41
132	54	69	f	2025-04-28 01:45:46
133	149	78	t	2025-07-12 04:42:41
134	127	12	t	2025-07-04 01:07:12
135	92	44	t	2025-09-10 07:05:17
136	107	15	f	2025-04-18 00:14:21
137	146	12	t	2025-04-05 22:30:55
138	38	81	t	2025-06-15 10:18:20
139	49	83	t	2025-08-17 17:41:21
140	144	76	t	2025-08-09 16:46:29
141	79	66	f	2025-06-03 17:39:02
142	110	61	t	2025-04-25 15:46:15
143	97	21	t	2025-04-12 12:10:19
144	79	31	t	2026-01-02 20:06:16
145	20	67	t	2026-02-11 12:07:04
146	113	64	t	2025-04-02 00:13:10
147	30	95	t	2026-01-24 02:33:56
148	147	30	t	2025-04-14 01:21:49
149	35	60	t	2025-06-07 17:42:55
150	150	21	t	2026-01-09 17:37:45
151	37	57	t	2025-04-04 07:40:27
152	59	40	f	2025-07-15 23:40:59
153	90	6	t	2025-03-30 22:15:28
154	146	16	t	2025-11-06 11:48:29
155	50	99	t	2026-02-01 16:00:38
156	35	58	t	2025-11-29 03:48:58
157	142	80	t	2025-04-17 03:40:26
158	30	35	t	2025-07-01 04:27:07
159	106	46	t	2025-03-11 12:52:36
160	142	18	t	2025-03-07 22:58:26
161	25	65	f	2026-02-18 00:22:07
162	91	74	t	2026-02-11 05:43:54
163	13	97	f	2026-01-02 16:04:18
164	40	4	t	2025-08-28 02:44:55
165	99	57	f	2025-03-27 04:45:56
166	36	80	t	2025-10-13 21:48:03
167	72	72	t	2025-12-29 02:20:08
168	109	34	t	2025-10-21 18:30:29
169	127	83	t	2025-04-22 03:04:57
170	11	88	t	2025-03-11 12:36:34
171	91	15	f	2025-11-05 08:27:05
172	53	41	t	2025-05-04 11:10:47
173	11	9	t	2025-05-30 09:01:36
174	12	75	t	2026-02-15 11:43:37
175	69	8	t	2025-08-30 08:32:15
176	107	61	t	2025-06-19 20:23:55
177	149	73	f	2025-06-18 10:58:01
178	106	83	t	2025-06-29 01:32:30
179	55	33	t	2025-11-12 21:43:00
180	126	30	t	2025-12-27 16:03:34
181	111	91	t	2025-03-30 00:45:14
182	105	41	t	2025-03-22 14:38:24
183	6	80	f	2025-08-18 05:51:35
184	121	88	t	2025-04-24 08:46:06
185	83	42	t	2025-09-12 06:36:53
186	19	48	t	2025-07-25 22:48:20
187	125	27	f	2025-11-06 01:26:35
188	134	39	t	2026-02-24 08:35:17
189	78	91	t	2025-11-29 20:54:15
190	143	37	f	2025-09-11 19:40:18
191	92	81	f	2025-10-27 01:35:31
192	62	69	t	2025-07-10 18:22:41
193	100	89	t	2025-05-26 07:22:11
194	52	91	t	2025-05-27 19:49:36
195	85	82	t	2025-10-02 14:43:53
196	13	95	t	2025-03-13 06:54:29
197	104	27	f	2025-10-17 14:04:10
198	14	9	t	2025-08-16 06:40:55
199	3	54	t	2026-02-27 17:29:35
200	15	5	t	2025-08-12 13:27:59
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.reviews (review_id, product_id, user_id, order_id, rating, title, body, is_verified_purchase, helpful_count, created_at) FROM stdin;
1	20	51	17	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	37	2025-09-18 15:00:04
2	7	10	151	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	66	2026-02-06 00:26:24
3	46	73	16	4	Satisfied with purchase	Works as expected. Delivery took a couple extra days but product quality is solid.	t	90	2026-02-01 08:06:17
4	33	81	173	2	Disappointed	Not what I expected based on the product photos. Quality is below average for this price point.	t	17	2025-07-09 19:34:32
5	1	55	7	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	f	26	2026-02-11 14:11:28
6	39	88	82	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	8	2025-09-20 07:30:16
7	43	54	91	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	11	2025-09-09 06:22:45
8	2	39	65	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	53	2025-09-02 08:59:46
9	26	88	180	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	77	2025-08-09 03:55:35
10	31	88	82	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	f	92	2025-09-20 07:30:16
11	1	23	42	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	36	2025-06-26 17:34:21
12	38	54	91	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	66	2025-09-17 06:22:45
13	48	43	39	4	Very good product	Good quality overall. Minor packaging issue but the product itself is great. Happy with the purchase.	t	104	2025-06-16 21:33:51
14	8	40	102	1	Very poor quality	Completely disappointed. Product stopped working within a week. Waste of money.	t	19	2025-08-18 06:43:05
15	43	71	188	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	12	2026-03-02 00:00:00
16	7	21	119	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	116	2025-04-28 04:09:44
17	15	86	168	2	Disappointed	Not what I expected based on the product photos. Quality is below average for this price point.	t	85	2025-05-17 10:51:47
18	36	43	39	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	106	2025-05-31 21:33:51
19	46	79	120	4	Happy with it	Product matches the description. Would have been 5 stars if delivery was faster.	t	96	2025-03-16 04:30:31
20	11	41	112	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	9	2025-07-17 05:21:01
21	8	55	5	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	20	2025-04-04 21:57:58
22	48	39	65	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	96	2025-09-08 08:59:46
23	50	15	193	3	Okay product	It works but the quality feels a bit cheap. Packaging was good though.	t	38	2025-12-02 21:42:29
24	26	99	18	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	70	2026-01-01 21:24:58
25	13	96	22	4	Happy with it	Product matches the description. Would have been 5 stars if delivery was faster.	f	34	2025-04-08 08:57:48
26	16	94	169	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	96	2025-05-04 05:46:23
27	8	79	120	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	97	2025-03-18 04:30:31
28	36	61	46	3	Not bad, not great	Does what it says on the box. Nothing more nothing less. Neutral experience overall.	t	84	2025-06-27 16:27:46
29	49	67	37	4	Good value for money	Nice product for the price. A few minor things could be improved but overall a good buy.	t	111	2025-06-07 11:39:01
30	29	81	173	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	f	106	2025-07-20 19:34:32
31	44	36	108	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	90	2026-01-05 15:35:12
32	48	84	118	3	Average experience	Product is okay but nothing special. Delivery was on time. May or may not buy again.	f	67	2025-06-02 21:48:08
33	29	84	165	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	94	2026-02-06 14:34:56
34	26	23	42	4	Good value for money	Nice product for the price. A few minor things could be improved but overall a good buy.	t	54	2025-06-23 17:34:21
35	31	99	18	3	Okay product	It works but the quality feels a bit cheap. Packaging was good though.	t	34	2025-12-21 21:24:58
36	4	99	18	3	Average experience	Product is okay but nothing special. Delivery was on time. May or may not buy again.	f	110	2025-12-22 21:24:58
37	32	87	170	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	1	2025-07-03 15:14:05
38	40	10	151	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	43	2026-02-22 00:26:24
39	10	46	111	4	Good value for money	Nice product for the price. A few minor things could be improved but overall a good buy.	f	71	2025-07-28 13:37:27
40	48	11	116	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	5	2025-12-29 13:29:10
41	42	15	193	4	Good value for money	Nice product for the price. A few minor things could be improved but overall a good buy.	t	119	2025-11-30 21:42:29
42	13	84	165	3	Okay product	It works but the quality feels a bit cheap. Packaging was good though.	t	72	2026-02-08 14:34:56
43	24	66	61	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	19	2025-12-05 06:21:48
44	40	81	173	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	36	2025-07-15 19:34:32
45	20	59	60	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	25	2026-02-25 03:06:46
46	11	86	48	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	68	2025-12-22 10:01:00
47	7	14	62	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	2	2026-01-22 23:24:58
48	39	67	128	2	Disappointed	Not what I expected based on the product photos. Quality is below average for this price point.	t	108	2025-11-13 06:28:21
49	21	80	26	1	Awful experience	Product arrived broken. Customer service was unhelpful. Avoid this seller.	t	12	2025-08-08 19:32:00
50	1	59	35	4	Good value for money	Nice product for the price. A few minor things could be improved but overall a good buy.	t	97	2025-04-19 11:19:36
51	8	62	80	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	86	2026-02-07 08:29:43
52	50	73	131	4	Happy with it	Product matches the description. Would have been 5 stars if delivery was faster.	t	7	2025-09-06 13:40:46
53	37	9	32	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	f	117	2025-06-24 09:19:56
54	23	28	155	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	53	2025-11-19 00:43:40
55	14	84	165	4	Happy with it	Product matches the description. Would have been 5 stars if delivery was faster.	t	70	2026-02-09 14:34:56
56	13	9	32	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	65	2025-06-22 09:19:56
57	40	28	155	4	Satisfied with purchase	Works as expected. Delivery took a couple extra days but product quality is solid.	t	94	2025-11-23 00:43:40
58	21	24	3	4	Good value for money	Nice product for the price. A few minor things could be improved but overall a good buy.	t	63	2025-12-08 07:32:18
59	31	36	184	3	Mixed feelings	Some features are great but the overall build quality leaves something to be desired.	t	10	2025-09-10 10:59:55
60	44	96	166	4	Decent product	Good build quality and looks great. Slightly different shade than shown in photos but acceptable.	f	71	2025-12-08 08:47:15
61	12	81	19	4	Satisfied with purchase	Works as expected. Delivery took a couple extra days but product quality is solid.	t	106	2025-09-08 05:28:25
62	36	83	164	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	10	2025-12-10 11:16:14
63	9	68	190	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	3	2025-07-17 18:23:28
64	27	43	39	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	1	2025-06-05 21:33:51
65	25	94	169	4	Very good product	Good quality overall. Minor packaging issue but the product itself is great. Happy with the purchase.	t	80	2025-05-09 05:46:23
66	3	86	168	3	Okay product	It works but the quality feels a bit cheap. Packaging was good though.	f	92	2025-05-27 10:51:47
67	28	24	107	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	50	2025-06-05 00:19:50
68	8	66	61	3	Not bad, not great	Does what it says on the box. Nothing more nothing less. Neutral experience overall.	t	10	2025-12-26 06:21:48
69	15	68	190	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	f	67	2025-08-07 18:23:28
70	44	61	46	4	Good value for money	Nice product for the price. A few minor things could be improved but overall a good buy.	t	30	2025-06-10 16:27:46
71	24	32	132	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	46	2026-01-21 23:30:15
72	3	99	18	2	Needs improvement	Several issues with the product right out of the box. Packaging was also damaged.	t	84	2025-12-17 21:24:58
73	16	73	131	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	6	2025-08-26 13:40:46
74	13	36	108	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	84	2026-01-07 15:35:12
75	19	55	5	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	107	2025-04-03 21:57:58
76	38	45	100	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	17	2026-01-03 12:15:30
77	39	39	146	4	Good value for money	Nice product for the price. A few minor things could be improved but overall a good buy.	t	85	2026-02-06 07:27:10
78	11	67	13	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	120	2025-12-25 09:46:14
79	8	71	24	4	Satisfied with purchase	Works as expected. Delivery took a couple extra days but product quality is solid.	f	47	2025-08-02 13:44:46
80	12	24	107	4	Very good product	Good quality overall. Minor packaging issue but the product itself is great. Happy with the purchase.	t	93	2025-05-22 00:19:50
81	23	92	33	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	f	56	2025-09-12 00:29:32
82	20	6	71	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	73	2025-04-25 10:43:21
83	21	87	170	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	86	2025-07-06 15:14:05
84	17	32	25	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	87	2026-03-02 00:00:00
85	9	8	135	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	f	59	2026-03-02 00:00:00
86	24	62	80	4	Good value for money	Nice product for the price. A few minor things could be improved but overall a good buy.	t	88	2026-01-27 08:29:43
87	27	69	199	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	37	2025-06-10 05:04:27
88	3	16	59	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	11	2025-12-05 11:41:29
89	34	96	166	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	20	2025-11-29 08:47:15
90	32	95	98	4	Very good product	Good quality overall. Minor packaging issue but the product itself is great. Happy with the purchase.	t	63	2025-12-12 12:09:05
91	41	56	8	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	82	2026-01-06 22:36:52
92	48	71	188	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	f	90	2026-03-02 00:00:00
93	41	86	168	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	26	2025-05-29 10:51:47
94	11	63	106	4	Good value for money	Nice product for the price. A few minor things could be improved but overall a good buy.	t	51	2026-02-14 21:09:31
95	32	9	32	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	95	2025-06-14 09:19:56
96	42	38	99	2	Needs improvement	Several issues with the product right out of the box. Packaging was also damaged.	t	87	2026-03-02 00:00:00
97	48	69	129	3	Mixed feelings	Some features are great but the overall build quality leaves something to be desired.	t	51	2025-06-06 07:36:22
98	35	56	8	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	60	2026-01-01 22:36:52
99	50	67	37	4	Happy with it	Product matches the description. Would have been 5 stars if delivery was faster.	t	113	2025-06-13 11:39:01
100	19	46	111	4	Satisfied with purchase	Works as expected. Delivery took a couple extra days but product quality is solid.	t	31	2025-07-17 13:37:27
101	45	28	176	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	42	2026-01-26 03:34:13
102	36	82	125	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	25	2026-02-15 22:23:21
103	48	56	187	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	30	2026-01-28 12:48:45
104	28	81	173	4	Decent product	Good build quality and looks great. Slightly different shade than shown in photos but acceptable.	t	50	2025-07-05 19:34:32
105	43	86	168	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	112	2025-05-25 10:51:47
106	45	64	47	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	65	2026-01-15 03:10:31
107	4	10	151	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	36	2026-02-23 00:26:24
108	29	83	164	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	37	2025-12-22 11:16:14
109	40	2	171	4	Decent product	Good build quality and looks great. Slightly different shade than shown in photos but acceptable.	t	63	2025-10-28 05:46:04
110	18	96	9	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	17	2025-12-22 09:36:43
111	10	36	108	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	109	2025-12-23 15:35:12
112	10	81	19	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	49	2025-09-11 05:28:25
113	41	39	65	4	Very good product	Good quality overall. Minor packaging issue but the product itself is great. Happy with the purchase.	f	11	2025-09-13 08:59:46
114	6	73	16	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	104	2026-01-31 08:06:17
115	37	46	111	4	Satisfied with purchase	Works as expected. Delivery took a couple extra days but product quality is solid.	t	88	2025-07-19 13:37:27
116	46	66	61	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	25	2025-12-05 06:21:48
117	9	71	188	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	f	41	2026-03-02 00:00:00
118	6	18	172	4	Decent product	Good build quality and looks great. Slightly different shade than shown in photos but acceptable.	t	22	2026-01-04 06:15:28
119	38	60	143	3	Could be better	Average quality for the price. Expected a bit more based on the product description.	f	17	2025-09-22 02:01:48
120	3	51	69	3	Mixed feelings	Some features are great but the overall build quality leaves something to be desired.	t	43	2025-09-23 23:04:56
121	1	73	131	4	Happy with it	Product matches the description. Would have been 5 stars if delivery was faster.	t	110	2025-09-13 13:40:46
122	37	58	10	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	66	2026-01-27 15:29:10
123	22	61	46	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	8	2025-06-12 16:27:46
124	13	73	16	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	73	2026-02-09 08:06:17
125	17	18	122	4	Very good product	Good quality overall. Minor packaging issue but the product itself is great. Happy with the purchase.	t	117	2025-04-28 18:44:49
126	41	99	18	4	Satisfied with purchase	Works as expected. Delivery took a couple extra days but product quality is solid.	t	96	2025-12-23 21:24:58
127	42	41	112	2	Not worth the price	Overpriced for the quality offered. Expected much better from this brand.	t	103	2025-07-09 05:21:01
128	7	96	9	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	72	2025-12-18 09:36:43
129	31	69	129	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	f	55	2025-06-15 07:36:22
130	23	61	46	4	Happy with it	Product matches the description. Would have been 5 stars if delivery was faster.	t	38	2025-06-20 16:27:46
131	2	8	135	4	Decent product	Good build quality and looks great. Slightly different shade than shown in photos but acceptable.	t	26	2026-02-20 16:17:15
132	10	8	135	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	17	2026-02-15 16:17:15
133	1	39	146	5	Highly recommended	Fantastic product. My family loves it. Customer service was also very responsive.	t	107	2026-01-22 07:27:10
134	23	88	82	2	Needs improvement	Several issues with the product right out of the box. Packaging was also damaged.	t	106	2025-10-06 07:30:16
135	3	36	184	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	f	108	2025-09-29 10:59:55
136	45	40	102	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	31	2025-08-09 06:43:05
137	2	99	18	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	22	2025-12-13 21:24:58
138	43	96	166	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	91	2025-11-28 08:47:15
139	26	86	168	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	79	2025-05-19 10:51:47
140	7	92	33	5	Best purchase this year	Amazing product for the price. Works exactly as described. Will definitely buy again from this store.	t	67	2025-09-07 00:29:32
141	19	59	60	5	Perfect!	Five stars without a doubt. Packaging was excellent and product looks even better in person.	t	92	2026-03-02 00:00:00
142	5	61	46	2	Below expectations	Product looks different from the images. Not very happy with this purchase.	f	26	2025-06-17 16:27:46
143	22	21	119	3	Could be better	Average quality for the price. Expected a bit more based on the product description.	f	105	2025-04-10 04:09:44
144	23	39	146	3	Not bad, not great	Does what it says on the box. Nothing more nothing less. Neutral experience overall.	t	36	2026-01-22 07:27:10
145	19	2	171	4	Happy with it	Product matches the description. Would have been 5 stars if delivery was faster.	f	59	2025-10-27 05:46:04
146	47	39	65	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	79	2025-09-25 08:59:46
147	36	41	112	5	Absolutely love it!	Exceeded all my expectations. Build quality is top notch and delivery was super fast. Highly recommended!	t	77	2025-06-24 05:21:01
148	46	96	22	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	115	2025-04-20 08:57:48
149	14	28	64	2	Not worth the price	Overpriced for the quality offered. Expected much better from this brand.	t	30	2025-12-04 04:58:03
150	50	98	77	5	Outstanding quality	Really impressed with the quality. Fast shipping and well packed. Great value for money.	t	12	2025-11-14 15:05:13
\.


--
-- Data for Name: shipment_tracking; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.shipment_tracking (tracking_id, shipment_id, event_description, location, event_time) FROM stdin;
1	1	Order picked up from seller	Bangalore Hub	2025-09-10 15:05:26
2	1	Shipment arrived at origin facility	Delhi Hub	2025-09-10 18:05:26
3	1	In transit to destination city	Ahmedabad Hub	2025-09-11 15:05:26
4	1	Arrived at destination facility	Kolkata Hub	2025-09-12 13:05:26
5	1	Out for delivery	Chennai Hub	2025-09-13 13:05:26
6	2	Order picked up from seller	Chennai Hub	2025-11-10 19:32:18
7	2	Shipment arrived at origin facility	Pune Hub	2025-11-10 21:32:18
8	2	In transit to destination city	Delhi Hub	2025-11-11 19:32:18
9	2	Arrived at destination facility	Delhi Hub	2025-11-12 18:32:18
10	2	Out for delivery	Pune Hub	2025-11-13 19:32:18
11	2	Successfully delivered	Pune Hub	2025-11-14 18:32:18
12	3	Order picked up from seller	Hyderabad Hub	2025-03-16 01:57:58
13	3	Shipment arrived at origin facility	Pune Hub	2025-03-16 06:57:58
14	3	In transit to destination city	Kolkata Hub	2025-03-17 03:57:58
15	3	Arrived at destination facility	Kolkata Hub	2025-03-18 01:57:58
16	3	Out for delivery	Bangalore Hub	2025-03-19 03:57:58
17	3	Successfully delivered	Delhi Hub	2025-03-20 01:57:58
18	4	Order picked up from seller	Chennai Hub	2025-03-14 11:17:27
19	4	Shipment arrived at origin facility	Pune Hub	2025-03-14 15:17:27
20	4	In transit to destination city	Pune Hub	2025-03-15 11:17:27
21	4	Arrived at destination facility	Ahmedabad Hub	2025-03-16 12:17:27
22	4	Out for delivery	Ahmedabad Hub	2025-03-17 11:17:27
23	4	Successfully delivered	Pune Hub	2025-03-18 12:17:27
24	5	Order picked up from seller	Pune Hub	2026-01-18 00:11:28
25	5	Shipment arrived at origin facility	Bangalore Hub	2026-01-18 05:11:28
26	5	In transit to destination city	Hyderabad Hub	2026-01-19 02:11:28
27	5	Arrived at destination facility	Chennai Hub	2026-01-20 00:11:28
28	5	Out for delivery	Kolkata Hub	2026-01-21 00:11:28
29	5	Successfully delivered	Ahmedabad Hub	2026-01-22 02:11:28
30	5	Return pickup scheduled	Mumbai Hub	2026-01-23 01:11:28
31	5	Item picked up for return	Mumbai Hub	2026-01-24 01:11:28
32	5	Return received at warehouse	Bangalore Hub	2026-01-25 00:11:28
33	6	Order picked up from seller	Pune Hub	2025-12-11 06:36:52
34	6	Shipment arrived at origin facility	Kolkata Hub	2025-12-11 11:36:52
35	6	In transit to destination city	Kolkata Hub	2025-12-12 07:36:52
36	6	Arrived at destination facility	Chennai Hub	2025-12-13 05:36:52
37	6	Out for delivery	Chennai Hub	2025-12-14 07:36:52
38	6	Successfully delivered	Bangalore Hub	2025-12-15 06:36:52
39	7	Order picked up from seller	Ahmedabad Hub	2025-12-14 23:36:43
40	7	Shipment arrived at origin facility	Chennai Hub	2025-12-15 01:36:43
41	7	In transit to destination city	Chennai Hub	2025-12-15 21:36:43
42	7	Arrived at destination facility	Delhi Hub	2025-12-16 21:36:43
43	7	Out for delivery	Chennai Hub	2025-12-17 22:36:43
44	7	Successfully delivered	Delhi Hub	2025-12-18 22:36:43
45	8	Order picked up from seller	Kolkata Hub	2026-01-17 03:29:10
46	8	Shipment arrived at origin facility	Chennai Hub	2026-01-17 09:29:10
47	8	In transit to destination city	Delhi Hub	2026-01-18 03:29:10
48	8	Arrived at destination facility	Pune Hub	2026-01-19 03:29:10
49	8	Out for delivery	Ahmedabad Hub	2026-01-20 05:29:10
50	8	Successfully delivered	Kolkata Hub	2026-01-21 05:29:10
51	9	Order picked up from seller	Chennai Hub	2025-10-05 11:41:37
52	9	Shipment arrived at origin facility	Kolkata Hub	2025-10-05 15:41:37
53	9	In transit to destination city	Pune Hub	2025-10-06 13:41:37
54	9	Arrived at destination facility	Bangalore Hub	2025-10-07 11:41:37
55	9	Out for delivery	Hyderabad Hub	2025-10-08 11:41:37
56	10	Order picked up from seller	Mumbai Hub	2025-11-30 13:46:14
57	10	Shipment arrived at origin facility	Bangalore Hub	2025-11-30 18:46:14
58	10	In transit to destination city	Pune Hub	2025-12-01 15:46:14
59	10	Arrived at destination facility	Bangalore Hub	2025-12-02 13:46:14
60	10	Out for delivery	Ahmedabad Hub	2025-12-03 15:46:14
61	10	Successfully delivered	Bangalore Hub	2025-12-04 13:46:14
62	11	Order picked up from seller	Delhi Hub	2025-04-02 23:10:41
63	11	Shipment arrived at origin facility	Mumbai Hub	2025-04-03 02:10:41
64	11	In transit to destination city	Mumbai Hub	2025-04-03 21:10:41
65	11	Arrived at destination facility	Delhi Hub	2025-04-04 23:10:41
66	11	Out for delivery	Delhi Hub	2025-04-05 23:10:41
67	12	Order picked up from seller	Delhi Hub	2025-08-14 06:34:35
68	12	Shipment arrived at origin facility	Delhi Hub	2025-08-14 12:34:35
69	12	In transit to destination city	Delhi Hub	2025-08-15 06:34:35
70	12	Arrived at destination facility	Pune Hub	2025-08-16 08:34:35
71	12	Out for delivery	Hyderabad Hub	2025-08-17 06:34:35
72	13	Order picked up from seller	Bangalore Hub	2026-01-14 10:06:17
73	13	Shipment arrived at origin facility	Hyderabad Hub	2026-01-14 14:06:17
74	13	In transit to destination city	Bangalore Hub	2026-01-15 10:06:17
75	13	Arrived at destination facility	Ahmedabad Hub	2026-01-16 10:06:17
76	13	Out for delivery	Kolkata Hub	2026-01-17 10:06:17
77	13	Successfully delivered	Delhi Hub	2026-01-18 11:06:17
78	14	Order picked up from seller	Hyderabad Hub	2025-09-06 17:00:04
79	14	Shipment arrived at origin facility	Hyderabad Hub	2025-09-06 22:00:04
80	14	In transit to destination city	Pune Hub	2025-09-07 17:00:04
81	14	Arrived at destination facility	Mumbai Hub	2025-09-08 17:00:04
82	14	Out for delivery	Mumbai Hub	2025-09-09 19:00:04
83	14	Successfully delivered	Chennai Hub	2025-09-10 18:00:04
84	14	Return pickup scheduled	Kolkata Hub	2025-09-11 19:00:04
85	14	Item picked up for return	Bangalore Hub	2025-09-12 18:00:04
86	14	Return received at warehouse	Pune Hub	2025-09-13 19:00:04
87	15	Order picked up from seller	Chennai Hub	2025-12-09 01:24:58
88	15	Shipment arrived at origin facility	Ahmedabad Hub	2025-12-09 05:24:58
89	15	In transit to destination city	Chennai Hub	2025-12-10 02:24:58
90	15	Arrived at destination facility	Bangalore Hub	2025-12-11 01:24:58
91	15	Out for delivery	Hyderabad Hub	2025-12-12 01:24:58
92	15	Successfully delivered	Chennai Hub	2025-12-13 01:24:58
93	16	Order picked up from seller	Ahmedabad Hub	2025-08-29 12:28:25
94	16	Shipment arrived at origin facility	Bangalore Hub	2025-08-29 14:28:25
95	16	In transit to destination city	Hyderabad Hub	2025-08-30 10:28:25
96	16	Arrived at destination facility	Hyderabad Hub	2025-08-31 10:28:25
97	16	Out for delivery	Bangalore Hub	2025-09-01 12:28:25
98	16	Successfully delivered	Mumbai Hub	2025-09-02 11:28:25
99	17	Order picked up from seller	Ahmedabad Hub	2025-10-05 02:09:05
100	17	Shipment arrived at origin facility	Pune Hub	2025-10-05 06:09:05
101	17	In transit to destination city	Pune Hub	2025-10-06 01:09:05
102	17	Arrived at destination facility	Bangalore Hub	2025-10-07 03:09:05
103	17	Out for delivery	Ahmedabad Hub	2025-10-08 02:09:05
104	18	Order picked up from seller	Pune Hub	2025-03-26 11:57:48
105	18	Shipment arrived at origin facility	Chennai Hub	2025-03-26 15:57:48
106	18	In transit to destination city	Kolkata Hub	2025-03-27 10:57:48
107	18	Arrived at destination facility	Ahmedabad Hub	2025-03-28 09:57:48
108	18	Out for delivery	Mumbai Hub	2025-03-29 11:57:48
109	18	Successfully delivered	Chennai Hub	2025-03-30 09:57:48
110	19	Order picked up from seller	Kolkata Hub	2025-07-19 23:44:46
111	19	Shipment arrived at origin facility	Hyderabad Hub	2025-07-20 04:44:46
112	19	In transit to destination city	Kolkata Hub	2025-07-21 01:44:46
113	19	Arrived at destination facility	Pune Hub	2025-07-22 01:44:46
114	19	Out for delivery	Bangalore Hub	2025-07-23 00:44:46
115	19	Successfully delivered	Ahmedabad Hub	2025-07-24 01:44:46
116	20	Order picked up from seller	Kolkata Hub	2026-02-28 07:44:15
117	20	Shipment arrived at origin facility	Ahmedabad Hub	2026-02-28 10:44:15
118	20	In transit to destination city	Mumbai Hub	2026-03-01 05:44:15
119	20	Arrived at destination facility	Chennai Hub	2026-03-02 00:00:00
120	20	Out for delivery	Ahmedabad Hub	2026-03-02 00:00:00
121	20	Successfully delivered	Bangalore Hub	2026-03-02 00:00:00
122	20	Return pickup scheduled	Chennai Hub	2026-03-02 00:00:00
123	20	Item picked up for return	Delhi Hub	2026-03-02 00:00:00
124	20	Return received at warehouse	Delhi Hub	2026-03-02 00:00:00
125	21	Order picked up from seller	Chennai Hub	2025-07-16 21:32:00
126	21	Shipment arrived at origin facility	Pune Hub	2025-07-17 01:32:00
127	21	In transit to destination city	Ahmedabad Hub	2025-07-17 23:32:00
128	21	Arrived at destination facility	Ahmedabad Hub	2025-07-18 23:32:00
129	21	Out for delivery	Hyderabad Hub	2025-07-19 21:32:00
130	21	Successfully delivered	Bangalore Hub	2025-07-20 23:32:00
131	22	Order picked up from seller	Chennai Hub	2025-08-01 23:48:20
132	22	Shipment arrived at origin facility	Ahmedabad Hub	2025-08-02 05:48:20
133	22	In transit to destination city	Chennai Hub	2025-08-03 01:48:20
134	22	Arrived at destination facility	Ahmedabad Hub	2025-08-03 23:48:20
135	22	Out for delivery	Mumbai Hub	2025-08-05 00:48:20
136	22	Successfully delivered	Delhi Hub	2025-08-06 00:48:20
137	23	Order picked up from seller	Hyderabad Hub	2025-04-17 11:39:07
138	23	Shipment arrived at origin facility	Bangalore Hub	2025-04-17 13:39:07
139	23	In transit to destination city	Bangalore Hub	2025-04-18 11:39:07
140	23	Arrived at destination facility	Hyderabad Hub	2025-04-19 09:39:07
141	23	Out for delivery	Delhi Hub	2025-04-20 11:39:07
142	24	Order picked up from seller	Delhi Hub	2025-12-08 18:40:18
143	24	Shipment arrived at origin facility	Kolkata Hub	2025-12-08 23:40:18
144	24	In transit to destination city	Pune Hub	2025-12-09 20:40:18
145	24	Arrived at destination facility	Ahmedabad Hub	2025-12-10 20:40:18
146	24	Out for delivery	Bangalore Hub	2025-12-11 18:40:18
147	24	Successfully delivered	Ahmedabad Hub	2025-12-12 20:40:18
148	25	Order picked up from seller	Chennai Hub	2025-06-08 16:19:56
149	25	Shipment arrived at origin facility	Chennai Hub	2025-06-08 20:19:56
150	25	In transit to destination city	Chennai Hub	2025-06-09 16:19:56
151	25	Arrived at destination facility	Delhi Hub	2025-06-10 18:19:56
152	25	Out for delivery	Chennai Hub	2025-06-11 16:19:56
153	25	Successfully delivered	Pune Hub	2025-06-12 16:19:56
154	26	Order picked up from seller	Chennai Hub	2025-08-31 12:29:32
155	26	Shipment arrived at origin facility	Ahmedabad Hub	2025-08-31 17:29:32
156	26	In transit to destination city	Kolkata Hub	2025-09-01 12:29:32
157	26	Arrived at destination facility	Chennai Hub	2025-09-02 14:29:32
158	26	Out for delivery	Hyderabad Hub	2025-09-03 14:29:32
159	26	Successfully delivered	Bangalore Hub	2025-09-04 12:29:32
160	27	Order picked up from seller	Bangalore Hub	2025-03-22 21:19:36
161	27	Shipment arrived at origin facility	Delhi Hub	2025-03-23 03:19:36
162	27	In transit to destination city	Kolkata Hub	2025-03-23 23:19:36
163	27	Arrived at destination facility	Bangalore Hub	2025-03-24 21:19:36
164	27	Out for delivery	Ahmedabad Hub	2025-03-25 21:19:36
165	27	Successfully delivered	Kolkata Hub	2025-03-26 23:19:36
166	28	Order picked up from seller	Ahmedabad Hub	2025-05-23 20:39:01
167	28	Shipment arrived at origin facility	Kolkata Hub	2025-05-24 00:39:01
168	28	In transit to destination city	Hyderabad Hub	2025-05-24 20:39:01
169	28	Arrived at destination facility	Kolkata Hub	2025-05-25 19:39:01
170	28	Out for delivery	Kolkata Hub	2025-05-26 18:39:01
171	28	Successfully delivered	Pune Hub	2025-05-27 20:39:01
172	29	Order picked up from seller	Mumbai Hub	2026-02-06 07:02:21
173	29	Shipment arrived at origin facility	Pune Hub	2026-02-06 12:02:21
174	29	In transit to destination city	Ahmedabad Hub	2026-02-07 09:02:21
175	29	Arrived at destination facility	Delhi Hub	2026-02-08 07:02:21
176	29	Out for delivery	Chennai Hub	2026-02-09 07:02:21
177	30	Order picked up from seller	Mumbai Hub	2025-05-20 08:33:51
178	30	Shipment arrived at origin facility	Chennai Hub	2025-05-20 13:33:51
179	30	In transit to destination city	Delhi Hub	2025-05-21 08:33:51
180	30	Arrived at destination facility	Pune Hub	2025-05-22 10:33:51
181	30	Out for delivery	Pune Hub	2025-05-23 08:33:51
182	30	Successfully delivered	Hyderabad Hub	2025-05-24 08:33:51
183	31	Order picked up from seller	Kolkata Hub	2025-10-27 11:19:59
184	31	Shipment arrived at origin facility	Ahmedabad Hub	2025-10-27 15:19:59
185	31	In transit to destination city	Pune Hub	2025-10-28 11:19:59
186	31	Arrived at destination facility	Ahmedabad Hub	2025-10-29 10:19:59
187	31	Out for delivery	Hyderabad Hub	2025-10-30 10:19:59
188	32	Order picked up from seller	Kolkata Hub	2025-06-10 02:34:21
189	32	Shipment arrived at origin facility	Pune Hub	2025-06-10 08:34:21
190	32	In transit to destination city	Pune Hub	2025-06-11 04:34:21
191	32	Arrived at destination facility	Chennai Hub	2025-06-12 02:34:21
192	32	Out for delivery	Kolkata Hub	2025-06-13 04:34:21
193	32	Successfully delivered	Pune Hub	2025-06-14 03:34:21
194	33	Order picked up from seller	Bangalore Hub	2025-03-03 07:25:00
195	33	Shipment arrived at origin facility	Delhi Hub	2025-03-03 13:25:00
196	33	In transit to destination city	Chennai Hub	2025-03-04 07:25:00
197	33	Arrived at destination facility	Hyderabad Hub	2025-03-05 07:25:00
198	33	Out for delivery	Chennai Hub	2025-03-06 09:25:00
199	34	Order picked up from seller	Chennai Hub	2025-06-02 21:27:46
200	34	Shipment arrived at origin facility	Kolkata Hub	2025-06-03 03:27:46
201	34	In transit to destination city	Ahmedabad Hub	2025-06-03 23:27:46
202	34	Arrived at destination facility	Pune Hub	2025-06-04 22:27:46
203	34	Out for delivery	Ahmedabad Hub	2025-06-05 22:27:46
204	34	Successfully delivered	Hyderabad Hub	2025-06-06 21:27:46
205	35	Order picked up from seller	Pune Hub	2026-01-02 17:10:31
206	35	Shipment arrived at origin facility	Pune Hub	2026-01-02 19:10:31
207	35	In transit to destination city	Kolkata Hub	2026-01-03 16:10:31
208	35	Arrived at destination facility	Mumbai Hub	2026-01-04 16:10:31
209	35	Out for delivery	Pune Hub	2026-01-05 17:10:31
210	35	Successfully delivered	Mumbai Hub	2026-01-06 16:10:31
211	35	Return pickup scheduled	Ahmedabad Hub	2026-01-07 15:10:31
212	35	Item picked up for return	Ahmedabad Hub	2026-01-08 15:10:31
213	35	Return received at warehouse	Mumbai Hub	2026-01-09 15:10:31
214	36	Order picked up from seller	Hyderabad Hub	2025-12-04 22:01:00
215	36	Shipment arrived at origin facility	Pune Hub	2025-12-05 03:01:00
216	36	In transit to destination city	Pune Hub	2025-12-05 23:01:00
217	36	Arrived at destination facility	Ahmedabad Hub	2025-12-06 23:01:00
218	36	Out for delivery	Ahmedabad Hub	2025-12-07 21:01:00
219	36	Successfully delivered	Mumbai Hub	2025-12-08 23:01:00
220	37	Order picked up from seller	Mumbai Hub	2025-08-29 07:42:59
221	37	Shipment arrived at origin facility	Bangalore Hub	2025-08-29 11:42:59
222	37	In transit to destination city	Delhi Hub	2025-08-30 06:42:59
223	37	Arrived at destination facility	Pune Hub	2025-08-31 06:42:59
224	37	Out for delivery	Pune Hub	2025-09-01 07:42:59
225	38	Order picked up from seller	Delhi Hub	2025-03-30 19:16:02
226	38	Shipment arrived at origin facility	Pune Hub	2025-03-31 01:16:02
227	38	In transit to destination city	Ahmedabad Hub	2025-03-31 21:16:02
228	38	Arrived at destination facility	Pune Hub	2025-04-01 20:16:02
229	38	Out for delivery	Kolkata Hub	2025-04-02 19:16:02
230	39	Order picked up from seller	Bangalore Hub	2025-05-29 14:15:21
231	39	Shipment arrived at origin facility	Chennai Hub	2025-05-29 16:15:21
232	39	In transit to destination city	Pune Hub	2025-05-30 14:15:21
233	39	Arrived at destination facility	Chennai Hub	2025-05-31 12:15:21
234	39	Out for delivery	Kolkata Hub	2025-06-01 12:15:21
235	39	Successfully delivered	Kolkata Hub	2025-06-02 14:15:21
236	40	Order picked up from seller	Mumbai Hub	2025-03-11 02:15:37
237	40	Shipment arrived at origin facility	Hyderabad Hub	2025-03-11 07:15:37
238	40	In transit to destination city	Delhi Hub	2025-03-12 02:15:37
239	40	Arrived at destination facility	Pune Hub	2025-03-13 03:15:37
240	40	Out for delivery	Bangalore Hub	2025-03-14 04:15:37
241	41	Order picked up from seller	Chennai Hub	2025-11-25 15:41:29
242	41	Shipment arrived at origin facility	Hyderabad Hub	2025-11-25 19:41:29
243	41	In transit to destination city	Delhi Hub	2025-11-26 13:41:29
244	41	Arrived at destination facility	Ahmedabad Hub	2025-11-27 14:41:29
245	41	Out for delivery	Delhi Hub	2025-11-28 14:41:29
246	41	Successfully delivered	Delhi Hub	2025-11-29 15:41:29
247	42	Order picked up from seller	Delhi Hub	2026-02-21 15:06:46
248	42	Shipment arrived at origin facility	Pune Hub	2026-02-21 18:06:46
249	42	In transit to destination city	Kolkata Hub	2026-02-22 14:06:46
250	42	Arrived at destination facility	Pune Hub	2026-02-23 14:06:46
251	42	Out for delivery	Delhi Hub	2026-02-24 15:06:46
252	42	Successfully delivered	Delhi Hub	2026-02-25 14:06:46
253	43	Order picked up from seller	Hyderabad Hub	2025-12-01 11:21:48
254	43	Shipment arrived at origin facility	Ahmedabad Hub	2025-12-01 17:21:48
255	43	In transit to destination city	Hyderabad Hub	2025-12-02 12:21:48
256	43	Arrived at destination facility	Delhi Hub	2025-12-03 11:21:48
257	43	Out for delivery	Kolkata Hub	2025-12-04 13:21:48
258	43	Successfully delivered	Bangalore Hub	2025-12-05 12:21:48
259	44	Order picked up from seller	Delhi Hub	2026-01-09 04:24:58
260	44	Shipment arrived at origin facility	Delhi Hub	2026-01-09 07:24:58
261	44	In transit to destination city	Pune Hub	2026-01-10 05:24:58
262	44	Arrived at destination facility	Mumbai Hub	2026-01-11 04:24:58
263	44	Out for delivery	Mumbai Hub	2026-01-12 03:24:58
264	44	Successfully delivered	Mumbai Hub	2026-01-13 04:24:58
265	45	Order picked up from seller	Delhi Hub	2026-02-08 11:50:34
266	45	Shipment arrived at origin facility	Pune Hub	2026-02-08 16:50:34
267	45	In transit to destination city	Mumbai Hub	2026-02-09 11:50:34
268	45	Arrived at destination facility	Kolkata Hub	2026-02-10 10:50:34
269	45	Out for delivery	Mumbai Hub	2026-02-11 11:50:34
270	45	Successfully delivered	Delhi Hub	2026-02-12 10:50:34
271	46	Order picked up from seller	Ahmedabad Hub	2025-11-11 06:58:03
272	46	Shipment arrived at origin facility	Mumbai Hub	2025-11-11 10:58:03
273	46	In transit to destination city	Kolkata Hub	2025-11-12 06:58:03
274	46	Arrived at destination facility	Mumbai Hub	2025-11-13 06:58:03
275	46	Out for delivery	Pune Hub	2025-11-14 07:58:03
276	46	Successfully delivered	Hyderabad Hub	2025-11-15 05:58:03
277	47	Order picked up from seller	Kolkata Hub	2025-08-29 17:59:46
278	47	Shipment arrived at origin facility	Kolkata Hub	2025-08-29 21:59:46
279	47	In transit to destination city	Delhi Hub	2025-08-30 18:59:46
280	47	Arrived at destination facility	Pune Hub	2025-08-31 17:59:46
281	47	Out for delivery	Hyderabad Hub	2025-09-01 16:59:46
282	47	Successfully delivered	Bangalore Hub	2025-09-02 16:59:46
283	48	Order picked up from seller	Hyderabad Hub	2025-04-21 08:16:15
284	48	Shipment arrived at origin facility	Mumbai Hub	2025-04-21 10:16:15
285	48	In transit to destination city	Delhi Hub	2025-04-22 06:16:15
286	48	Arrived at destination facility	Mumbai Hub	2025-04-23 08:16:15
287	48	Out for delivery	Pune Hub	2025-04-24 06:16:15
288	49	Order picked up from seller	Ahmedabad Hub	2025-08-21 04:36:45
289	49	Shipment arrived at origin facility	Kolkata Hub	2025-08-21 08:36:45
290	49	In transit to destination city	Hyderabad Hub	2025-08-22 03:36:45
291	49	Arrived at destination facility	Delhi Hub	2025-08-23 04:36:45
292	49	Out for delivery	Mumbai Hub	2025-08-24 04:36:45
293	50	Order picked up from seller	Pune Hub	2025-09-17 23:04:56
294	50	Shipment arrived at origin facility	Hyderabad Hub	2025-09-18 04:04:56
295	50	In transit to destination city	Ahmedabad Hub	2025-09-19 00:04:56
296	50	Arrived at destination facility	Ahmedabad Hub	2025-09-19 23:04:56
297	50	Out for delivery	Kolkata Hub	2025-09-20 23:04:56
298	50	Successfully delivered	Pune Hub	2025-09-21 23:04:56
299	51	Order picked up from seller	Mumbai Hub	2025-04-05 18:43:21
300	51	Shipment arrived at origin facility	Pune Hub	2025-04-06 00:43:21
301	51	In transit to destination city	Pune Hub	2025-04-06 18:43:21
302	51	Arrived at destination facility	Mumbai Hub	2025-04-07 19:43:21
303	51	Out for delivery	Pune Hub	2025-04-08 20:43:21
304	51	Successfully delivered	Chennai Hub	2025-04-09 19:43:21
305	52	Order picked up from seller	Pune Hub	2025-07-18 04:33:24
306	52	Shipment arrived at origin facility	Hyderabad Hub	2025-07-18 08:33:24
307	52	In transit to destination city	Pune Hub	2025-07-19 04:33:24
308	52	Arrived at destination facility	Mumbai Hub	2025-07-20 03:33:24
309	52	Out for delivery	Mumbai Hub	2025-07-21 03:33:24
310	53	Order picked up from seller	Ahmedabad Hub	2025-05-18 23:24:01
311	53	Shipment arrived at origin facility	Chennai Hub	2025-05-19 03:24:01
312	53	In transit to destination city	Pune Hub	2025-05-19 21:24:01
313	53	Arrived at destination facility	Delhi Hub	2025-05-20 23:24:01
314	53	Out for delivery	Hyderabad Hub	2025-05-21 23:24:01
315	53	Successfully delivered	Mumbai Hub	2025-05-22 23:24:01
316	54	Order picked up from seller	Chennai Hub	2025-10-21 02:05:13
317	54	Shipment arrived at origin facility	Bangalore Hub	2025-10-21 06:05:13
318	54	In transit to destination city	Bangalore Hub	2025-10-22 02:05:13
319	54	Arrived at destination facility	Hyderabad Hub	2025-10-23 00:05:13
320	54	Out for delivery	Pune Hub	2025-10-24 02:05:13
321	54	Successfully delivered	Bangalore Hub	2025-10-25 01:05:13
322	55	Order picked up from seller	Hyderabad Hub	2025-09-30 12:39:01
323	55	Shipment arrived at origin facility	Kolkata Hub	2025-09-30 17:39:01
324	55	In transit to destination city	Ahmedabad Hub	2025-10-01 12:39:01
325	55	Arrived at destination facility	Bangalore Hub	2025-10-02 12:39:01
326	55	Out for delivery	Mumbai Hub	2025-10-03 13:39:01
327	56	Order picked up from seller	Delhi Hub	2026-01-20 15:29:43
328	56	Shipment arrived at origin facility	Pune Hub	2026-01-20 21:29:43
329	56	In transit to destination city	Mumbai Hub	2026-01-21 15:29:43
330	56	Arrived at destination facility	Mumbai Hub	2026-01-22 17:29:43
331	56	Out for delivery	Kolkata Hub	2026-01-23 16:29:43
332	56	Successfully delivered	Kolkata Hub	2026-01-24 17:29:43
333	57	Order picked up from seller	Mumbai Hub	2025-05-13 03:11:42
334	57	Shipment arrived at origin facility	Hyderabad Hub	2025-05-13 07:11:42
335	57	In transit to destination city	Hyderabad Hub	2025-05-14 02:11:42
336	57	Arrived at destination facility	Kolkata Hub	2025-05-15 03:11:42
337	57	Out for delivery	Mumbai Hub	2025-05-16 01:11:42
338	58	Order picked up from seller	Ahmedabad Hub	2025-09-12 20:30:16
339	58	Shipment arrived at origin facility	Bangalore Hub	2025-09-12 23:30:16
340	58	In transit to destination city	Chennai Hub	2025-09-13 19:30:16
341	58	Arrived at destination facility	Delhi Hub	2025-09-14 21:30:16
342	58	Out for delivery	Ahmedabad Hub	2025-09-15 21:30:16
343	58	Successfully delivered	Chennai Hub	2025-09-16 21:30:16
344	59	Order picked up from seller	Hyderabad Hub	2025-11-26 13:27:45
345	59	Shipment arrived at origin facility	Hyderabad Hub	2025-11-26 16:27:45
346	59	In transit to destination city	Ahmedabad Hub	2025-11-27 11:27:45
347	59	Arrived at destination facility	Kolkata Hub	2025-11-28 12:27:45
348	59	Out for delivery	Hyderabad Hub	2025-11-29 11:27:45
349	60	Order picked up from seller	Kolkata Hub	2025-07-29 19:56:49
350	60	Shipment arrived at origin facility	Pune Hub	2025-07-30 01:56:49
351	60	In transit to destination city	Pune Hub	2025-07-30 19:56:49
352	60	Arrived at destination facility	Kolkata Hub	2025-07-31 20:56:49
353	60	Out for delivery	Mumbai Hub	2025-08-01 20:56:49
354	61	Order picked up from seller	Chennai Hub	2025-08-26 09:22:45
355	61	Shipment arrived at origin facility	Chennai Hub	2025-08-26 15:22:45
356	61	In transit to destination city	Chennai Hub	2025-08-27 09:22:45
357	61	Arrived at destination facility	Mumbai Hub	2025-08-28 09:22:45
358	61	Out for delivery	Hyderabad Hub	2025-08-29 09:22:45
359	61	Successfully delivered	Delhi Hub	2025-08-30 10:22:45
360	62	Order picked up from seller	Pune Hub	2025-08-29 22:17:48
361	62	Shipment arrived at origin facility	Pune Hub	2025-08-30 00:17:48
362	62	In transit to destination city	Kolkata Hub	2025-08-30 21:17:48
363	62	Arrived at destination facility	Delhi Hub	2025-08-31 21:17:48
364	62	Out for delivery	Pune Hub	2025-09-01 21:17:48
365	63	Order picked up from seller	Bangalore Hub	2025-10-15 13:31:33
366	63	Shipment arrived at origin facility	Delhi Hub	2025-10-15 16:31:33
367	63	In transit to destination city	Hyderabad Hub	2025-10-16 12:31:33
368	63	Arrived at destination facility	Bangalore Hub	2025-10-17 12:31:33
369	63	Out for delivery	Delhi Hub	2025-10-18 14:31:33
370	63	Successfully delivered	Bangalore Hub	2025-10-19 12:31:33
371	63	Return pickup scheduled	Hyderabad Hub	2025-10-20 14:31:33
372	63	Item picked up for return	Delhi Hub	2025-10-21 14:31:33
373	63	Return received at warehouse	Chennai Hub	2025-10-22 14:31:33
374	64	Order picked up from seller	Ahmedabad Hub	2025-11-16 20:09:05
375	64	Shipment arrived at origin facility	Bangalore Hub	2025-11-17 00:09:05
376	64	In transit to destination city	Bangalore Hub	2025-11-17 21:09:05
377	64	Arrived at destination facility	Hyderabad Hub	2025-11-18 19:09:05
378	64	Out for delivery	Ahmedabad Hub	2025-11-19 21:09:05
379	64	Successfully delivered	Delhi Hub	2025-11-20 21:09:05
380	65	Order picked up from seller	Chennai Hub	2026-03-02 00:00:00
381	65	Shipment arrived at origin facility	Kolkata Hub	2026-03-02 00:00:00
382	65	In transit to destination city	Kolkata Hub	2026-03-02 00:00:00
383	65	Arrived at destination facility	Bangalore Hub	2026-03-02 00:00:00
384	65	Out for delivery	Ahmedabad Hub	2026-03-02 00:00:00
385	65	Successfully delivered	Ahmedabad Hub	2026-03-02 00:00:00
386	66	Order picked up from seller	Hyderabad Hub	2025-12-22 14:15:30
387	66	Shipment arrived at origin facility	Kolkata Hub	2025-12-22 19:15:30
388	66	In transit to destination city	Bangalore Hub	2025-12-23 14:15:30
389	66	Arrived at destination facility	Ahmedabad Hub	2025-12-24 14:15:30
390	66	Out for delivery	Pune Hub	2025-12-25 14:15:30
391	66	Successfully delivered	Mumbai Hub	2025-12-26 14:15:30
392	67	Order picked up from seller	Pune Hub	2025-07-29 20:43:05
393	67	Shipment arrived at origin facility	Pune Hub	2025-07-29 22:43:05
394	67	In transit to destination city	Chennai Hub	2025-07-30 18:43:05
395	67	Arrived at destination facility	Chennai Hub	2025-07-31 19:43:05
396	67	Out for delivery	Ahmedabad Hub	2025-08-01 18:43:05
397	67	Successfully delivered	Pune Hub	2025-08-02 20:43:05
398	68	Order picked up from seller	Bangalore Hub	2025-11-12 21:38:26
399	68	Shipment arrived at origin facility	Delhi Hub	2025-11-13 03:38:26
400	68	In transit to destination city	Delhi Hub	2025-11-13 23:38:26
401	68	Arrived at destination facility	Hyderabad Hub	2025-11-14 21:38:26
402	68	Out for delivery	Ahmedabad Hub	2025-11-15 23:38:26
403	69	Order picked up from seller	Hyderabad Hub	2026-01-23 06:09:31
404	69	Shipment arrived at origin facility	Kolkata Hub	2026-01-23 11:09:31
405	69	In transit to destination city	Bangalore Hub	2026-01-24 05:09:31
406	69	Arrived at destination facility	Ahmedabad Hub	2026-01-25 05:09:31
407	69	Out for delivery	Mumbai Hub	2026-01-26 07:09:31
408	69	Successfully delivered	Chennai Hub	2026-01-27 07:09:31
409	70	Order picked up from seller	Mumbai Hub	2025-05-18 13:19:50
410	70	Shipment arrived at origin facility	Kolkata Hub	2025-05-18 16:19:50
411	70	In transit to destination city	Ahmedabad Hub	2025-05-19 12:19:50
412	70	Arrived at destination facility	Pune Hub	2025-05-20 11:19:50
413	70	Out for delivery	Delhi Hub	2025-05-21 11:19:50
414	70	Successfully delivered	Bangalore Hub	2025-05-22 11:19:50
415	71	Order picked up from seller	Pune Hub	2025-12-16 20:35:12
416	71	Shipment arrived at origin facility	Chennai Hub	2025-12-17 00:35:12
417	71	In transit to destination city	Kolkata Hub	2025-12-17 21:35:12
418	71	Arrived at destination facility	Chennai Hub	2025-12-18 19:35:12
419	71	Out for delivery	Hyderabad Hub	2025-12-19 19:35:12
420	71	Successfully delivered	Chennai Hub	2025-12-20 20:35:12
421	72	Order picked up from seller	Delhi Hub	2025-06-30 23:37:27
422	72	Shipment arrived at origin facility	Hyderabad Hub	2025-07-01 02:37:27
423	72	In transit to destination city	Bangalore Hub	2025-07-01 22:37:27
424	72	Arrived at destination facility	Chennai Hub	2025-07-02 22:37:27
425	72	Out for delivery	Chennai Hub	2025-07-04 00:37:27
426	72	Successfully delivered	Kolkata Hub	2025-07-05 00:37:27
427	73	Order picked up from seller	Chennai Hub	2025-06-20 10:21:01
428	73	Shipment arrived at origin facility	Hyderabad Hub	2025-06-20 15:21:01
429	73	In transit to destination city	Delhi Hub	2025-06-21 10:21:01
430	73	Arrived at destination facility	Bangalore Hub	2025-06-22 10:21:01
431	73	Out for delivery	Chennai Hub	2025-06-23 11:21:01
432	73	Successfully delivered	Hyderabad Hub	2025-06-24 10:21:01
433	74	Order picked up from seller	Pune Hub	2025-12-06 22:29:10
434	74	Shipment arrived at origin facility	Hyderabad Hub	2025-12-07 02:29:10
435	74	In transit to destination city	Hyderabad Hub	2025-12-07 20:29:10
436	74	Arrived at destination facility	Ahmedabad Hub	2025-12-08 21:29:10
437	74	Out for delivery	Bangalore Hub	2025-12-09 20:29:10
438	74	Successfully delivered	Hyderabad Hub	2025-12-10 20:29:10
439	75	Order picked up from seller	Pune Hub	2025-07-28 13:03:18
440	75	Shipment arrived at origin facility	Mumbai Hub	2025-07-28 17:03:18
441	75	In transit to destination city	Hyderabad Hub	2025-07-29 12:03:18
442	75	Arrived at destination facility	Ahmedabad Hub	2025-07-30 14:03:18
443	75	Out for delivery	Kolkata Hub	2025-07-31 12:03:18
444	76	Order picked up from seller	Delhi Hub	2025-05-13 23:48:08
445	76	Shipment arrived at origin facility	Ahmedabad Hub	2025-05-14 03:48:08
446	76	In transit to destination city	Kolkata Hub	2025-05-15 00:48:08
447	76	Arrived at destination facility	Delhi Hub	2025-05-16 01:48:08
448	76	Out for delivery	Bangalore Hub	2025-05-16 23:48:08
449	76	Successfully delivered	Pune Hub	2025-05-18 01:48:08
450	77	Order picked up from seller	Kolkata Hub	2025-04-07 07:09:44
451	77	Shipment arrived at origin facility	Pune Hub	2025-04-07 13:09:44
452	77	In transit to destination city	Bangalore Hub	2025-04-08 07:09:44
453	77	Arrived at destination facility	Bangalore Hub	2025-04-09 07:09:44
454	77	Out for delivery	Pune Hub	2025-04-10 09:09:44
455	77	Successfully delivered	Hyderabad Hub	2025-04-11 08:09:44
456	78	Order picked up from seller	Bangalore Hub	2025-03-07 08:30:31
457	78	Shipment arrived at origin facility	Kolkata Hub	2025-03-07 10:30:31
458	78	In transit to destination city	Chennai Hub	2025-03-08 08:30:31
459	78	Arrived at destination facility	Ahmedabad Hub	2025-03-09 08:30:31
460	78	Out for delivery	Hyderabad Hub	2025-03-10 07:30:31
461	78	Successfully delivered	Delhi Hub	2025-03-11 08:30:31
462	79	Order picked up from seller	Kolkata Hub	2025-04-21 03:44:49
463	79	Shipment arrived at origin facility	Kolkata Hub	2025-04-21 07:44:49
464	79	In transit to destination city	Pune Hub	2025-04-22 01:44:49
465	79	Arrived at destination facility	Hyderabad Hub	2025-04-23 01:44:49
466	79	Out for delivery	Hyderabad Hub	2025-04-24 03:44:49
467	79	Successfully delivered	Pune Hub	2025-04-25 03:44:49
468	80	Order picked up from seller	Delhi Hub	2025-11-09 00:50:04
469	80	Shipment arrived at origin facility	Chennai Hub	2025-11-09 06:50:04
470	80	In transit to destination city	Delhi Hub	2025-11-10 00:50:04
471	80	Arrived at destination facility	Chennai Hub	2025-11-11 00:50:04
472	80	Out for delivery	Chennai Hub	2025-11-12 02:50:04
473	81	Order picked up from seller	Hyderabad Hub	2026-01-20 10:23:21
474	81	Shipment arrived at origin facility	Chennai Hub	2026-01-20 16:23:21
475	81	In transit to destination city	Bangalore Hub	2026-01-21 11:23:21
476	81	Arrived at destination facility	Pune Hub	2026-01-22 11:23:21
477	81	Out for delivery	Chennai Hub	2026-01-23 10:23:21
478	81	Successfully delivered	Pune Hub	2026-01-24 10:23:21
479	82	Order picked up from seller	Delhi Hub	2025-05-03 01:15:21
480	82	Shipment arrived at origin facility	Bangalore Hub	2025-05-03 05:15:21
481	82	In transit to destination city	Delhi Hub	2025-05-04 02:15:21
482	82	Arrived at destination facility	Delhi Hub	2025-05-05 00:15:21
483	82	Out for delivery	Kolkata Hub	2025-05-06 00:15:21
484	82	Successfully delivered	Hyderabad Hub	2025-05-07 02:15:21
485	83	Order picked up from seller	Chennai Hub	2026-03-01 03:36:24
486	83	Shipment arrived at origin facility	Bangalore Hub	2026-03-01 08:36:24
487	83	In transit to destination city	Hyderabad Hub	2026-03-02 00:00:00
488	83	Arrived at destination facility	Pune Hub	2026-03-02 00:00:00
489	83	Out for delivery	Bangalore Hub	2026-03-02 00:00:00
490	84	Order picked up from seller	Bangalore Hub	2025-10-28 14:28:21
491	84	Shipment arrived at origin facility	Pune Hub	2025-10-28 17:28:21
492	84	In transit to destination city	Chennai Hub	2025-10-29 13:28:21
493	84	Arrived at destination facility	Ahmedabad Hub	2025-10-30 15:28:21
494	84	Out for delivery	Bangalore Hub	2025-10-31 15:28:21
495	84	Successfully delivered	Chennai Hub	2025-11-01 15:28:21
496	85	Order picked up from seller	Pune Hub	2025-05-31 10:36:22
497	85	Shipment arrived at origin facility	Pune Hub	2025-05-31 15:36:22
498	85	In transit to destination city	Mumbai Hub	2025-06-01 11:36:22
499	85	Arrived at destination facility	Hyderabad Hub	2025-06-02 10:36:22
500	85	Out for delivery	Bangalore Hub	2025-06-03 11:36:22
501	85	Successfully delivered	Delhi Hub	2025-06-04 12:36:22
502	86	Order picked up from seller	Pune Hub	2025-03-27 13:39:38
503	86	Shipment arrived at origin facility	Chennai Hub	2025-03-27 19:39:38
504	86	In transit to destination city	Chennai Hub	2025-03-28 13:39:38
505	86	Arrived at destination facility	Mumbai Hub	2025-03-29 13:39:38
506	86	Out for delivery	Pune Hub	2025-03-30 13:39:38
507	86	Successfully delivered	Kolkata Hub	2025-03-31 15:39:38
508	86	Return pickup scheduled	Hyderabad Hub	2025-04-01 14:39:38
509	86	Item picked up for return	Delhi Hub	2025-04-02 15:39:38
510	86	Return received at warehouse	Pune Hub	2025-04-03 15:39:38
511	87	Order picked up from seller	Mumbai Hub	2025-08-19 16:40:46
512	87	Shipment arrived at origin facility	Ahmedabad Hub	2025-08-19 19:40:46
513	87	In transit to destination city	Hyderabad Hub	2025-08-20 16:40:46
514	87	Arrived at destination facility	Kolkata Hub	2025-08-21 14:40:46
515	87	Out for delivery	Pune Hub	2025-08-22 14:40:46
516	87	Successfully delivered	Chennai Hub	2025-08-23 14:40:46
517	88	Order picked up from seller	Delhi Hub	2026-01-04 09:30:15
518	88	Shipment arrived at origin facility	Mumbai Hub	2026-01-04 12:30:15
519	88	In transit to destination city	Delhi Hub	2026-01-05 09:30:15
520	88	Arrived at destination facility	Hyderabad Hub	2026-01-06 08:30:15
521	88	Out for delivery	Mumbai Hub	2026-01-07 09:30:15
522	88	Successfully delivered	Chennai Hub	2026-01-08 07:30:15
523	89	Order picked up from seller	Pune Hub	2025-08-16 20:44:59
524	89	Shipment arrived at origin facility	Bangalore Hub	2025-08-16 22:44:59
525	89	In transit to destination city	Bangalore Hub	2025-08-17 18:44:59
526	89	Arrived at destination facility	Bangalore Hub	2025-08-18 18:44:59
527	89	Out for delivery	Pune Hub	2025-08-19 18:44:59
528	90	Order picked up from seller	Delhi Hub	2026-02-11 19:17:15
529	90	Shipment arrived at origin facility	Delhi Hub	2026-02-12 00:17:15
530	90	In transit to destination city	Pune Hub	2026-02-12 21:17:15
531	90	Arrived at destination facility	Kolkata Hub	2026-02-13 19:17:15
532	90	Out for delivery	Chennai Hub	2026-02-14 19:17:15
533	90	Successfully delivered	Delhi Hub	2026-02-15 20:17:15
534	91	Order picked up from seller	Pune Hub	2025-11-10 02:03:15
535	91	Shipment arrived at origin facility	Chennai Hub	2025-11-10 06:03:15
536	91	In transit to destination city	Hyderabad Hub	2025-11-11 03:03:15
537	91	Arrived at destination facility	Pune Hub	2025-11-12 03:03:15
538	91	Out for delivery	Mumbai Hub	2025-11-13 02:03:15
539	92	Order picked up from seller	Kolkata Hub	2025-10-29 07:08:02
540	92	Shipment arrived at origin facility	Pune Hub	2025-10-29 12:08:02
541	92	In transit to destination city	Bangalore Hub	2025-10-30 09:08:02
542	92	Arrived at destination facility	Bangalore Hub	2025-10-31 08:08:02
543	92	Out for delivery	Ahmedabad Hub	2025-11-01 09:08:02
544	93	Order picked up from seller	Chennai Hub	2025-10-01 20:11:33
545	93	Shipment arrived at origin facility	Pune Hub	2025-10-02 01:11:33
546	93	In transit to destination city	Mumbai Hub	2025-10-02 21:11:33
547	93	Arrived at destination facility	Delhi Hub	2025-10-03 19:11:33
548	93	Out for delivery	Kolkata Hub	2025-10-04 19:11:33
549	94	Order picked up from seller	Hyderabad Hub	2025-09-12 15:01:48
550	94	Shipment arrived at origin facility	Pune Hub	2025-09-12 19:01:48
551	94	In transit to destination city	Delhi Hub	2025-09-13 14:01:48
552	94	Arrived at destination facility	Mumbai Hub	2025-09-14 15:01:48
553	94	Out for delivery	Bangalore Hub	2025-09-15 13:01:48
554	94	Successfully delivered	Hyderabad Hub	2025-09-16 15:01:48
555	95	Order picked up from seller	Bangalore Hub	2026-02-12 06:39:25
556	95	Shipment arrived at origin facility	Pune Hub	2026-02-12 09:39:25
557	95	In transit to destination city	Hyderabad Hub	2026-02-13 05:39:25
558	95	Arrived at destination facility	Mumbai Hub	2026-02-14 05:39:25
559	95	Out for delivery	Chennai Hub	2026-02-15 06:39:25
560	95	Successfully delivered	Chennai Hub	2026-02-16 05:39:25
561	96	Order picked up from seller	Pune Hub	2026-01-16 18:27:10
562	96	Shipment arrived at origin facility	Ahmedabad Hub	2026-01-16 23:27:10
563	96	In transit to destination city	Kolkata Hub	2026-01-17 19:27:10
564	96	Arrived at destination facility	Mumbai Hub	2026-01-18 20:27:10
565	96	Out for delivery	Bangalore Hub	2026-01-19 19:27:10
566	96	Successfully delivered	Bangalore Hub	2026-01-20 19:27:10
567	97	Order picked up from seller	Hyderabad Hub	2025-06-20 18:38:20
568	97	Shipment arrived at origin facility	Delhi Hub	2025-06-20 23:38:20
569	97	In transit to destination city	Ahmedabad Hub	2025-06-21 17:38:20
570	97	Arrived at destination facility	Delhi Hub	2025-06-22 18:38:20
571	97	Out for delivery	Delhi Hub	2025-06-23 18:38:20
572	97	Successfully delivered	Hyderabad Hub	2025-06-24 18:38:20
573	98	Order picked up from seller	Chennai Hub	2025-07-09 01:57:20
574	98	Shipment arrived at origin facility	Chennai Hub	2025-07-09 06:57:20
575	98	In transit to destination city	Pune Hub	2025-07-10 03:57:20
576	98	Arrived at destination facility	Kolkata Hub	2025-07-11 01:57:20
577	98	Out for delivery	Hyderabad Hub	2025-07-12 03:57:20
578	99	Order picked up from seller	Hyderabad Hub	2025-04-06 07:19:59
579	99	Shipment arrived at origin facility	Chennai Hub	2025-04-06 09:19:59
580	99	In transit to destination city	Hyderabad Hub	2025-04-07 07:19:59
581	99	Arrived at destination facility	Mumbai Hub	2025-04-08 06:19:59
582	99	Out for delivery	Kolkata Hub	2025-04-09 05:19:59
583	99	Successfully delivered	Chennai Hub	2025-04-10 07:19:59
584	100	Order picked up from seller	Chennai Hub	2026-02-26 17:43:53
585	100	Shipment arrived at origin facility	Kolkata Hub	2026-02-26 22:43:53
586	100	In transit to destination city	Ahmedabad Hub	2026-02-27 17:43:53
587	100	Arrived at destination facility	Ahmedabad Hub	2026-02-28 18:43:53
588	100	Out for delivery	Bangalore Hub	2026-03-01 19:43:53
589	100	Successfully delivered	Hyderabad Hub	2026-03-02 00:00:00
590	101	Order picked up from seller	Bangalore Hub	2026-01-30 11:26:24
591	101	Shipment arrived at origin facility	Hyderabad Hub	2026-01-30 13:26:24
592	101	In transit to destination city	Kolkata Hub	2026-01-31 11:26:24
593	101	Arrived at destination facility	Mumbai Hub	2026-02-01 09:26:24
594	101	Out for delivery	Hyderabad Hub	2026-02-02 09:26:24
595	101	Successfully delivered	Kolkata Hub	2026-02-03 09:26:24
596	102	Order picked up from seller	Kolkata Hub	2025-11-03 06:32:03
597	102	Shipment arrived at origin facility	Hyderabad Hub	2025-11-03 11:32:03
598	102	In transit to destination city	Ahmedabad Hub	2025-11-04 06:32:03
599	102	Arrived at destination facility	Hyderabad Hub	2025-11-05 06:32:03
600	102	Out for delivery	Pune Hub	2025-11-06 05:32:03
601	103	Order picked up from seller	Bangalore Hub	2025-10-28 14:43:40
602	103	Shipment arrived at origin facility	Kolkata Hub	2025-10-28 16:43:40
603	103	In transit to destination city	Mumbai Hub	2025-10-29 12:43:40
604	103	Arrived at destination facility	Hyderabad Hub	2025-10-30 12:43:40
605	103	Out for delivery	Pune Hub	2025-10-31 12:43:40
606	103	Successfully delivered	Delhi Hub	2025-11-01 12:43:40
607	104	Order picked up from seller	Delhi Hub	2025-10-21 21:30:08
608	104	Shipment arrived at origin facility	Mumbai Hub	2025-10-22 02:30:08
609	104	In transit to destination city	Mumbai Hub	2025-10-22 20:30:08
610	104	Arrived at destination facility	Hyderabad Hub	2025-10-23 21:30:08
611	104	Out for delivery	Pune Hub	2025-10-24 21:30:08
612	105	Order picked up from seller	Kolkata Hub	2025-09-26 04:37:58
613	105	Shipment arrived at origin facility	Kolkata Hub	2025-09-26 06:37:58
614	105	In transit to destination city	Bangalore Hub	2025-09-27 02:37:58
615	105	Arrived at destination facility	Delhi Hub	2025-09-28 03:37:58
616	105	Out for delivery	Ahmedabad Hub	2025-09-29 02:37:58
617	106	Order picked up from seller	Delhi Hub	2025-11-27 18:16:14
618	106	Shipment arrived at origin facility	Hyderabad Hub	2025-11-28 00:16:14
619	106	In transit to destination city	Pune Hub	2025-11-28 19:16:14
620	106	Arrived at destination facility	Ahmedabad Hub	2025-11-29 18:16:14
621	106	Out for delivery	Kolkata Hub	2025-11-30 18:16:14
622	106	Successfully delivered	Hyderabad Hub	2025-12-01 18:16:14
623	106	Return pickup scheduled	Ahmedabad Hub	2025-12-02 19:16:14
624	106	Item picked up for return	Kolkata Hub	2025-12-03 20:16:14
625	106	Return received at warehouse	Ahmedabad Hub	2025-12-04 18:16:14
626	107	Order picked up from seller	Pune Hub	2026-01-31 22:34:56
627	107	Shipment arrived at origin facility	Delhi Hub	2026-02-01 02:34:56
628	107	In transit to destination city	Bangalore Hub	2026-02-01 21:34:56
629	107	Arrived at destination facility	Hyderabad Hub	2026-02-02 21:34:56
630	107	Out for delivery	Delhi Hub	2026-02-03 22:34:56
631	107	Successfully delivered	Pune Hub	2026-02-04 22:34:56
632	108	Order picked up from seller	Kolkata Hub	2025-11-16 15:47:15
633	108	Shipment arrived at origin facility	Pune Hub	2025-11-16 18:47:15
634	108	In transit to destination city	Hyderabad Hub	2025-11-17 15:47:15
635	108	Arrived at destination facility	Pune Hub	2025-11-18 13:47:15
636	108	Out for delivery	Delhi Hub	2025-11-19 15:47:15
637	108	Successfully delivered	Kolkata Hub	2025-11-20 13:47:15
638	109	Order picked up from seller	Chennai Hub	2025-11-27 12:03:20
639	109	Shipment arrived at origin facility	Kolkata Hub	2025-11-27 16:03:20
640	109	In transit to destination city	Chennai Hub	2025-11-28 11:03:20
641	109	Arrived at destination facility	Chennai Hub	2025-11-29 11:03:20
642	109	Out for delivery	Bangalore Hub	2025-11-30 11:03:20
643	110	Order picked up from seller	Kolkata Hub	2025-05-13 21:51:47
644	110	Shipment arrived at origin facility	Chennai Hub	2025-05-14 00:51:47
645	110	In transit to destination city	Delhi Hub	2025-05-14 20:51:47
646	110	Arrived at destination facility	Delhi Hub	2025-05-15 21:51:47
647	110	Out for delivery	Kolkata Hub	2025-05-16 22:51:47
648	110	Successfully delivered	Hyderabad Hub	2025-05-17 22:51:47
649	111	Order picked up from seller	Kolkata Hub	2025-04-30 13:46:23
650	111	Shipment arrived at origin facility	Kolkata Hub	2025-04-30 17:46:23
651	111	In transit to destination city	Hyderabad Hub	2025-05-01 14:46:23
652	111	Arrived at destination facility	Ahmedabad Hub	2025-05-02 14:46:23
653	111	Out for delivery	Ahmedabad Hub	2025-05-03 15:46:23
654	111	Successfully delivered	Mumbai Hub	2025-05-04 13:46:23
655	112	Order picked up from seller	Mumbai Hub	2025-06-14 00:14:05
656	112	Shipment arrived at origin facility	Chennai Hub	2025-06-14 04:14:05
657	112	In transit to destination city	Delhi Hub	2025-06-15 02:14:05
658	112	Arrived at destination facility	Chennai Hub	2025-06-16 02:14:05
659	112	Out for delivery	Delhi Hub	2025-06-17 02:14:05
660	112	Successfully delivered	Pune Hub	2025-06-18 00:14:05
661	113	Order picked up from seller	Ahmedabad Hub	2025-10-23 17:46:04
662	113	Shipment arrived at origin facility	Pune Hub	2025-10-23 23:46:04
663	113	In transit to destination city	Chennai Hub	2025-10-24 19:46:04
664	113	Arrived at destination facility	Bangalore Hub	2025-10-25 18:46:04
665	113	Out for delivery	Mumbai Hub	2025-10-26 18:46:04
666	113	Successfully delivered	Delhi Hub	2025-10-27 17:46:04
667	113	Return pickup scheduled	Mumbai Hub	2025-10-28 19:46:04
668	113	Item picked up for return	Hyderabad Hub	2025-10-29 17:46:04
669	113	Return received at warehouse	Chennai Hub	2025-10-30 19:46:04
670	114	Order picked up from seller	Mumbai Hub	2025-12-11 06:15:28
671	114	Shipment arrived at origin facility	Delhi Hub	2025-12-11 12:15:28
672	114	In transit to destination city	Bangalore Hub	2025-12-12 06:15:28
673	114	Arrived at destination facility	Chennai Hub	2025-12-13 07:15:28
674	114	Out for delivery	Pune Hub	2025-12-14 07:15:28
675	114	Successfully delivered	Chennai Hub	2025-12-15 07:15:28
676	115	Order picked up from seller	Mumbai Hub	2025-06-26 20:34:32
677	115	Shipment arrived at origin facility	Mumbai Hub	2025-06-26 23:34:32
678	115	In transit to destination city	Bangalore Hub	2025-06-27 19:34:32
679	115	Arrived at destination facility	Mumbai Hub	2025-06-28 19:34:32
680	115	Out for delivery	Hyderabad Hub	2025-06-29 19:34:32
681	115	Successfully delivered	Mumbai Hub	2025-06-30 20:34:32
682	116	Order picked up from seller	Mumbai Hub	2025-11-27 15:31:02
683	116	Shipment arrived at origin facility	Chennai Hub	2025-11-27 17:31:02
684	116	In transit to destination city	Mumbai Hub	2025-11-28 13:31:02
685	116	Arrived at destination facility	Kolkata Hub	2025-11-29 14:31:02
686	116	Out for delivery	Hyderabad Hub	2025-11-30 14:31:02
687	117	Order picked up from seller	Chennai Hub	2025-12-31 04:34:13
688	117	Shipment arrived at origin facility	Pune Hub	2025-12-31 09:34:13
689	117	In transit to destination city	Mumbai Hub	2026-01-01 06:34:13
690	117	Arrived at destination facility	Mumbai Hub	2026-01-02 06:34:13
691	117	Out for delivery	Pune Hub	2026-01-03 05:34:13
692	117	Successfully delivered	Pune Hub	2026-01-04 06:34:13
693	118	Order picked up from seller	Chennai Hub	2025-05-27 08:06:12
694	118	Shipment arrived at origin facility	Mumbai Hub	2025-05-27 13:06:12
695	118	In transit to destination city	Ahmedabad Hub	2025-05-28 08:06:12
696	118	Arrived at destination facility	Ahmedabad Hub	2025-05-29 09:06:12
697	118	Out for delivery	Mumbai Hub	2025-05-30 08:06:12
698	119	Order picked up from seller	Ahmedabad Hub	2025-07-25 09:55:35
699	119	Shipment arrived at origin facility	Kolkata Hub	2025-07-25 12:55:35
700	119	In transit to destination city	Bangalore Hub	2025-07-26 08:55:35
701	119	Arrived at destination facility	Ahmedabad Hub	2025-07-27 08:55:35
702	119	Out for delivery	Delhi Hub	2025-07-28 08:55:35
703	119	Successfully delivered	Kolkata Hub	2025-07-29 08:55:35
704	120	Order picked up from seller	Chennai Hub	2026-01-21 17:28:50
705	120	Shipment arrived at origin facility	Kolkata Hub	2026-01-21 20:28:50
706	120	In transit to destination city	Chennai Hub	2026-01-22 15:28:50
707	120	Arrived at destination facility	Pune Hub	2026-01-23 15:28:50
708	120	Out for delivery	Chennai Hub	2026-01-24 16:28:50
709	121	Order picked up from seller	Chennai Hub	2025-09-02 21:59:55
710	121	Shipment arrived at origin facility	Kolkata Hub	2025-09-02 23:59:55
711	121	In transit to destination city	Pune Hub	2025-09-03 21:59:55
712	121	Arrived at destination facility	Delhi Hub	2025-09-04 19:59:55
713	121	Out for delivery	Mumbai Hub	2025-09-05 21:59:55
714	121	Successfully delivered	Bangalore Hub	2025-09-06 20:59:55
715	122	Order picked up from seller	Kolkata Hub	2025-10-23 15:44:58
716	122	Shipment arrived at origin facility	Ahmedabad Hub	2025-10-23 20:44:58
717	122	In transit to destination city	Delhi Hub	2025-10-24 16:44:58
718	122	Arrived at destination facility	Delhi Hub	2025-10-25 14:44:58
719	122	Out for delivery	Mumbai Hub	2025-10-26 14:44:58
720	123	Order picked up from seller	Hyderabad Hub	2026-01-16 22:48:45
721	123	Shipment arrived at origin facility	Ahmedabad Hub	2026-01-17 04:48:45
722	123	In transit to destination city	Hyderabad Hub	2026-01-18 00:48:45
723	123	Arrived at destination facility	Hyderabad Hub	2026-01-18 23:48:45
724	123	Out for delivery	Kolkata Hub	2026-01-19 23:48:45
725	123	Successfully delivered	Delhi Hub	2026-01-20 22:48:45
726	124	Order picked up from seller	Kolkata Hub	2026-02-19 18:51:51
727	124	Shipment arrived at origin facility	Ahmedabad Hub	2026-02-19 20:51:51
728	124	In transit to destination city	Delhi Hub	2026-02-20 16:51:51
729	124	Arrived at destination facility	Delhi Hub	2026-02-21 18:51:51
730	124	Out for delivery	Hyderabad Hub	2026-02-22 17:51:51
731	124	Successfully delivered	Ahmedabad Hub	2026-02-23 17:51:51
732	125	Order picked up from seller	Delhi Hub	2025-07-14 05:23:28
733	125	Shipment arrived at origin facility	Pune Hub	2025-07-14 09:23:28
734	125	In transit to destination city	Kolkata Hub	2025-07-15 03:23:28
735	125	Arrived at destination facility	Delhi Hub	2025-07-16 03:23:28
736	125	Out for delivery	Pune Hub	2025-07-17 04:23:28
737	125	Successfully delivered	Pune Hub	2025-07-18 05:23:28
738	125	Return pickup scheduled	Bangalore Hub	2025-07-19 03:23:28
739	125	Item picked up for return	Mumbai Hub	2025-07-20 03:23:28
740	125	Return received at warehouse	Hyderabad Hub	2025-07-21 04:23:28
741	126	Order picked up from seller	Kolkata Hub	2025-11-23 04:42:29
742	126	Shipment arrived at origin facility	Pune Hub	2025-11-23 08:42:29
743	126	In transit to destination city	Hyderabad Hub	2025-11-24 03:42:29
744	126	Arrived at destination facility	Pune Hub	2025-11-25 03:42:29
745	126	Out for delivery	Bangalore Hub	2025-11-26 03:42:29
746	126	Successfully delivered	Delhi Hub	2025-11-27 02:42:29
747	127	Order picked up from seller	Bangalore Hub	2025-04-05 03:19:01
748	127	Shipment arrived at origin facility	Bangalore Hub	2025-04-05 05:19:01
749	127	In transit to destination city	Ahmedabad Hub	2025-04-06 03:19:01
750	127	Arrived at destination facility	Bangalore Hub	2025-04-07 02:19:01
751	127	Out for delivery	Kolkata Hub	2025-04-08 01:19:01
752	128	Order picked up from seller	Pune Hub	2025-09-11 19:08:48
753	128	Shipment arrived at origin facility	Pune Hub	2025-09-11 23:08:48
754	128	In transit to destination city	Ahmedabad Hub	2025-09-12 18:08:48
755	128	Arrived at destination facility	Hyderabad Hub	2025-09-13 18:08:48
756	128	Out for delivery	Kolkata Hub	2025-09-14 17:08:48
757	129	Order picked up from seller	Ahmedabad Hub	2025-05-16 16:04:27
758	129	Shipment arrived at origin facility	Ahmedabad Hub	2025-05-16 18:04:27
759	129	In transit to destination city	Bangalore Hub	2025-05-17 16:04:27
760	129	Arrived at destination facility	Kolkata Hub	2025-05-18 16:04:27
761	129	Out for delivery	Bangalore Hub	2025-05-19 16:04:27
762	129	Successfully delivered	Ahmedabad Hub	2025-05-20 15:04:27
763	129	Return pickup scheduled	Ahmedabad Hub	2025-05-21 16:04:27
764	129	Item picked up for return	Mumbai Hub	2025-05-22 14:04:27
765	129	Return received at warehouse	Pune Hub	2025-05-23 16:04:27
\.


--
-- Data for Name: shipments; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.shipments (shipment_id, order_id, carrier, tracking_number, status, weight_kg, shipping_charge, shipped_at, delivered_at) FROM stdin;
1	2	Blue Dart	BLU2079130252	in_transit	1.94	49.00	2025-09-10 13:05:26	\N
2	3	Delhivery	DEL7482735562	delivered	0.36	49.00	2025-11-10 17:32:18	2025-11-12 17:32:18
3	5	Ekart	EKA3000032053	delivered	3.47	99.00	2025-03-16 01:57:58	2025-03-20 01:57:58
4	6	DTDC	DTD8242632879	delivered	9.79	0.00	2025-03-14 10:17:27	2025-03-18 10:17:27
5	7	Blue Dart	BLU7506121605	returned	1.39	0.00	2026-01-18 00:11:28	2026-01-22 00:11:28
6	8	Ekart	EKA1608427530	delivered	4.90	0.00	2025-12-11 05:36:52	2025-12-14 05:36:52
7	9	Xpressbees	XPR9272791869	delivered	7.73	49.00	2025-12-14 21:36:43	2025-12-20 21:36:43
8	10	Blue Dart	BLU3768112689	delivered	4.76	0.00	2026-01-17 03:29:10	2026-01-20 03:29:10
9	12	Shadowfax	SHA7516657898	in_transit	4.90	0.00	2025-10-05 11:41:37	\N
10	13	DTDC	DTD4694433572	delivered	5.65	0.00	2025-11-30 13:46:14	2025-12-04 13:46:14
11	14	Xpressbees	XPR1441644725	in_transit	8.71	149.00	2025-04-02 21:10:41	\N
12	15	Shadowfax	SHA9182863369	in_transit	5.53	99.00	2025-08-14 06:34:35	\N
13	16	DTDC	DTD7093147042	delivered	7.97	149.00	2026-01-14 09:06:17	2026-01-21 09:06:17
14	17	Blue Dart	BLU8176563158	returned	7.81	149.00	2025-09-06 17:00:04	2025-09-12 17:00:04
15	18	Blue Dart	BLU5413166229	delivered	7.81	0.00	2025-12-09 01:24:58	2025-12-12 01:24:58
16	19	Xpressbees	XPR8045891233	delivered	7.05	149.00	2025-08-29 10:28:25	2025-09-01 10:28:25
17	21	Shadowfax	SHA3108446452	in_transit	8.11	149.00	2025-10-05 01:09:05	\N
18	22	India Post	IND1924081689	delivered	9.31	0.00	2025-03-26 09:57:48	2025-03-31 09:57:48
19	24	Xpressbees	XPR8672030718	delivered	3.34	149.00	2025-07-19 23:44:46	2025-07-24 23:44:46
20	25	DTDC	DTD2642227910	returned	0.50	99.00	2026-02-28 05:44:15	2026-03-03 05:44:15
21	26	Blue Dart	BLU2787350431	delivered	10.00	149.00	2025-07-16 21:32:00	2025-07-22 21:32:00
22	27	Delhivery	DEL5611404245	delivered	7.86	49.00	2025-08-01 23:48:20	2025-08-04 23:48:20
23	29	Blue Dart	BLU6479130637	in_transit	7.39	149.00	2025-04-17 09:39:07	\N
24	30	Xpressbees	XPR2110596323	delivered	2.94	99.00	2025-12-08 18:40:18	2025-12-10 18:40:18
25	32	Ekart	EKA8208248382	delivered	5.37	99.00	2025-06-08 16:19:56	2025-06-15 16:19:56
26	33	India Post	IND4871206792	delivered	9.54	0.00	2025-08-31 12:29:32	2025-09-07 12:29:32
27	35	DTDC	DTD2518053019	delivered	6.11	0.00	2025-03-22 21:19:36	2025-03-28 21:19:36
28	37	Delhivery	DEL7160723883	delivered	3.17	149.00	2025-05-23 18:39:01	2025-05-26 18:39:01
29	38	India Post	IND5861296633	in_transit	1.06	0.00	2026-02-06 07:02:21	\N
30	39	India Post	IND8780661749	delivered	4.00	0.00	2025-05-20 08:33:51	2025-05-27 08:33:51
31	41	Xpressbees	XPR4548522320	in_transit	8.39	0.00	2025-10-27 10:19:59	\N
32	42	Xpressbees	XPR9896554374	delivered	8.03	49.00	2025-06-10 02:34:21	2025-06-16 02:34:21
33	43	India Post	IND3999952351	in_transit	4.45	99.00	2025-03-03 07:25:00	\N
34	46	DTDC	DTD1461123603	delivered	4.76	99.00	2025-06-02 21:27:46	2025-06-05 21:27:46
35	47	India Post	IND4908433066	returned	1.75	99.00	2026-01-02 15:10:31	2026-01-08 15:10:31
36	48	Blue Dart	BLU5798203266	delivered	1.40	0.00	2025-12-04 21:01:00	2025-12-10 21:01:00
37	49	India Post	IND9491939277	in_transit	0.56	99.00	2025-08-29 06:42:59	\N
38	52	Xpressbees	XPR3411120325	in_transit	9.59	0.00	2025-03-30 19:16:02	\N
39	53	Blue Dart	BLU5975501461	delivered	9.11	0.00	2025-05-29 12:15:21	2025-06-03 12:15:21
40	58	Ekart	EKA7825717390	in_transit	8.73	0.00	2025-03-11 02:15:37	\N
41	59	DTDC	DTD7302059394	delivered	9.27	0.00	2025-11-25 13:41:29	2025-12-02 13:41:29
42	60	Delhivery	DEL1680345154	delivered	0.52	0.00	2026-02-21 14:06:46	2026-02-24 14:06:46
43	61	Ekart	EKA9607032725	delivered	3.79	0.00	2025-12-01 11:21:48	2025-12-06 11:21:48
44	62	India Post	IND3196799071	delivered	3.16	49.00	2026-01-09 03:24:58	2026-01-11 03:24:58
45	63	DTDC	DTD8085931845	delivered	8.31	0.00	2026-02-08 10:50:34	2026-02-15 10:50:34
46	64	Xpressbees	XPR8185275391	delivered	6.52	49.00	2025-11-11 05:58:03	2025-11-17 05:58:03
47	65	Xpressbees	XPR6553659424	delivered	7.21	99.00	2025-08-29 16:59:46	2025-09-03 16:59:46
48	66	India Post	IND3682030467	in_transit	8.35	149.00	2025-04-21 06:16:15	\N
49	68	Ekart	EKA9574237482	in_transit	1.68	0.00	2025-08-21 03:36:45	\N
50	69	Xpressbees	XPR4809175734	delivered	7.76	0.00	2025-09-17 23:04:56	2025-09-19 23:04:56
51	71	Shadowfax	SHA8977171017	delivered	3.47	99.00	2025-04-05 18:43:21	2025-04-09 18:43:21
52	72	Shadowfax	SHA1447246645	in_transit	3.12	149.00	2025-07-18 03:33:24	\N
53	75	India Post	IND6466919266	delivered	6.99	49.00	2025-05-18 21:24:01	2025-05-25 21:24:01
54	77	DTDC	DTD4543639991	delivered	8.05	99.00	2025-10-21 00:05:13	2025-10-24 00:05:13
55	79	DTDC	DTD1134860257	in_transit	7.51	149.00	2025-09-30 11:39:01	\N
56	80	Blue Dart	BLU9250652575	delivered	1.75	49.00	2026-01-20 15:29:43	2026-01-22 15:29:43
57	81	Delhivery	DEL1995066001	in_transit	5.90	49.00	2025-05-13 01:11:42	\N
58	82	Shadowfax	SHA8090362487	delivered	7.07	99.00	2025-09-12 19:30:16	2025-09-15 19:30:16
59	83	Shadowfax	SHA4296217380	in_transit	2.18	0.00	2025-11-26 11:27:45	\N
60	88	Shadowfax	SHA8913393680	in_transit	9.55	0.00	2025-07-29 19:56:49	\N
61	91	India Post	IND7546865548	delivered	5.67	149.00	2025-08-26 09:22:45	2025-09-01 09:22:45
62	94	India Post	IND4397689838	in_transit	4.07	0.00	2025-08-29 20:17:48	\N
63	97	Shadowfax	SHA5707171833	returned	7.93	0.00	2025-10-15 12:31:33	2025-10-18 12:31:33
64	98	Xpressbees	XPR1326836936	delivered	9.82	0.00	2025-11-16 19:09:05	2025-11-22 19:09:05
65	99	Blue Dart	BLU5530539445	delivered	6.64	49.00	2026-03-02 01:56:40	2026-03-08 01:56:40
66	100	Shadowfax	SHA5114172894	delivered	8.26	149.00	2025-12-22 13:15:30	2025-12-25 13:15:30
67	102	Xpressbees	XPR8578531770	delivered	7.73	149.00	2025-07-29 18:43:05	2025-08-02 18:43:05
68	103	Ekart	EKA6610713502	in_transit	1.40	49.00	2025-11-12 21:38:26	\N
69	106	DTDC	DTD6683590787	delivered	3.05	99.00	2026-01-23 05:09:31	2026-01-29 05:09:31
70	107	Blue Dart	BLU2531927015	delivered	7.34	149.00	2025-05-18 11:19:50	2025-05-23 11:19:50
71	108	Blue Dart	BLU2044569997	delivered	8.96	49.00	2025-12-16 19:35:12	2025-12-23 19:35:12
72	111	Blue Dart	BLU3656090269	delivered	2.89	0.00	2025-06-30 22:37:27	2025-07-06 22:37:27
73	112	DTDC	DTD4541626178	delivered	9.28	0.00	2025-06-20 10:21:01	2025-06-27 10:21:01
74	116	Delhivery	DEL9049349182	delivered	5.45	49.00	2025-12-06 20:29:10	2025-12-13 20:29:10
75	117	India Post	IND8593939058	in_transit	2.23	149.00	2025-07-28 12:03:18	\N
76	118	Xpressbees	XPR7357102766	delivered	7.86	0.00	2025-05-13 23:48:08	2025-05-18 23:48:08
77	119	Blue Dart	BLU2509341397	delivered	3.98	49.00	2025-04-07 07:09:44	2025-04-13 07:09:44
78	120	DTDC	DTD5751367925	delivered	7.11	0.00	2025-03-07 06:30:31	2025-03-12 06:30:31
79	122	Blue Dart	BLU2853874652	delivered	5.84	0.00	2025-04-21 01:44:49	2025-04-23 01:44:49
80	124	Delhivery	DEL3189834317	in_transit	7.31	0.00	2025-11-09 00:50:04	\N
81	125	Xpressbees	XPR7368401254	delivered	4.00	149.00	2026-01-20 10:23:21	2026-01-23 10:23:21
82	126	India Post	IND7854694535	delivered	3.52	149.00	2025-05-03 00:15:21	2025-05-10 00:15:21
83	127	Delhivery	DEL5275538754	in_transit	7.55	0.00	2026-03-01 02:36:24	\N
84	128	Blue Dart	BLU9045372568	delivered	3.03	49.00	2025-10-28 13:28:21	2025-11-02 13:28:21
85	129	DTDC	DTD4370707632	delivered	0.73	0.00	2025-05-31 10:36:22	2025-06-02 10:36:22
86	130	Shadowfax	SHA1627431955	returned	1.54	0.00	2025-03-27 13:39:38	2025-04-02 13:39:38
87	131	Shadowfax	SHA6755349248	delivered	6.74	49.00	2025-08-19 14:40:46	2025-08-24 14:40:46
88	132	Delhivery	DEL3750993811	delivered	0.43	149.00	2026-01-04 07:30:15	2026-01-11 07:30:15
89	133	Blue Dart	BLU4716600107	in_transit	7.47	99.00	2025-08-16 18:44:59	\N
90	135	Delhivery	DEL4923374120	delivered	7.12	99.00	2026-02-11 19:17:15	2026-02-15 19:17:15
91	139	Shadowfax	SHA1404476269	in_transit	6.88	99.00	2025-11-10 02:03:15	\N
92	140	Delhivery	DEL8626454506	in_transit	4.91	0.00	2025-10-29 07:08:02	\N
93	142	Delhivery	DEL1807507268	in_transit	3.47	149.00	2025-10-01 19:11:33	\N
94	143	Xpressbees	XPR8956533502	delivered	7.02	49.00	2025-09-12 13:01:48	2025-09-19 13:01:48
95	145	DTDC	DTD6389621414	delivered	8.80	0.00	2026-02-12 04:39:25	2026-02-17 04:39:25
96	146	Blue Dart	BLU7579598062	delivered	3.20	149.00	2026-01-16 18:27:10	2026-01-22 18:27:10
97	147	DTDC	DTD7230917723	delivered	7.03	99.00	2025-06-20 17:38:20	2025-06-25 17:38:20
98	148	Blue Dart	BLU2138283490	in_transit	1.52	49.00	2025-07-09 01:57:20	\N
99	149	Ekart	EKA7280907732	delivered	4.19	149.00	2025-04-06 05:19:59	2025-04-09 05:19:59
100	150	Blue Dart	BLU2698943429	delivered	4.98	0.00	2026-02-26 17:43:53	2026-03-05 17:43:53
101	151	Ekart	EKA5436226511	delivered	2.19	149.00	2026-01-30 09:26:24	2026-02-03 09:26:24
102	153	Shadowfax	SHA3312314862	in_transit	5.20	0.00	2025-11-03 05:32:03	\N
103	155	India Post	IND5520258807	delivered	3.37	49.00	2025-10-28 12:43:40	2025-11-01 12:43:40
104	161	Shadowfax	SHA7459053923	in_transit	9.62	99.00	2025-10-21 20:30:08	\N
105	162	Xpressbees	XPR2295149209	in_transit	7.70	99.00	2025-09-26 02:37:58	\N
106	164	Blue Dart	BLU3324971484	returned	6.52	99.00	2025-11-27 18:16:14	2025-12-03 18:16:14
107	165	Blue Dart	BLU6821285603	delivered	6.48	0.00	2026-01-31 20:34:56	2026-02-05 20:34:56
108	166	Blue Dart	BLU1654874096	delivered	1.21	49.00	2025-11-16 13:47:15	2025-11-19 13:47:15
109	167	Xpressbees	XPR7231599341	in_transit	0.49	99.00	2025-11-27 10:03:20	\N
110	168	Ekart	EKA3181821627	delivered	1.79	149.00	2025-05-13 20:51:47	2025-05-19 20:51:47
111	169	Delhivery	DEL3048416642	delivered	5.22	99.00	2025-04-30 13:46:23	2025-05-05 13:46:23
112	170	DTDC	DTD4434158843	delivered	3.04	0.00	2025-06-14 00:14:05	2025-06-19 00:14:05
113	171	DTDC	DTD3540871166	returned	5.08	49.00	2025-10-23 17:46:04	2025-10-28 17:46:04
114	172	DTDC	DTD4798291645	delivered	5.28	0.00	2025-12-11 06:15:28	2025-12-15 06:15:28
115	173	Delhivery	DEL3895805200	delivered	4.14	149.00	2025-06-26 19:34:32	2025-07-03 19:34:32
116	174	Ekart	EKA8805733325	in_transit	7.97	99.00	2025-11-27 13:31:02	\N
117	176	India Post	IND3968851367	delivered	2.67	49.00	2025-12-31 04:34:13	2026-01-03 04:34:13
118	179	India Post	IND2841308031	in_transit	7.74	149.00	2025-05-27 07:06:12	\N
119	180	Delhivery	DEL8709225117	delivered	2.74	49.00	2025-07-25 08:55:35	2025-07-30 08:55:35
120	182	Delhivery	DEL6775190995	in_transit	4.82	0.00	2026-01-21 15:28:50	\N
121	184	Blue Dart	BLU7611317433	delivered	6.44	49.00	2025-09-02 19:59:55	2025-09-05 19:59:55
122	186	Blue Dart	BLU2933776248	in_transit	4.28	49.00	2025-10-23 14:44:58	\N
123	187	Delhivery	DEL8720835884	delivered	2.84	149.00	2026-01-16 22:48:45	2026-01-18 22:48:45
124	188	Ekart	EKA4509788224	delivered	5.80	49.00	2026-02-19 16:51:51	2026-02-26 16:51:51
125	190	Shadowfax	SHA4468043921	returned	2.36	99.00	2025-07-14 03:23:28	2025-07-19 03:23:28
126	193	Shadowfax	SHA7148502772	delivered	0.48	149.00	2025-11-23 02:42:29	2025-11-26 02:42:29
127	195	India Post	IND5631736707	in_transit	6.76	99.00	2025-04-05 01:19:01	\N
128	196	Shadowfax	SHA3729976371	in_transit	3.51	0.00	2025-09-11 17:08:48	\N
129	199	Delhivery	DEL2431872894	returned	5.09	0.00	2025-05-16 14:04:27	2025-05-19 14:04:27
\.


--
-- Data for Name: user_role_mapping; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.user_role_mapping (mapping_id, user_id, role_id, assigned_at) FROM stdin;
1	1	3	2026-01-29 04:45:59
2	2	3	2025-08-09 02:13:04
3	3	3	2025-10-14 00:50:12
4	4	3	2025-12-11 17:57:59
5	5	3	2026-02-24 01:29:42
6	6	3	2026-02-22 22:52:09
7	7	3	2026-01-10 21:57:14
8	8	3	2026-02-17 18:12:42
9	9	3	2025-12-28 21:07:34
10	10	3	2026-01-10 19:24:25
11	11	3	2025-12-28 22:24:20
12	12	3	2025-12-08 13:41:33
13	13	3	2026-02-25 13:40:18
14	14	3	2026-01-30 14:31:04
15	15	3	2026-01-10 19:07:12
16	16	3	2026-01-16 17:15:03
17	17	3	2025-12-13 14:57:37
18	18	3	2025-07-31 16:11:49
19	19	3	2025-09-04 12:01:34
20	20	3	2025-08-10 21:43:28
21	21	3	2026-02-09 08:42:22
22	22	3	2025-06-30 16:27:08
23	23	3	2025-11-15 01:05:04
24	24	3	2026-01-27 13:40:48
25	25	3	2026-01-15 13:12:26
26	26	3	2026-02-20 15:15:37
27	27	3	2025-11-23 16:23:49
28	28	3	2025-12-13 06:11:40
29	29	3	2025-09-21 23:01:07
30	30	3	2025-10-28 03:57:53
31	31	3	2026-02-28 19:15:05
32	32	3	2026-02-04 21:17:19
33	33	3	2026-02-04 00:54:04
34	34	3	2025-12-02 06:33:26
35	35	3	2025-11-07 12:23:10
36	36	3	2026-01-30 19:05:57
37	37	3	2025-11-28 06:35:03
38	38	3	2026-02-27 23:01:26
39	39	3	2026-02-04 08:20:58
40	40	3	2026-02-11 23:56:27
41	41	3	2026-02-24 03:34:32
42	42	3	2026-01-16 03:46:29
43	43	3	2025-12-29 05:06:54
44	44	3	2026-02-09 01:41:14
45	45	3	2026-02-20 00:12:16
46	46	3	2025-11-04 04:06:49
47	47	3	2026-02-06 15:27:49
48	48	3	2025-09-09 05:50:51
49	49	3	2025-05-24 06:48:25
50	50	3	2025-08-11 13:46:53
51	51	3	2025-10-01 09:09:43
52	52	3	2026-02-21 22:43:50
53	53	3	2026-01-16 01:24:07
54	54	3	2025-08-29 17:20:50
55	55	3	2025-12-02 04:46:23
56	56	3	2026-02-20 02:24:35
57	57	3	2025-12-20 20:30:09
58	58	3	2026-01-31 13:25:52
59	59	3	2026-01-11 10:36:56
60	60	3	2026-02-09 02:33:05
61	61	3	2026-03-01 12:50:55
62	62	3	2026-01-17 15:51:29
63	63	3	2025-10-06 08:45:34
64	64	3	2026-02-21 19:45:11
65	65	3	2025-08-10 07:45:03
66	66	3	2026-01-27 20:48:13
67	67	3	2025-06-15 11:13:15
68	68	3	2026-02-24 07:03:39
69	69	3	2026-02-21 21:59:50
70	70	3	2026-02-25 06:52:45
71	71	3	2026-02-25 23:40:33
72	72	3	2025-12-19 08:38:42
73	73	3	2025-11-05 23:32:02
74	74	3	2026-01-28 15:42:20
75	75	3	2025-09-12 03:36:26
76	76	3	2026-02-28 12:21:38
77	77	3	2026-01-19 16:51:07
78	78	3	2026-01-27 20:25:52
79	79	3	2025-12-29 01:20:26
80	80	3	2026-02-21 19:16:43
81	81	3	2025-11-28 00:45:53
82	82	3	2026-02-06 19:40:34
83	83	3	2025-12-19 06:30:47
84	84	3	2025-11-15 15:23:58
85	85	3	2026-01-29 18:46:03
86	86	3	2025-09-20 02:07:46
87	87	3	2025-11-09 21:03:52
88	88	3	2025-11-21 03:39:27
89	89	3	2025-09-02 23:09:52
90	90	3	2025-09-07 23:15:35
91	91	3	2026-02-25 19:08:30
92	92	3	2025-07-09 21:57:02
93	93	3	2026-02-13 23:50:01
94	94	3	2026-02-23 09:34:11
95	95	3	2025-08-31 01:13:55
96	96	3	2026-01-20 16:21:02
97	97	3	2025-11-11 01:25:52
98	98	3	2026-01-05 14:02:27
99	99	3	2025-12-13 11:55:01
100	100	3	2025-07-17 23:36:59
101	74	1	2026-02-07 16:18:33
102	87	1	2025-09-07 08:37:44
103	70	1	2026-02-22 01:15:48
104	99	2	2026-01-12 12:20:36
105	19	2	2025-12-25 04:47:06
106	38	2	2026-02-28 05:16:53
107	6	2	2026-02-24 12:14:28
108	37	2	2025-11-28 00:12:06
109	92	2	2025-06-10 18:44:18
110	11	2	2025-08-31 10:56:10
111	45	2	2026-02-27 04:51:32
112	35	4	2025-12-12 18:09:03
113	72	4	2025-10-17 09:08:26
114	90	4	2025-06-23 07:12:13
115	18	4	2026-01-01 17:22:38
116	14	4	2025-09-05 15:08:37
117	79	4	2026-01-14 04:03:02
118	95	4	2025-10-30 09:19:17
119	76	4	2025-12-06 12:22:54
120	31	4	2026-02-28 22:58:47
121	32	4	2025-08-17 14:48:10
122	7	4	2025-11-14 19:34:05
123	86	4	2026-01-03 11:15:32
124	68	4	2026-02-20 05:42:47
125	29	4	2025-08-26 16:10:10
126	82	4	2026-02-23 10:45:07
127	61	5	2026-02-18 15:31:29
128	62	5	2025-10-30 18:40:06
129	84	5	2025-12-03 17:30:55
130	26	5	2026-01-20 18:57:13
131	97	5	2025-07-21 13:47:06
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.user_roles (role_id, role_name, description, is_active) FROM stdin;
1	super_admin	Full system access	t
2	admin	Manage products, orders, users	t
3	customer	Browse and purchase products	t
4	seller	List and manage own products	t
5	support_agent	Handle customer queries and returns	t
\.


--
-- Data for Name: user_sessions; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.user_sessions (session_id, session_uuid, user_id, token, created_at, expires_at, is_active, device, ip_address) FROM stdin;
1	451c63c4-bf7a-4b00-9137-33de78694692	55	1e69caada68c4a5890c1e1f6c8c8de96	2025-08-08 09:29:55	2025-08-11 09:29:55	t	Mobile App/Android	39.136.72.19
2	300fa6dc-d287-4a35-9df5-86326088e064	8	923bb6d2c8f44bc2a352dc7383af04f7	2026-01-27 23:47:11	2026-01-28 11:47:11	f	Firefox/Linux	32.239.155.180
3	e84d2b1a-7d22-4f9c-93d4-e8a1b06fae69	52	7e5b8daa37a846c6b491a28597b9b9c1	2026-02-20 22:35:11	2026-02-23 22:35:11	f	Firefox/Linux	21.20.221.189
4	0bac5660-54ae-4a64-bd03-a0610e482e11	42	d5bd62fbe81e4173b7cd0b9d69c7dec1	2026-02-28 13:28:08	2026-03-01 01:28:08	t	Chrome/Windows	59.10.137.148
5	31bdb609-f0b3-4df2-a2e2-7e15ccc88547	6	e1ce15c6aa3b4531be0cf5b8a6d88364	2026-02-27 13:44:13	2026-02-27 19:44:13	f	Mobile App/iOS	167.226.142.47
6	1b04769c-d394-405c-a86d-2ee3b522df69	75	9251e178552b44a2adf5a482e603cf4e	2025-09-02 21:58:31	2025-09-09 21:58:31	f	Chrome/Windows	121.178.209.86
7	bb011d34-faf1-4b36-961e-8e35c1ee6ed6	42	feb4815a77134a22a667f28771c252c7	2025-11-23 15:25:48	2025-11-23 21:25:48	f	Firefox/Linux	178.253.147.170
8	78ec3e70-0472-4b0f-95de-be9349d842c8	52	e385620de8e046b196ea3eb3754241d9	2026-02-27 16:26:46	2026-02-27 17:26:46	f	Chrome/Windows	81.129.165.30
9	05cc10b9-28d4-4eb0-b294-382e209d9562	99	5c4dc07d91f547a4b0373be41e7817b1	2026-01-05 02:18:49	2026-01-08 02:18:49	t	Mobile App/Android	223.236.211.14
10	b1234830-f900-44d2-b657-9ee371dd5309	25	3823169e95c848f78f3d76044c7fd352	2026-02-25 11:25:38	2026-02-25 23:25:38	f	Mobile App/Android	114.26.104.69
11	4887305e-213c-4f77-a7dd-cfb20f3e4b35	71	e87137c378074fdca883de924b3cb7f4	2026-01-18 16:30:30	2026-01-19 04:30:30	f	Mobile App/Android	125.62.14.250
12	6b4a5a00-ad5a-49b4-9925-3565d246e40d	81	432678446a3f40d9a8b45d6fadd6ff12	2025-11-18 07:08:41	2025-11-25 07:08:41	t	Chrome/Android	142.7.208.24
13	173fb919-ef3e-4bb6-8376-1e8b01f01e78	29	f9021fc169b3482c9e5b2c6e959516a5	2026-02-11 09:59:11	2026-02-11 10:59:11	f	Chrome/Windows	166.78.255.239
14	027dca01-1752-4b45-b896-c2dddb9ac11d	92	586311afaf184d6d864ff6d57c5f8bd2	2025-07-11 00:35:01	2025-07-14 00:35:01	f	Firefox/Linux	214.247.241.63
15	29b4f9a1-f8e3-4b59-95d3-473874a4d91d	59	b8554e7c66e248dfba8c49039e2e8766	2026-01-30 15:28:54	2026-01-30 21:28:54	f	Safari/iOS	236.69.35.71
16	e2574c2d-d6ab-4f68-99ea-57bfadf411b3	99	ad2ae1cfa0804f92a472c9ca0890f2cf	2026-01-07 04:29:35	2026-01-07 16:29:35	f	Chrome/Windows	73.152.250.222
17	1e4476db-3202-4b89-af4a-b14233154f16	20	9a4df943ee0140608958c52a60c82abd	2025-09-24 16:28:16	2025-09-27 16:28:16	f	Chrome/Android	86.193.233.239
18	b0d87874-a5bb-4b4e-b121-368191b0d7dd	42	aeec994a331f4fbc82ddb10ac40e2700	2025-12-09 23:08:35	2025-12-16 23:08:35	t	Mobile App/iOS	99.119.210.12
19	59da5257-463c-46d8-8719-296bbbf170a6	41	538035de80cf4abe91b4c2d4193d42c2	2025-11-19 18:07:21	2025-11-26 18:07:21	f	Firefox/Linux	254.77.253.247
20	b7cbbbf1-38a5-44f7-b502-ac58fcdddd03	5	7072e86a51d34cdb92f819a1744f5182	2026-01-31 06:18:27	2026-02-03 06:18:27	f	Chrome/Windows	224.225.51.135
21	1d4805c8-0c0c-4d81-8fbd-e34d30a199ef	59	2b11f2f227da470e8821fb6b4a540c50	2025-07-06 12:22:07	2025-07-13 12:22:07	t	Firefox/Linux	223.79.38.121
22	b36ffdbe-df55-4548-b2f7-b989b607c041	34	062735f216144d05a36cd010aa8f2565	2025-12-23 19:56:19	2025-12-26 19:56:19	f	Mobile App/Android	21.168.194.245
23	b93814d1-7e48-4986-a614-c46fdb84a324	41	ee021f9839ee443f88e5252b77191f36	2026-01-18 11:51:22	2026-01-25 11:51:22	f	Mobile App/iOS	10.35.120.162
24	dfb988d2-4947-44e4-9373-b81144c5b3aa	88	dd1b7cbee8ba47888cb4ef0fcb9a6659	2025-11-18 23:50:02	2025-11-19 05:50:02	t	Firefox/Linux	251.50.51.114
25	eebee391-d1dd-4640-a681-7cf939bacd2a	22	6ad25b616cbf474ca4e9f2da9928cbce	2026-02-12 15:25:23	2026-02-13 03:25:23	t	Chrome/Windows	84.28.150.92
26	b22bd84a-d884-4225-81d7-a9073c25ab61	48	fa394f4a9fdb4122916798e3c20511ed	2026-01-11 19:50:20	2026-01-12 01:50:20	t	Mobile App/iOS	106.92.87.45
27	fbb4cafe-baf6-4dce-80a2-2022491f4bfe	11	3e13d1c9c16a4527a7723fe924f957e7	2026-02-05 16:24:03	2026-02-06 16:24:03	t	Firefox/Linux	234.73.118.119
28	60e932dc-8283-4575-aab9-71d92fd5d64a	82	6d6a9e30e1d3467f826bb1f2c97346ea	2025-09-21 12:35:26	2025-09-22 12:35:26	f	Mobile App/Android	3.238.147.174
29	542f1339-d3f9-4ac2-b994-b30f1077f1ac	70	674512e1145849b9a469bce5588726e8	2026-02-17 12:14:07	2026-02-17 13:14:07	f	Chrome/Android	253.153.217.177
30	9d86544e-d5c1-4814-b2da-4cd282c39781	33	ec1048432a2d4f8481d608a55140aad6	2026-01-11 13:56:20	2026-01-12 01:56:20	t	Firefox/Linux	219.247.54.61
31	2e94c2c7-33ab-4c26-92e1-4d1b85eb7b63	49	f9b58bb8892e4504a6a0754ced868312	2025-10-19 07:16:27	2025-10-19 19:16:27	f	Mobile App/Android	76.11.202.71
32	e7b827d0-b678-4673-8425-85d8a85639ed	2	e46ebdbde1b44439a704052ca3dac7f2	2025-11-13 04:08:36	2025-11-20 04:08:36	t	Mobile App/iOS	191.254.146.199
33	e604291a-7b56-42c3-b7b1-b41e25ffeb1c	30	0a13350a3e394ef2bc844302140e5469	2026-01-02 11:37:52	2026-01-02 23:37:52	t	Mobile App/Android	49.128.70.161
34	79d87dff-e2a6-4bf1-95ce-c3b09a6c9d23	13	f1e85bfe8afa4bb899771448b22be0a5	2026-02-28 21:50:11	2026-03-02 00:00:00	t	Chrome/Android	202.225.17.149
35	ed1f3e9a-b492-42b0-9fc2-fa91b1861aec	47	ae1151c7d36b42268117467877fc9587	2026-02-22 03:48:01	2026-02-22 09:48:01	t	Chrome/Android	84.212.89.52
36	493ce6c1-3162-4b1e-9951-529190a18608	17	2823c7438c134da3b556216585c9594b	2026-02-12 03:12:57	2026-02-15 03:12:57	f	Mobile App/iOS	129.139.84.66
37	168f94e6-edf5-4e79-8b6f-c613188a8b1f	62	7cd719cef55f49489917dd0fbdb29b93	2026-02-02 00:25:38	2026-02-02 12:25:38	f	Chrome/Windows	120.38.72.194
38	f2cc7740-33dc-47d9-a8f4-8bb3e4b14e4a	29	90339a5f765f4d9c9efd3ec081a4fb1e	2026-02-18 16:36:31	2026-02-25 16:36:31	f	Mobile App/iOS	94.46.202.4
39	22c33f2a-880f-4fce-9a61-f72ef7f527b2	34	10df0fa01a304561a734fed8cbfd2fe3	2026-01-31 06:44:14	2026-01-31 07:44:14	f	Chrome/Android	173.134.195.211
40	4246786e-fa25-40e0-a5df-c0c1696afbe1	82	f5390aead4b34561be45ac625fe83f33	2025-11-06 03:44:08	2025-11-06 04:44:08	t	Firefox/Linux	7.167.113.166
41	f1930a34-5816-4310-8672-83f8f87435b1	9	a211f78e6caa4bdb94e426a7458fe579	2026-02-24 22:42:32	2026-02-25 22:42:32	f	Mobile App/Android	105.59.71.12
42	6a55b562-71f9-43d7-97f4-41dc289c54cf	5	712c771e01c040c6897b7c09c558ddc0	2026-02-08 21:49:49	2026-02-09 21:49:49	t	Chrome/Windows	61.69.198.117
43	4302ae56-e2f3-47a6-9e7e-8b9874904504	48	dfafc7096d1a4fa0be1d78ec99f10592	2026-02-23 08:30:22	2026-02-24 08:30:22	t	Firefox/Linux	168.50.250.158
44	44521644-593f-44a2-bba3-cb8616382a9d	53	84a354b1616241f2988f811706b8f90a	2026-01-02 13:24:54	2026-01-02 14:24:54	f	Safari/iOS	114.227.120.219
45	3d793316-0b47-4025-ae31-04c0445b4a80	47	28af4369fbb54364a1d4a5128ec8400f	2025-12-22 16:47:28	2025-12-29 16:47:28	f	Mobile App/iOS	231.183.31.102
46	fc399f07-3b63-4111-b027-b8f06bcb9fc8	36	ff456cba1d9f47e19fdd6597da81c4bd	2025-12-23 13:40:38	2025-12-23 14:40:38	f	Chrome/Windows	170.108.10.13
47	21d813e0-09c6-4674-8632-abdd0bd09b8d	43	d6636f1fb6ac4caea0bd6ea803935232	2026-01-07 12:19:45	2026-01-07 18:19:45	t	Chrome/Windows	213.106.110.209
48	ad339223-c0f9-4677-ac99-037bbabba94d	30	11f2db26434d41b99bfa0ef47aa05048	2025-11-09 09:42:06	2025-11-09 15:42:06	t	Chrome/Android	220.74.66.139
49	7c7bd666-ffcf-4cd6-8eb6-b4410bc21106	33	efc9fb6e3aff4887979c4d8396f869cc	2025-11-17 18:08:42	2025-11-17 19:08:42	t	Safari/iOS	4.183.121.151
50	d2ede1d8-3c56-40bf-b44e-414d18c04599	42	2134e8ceea9b44b6984230eddcf0c31f	2025-11-06 09:30:16	2025-11-06 15:30:16	f	Chrome/Windows	33.215.58.191
51	488e7687-1446-4f17-a507-23cdef1720ec	9	dbf0bdf2280847edb981942bd9794831	2026-01-25 00:58:45	2026-01-26 00:58:45	f	Mobile App/iOS	152.55.231.129
52	0b1152c7-58c7-47e2-830d-c7ab4d781494	29	60e8e78d70954bdf887c974099fd7c41	2025-11-15 12:43:42	2025-11-15 13:43:42	f	Firefox/Linux	165.15.31.123
53	8bee717f-13eb-41bd-abe6-aacd3bb49fcb	52	1f77b5d3a1434cde98710526858e0b65	2026-02-24 16:18:50	2026-03-02 00:00:00	t	Firefox/Linux	183.227.37.231
54	8ef5f146-f25f-4ec0-a236-d9fc8a4b5e8d	11	2e2006d469974172a6d255cf9784938b	2025-10-17 01:49:32	2025-10-20 01:49:32	t	Chrome/Windows	33.140.166.98
55	0b493f85-3c7c-44d4-af9d-b085ba160ed0	77	f200f17bd50e4dbd83bc30480c96a6b5	2026-02-06 23:27:33	2026-02-07 11:27:33	f	Mobile App/iOS	155.220.50.204
56	22d43b63-59f8-4acf-9f5f-3c7792c033d4	90	0d4d2b6d013c4c95aa2987af453b65fb	2025-06-28 19:42:27	2025-07-05 19:42:27	t	Firefox/Linux	116.116.211.87
57	61e9b286-d962-4bec-ba8e-4407ba3c33f5	59	68757dedcece4698bab03ac4b8fa3310	2025-12-02 09:45:12	2025-12-03 09:45:12	t	Chrome/Android	110.160.130.96
58	51acef04-5839-4c8a-b303-4c4c94e22b8c	20	566dcedcb25a4f62a3396f191884f9a3	2025-12-26 23:59:01	2025-12-27 23:59:01	t	Chrome/Windows	213.43.47.111
59	0035b398-c6ed-4ca7-b360-baed7fde92b8	13	cac637a83e394af58d8c08634ec54b8b	2026-02-22 17:23:53	2026-02-22 23:23:53	t	Mobile App/iOS	245.168.62.106
60	e8e1316a-9338-4117-84ef-87d1ac02703f	46	749eaf1af6ce44fc985f7acd19023dbf	2026-01-19 04:00:46	2026-01-26 04:00:46	t	Chrome/Android	154.159.180.27
61	23241809-0f30-4b75-ae9b-b2373df4b988	74	e560fd267d4c4c4799e659f9c8f08d8f	2026-02-13 21:06:43	2026-02-14 03:06:43	t	Mobile App/Android	124.114.55.90
62	40971099-b163-47f5-996a-b08ee06b2186	72	b42c2812e3604784956c08cf85c5449e	2025-12-17 13:28:23	2025-12-17 14:28:23	f	Mobile App/iOS	58.219.13.156
63	e0d10ee0-0c9f-4061-b5b3-3ed060fcd504	85	3e14b77d592b4ab0a00a0d74fe08fda8	2026-01-31 19:32:05	2026-01-31 20:32:05	t	Chrome/Android	180.158.173.90
64	691b0920-a649-468e-8c52-5ce084907ddb	1	ca07f921ab104552a3e9bd244965c620	2025-08-14 13:22:47	2025-08-14 19:22:47	f	Chrome/Windows	37.15.46.192
65	33be100e-02cb-4f94-a36b-06c3ffe49549	68	1c22a290e36f450b9b9769c082bb6762	2026-02-21 15:01:47	2026-02-22 15:01:47	f	Firefox/Linux	88.80.189.80
66	b203e72e-309e-4e8c-9b2d-fb5a45878040	93	5a138ac8b34f4c26aca6046f28e7aea0	2026-02-19 16:16:15	2026-02-22 16:16:15	t	Chrome/Windows	40.80.25.173
67	e91e45de-7eb3-469b-a653-e1aa0096b79d	11	d09fdeac79594ca58d224b5660b294f9	2025-09-27 15:42:29	2025-09-28 15:42:29	f	Firefox/Linux	156.226.212.70
68	bec2fd27-76f2-45bc-b2fc-7e5baf27c31f	28	125fb5d81056451fbf72a43e25998dc9	2026-02-12 15:10:25	2026-02-15 15:10:25	t	Chrome/Android	111.56.145.174
69	5fb33a95-e670-43fa-afb9-20d2086e945e	87	e080f151b59d44cd90f917da5e0bea89	2025-11-23 11:43:54	2025-11-24 11:43:54	f	Chrome/Windows	57.202.28.2
70	d2db554e-3fcb-4d4b-835f-8e130a513244	27	6b7d0c5da5ff412a83aba9f8460610b0	2026-01-16 00:55:41	2026-01-16 06:55:41	t	Chrome/Android	75.167.61.2
71	1f3f088d-08e0-43f0-89c7-98c897c33781	64	1c9b0307806e4707a7ad01cb1a1b4282	2026-02-23 19:48:00	2026-02-24 19:48:00	t	Safari/iOS	98.117.181.19
72	35233653-f26e-49bc-b6a2-aca09e34ab0f	51	11b3277aa75d408f999e83bb9d7b46ab	2026-01-26 06:42:40	2026-01-26 07:42:40	f	Chrome/Windows	118.39.160.148
73	28d1870b-9ee6-465e-bb38-3cd9629fa949	55	4ac1a784e0fb4e3f93e166ba52dc96c9	2026-02-02 12:10:42	2026-02-03 12:10:42	f	Chrome/Android	30.207.10.248
74	ad94c365-2c6e-467b-ac12-d219179528c4	42	05d74b48cb244cc1ba6787e2c05259c7	2025-12-06 16:56:47	2025-12-09 16:56:47	f	Mobile App/Android	236.185.45.112
75	a4098f6e-c90d-4e1e-af69-ee7eada686f3	14	894ab2c461d842f8b7f844c7aec3d334	2025-08-02 20:27:29	2025-08-03 20:27:29	f	Mobile App/iOS	21.202.158.191
76	be59d980-d0a5-4b1a-80f7-59c5532650b4	44	45e7d2fbeee6495ab73f780893466dc3	2025-11-11 21:52:14	2025-11-12 09:52:14	t	Chrome/Windows	131.58.99.232
77	ba2cc6c4-f535-468f-b063-5f3fd2bebd81	100	0bc2c880c0cb439d8d3a3eaf2906f8bb	2025-10-14 08:04:51	2025-10-14 20:04:51	t	Safari/iOS	27.74.131.51
78	36ef64ef-c6c3-4c8b-a33a-15900e378ed6	23	3cb78441446d4fea8f6f8c7b07bcc358	2026-01-26 05:24:47	2026-01-26 11:24:47	t	Safari/iOS	244.252.237.194
79	5d67d687-27f2-41c3-bc3a-3aa26ae1dacb	73	aac4211554f44e098595d17eed320f80	2026-02-17 04:10:54	2026-02-18 04:10:54	f	Mobile App/Android	81.77.225.18
80	67e8be6b-ed76-4f62-b71f-e9f32ed900e7	61	73958ef1c2b84868a6295f96f9b30b34	2026-02-22 09:47:50	2026-03-01 09:47:50	f	Chrome/Android	152.28.180.130
81	379fbff6-5b2c-4e0e-bd3e-1d72c79aa272	10	58a85df67eb244dcbc62f9f751b0130b	2025-12-03 13:45:11	2025-12-04 13:45:11	f	Chrome/Windows	15.188.146.20
82	433a31dd-e4bf-4cd8-89d5-521c482a5ef9	83	44683011a64a453e84c9cca4749a61b6	2025-07-19 07:15:06	2025-07-22 07:15:06	f	Firefox/Linux	149.21.230.233
83	f166328c-9687-46a0-a599-53a7dc29ca26	74	c092425444ce4d0b80551940f5b9fec6	2026-02-20 21:22:45	2026-02-21 03:22:45	f	Mobile App/iOS	122.77.31.116
84	f7c1bbcc-5c2b-479e-8f0d-7a53d384a4f8	14	af6bf1af86b94e388a8deeae02782687	2025-09-10 17:39:22	2025-09-17 17:39:22	t	Mobile App/iOS	166.88.20.64
85	b54ddaa0-5a2d-4dab-847e-ef76372fddab	91	97b1058485d8488a9aa75a30047f9943	2026-02-09 14:41:02	2026-02-10 14:41:02	t	Chrome/Android	96.144.198.105
86	961328e4-0fae-41e1-9836-479a91340ff9	100	5047baf5b32b43399d68a34ca02287e9	2025-10-10 01:28:40	2025-10-17 01:28:40	t	Mobile App/Android	166.171.33.85
87	418215d1-5df8-44bc-b17d-db56a215186f	13	4e773487f60d405b81a4ca852c0aa6b8	2026-02-27 05:21:09	2026-03-02 00:00:00	f	Chrome/Android	65.76.170.21
88	a379a87a-7ce4-41d3-803b-7350f9c70c44	75	f6daf7e4ebc843d99a524c005e0f756f	2025-11-30 08:32:45	2025-11-30 14:32:45	f	Chrome/Android	248.200.66.153
89	7a6dfd51-976e-4416-8c0b-ebbab57d607d	91	0eb0de237b194adc86146b615b0dd124	2026-01-23 11:21:48	2026-01-23 23:21:48	f	Mobile App/Android	203.168.65.172
90	66d03ded-b580-4ba0-8116-23ba323b2011	90	3cda8162a619442688063710b335bdd1	2026-02-26 07:10:12	2026-03-02 00:00:00	t	Mobile App/Android	172.216.185.5
91	c2b50dde-23f5-44ce-8cfe-ead144c89917	47	7a47d8afa542447d8b663337c10ecd12	2026-01-12 00:59:18	2026-01-12 06:59:18	t	Chrome/Android	243.248.98.58
92	6db6994a-8e1c-4e62-9131-abb1b367f1db	18	c125d41d18344cdcbdd57fd7de96bd69	2025-09-23 09:19:23	2025-09-23 10:19:23	f	Chrome/Windows	130.19.172.225
93	41c1d0c0-5400-4161-842c-ef935d15a03c	99	9da89d4e7ad44e0786f467068f5648e1	2026-02-15 14:57:24	2026-02-15 20:57:24	f	Safari/iOS	42.92.84.185
94	e440ddef-3596-442f-af4f-6f4d5fc34604	57	f5700b25ca434f1c8a6e544223fe0ab1	2025-11-19 17:55:12	2025-11-20 17:55:12	f	Mobile App/Android	185.121.227.157
95	bda14da0-df73-421b-be18-204c4b3d8cab	37	d3bf76d5cbd34dadbcfbc809e4539cf3	2026-01-20 01:55:39	2026-01-27 01:55:39	f	Safari/iOS	137.122.158.248
96	f53c1b44-a32b-4cfd-bc36-7a110bc735f8	61	5188439b7fc64689bd05c6897f7d064a	2026-02-16 09:12:54	2026-02-16 21:12:54	f	Firefox/Linux	197.144.195.129
97	02e9c347-99a0-44b0-9b4b-8598f3c0c6ff	68	ae05de7b1eb04f0bbd49f90175fe54d1	2026-02-26 13:35:36	2026-02-26 19:35:36	t	Mobile App/iOS	36.128.26.165
98	007be792-f93e-40e6-9406-d8396c5b6466	62	f45d0ec425044ba9b5c447bf1cac71b7	2026-02-15 03:35:55	2026-02-15 15:35:55	t	Mobile App/Android	217.63.145.22
99	180114cd-fbf9-42e7-876f-325d1d8ca14d	98	6dd5c5f83c9c4eb6a1878c5722340062	2025-12-14 14:44:45	2025-12-15 02:44:45	f	Mobile App/iOS	38.223.46.243
100	00dcd461-5088-4b8d-b2f5-7c27564405ec	29	fe4dd72dfad34bd993faeba4f417205b	2026-02-01 19:44:35	2026-02-02 19:44:35	f	Chrome/Windows	107.27.202.129
101	2e5e4482-69bb-4b17-b2aa-d64a436d1ba1	48	c151b79c4c0848ac89f19e6421612071	2025-10-28 03:09:29	2025-10-29 03:09:29	t	Chrome/Android	58.14.163.239
102	c126b5dd-d676-40fd-a3ad-f27cd489e92d	13	9b7a4f5e73e74460ba8738f16d06c9bc	2026-03-01 10:56:42	2026-03-01 22:56:42	t	Safari/iOS	10.146.241.179
103	25c819d2-53d2-411d-a24d-6751f1e88cf0	18	09301f6dca834b9699b1093ce3366ed7	2026-01-23 09:33:09	2026-01-24 09:33:09	t	Chrome/Windows	5.131.110.214
104	1008275c-e432-4927-aa39-e2107b2b5030	20	5f0ec1e3e05d4f0c93336a72fc871c0d	2025-11-03 09:34:26	2025-11-10 09:34:26	f	Chrome/Windows	199.147.121.78
105	e84c3dae-69bb-426a-8305-faede02fc024	16	60bb96c08ba5410fb687a8013fdd6189	2025-12-23 05:57:09	2025-12-23 11:57:09	f	Mobile App/Android	204.234.32.29
106	22f09300-4d02-40b6-8dd8-cf98cc6da985	64	c3d9d3b4491d4266a01dc62c24f9e387	2026-02-16 12:43:00	2026-02-19 12:43:00	t	Mobile App/Android	132.123.73.75
107	f1767a9c-98dd-46ce-a3ee-6926eb297f97	55	887564adf7834916b061eaea6edced4a	2025-06-25 10:17:12	2025-06-28 10:17:12	f	Safari/iOS	147.213.95.171
108	c027b685-03ba-4ccd-940f-98d484aa3d01	86	90c14b6781874bafa8020c8900b422f1	2025-07-06 23:34:52	2025-07-09 23:34:52	f	Chrome/Windows	245.10.199.224
109	433707f2-c3a2-465a-aeb6-e8744f7e08f5	61	358fdc2527c24b3b9440deae850af94b	2026-02-12 17:33:11	2026-02-19 17:33:11	f	Chrome/Android	65.8.182.202
110	9465afb9-bee2-4e0c-af52-02bc3d327359	9	a6c78eca751c456798576d10d646b9a0	2025-12-30 12:24:29	2025-12-30 18:24:29	t	Mobile App/iOS	189.170.68.12
111	858e0001-5548-44cd-bb8e-a1ecf4a3ad2f	46	cbef8e4c3ceb49dab4cb78974612afeb	2026-02-12 01:35:34	2026-02-12 13:35:34	t	Mobile App/Android	119.245.93.208
112	1ec5fef4-038e-4c93-ad17-0fa7eb614337	18	6d64b1cc581846fa8973398e8050fd1b	2025-08-18 17:16:08	2025-08-25 17:16:08	f	Chrome/Windows	76.103.22.203
113	ffce0dc1-e328-49c7-b551-8d8b4afaaf85	26	6dafc4aa73204cb3a7a18d6b90de6b31	2025-05-31 05:20:26	2025-05-31 17:20:26	f	Mobile App/iOS	102.242.129.10
114	917ebb4a-8d12-42e1-9504-a5ca69779a29	97	4f83f74daf2c491599182924c17f6b37	2025-09-10 19:33:47	2025-09-11 07:33:47	f	Chrome/Windows	222.169.139.32
115	3b84c352-422f-46d4-b546-a154c70e3221	48	d01bd5f941c64ad6b6a95cd3390288ec	2026-01-14 06:13:45	2026-01-15 06:13:45	f	Firefox/Linux	87.95.254.178
116	7f39b618-f765-4039-8577-2160a78270fd	64	6e23e1f24c4047cca7bff655e9007d1b	2026-02-05 09:27:20	2026-02-08 09:27:20	f	Chrome/Windows	187.217.40.111
117	c9e2c1cb-01ca-43be-9ed3-ab057548ee17	78	323457353aab4d12ab22fd4581f473a8	2025-12-25 02:19:20	2025-12-28 02:19:20	f	Chrome/Android	27.40.167.170
118	070cc6bf-cf3f-4db7-8049-838cbbed36ec	38	e3399f5748984189aafcbf7be570432b	2026-02-28 08:55:34	2026-03-01 08:55:34	f	Safari/iOS	177.227.179.115
119	0d829461-f9df-47a3-bfc4-9b9d80e5c9ed	6	d982a4bc292843069ed0543d167645df	2026-02-20 12:35:31	2026-02-21 00:35:31	f	Chrome/Android	164.29.38.172
120	28442fa1-ede4-4f9a-ae9f-8b46af70cec8	82	f5d4eb0cb1ee4b84b609fc023190e492	2025-11-19 15:30:14	2025-11-20 03:30:14	t	Chrome/Windows	37.224.17.33
121	26bda801-9c2c-4607-bf1a-ef5394ac90c6	9	3dfb6d70084d4236ada792ff0861d5ba	2025-12-09 09:19:49	2025-12-16 09:19:49	f	Chrome/Android	99.16.78.174
122	475b8ed0-b53f-40e7-9776-0599ceea7ba1	58	3dc32d3ddf034388987b75c40fb111e8	2026-01-23 21:45:13	2026-01-24 09:45:13	f	Chrome/Windows	147.70.187.102
123	9fa8c994-7b0c-4ee9-8c4a-6c80418615cd	41	8d834da5cffa4373b55256061cc997fc	2026-01-27 08:00:33	2026-01-27 20:00:33	t	Chrome/Windows	7.95.255.133
124	ad63bea1-7413-460e-8954-0998b37c967a	50	34b7cf683dba410f98b5609c7ade7b5d	2025-09-18 22:53:04	2025-09-19 10:53:04	f	Mobile App/Android	115.109.146.178
125	4adb6c8c-ea1c-4dc4-bb6d-be39df608761	63	85f0f16b84864ea79f1caf3d1c79e393	2025-11-02 03:24:23	2025-11-02 04:24:23	t	Chrome/Windows	116.88.227.23
126	83d6e86b-5fbc-4da0-9d7a-3f5380be365f	88	544e042dbc08492abfab65bd215ea0df	2025-11-25 05:56:16	2025-12-02 05:56:16	f	Mobile App/Android	17.148.153.218
127	be3df3dc-157b-4470-917e-1e586b4da405	21	a30e38bc9c914883b8b4825198bdce3d	2026-02-16 17:48:42	2026-02-23 17:48:42	t	Chrome/Android	131.114.62.253
128	dcf829ea-023b-40ec-9483-026b6e1306cf	26	bda79462d9b74f6291e64d9465b190ce	2025-07-07 21:10:30	2025-07-08 03:10:30	f	Chrome/Windows	93.188.239.206
129	72747ef9-4f06-4ec7-b684-b944f4ad2c17	71	9f090fb0bb5540f1913f0ecbf36aebfc	2026-01-18 13:36:51	2026-01-21 13:36:51	t	Chrome/Windows	80.203.245.135
130	cfcfa699-fd9e-467b-b731-a95d9fef5c56	53	71cfbc8e67444f8c9f6bc36fec4da5be	2026-02-19 01:51:23	2026-02-20 01:51:23	t	Safari/iOS	249.162.37.116
131	5422d90e-4e17-414a-af22-4b131370b5ba	60	e59f167bbef74ae8b3509ae19b3a7122	2026-02-26 21:00:53	2026-02-27 09:00:53	t	Mobile App/iOS	164.93.66.111
132	aa6b9a7e-99f6-4093-9417-d9d418be187f	65	fa73919d4a95423999dea3d8f831ec34	2025-07-09 05:12:50	2025-07-09 06:12:50	t	Chrome/Android	43.82.165.240
133	ec3a9a4a-d220-4197-88f0-c5c363ddb673	91	fbe109ba82c2493ca0a9df875242fb39	2026-01-30 07:21:01	2026-01-30 19:21:01	f	Chrome/Windows	65.100.140.33
134	6c8446f0-ff57-4d75-950a-b6425f0cdecc	81	f8f26a2ce22144ccb7eb1904aa18c570	2025-12-12 23:15:38	2025-12-15 23:15:38	t	Mobile App/iOS	165.86.78.44
135	8bc22352-df2d-4379-ab8a-bfbb4c1c2965	85	a59e816a1e184c7abac7b9565655d298	2026-02-07 15:02:49	2026-02-10 15:02:49	t	Chrome/Windows	21.23.135.167
136	ce64e99b-6374-4b90-b368-2b6b1f746637	27	f67cc23430f94fb9ac1266f6727cf1b9	2026-02-07 09:38:50	2026-02-10 09:38:50	t	Firefox/Linux	228.148.154.124
137	738e6006-c5fc-4251-be26-2ba46c4e9a64	32	5e1d31679e484d6c8abd7156541bfd4a	2025-11-29 22:34:26	2025-11-30 10:34:26	f	Chrome/Windows	177.30.80.113
138	37e0cf04-3544-4b13-894e-8abfbd00788b	54	19e30b0eaf944aefaad3eb57d62326c6	2026-01-05 23:27:12	2026-01-06 23:27:12	t	Chrome/Android	156.73.160.221
139	604ecd49-dce5-492f-b9d3-bb9fb747a5ae	92	fa81463bdfa74a0ca0a57357a9b0f910	2025-07-21 16:28:53	2025-07-28 16:28:53	f	Firefox/Linux	34.189.54.82
140	28b97081-5318-4885-a7c9-1c677d7a4a97	31	bc96e2487de042a6a519d566fa465f2a	2026-02-27 15:42:32	2026-02-27 16:42:32	f	Firefox/Linux	64.72.49.13
141	b977542e-ebc8-40fd-8612-aa313d905dae	38	c838927445594a6c9fda8b49d3e9b6ab	2026-02-28 14:34:50	2026-03-02 00:00:00	f	Safari/iOS	247.81.167.240
142	60f93682-0dbe-4c21-bb50-61b7a2640a08	74	e778fac7a5c547c38580ff113e52b9b1	2026-02-24 06:06:32	2026-02-24 18:06:32	t	Safari/iOS	128.239.255.226
143	fff22de0-b869-49d3-8326-66ba915b6cf8	40	7620cdba2b794c21920ae8d4d95115ba	2025-12-22 20:49:40	2025-12-22 21:49:40	t	Firefox/Linux	130.234.123.56
144	88b9c0d6-27e4-4e99-9612-3ad2233241cb	75	eac9a802d5114fcaa31c6e8a296985e9	2025-08-01 16:27:12	2025-08-01 17:27:12	t	Chrome/Android	127.240.146.138
145	277648e2-2428-475d-92f1-55f6f0e27808	2	1ac22d0e1d9a4941b40bab6887a0fce5	2025-05-19 03:14:53	2025-05-20 03:14:53	t	Chrome/Android	187.187.206.94
146	15ed298e-c787-41df-931d-e57d88c2a640	6	da1bceaf053549259e4de87c7861c1f2	2025-12-19 04:14:13	2025-12-19 05:14:13	t	Chrome/Android	142.147.37.99
147	53ead1a8-d18f-4428-a041-f02a0dde703c	65	c2d1ef3403ba41ef91982d7d98ffe7a8	2025-12-09 14:20:09	2025-12-12 14:20:09	f	Mobile App/iOS	175.60.65.250
148	f9a55b4f-981f-4545-b1be-e4167f9a117d	13	1ed145b9dbfb41b89840e0d0f391f307	2026-02-23 05:46:51	2026-02-23 17:46:51	f	Mobile App/iOS	241.187.73.51
149	ccd9771f-527f-4130-96f1-3fb7e8f53d12	78	dfcdee7a3bf24d6b890695b9f2c0cbed	2026-02-26 22:01:01	2026-02-27 22:01:01	t	Chrome/Windows	10.70.170.206
150	29a3fbae-d6c1-4366-a3ad-e6b066561441	61	198b06fe349643089e5527ec90bfaffb	2026-02-24 06:43:32	2026-02-25 06:43:32	t	Mobile App/iOS	229.71.167.239
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.users (user_id, user_uuid, first_name, last_name, full_name, email, password_hash, phone, city, created_at, updated_at, is_email_verified, status) FROM stdin;
1	5b8a13b6-e7bc-4a53-b26d-a59b9333a6ad	Ajay	Patel	Ajay Patel	ajay.patel26@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918181241943	Jaipur	2025-06-05 02:33:27	2025-08-30 19:01:56	t	active
13	96faae5e-24b6-495c-b834-1a5adf9776b1	Girish	Joshi	Girish Joshi	girish.joshi765@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918840109255	Bangalore	2026-02-13 16:18:56	2026-02-27 20:14:53	t	active
14	a6957939-45d7-4a74-884e-580dff670f3e	Sunil	Menon	Sunil Menon	sunil.menon94@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917470939445	Lucknow	2025-04-30 08:35:03	2025-12-30 00:48:18	t	active
15	a671ff30-d941-4eaa-b052-54da57afdbfa	Krishna	Rao	Krishna Rao	krishna.rao391@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919010258946	Mumbai	2025-09-23 11:42:11	2025-11-11 07:22:39	f	inactive
16	d8374644-cbd2-4fb5-b4e7-d78e96f30051	Naresh	Bhatia	Naresh Bhatia	naresh.bhatia118@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919306270004	Chennai	2025-12-18 14:41:18	2026-01-13 12:26:09	f	active
17	bd44ea03-de11-4cad-aa21-e1374a7e22ed	Seema	Kumar	Seema Kumar	seema.kumar465@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918131247330	Chennai	2025-09-12 09:48:02	2026-02-07 08:48:06	t	inactive
18	cfa9abdf-f281-4c1d-87c5-a6c2ad10fd3f	Ajay	Iyer	Ajay Iyer	ajay.iyer624@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917656439677	Jaipur	2025-07-25 05:07:46	2025-09-25 22:52:32	t	active
19	8b33ecdf-acea-4eb7-b9c7-6e538c6151f5	Aarav	Subramanian	Aarav Subramanian	aarav.subramanian332@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917083651970	Chennai	2025-04-14 10:40:57	2025-09-02 09:54:30	f	active
20	4038c9e2-50ce-4ecc-b5d9-37295523ae48	Shreya	Verma	Shreya Verma	shreya.verma247@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917338258951	Jaipur	2025-04-04 06:20:52	2026-01-13 12:13:15	t	active
21	40670bdc-8102-481b-9ff0-c7f1f1974e48	Parvathi	Gupta	Parvathi Gupta	parvathi.gupta132@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919041322270	Pune	2025-10-01 12:32:27	2025-11-02 14:05:17	t	inactive
22	e0f9f6c8-9b3c-48ea-84de-d01daed488bb	Rajesh	Pandey	Rajesh Pandey	rajesh.pandey553@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919962958940	Kolkata	2025-05-19 02:51:49	2026-02-20 00:01:46	t	banned
23	c740b5de-1691-46f5-b8b9-4f38232e7f27	Usha	Tiwari	Usha Tiwari	usha.tiwari530@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917519709079	Jaipur	2025-06-06 06:38:52	2025-09-01 12:58:43	t	active
24	29e89774-c172-47be-b9e2-903afd8fccb2	Naveen	Krishnan	Naveen Krishnan	naveen.krishnan226@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917304912982	Mumbai	2025-12-01 21:33:20	2026-02-01 04:07:55	t	active
25	89c7ef73-9e9c-4255-9f43-4b3edc7121df	Harsh	Singh	Harsh Singh	harsh.singh527@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918196050747	Lucknow	2025-11-16 19:19:29	2026-02-19 01:31:12	t	active
26	17570902-67bb-42a9-976e-4e7dc0312b94	Vandana	Menon	Vandana Menon	vandana.menon249@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918748309234	Pune	2025-05-14 22:44:56	2025-06-20 13:55:44	t	active
27	2e78d390-363f-4b4f-a0e3-ef161b6d2cda	Asha	Nair	Asha Nair	asha.nair885@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917232663462	Delhi	2025-11-18 12:12:44	2025-12-07 14:52:21	t	active
28	9fab0e6c-91ea-47df-a257-55e994cd3af7	Anjali	Yadav	Anjali Yadav	anjali.yadav195@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918926780541	Delhi	2025-04-25 10:35:37	2025-10-06 06:48:55	t	active
29	5154d7a8-7e36-43ba-9608-5544dff4c5df	Usha	Ahuja	Usha Ahuja	usha.ahuja883@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917420514789	Delhi	2025-03-21 15:31:02	2025-11-29 21:56:53	f	active
30	8e8a555d-e155-4f42-a2b0-68c172a3436f	Sumathi	Sehgal	Sumathi Sehgal	sumathi.sehgal243@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918745535098	Mumbai	2025-09-06 14:30:12	2025-12-09 01:47:46	t	active
31	aed3c3a9-cea1-4586-853f-e3a06d65b606	Rohan	Rao	Rohan Rao	rohan.rao3@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918139038460	Jaipur	2026-02-24 19:46:27	2026-03-01 13:57:45	f	active
32	2a546274-24ea-496b-bf4f-8d11d2ecac1e	Murugan	Chopra	Murugan Chopra	murugan.chopra499@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917815605132	Jaipur	2025-06-25 05:31:02	2025-09-17 18:38:11	f	active
33	b081b165-135e-4f90-aa55-b7f546f38de3	Ayaan	Bhatia	Ayaan Bhatia	ayaan.bhatia322@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917215359682	Bangalore	2025-10-14 20:55:47	2026-01-15 10:55:30	t	inactive
34	cb8190d8-436c-4ac3-8d23-80952a11d08e	Ayaan	Iyer	Ayaan Iyer	ayaan.iyer83@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917294296873	Delhi	2025-10-19 02:07:45	2025-11-01 06:50:59	t	active
35	424540af-473f-4bb2-ad76-2a8bfe31eeb4	Sudha	Mehta	Sudha Mehta	sudha.mehta593@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917170689150	Jaipur	2025-10-28 13:03:14	2025-11-13 11:07:27	t	active
36	0649103b-a688-4145-9898-bc16d2d4deb6	Aryan	Pandey	Aryan Pandey	aryan.pandey268@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919876451163	Chennai	2025-12-05 03:23:29	2026-01-04 15:29:34	t	active
37	0121b08e-2fba-4718-aa6f-196e6aa21a39	Chitra	Reddy	Chitra Reddy	chitra.reddy952@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917040009587	Delhi	2025-08-26 23:31:50	2025-12-25 14:20:32	f	banned
38	1bd814ec-2f42-4504-a4b9-20bccef9baf7	Girish	Yadav	Girish Yadav	girish.yadav519@hotmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917568896616	Kolkata	2026-02-27 10:36:28	2026-02-28 12:01:18	f	inactive
39	f4109917-6878-4524-a013-12f281b44707	Rekha	Kumar	Rekha Kumar	rekha.kumar449@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918299301222	Jaipur	2025-10-25 13:14:59	2026-03-01 13:00:00	t	active
40	1deda6f6-77c3-4ebb-ade7-b816c7bb0d1d	Geeta	Pandey	Geeta Pandey	geeta.pandey680@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917576775951	Bangalore	2025-06-12 17:00:03	2025-07-27 12:52:26	f	active
41	f94ffcb0-7979-4d09-8136-3ac421c3ecbf	Sonal	Shah	Sonal Shah	sonal.shah620@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918472659626	Ahmedabad	2025-05-20 01:39:52	2026-02-11 01:36:07	t	active
42	adb8d638-3843-4d5a-b50c-cfe26a164f3b	Swati	Tiwari	Swati Tiwari	swati.tiwari930@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917396418889	Kolkata	2025-11-03 07:57:34	2026-01-24 13:57:56	f	active
43	307637f7-cad4-4059-9505-c45a52987c58	Parvathi	Gupta	Parvathi Gupta	parvathi.gupta653@hotmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917693989311	Mumbai	2025-12-14 20:46:22	2026-01-26 18:19:26	t	active
44	61e9db0c-1945-420c-afba-e85240140aa7	Pooja	Singh	Pooja Singh	pooja.singh968@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917640183291	Bangalore	2025-09-29 21:16:12	2025-10-06 21:10:23	f	active
45	38357901-c100-4b7f-a1f0-0263d48b2c2e	Seema	Gupta	Seema Gupta	seema.gupta43@hotmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918566166314	Hyderabad	2026-02-14 03:06:53	2026-02-15 02:21:18	f	active
46	4da15be3-ddda-44b5-8578-b701d6fefbdb	Senthil	Patel	Senthil Patel	senthil.patel363@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918745377599	Bangalore	2025-10-29 00:59:04	2025-11-28 01:15:18	f	active
47	efd557c5-02f2-4025-b5c9-c1cb8b1b5789	Amit	Tiwari	Amit Tiwari	amit.tiwari423@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917770348179	Hyderabad	2025-12-13 01:16:42	2026-01-14 07:19:35	f	active
48	2337c69e-f4e4-47e7-881c-f527a402f75c	Sonal	Kumar	Sonal Kumar	sonal.kumar807@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917464267175	Ahmedabad	2025-07-28 13:32:50	2025-08-12 14:29:12	f	active
49	abdcb5e3-1725-4d99-bae1-79ed43ca0725	Gaurav	Shah	Gaurav Shah	gaurav.shah841@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917957449367	Delhi	2025-03-11 04:34:06	2025-11-22 12:31:24	t	active
50	ffdab2e8-6c79-4524-a448-44accdb9cc20	Parvathi	Joshi	Parvathi Joshi	parvathi.joshi360@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919187880715	Chennai	2025-08-04 05:16:21	2026-02-28 11:09:55	t	active
51	41cbd71b-8270-487b-83d6-564b5246fdc1	Amit	Krishnan	Amit Krishnan	amit.krishnan986@hotmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917164313410	Kolkata	2025-04-13 02:23:05	2025-11-30 18:49:54	t	active
52	9ab36e65-8e8c-453d-bc46-23309e775d1d	Seema	Subramanian	Seema Subramanian	seema.subramanian524@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918654401763	Pune	2026-02-14 07:59:30	2026-02-28 07:52:42	t	active
53	8a3387e4-24f7-49c5-a341-d669c753c65e	Aarav	Iyer	Aarav Iyer	aarav.iyer948@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919950028965	Pune	2025-12-06 09:34:24	2026-02-16 10:26:32	t	active
54	e96e0883-16db-40b4-bfac-60d86e3a8e45	Krishna	Kapoor	Krishna Kapoor	krishna.kapoor943@hotmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919676432103	Chennai	2025-07-01 21:54:21	2025-08-19 07:29:52	t	active
55	76804100-486d-4fd9-8e16-64dcfa551a31	Senthil	Pillai	Senthil Pillai	senthil.pillai335@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919994487334	Pune	2025-06-24 19:42:22	2026-01-26 03:12:17	t	active
56	69ac182b-59a9-40a6-a286-952d2a3830ba	Kartik	Bhatia	Kartik Bhatia	kartik.bhatia925@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919643616431	Chennai	2025-10-09 00:26:43	2025-12-06 10:58:24	t	active
57	ef8a092c-a3ad-4401-a282-4212de38bb81	Rekha	Yadav	Rekha Yadav	rekha.yadav441@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919605591588	Hyderabad	2025-11-11 06:17:55	2026-01-12 20:05:19	t	active
58	b7f26bf3-60ab-442b-8981-848519bb6200	Sunil	Menon	Sunil Menon	sunil.menon813@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917728818981	Lucknow	2025-11-12 20:56:02	2025-11-29 08:06:35	t	active
59	599e8d3e-f03f-4aa6-bc51-d12d5f49abbf	Harsh	Singh	Harsh Singh	harsh.singh839@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919889635392	Mumbai	2025-06-30 13:19:08	2025-09-25 19:07:17	f	active
60	67325793-c953-4d15-a8da-2f74456d14a0	Anjali	Menon	Anjali Menon	anjali.menon626@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918955997540	Pune	2025-08-09 22:52:12	2025-10-24 11:08:15	t	active
61	ed9f217d-1e36-4ea1-a995-36b0406a94c6	Anjali	Gupta	Anjali Gupta	anjali.gupta672@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917023814791	Pune	2026-02-11 16:11:33	2026-03-01 21:39:39	f	inactive
62	0c8aec9c-6736-4246-912d-7ea7cfe8409f	Mahesh	Kumar	Mahesh Kumar	mahesh.kumar824@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919224611603	Delhi	2025-08-29 09:55:07	2025-09-08 03:57:11	t	inactive
63	7c21041d-34f7-49be-88c1-cf5285a9cba6	Chitra	Gupta	Chitra Gupta	chitra.gupta821@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919867224513	Ahmedabad	2025-09-24 06:30:28	2026-01-10 19:17:18	t	inactive
64	32f23c4b-d214-4851-b092-9d538467832b	Shobha	Khanna	Shobha Khanna	shobha.khanna737@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918832837596	Ahmedabad	2026-01-18 13:27:56	2026-02-14 03:46:57	t	active
65	4454b0cb-f049-4601-aa58-def99f354116	Veena	Joshi	Veena Joshi	veena.joshi770@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919738735023	Ahmedabad	2025-06-17 16:43:44	2026-01-06 03:35:43	t	active
66	fa0be298-d45f-43bd-9b58-7889f2cdbae2	Ishaan	Chopra	Ishaan Chopra	ishaan.chopra293@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918167007513	Bangalore	2025-07-10 10:19:33	2025-11-11 14:14:05	f	active
67	d517990f-7fc7-4b77-a66e-6168f7509e82	Naveen	Rao	Naveen Rao	naveen.rao711@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917918920620	Pune	2025-03-26 22:39:22	2025-09-04 01:30:18	t	active
68	475d8915-c8eb-4ac7-a57d-ba34abd6a3ae	Ayaan	Yadav	Ayaan Yadav	ayaan.yadav853@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918672790155	Pune	2026-02-16 09:42:21	2026-02-16 21:05:02	f	active
69	d2590bee-5a95-4734-8aec-c1b90cbc8cbd	Abhishek	Sharma	Abhishek Sharma	abhishek.sharma966@hotmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918282531582	Pune	2025-12-19 14:53:49	2026-01-26 11:37:54	f	inactive
70	aa39c418-fa7d-4031-9e6c-b86b2a315836	Girish	Bhatia	Girish Bhatia	girish.bhatia753@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919590950133	Ahmedabad	2026-02-13 16:12:29	2026-02-19 00:40:52	t	active
71	af13f682-7e92-4918-a1d5-5e246e8c6f84	Vihaan	Rao	Vihaan Rao	vihaan.rao345@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919916892179	Bangalore	2026-01-05 23:13:32	2026-02-14 05:21:06	t	active
72	3a352675-78f0-41d2-a96c-fc09887b00b4	Lata	Iyengar	Lata Iyengar	lata.iyengar28@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919542160120	Bangalore	2025-10-07 04:30:52	2026-02-12 22:19:02	t	active
73	8c53657b-e904-4225-aeb9-e124251f35dd	Savita	Kumar	Savita Kumar	savita.kumar52@hotmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918628238707	Pune	2025-07-07 03:08:52	2025-09-27 07:57:52	t	active
74	73e0f8ac-1ea1-485a-9006-225841919adc	Pallavi	Arora	Pallavi Arora	pallavi.arora975@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918083497965	Mumbai	2026-01-20 05:56:01	2026-01-24 05:21:40	t	active
75	465bd9d4-0db8-4129-b89c-4172acbd3687	Gaurav	Mehta	Gaurav Mehta	gaurav.mehta666@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919799264931	Mumbai	2025-03-17 15:13:58	2026-01-04 13:11:44	t	active
76	cd73f407-f760-43ab-831d-f784eb2ee54e	Lata	Gupta	Lata Gupta	lata.gupta245@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919033929266	Chennai	2025-11-16 23:48:31	2025-12-09 04:54:07	t	active
77	3cdd9dd7-5894-458e-a22b-3030093a494e	Parvathi	Naidu	Parvathi Naidu	parvathi.naidu172@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919608108101	Chennai	2025-12-17 11:10:20	2026-02-25 05:03:57	t	active
78	6c006d62-9b46-4d1c-886a-0f4b84978351	Sneha	Krishnan	Sneha Krishnan	sneha.krishnan27@hotmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919473028098	Delhi	2025-11-20 01:20:03	2026-01-31 22:23:28	t	active
79	0a037a1c-eb8f-4b4a-b55a-b29bfb1becb1	Pushpa	Chopra	Pushpa Chopra	pushpa.chopra851@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918043030161	Lucknow	2025-04-10 13:47:20	2026-01-06 08:05:55	f	inactive
80	c84f9eac-e055-40bc-a650-5fbc97103006	Kavya	Ahuja	Kavya Ahuja	kavya.ahuja580@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918491228808	Kolkata	2025-09-24 21:32:44	2025-12-17 01:55:54	t	active
81	75f65374-a929-40d7-b2c1-13a267a79143	Vivaan	Sehgal	Vivaan Sehgal	vivaan.sehgal431@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917453285987	Bangalore	2025-08-17 08:43:51	2026-01-05 00:34:04	t	active
82	99c7bcc8-2645-400e-8bdc-5fa4392758ac	Seema	Kumar	Seema Kumar	seema.kumar752@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919793693337	Ahmedabad	2025-06-14 21:21:01	2026-02-09 02:04:10	f	active
83	64f9ddbb-a185-4b1e-bd4a-309f7b591f68	Savita	Pillai	Savita Pillai	savita.pillai846@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919544659112	Delhi	2025-06-14 05:37:39	2025-10-17 09:43:26	f	active
84	e6a36b44-01b1-4f42-9234-395b9baae7d8	Pallavi	Tiwari	Pallavi Tiwari	pallavi.tiwari462@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918995907669	Ahmedabad	2025-10-09 07:23:01	2026-02-04 19:44:07	t	active
85	b30af98b-8120-42c3-b01c-a1e318b172eb	Nikhil	Kumar	Nikhil Kumar	nikhil.kumar500@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918523961606	Chennai	2026-01-05 20:20:11	2026-01-30 22:20:28	t	inactive
86	427839a7-7cd7-4c67-b660-a010ac39d6c6	Archana	Sharma	Archana Sharma	archana.sharma530@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917367704871	Ahmedabad	2025-06-03 17:36:05	2025-11-08 13:47:09	t	active
2	51c26d6c-49e3-4e92-8125-bf8b8af950b0	Ananya	Krishnan	Ananya Krishnan	ananya.krishnan433@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917127978094	Jaipur	2025-04-07 09:18:10	2025-07-01 07:09:23	t	active
3	cf6ecc27-7e06-47fa-86f7-466147b127d5	Kiran	Chopra	Kiran Chopra	kiran.chopra666@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919340505846	Mumbai	2025-08-11 22:12:29	2025-11-05 12:51:48	t	active
4	af064056-094d-466a-a5bc-5414fd2c679c	Indira	Ahuja	Indira Ahuja	indira.ahuja164@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918815115025	Kolkata	2025-07-12 03:21:52	2025-10-28 01:18:47	t	inactive
5	14a4a8ef-b37c-407d-ad9c-035602ecfba6	Sneha	Singh	Sneha Singh	sneha.singh390@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918541804686	Ahmedabad	2026-01-25 03:13:12	2026-02-10 19:57:26	t	active
6	830b6ca0-a100-4668-a24a-26e827f9fe68	Girish	Patel	Girish Patel	girish.patel997@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917338444264	Kolkata	2025-10-02 09:23:29	2025-11-28 07:42:04	f	active
7	94b5e9e1-6fdc-41d2-96b3-2dff9e3f99c3	Vandana	Yadav	Vandana Yadav	vandana.yadav722@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917196814233	Hyderabad	2025-11-13 19:25:15	2025-12-28 01:30:13	f	banned
8	e724a55b-e9af-45d1-ac62-89eb62af0fa4	Divya	Rao	Divya Rao	divya.rao285@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919730243887	Chennai	2026-01-19 22:28:21	2026-02-06 15:31:58	t	active
9	6afa5027-f9b4-4590-91b5-a35404ef18a8	Tarun	Pandey	Tarun Pandey	tarun.pandey700@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917306671447	Bangalore	2025-10-24 13:30:44	2026-02-24 20:43:31	t	active
10	11216ddc-5141-4cfc-a400-d08a42dbf498	Savita	Rao	Savita Rao	savita.rao277@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919955633092	Mumbai	2025-10-04 07:08:52	2025-11-15 22:37:43	t	active
11	a6d7a921-6dad-4198-8e31-48192351ca33	Naveen	Khanna	Naveen Khanna	naveen.khanna33@hotmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918722989659	Kolkata	2025-06-13 23:31:33	2025-07-09 16:26:54	t	inactive
12	29eb0f69-a4d4-4d87-a876-8e5b5b2eecc3	Rajesh	Malhotra	Rajesh Malhotra	rajesh.malhotra512@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919761027762	Jaipur	2025-08-27 04:48:33	2025-09-23 22:38:20	t	active
87	a49cbfb2-5618-4eef-9a02-64894190ea2f	Vijayakumar	Chopra	Vijayakumar Chopra	vijayakumar.chopra503@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917074059253	Chennai	2025-04-07 03:19:12	2025-07-30 09:47:39	t	active
88	ff136eda-8e72-4bea-8257-51bc21d54b5c	Murugan	Krishnan	Murugan Krishnan	murugan.krishnan378@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919377148230	Kolkata	2025-09-24 04:33:03	2025-11-29 22:34:35	t	active
89	7b9c1a68-fe33-4ff1-b371-b8394553311c	Tushar	Chopra	Tushar Chopra	tushar.chopra465@hotmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918316935719	Delhi	2025-06-07 15:15:07	2025-09-05 04:01:20	t	active
90	907715d7-940b-4e78-8912-7d162bf74f4c	Mythili	Iyengar	Mythili Iyengar	mythili.iyengar974@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917795212538	Lucknow	2025-05-15 09:17:28	2025-08-07 10:08:31	t	active
91	40c0b8ab-9c30-46bc-8d99-ea07316b4839	Indira	Iyer	Indira Iyer	indira.iyer612@hotmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917431756350	Chennai	2026-01-19 08:39:31	2026-01-28 18:49:19	t	active
92	73db4e9f-79c4-4e00-bf45-9d3382c759c6	Vivaan	Chopra	Vivaan Chopra	vivaan.chopra547@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918178158203	Bangalore	2025-03-19 16:14:13	2025-04-09 20:27:22	t	active
93	df59d0c0-f690-42bf-a6bb-59d703558410	Ajay	Sehgal	Ajay Sehgal	ajay.sehgal771@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917440610570	Ahmedabad	2026-02-03 22:20:15	2026-02-04 12:37:39	t	active
94	afb6040d-5c69-4920-9f08-dac414eaa98f	Varun	Kumar	Varun Kumar	varun.kumar989@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918084386400	Ahmedabad	2026-01-30 15:50:24	2026-02-22 20:26:05	t	active
95	a459b751-9fec-4d89-adb7-85f5002e178e	Ishaan	Krishnan	Ishaan Krishnan	ishaan.krishnan645@ymail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	917230249217	Delhi	2025-04-29 22:11:53	2025-06-26 20:49:13	f	inactive
96	3106f841-4d98-4116-a0d4-d64b1f6411fc	Anjali	Patel	Anjali Patel	anjali.patel572@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919604114475	Ahmedabad	2025-10-19 12:18:17	2026-02-16 14:20:35	t	active
97	6414e53e-2012-4696-a3b6-c5b40f3861b9	Usha	Shah	Usha Shah	usha.shah881@rediffmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918841810119	Delhi	2025-06-28 14:21:00	2026-02-04 10:21:38	t	active
98	36d8801e-20e3-40ff-9950-d46dd8baa4bb	Indira	Yadav	Indira Yadav	indira.yadav641@yahoo.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	918136646449	Delhi	2025-11-13 11:38:11	2025-11-29 05:59:50	t	active
99	ec6ad519-3f87-465f-95d4-5140681cc89d	Rahul	Sharma	Rahul Sharma	rahul.sharma419@outlook.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919960826470	Chennai	2025-10-18 14:43:17	2026-01-17 20:40:20	t	active
100	6aabc94d-00c5-4dfb-83da-cd7b2e9cfeed	Tarun	Sehgal	Tarun Sehgal	tarun.sehgal465@gmail.com	$2b$12$paWoeDvcPia1/73uqQakA.9DRRdbBe.yL2DJ5YT7CbfDrAbB3nb2C	919952295757	Hyderabad	2025-05-31 15:40:03	2025-09-11 09:29:43	f	active
\.


--
-- Data for Name: variant_attributes; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.variant_attributes (id, variant_id, attribute_id, value_id) FROM stdin;
1	1	5	30
2	1	1	7
3	2	4	28
4	3	1	1
5	4	1	4
6	5	2	11
7	5	1	5
8	6	2	19
9	6	5	35
10	7	1	2
11	8	1	5
12	8	2	15
13	9	5	33
14	9	1	5
15	10	5	32
16	10	6	36
17	11	2	14
18	11	1	4
19	12	6	38
20	13	6	36
21	13	4	29
22	14	5	35
23	14	2	17
24	15	1	6
25	15	6	36
26	16	4	25
27	17	5	32
28	18	3	24
29	18	2	14
30	19	6	38
31	20	1	7
32	20	3	21
33	21	1	3
34	22	4	28
35	23	5	33
36	23	6	37
37	24	3	21
38	24	1	6
39	25	1	5
40	26	1	6
41	27	3	21
42	27	5	34
43	28	5	35
44	29	3	21
45	29	4	26
46	30	3	20
47	31	2	15
48	31	6	38
49	32	3	22
50	33	6	36
51	33	4	27
52	34	4	26
53	35	6	37
54	35	1	5
55	36	5	30
56	37	4	25
57	38	5	35
58	38	2	14
59	39	1	1
60	40	6	38
61	41	4	26
62	42	4	26
63	42	1	1
64	43	2	19
65	44	2	17
66	44	6	37
67	45	5	35
68	45	1	1
69	46	1	4
70	46	6	38
71	47	3	21
72	47	4	27
73	48	6	38
74	48	2	9
75	49	5	34
76	49	3	21
77	50	6	36
78	50	3	24
79	51	4	28
80	51	1	7
81	52	5	33
82	52	3	20
83	53	1	5
84	54	2	19
85	55	2	17
86	56	3	22
87	57	4	28
88	57	3	21
89	58	3	20
90	58	2	11
91	59	4	28
92	59	3	22
93	60	3	24
94	61	6	38
95	62	5	33
96	63	4	26
97	64	6	37
98	65	4	27
99	65	5	32
100	66	6	36
101	67	2	19
102	68	4	26
103	69	6	37
104	70	3	20
105	71	1	1
106	72	6	37
107	73	2	16
108	73	3	22
109	74	2	19
110	75	5	32
111	75	4	27
112	76	5	31
113	77	5	35
114	77	3	21
115	78	4	26
116	78	6	37
117	79	5	32
118	79	6	38
119	80	5	30
120	80	4	28
121	81	6	37
122	82	1	6
123	83	1	7
124	83	4	27
125	84	6	36
126	85	1	7
127	86	1	3
128	87	2	12
129	88	1	1
130	88	3	20
131	89	1	4
132	90	5	31
133	91	5	30
134	92	4	27
135	93	3	22
136	93	6	37
137	94	3	20
138	95	1	1
139	95	2	12
140	96	3	22
141	96	6	36
142	97	3	23
143	97	6	38
144	98	1	1
145	98	4	27
146	99	3	20
147	100	4	27
\.


--
-- Name: addresses_address_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.addresses_address_id_seq', 1, false);


--
-- Name: attribute_values_value_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.attribute_values_value_id_seq', 1, false);


--
-- Name: attributes_attribute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.attributes_attribute_id_seq', 1, false);


--
-- Name: brands_brand_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.brands_brand_id_seq', 1, false);


--
-- Name: categories_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.categories_category_id_seq', 1, false);


--
-- Name: inventory_log_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.inventory_log_log_id_seq', 1, false);


--
-- Name: order_items_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.order_items_item_id_seq', 1, false);


--
-- Name: order_status_history_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.order_status_history_history_id_seq', 1, false);


--
-- Name: orders_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.orders_order_id_seq', 1, false);


--
-- Name: payments_payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.payments_payment_id_seq', 1, false);


--
-- Name: product_images_image_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.product_images_image_id_seq', 1, false);


--
-- Name: product_variants_variant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.product_variants_variant_id_seq', 1, false);


--
-- Name: products_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.products_product_id_seq', 1, false);


--
-- Name: refunds_refund_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.refunds_refund_id_seq', 1, false);


--
-- Name: review_images_image_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.review_images_image_id_seq', 1, false);


--
-- Name: review_votes_vote_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.review_votes_vote_id_seq', 1, false);


--
-- Name: reviews_review_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.reviews_review_id_seq', 1, false);


--
-- Name: shipment_tracking_tracking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.shipment_tracking_tracking_id_seq', 1, false);


--
-- Name: shipments_shipment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.shipments_shipment_id_seq', 1, false);


--
-- Name: user_role_mapping_mapping_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.user_role_mapping_mapping_id_seq', 1, false);


--
-- Name: user_roles_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.user_roles_role_id_seq', 1, false);


--
-- Name: user_sessions_session_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.user_sessions_session_id_seq', 1, false);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.users_user_id_seq', 1, false);


--
-- Name: variant_attributes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.variant_attributes_id_seq', 1, false);


--
-- Name: addresses addresses_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (address_id);


--
-- Name: attribute_values attribute_values_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.attribute_values
    ADD CONSTRAINT attribute_values_pkey PRIMARY KEY (value_id);


--
-- Name: attributes attributes_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.attributes
    ADD CONSTRAINT attributes_pkey PRIMARY KEY (attribute_id);


--
-- Name: brands brands_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.brands
    ADD CONSTRAINT brands_pkey PRIMARY KEY (brand_id);


--
-- Name: brands brands_slug_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.brands
    ADD CONSTRAINT brands_slug_key UNIQUE (slug);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- Name: categories categories_slug_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_slug_key UNIQUE (slug);


--
-- Name: inventory_log inventory_log_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.inventory_log
    ADD CONSTRAINT inventory_log_pkey PRIMARY KEY (log_id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (item_id);


--
-- Name: order_status_history order_status_history_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.order_status_history
    ADD CONSTRAINT order_status_history_pkey PRIMARY KEY (history_id);


--
-- Name: orders orders_order_uuid_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_order_uuid_key UNIQUE (order_uuid);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (payment_id);


--
-- Name: product_images product_images_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_pkey PRIMARY KEY (image_id);


--
-- Name: product_variants product_variants_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.product_variants
    ADD CONSTRAINT product_variants_pkey PRIMARY KEY (variant_id);


--
-- Name: product_variants product_variants_sku_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.product_variants
    ADD CONSTRAINT product_variants_sku_key UNIQUE (sku);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: products products_product_uuid_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_product_uuid_key UNIQUE (product_uuid);


--
-- Name: products products_slug_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_slug_key UNIQUE (slug);


--
-- Name: refunds refunds_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.refunds
    ADD CONSTRAINT refunds_pkey PRIMARY KEY (refund_id);


--
-- Name: review_images review_images_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.review_images
    ADD CONSTRAINT review_images_pkey PRIMARY KEY (image_id);


--
-- Name: review_votes review_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.review_votes
    ADD CONSTRAINT review_votes_pkey PRIMARY KEY (vote_id);


--
-- Name: review_votes review_votes_review_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.review_votes
    ADD CONSTRAINT review_votes_review_id_user_id_key UNIQUE (review_id, user_id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (review_id);


--
-- Name: shipment_tracking shipment_tracking_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.shipment_tracking
    ADD CONSTRAINT shipment_tracking_pkey PRIMARY KEY (tracking_id);


--
-- Name: shipments shipments_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_pkey PRIMARY KEY (shipment_id);


--
-- Name: user_role_mapping user_role_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT user_role_mapping_pkey PRIMARY KEY (mapping_id);


--
-- Name: user_role_mapping user_role_mapping_user_id_role_id_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT user_role_mapping_user_id_role_id_key UNIQUE (user_id, role_id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (role_id);


--
-- Name: user_roles user_roles_role_name_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_name_key UNIQUE (role_name);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (session_id);


--
-- Name: user_sessions user_sessions_session_uuid_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_session_uuid_key UNIQUE (session_uuid);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_user_uuid_key; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_user_uuid_key UNIQUE (user_uuid);


--
-- Name: variant_attributes variant_attributes_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.variant_attributes
    ADD CONSTRAINT variant_attributes_pkey PRIMARY KEY (id);


--
-- Name: addresses addresses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.addresses
    ADD CONSTRAINT addresses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: attribute_values attribute_values_attribute_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.attribute_values
    ADD CONSTRAINT attribute_values_attribute_id_fkey FOREIGN KEY (attribute_id) REFERENCES public.attributes(attribute_id) ON DELETE CASCADE;


--
-- Name: categories categories_parent_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_parent_category_id_fkey FOREIGN KEY (parent_category_id) REFERENCES public.categories(category_id) ON DELETE SET NULL;


--
-- Name: inventory_log inventory_log_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.inventory_log
    ADD CONSTRAINT inventory_log_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES public.product_variants(variant_id) ON DELETE CASCADE;


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE CASCADE;


--
-- Name: order_items order_items_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES public.product_variants(variant_id) ON DELETE RESTRICT;


--
-- Name: order_status_history order_status_history_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.order_status_history
    ADD CONSTRAINT order_status_history_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE CASCADE;


--
-- Name: orders orders_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.addresses(address_id) ON DELETE SET NULL;


--
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE RESTRICT;


--
-- Name: payments payments_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE RESTRICT;


--
-- Name: product_images product_images_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON DELETE CASCADE;


--
-- Name: product_images product_images_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES public.product_variants(variant_id) ON DELETE SET NULL;


--
-- Name: product_variants product_variants_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.product_variants
    ADD CONSTRAINT product_variants_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON DELETE CASCADE;


--
-- Name: products products_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES public.brands(brand_id) ON DELETE SET NULL;


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE SET NULL;


--
-- Name: refunds refunds_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.refunds
    ADD CONSTRAINT refunds_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE RESTRICT;


--
-- Name: refunds refunds_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.refunds
    ADD CONSTRAINT refunds_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES public.payments(payment_id) ON DELETE RESTRICT;


--
-- Name: review_images review_images_review_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.review_images
    ADD CONSTRAINT review_images_review_id_fkey FOREIGN KEY (review_id) REFERENCES public.reviews(review_id) ON DELETE CASCADE;


--
-- Name: review_votes review_votes_review_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.review_votes
    ADD CONSTRAINT review_votes_review_id_fkey FOREIGN KEY (review_id) REFERENCES public.reviews(review_id) ON DELETE CASCADE;


--
-- Name: review_votes review_votes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.review_votes
    ADD CONSTRAINT review_votes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: reviews reviews_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE SET NULL;


--
-- Name: reviews reviews_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON DELETE CASCADE;


--
-- Name: reviews reviews_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: shipment_tracking shipment_tracking_shipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.shipment_tracking
    ADD CONSTRAINT shipment_tracking_shipment_id_fkey FOREIGN KEY (shipment_id) REFERENCES public.shipments(shipment_id) ON DELETE CASCADE;


--
-- Name: shipments shipments_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE RESTRICT;


--
-- Name: user_role_mapping user_role_mapping_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT user_role_mapping_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.user_roles(role_id) ON DELETE CASCADE;


--
-- Name: user_role_mapping user_role_mapping_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT user_role_mapping_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: variant_attributes variant_attributes_attribute_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.variant_attributes
    ADD CONSTRAINT variant_attributes_attribute_id_fkey FOREIGN KEY (attribute_id) REFERENCES public.attributes(attribute_id) ON DELETE CASCADE;


--
-- Name: variant_attributes variant_attributes_value_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.variant_attributes
    ADD CONSTRAINT variant_attributes_value_id_fkey FOREIGN KEY (value_id) REFERENCES public.attribute_values(value_id) ON DELETE CASCADE;


--
-- Name: variant_attributes variant_attributes_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.variant_attributes
    ADD CONSTRAINT variant_attributes_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES public.product_variants(variant_id) ON DELETE CASCADE;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO analyst_bot;


--
-- PostgreSQL database dump complete
--

\unrestrict 6BjLOgcBYzomTP7jigNI8p67Q8JLli31SvuFjSNd88bO8MHfANo9ku1YVkLOaTV

