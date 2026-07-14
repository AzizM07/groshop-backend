--
-- PostgreSQL database dump
--

\restrict 2uth1l2s65Dw7no5kuQrZlAJ5cbqDug9CShjfSwQFtyVruxTwOx8xe9N8RzcOxq

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.wishlists DROP CONSTRAINT IF EXISTS wishlists_user_id_6280b16e_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.wishlists DROP CONSTRAINT IF EXISTS wishlists_supplier_id_e4aaf659_fk_supplier_profiles_id;
ALTER TABLE IF EXISTS ONLY public.wishlists DROP CONSTRAINT IF EXISTS wishlists_product_id_6f2a0dee_fk_products_id;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_user_id_92473840_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissio_permission_id_6d08dcd2_fk_auth_perm;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_user_id_f500bee5_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_group_id_2f3517aa_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.user_spins DROP CONSTRAINT IF EXISTS user_spins_user_id_a7d8ee45_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.user_spins DROP CONSTRAINT IF EXISTS user_spins_prize_id_40b20cae_fk_spin_prizes_id;
ALTER TABLE IF EXISTS ONLY public.user_spins DROP CONSTRAINT IF EXISTS user_spins_coupon_id_2fb21a5e_fk_coupons_id;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_outstandingtoken DROP CONSTRAINT IF EXISTS token_blacklist_outstandingtoken_user_id_83bc629a_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_blacklistedtoken DROP CONSTRAINT IF EXISTS token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk;
ALTER TABLE IF EXISTS ONLY public.supplier_subscriptions DROP CONSTRAINT IF EXISTS supplier_subscriptions_changed_by_id_d22b0a7c_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.supplier_subscriptions DROP CONSTRAINT IF EXISTS supplier_subscriptio_supplier_id_84f377c6_fk_supplier_;
ALTER TABLE IF EXISTS ONLY public.supplier_subscriptions DROP CONSTRAINT IF EXISTS supplier_subscriptio_plan_id_a6b37853_fk_subscript;
ALTER TABLE IF EXISTS ONLY public.supplier_store DROP CONSTRAINT IF EXISTS supplier_store_supplier_id_d7bbffc3_fk_supplier_profiles_id;
ALTER TABLE IF EXISTS ONLY public.supplier_profiles DROP CONSTRAINT IF EXISTS supplier_profiles_user_id_c7ab43fb_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.supplier_documents DROP CONSTRAINT IF EXISTS supplier_documents_supplier_id_b4c40cf4_fk_supplier_profiles_id;
ALTER TABLE IF EXISTS ONLY public.sub_orders DROP CONSTRAINT IF EXISTS sub_orders_supplier_id_da7f0756_fk_supplier_profiles_id;
ALTER TABLE IF EXISTS ONLY public.sub_orders DROP CONSTRAINT IF EXISTS sub_orders_order_id_24b9bae3_fk_orders_id;
ALTER TABLE IF EXISTS ONLY public.search_history DROP CONSTRAINT IF EXISTS search_history_user_id_b2c466f7_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS reviews_variant_id_6f6b041c_fk_product_variants_id;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS reviews_supplier_id_38f37b3e_fk_supplier_profiles_id;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS reviews_reviewer_id_dbb954a8_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS reviews_product_id_d4b78cfe_fk_products_id;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS reviews_order_id_35d02b74_fk_orders_id;
ALTER TABLE IF EXISTS ONLY public.review_photos DROP CONSTRAINT IF EXISTS review_photos_review_id_e79d7d0f_fk_reviews_id;
ALTER TABLE IF EXISTS ONLY public.quotes DROP CONSTRAINT IF EXISTS quotes_supplier_id_4f28ef00_fk_supplier_profiles_id;
ALTER TABLE IF EXISTS ONLY public.quotes DROP CONSTRAINT IF EXISTS quotes_product_id_1acb7bad_fk_products_id;
ALTER TABLE IF EXISTS ONLY public.quotes DROP CONSTRAINT IF EXISTS quotes_buyer_id_22f5da77_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_supplier_id_ae23c972_fk_supplier_profiles_id;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_category_id_a7a3a156_fk_categories_id;
ALTER TABLE IF EXISTS ONLY public.product_variants DROP CONSTRAINT IF EXISTS product_variants_product_id_019d9f04_fk_products_id;
ALTER TABLE IF EXISTS ONLY public.product_price_tiers DROP CONSTRAINT IF EXISTS product_price_tiers_product_id_0b11ff1b_fk_products_id;
ALTER TABLE IF EXISTS ONLY public.product_interactions DROP CONSTRAINT IF EXISTS product_interactions_user_id_7d8a05fd_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.product_interactions DROP CONSTRAINT IF EXISTS product_interactions_product_id_3b05e327_fk_products_id;
ALTER TABLE IF EXISTS ONLY public.product_images DROP CONSTRAINT IF EXISTS product_images_product_id_28ebf5f0_fk_products_id;
ALTER TABLE IF EXISTS ONLY public.orders DROP CONSTRAINT IF EXISTS orders_buyer_id_3d1f9476_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.order_items DROP CONSTRAINT IF EXISTS order_items_sub_order_id_402616ff_fk_sub_orders_id;
ALTER TABLE IF EXISTS ONLY public.order_items DROP CONSTRAINT IF EXISTS order_items_product_id_dd557d5a_fk_products_id;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_user_id_468e288d_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_sender_id_dc5a0bbd_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_conversation_id_5ef638db_fk_conversations_id;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_content_type_id_c4bce8eb_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.coupons DROP CONSTRAINT IF EXISTS coupons_user_id_bee5d0f0_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.conversations DROP CONSTRAINT IF EXISTS conversations_supplier_id_b1a02e5b_fk_supplier_profiles_id;
ALTER TABLE IF EXISTS ONLY public.conversations DROP CONSTRAINT IF EXISTS conversations_product_id_c2c693e3_fk_products_id;
ALTER TABLE IF EXISTS ONLY public.conversations DROP CONSTRAINT IF EXISTS conversations_buyer_id_d99807d5_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.commissions DROP CONSTRAINT IF EXISTS commissions_supplier_id_63abfe1e_fk_supplier_profiles_id;
ALTER TABLE IF EXISTS ONLY public.commissions DROP CONSTRAINT IF EXISTS commissions_sub_order_id_e9e09e8b_fk_sub_orders_id;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_parent_id_fc02df82_fk_categories_id;
ALTER TABLE IF EXISTS ONLY public.cart_items DROP CONSTRAINT IF EXISTS cart_items_variant_id_6e25bb33_fk_product_variants_id;
ALTER TABLE IF EXISTS ONLY public.cart_items DROP CONSTRAINT IF EXISTS cart_items_product_id_9398bb89_fk_products_id;
ALTER TABLE IF EXISTS ONLY public.cart_items DROP CONSTRAINT IF EXISTS cart_items_buyer_id_fd91efa0_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.buyer_profiles DROP CONSTRAINT IF EXISTS buyer_profiles_user_id_405ef80f_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.banners DROP CONSTRAINT IF EXISTS banners_supplier_id_56a381c8_fk_supplier_profiles_id;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_2f476e4b_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
DROP INDEX IF EXISTS public.wishlists_user_id_6280b16e;
DROP INDEX IF EXISTS public.wishlists_supplier_id_e4aaf659;
DROP INDEX IF EXISTS public.wishlists_product_id_6f2a0dee;
DROP INDEX IF EXISTS public.users_user_permissions_user_id_92473840;
DROP INDEX IF EXISTS public.users_user_permissions_permission_id_6d08dcd2;
DROP INDEX IF EXISTS public.users_groups_user_id_f500bee5;
DROP INDEX IF EXISTS public.users_groups_group_id_2f3517aa;
DROP INDEX IF EXISTS public.users_email_0ea73cca_like;
DROP INDEX IF EXISTS public.user_spins_video_ref_9a4a7a6d_like;
DROP INDEX IF EXISTS public.user_spins_user_id_a7d8ee45;
DROP INDEX IF EXISTS public.user_spins_prize_id_40b20cae;
DROP INDEX IF EXISTS public.user_spins_coupon_id_2fb21a5e;
DROP INDEX IF EXISTS public.token_blacklist_outstandingtoken_user_id_83bc629a;
DROP INDEX IF EXISTS public.token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_like;
DROP INDEX IF EXISTS public.supplier_subscriptions_supplier_id_84f377c6;
DROP INDEX IF EXISTS public.supplier_subscriptions_plan_id_a6b37853;
DROP INDEX IF EXISTS public.supplier_subscriptions_changed_by_id_d22b0a7c;
DROP INDEX IF EXISTS public.supplier_profiles_slug_e553b94a_like;
DROP INDEX IF EXISTS public.supplier_documents_supplier_id_b4c40cf4;
DROP INDEX IF EXISTS public.sub_orders_supplier_id_da7f0756;
DROP INDEX IF EXISTS public.sub_orders_order_id_24b9bae3;
DROP INDEX IF EXISTS public.search_history_user_id_b2c466f7;
DROP INDEX IF EXISTS public.search_hist_user_id_f49661_idx;
DROP INDEX IF EXISTS public.reviews_variant_id_6f6b041c;
DROP INDEX IF EXISTS public.reviews_supplier_id_38f37b3e;
DROP INDEX IF EXISTS public.reviews_reviewer_id_dbb954a8;
DROP INDEX IF EXISTS public.reviews_product_id_d4b78cfe;
DROP INDEX IF EXISTS public.reviews_order_id_35d02b74;
DROP INDEX IF EXISTS public.review_photos_review_id_e79d7d0f;
DROP INDEX IF EXISTS public.quotes_supplier_id_4f28ef00;
DROP INDEX IF EXISTS public.quotes_product_id_1acb7bad;
DROP INDEX IF EXISTS public.quotes_buyer_id_22f5da77;
DROP INDEX IF EXISTS public.products_supplier_id_ae23c972;
DROP INDEX IF EXISTS public.products_supplie_1396c7_idx;
DROP INDEX IF EXISTS public.products_status_a30e64_idx;
DROP INDEX IF EXISTS public.products_sold_co_e478bd_idx;
DROP INDEX IF EXISTS public.products_slug_8f20884e_like;
DROP INDEX IF EXISTS public.products_category_id_a7a3a156;
DROP INDEX IF EXISTS public.products_categor_4083ff_idx;
DROP INDEX IF EXISTS public.product_variants_product_id_019d9f04;
DROP INDEX IF EXISTS public.product_price_tiers_product_id_0b11ff1b;
DROP INDEX IF EXISTS public.product_interactions_user_id_7d8a05fd;
DROP INDEX IF EXISTS public.product_interactions_product_id_3b05e327;
DROP INDEX IF EXISTS public.product_int_user_id_300aa7_idx;
DROP INDEX IF EXISTS public.product_int_product_877230_idx;
DROP INDEX IF EXISTS public.product_images_product_id_28ebf5f0;
DROP INDEX IF EXISTS public.orders_buyer_id_3d1f9476;
DROP INDEX IF EXISTS public.order_items_sub_order_id_402616ff;
DROP INDEX IF EXISTS public.order_items_product_id_dd557d5a;
DROP INDEX IF EXISTS public.notifications_user_id_468e288d;
DROP INDEX IF EXISTS public.notificatio_user_id_a4dd5c_idx;
DROP INDEX IF EXISTS public.messages_sender_id_dc5a0bbd;
DROP INDEX IF EXISTS public.messages_conversation_id_5ef638db;
DROP INDEX IF EXISTS public.django_session_session_key_c0390e0f_like;
DROP INDEX IF EXISTS public.django_session_expire_date_a5c62663;
DROP INDEX IF EXISTS public.django_admin_log_user_id_c564eba6;
DROP INDEX IF EXISTS public.django_admin_log_content_type_id_c4bce8eb;
DROP INDEX IF EXISTS public.coupons_user_id_bee5d0f0;
DROP INDEX IF EXISTS public.coupons_code_ca4a2ab4_like;
DROP INDEX IF EXISTS public.conversations_supplier_id_b1a02e5b;
DROP INDEX IF EXISTS public.conversations_product_id_c2c693e3;
DROP INDEX IF EXISTS public.conversations_buyer_id_d99807d5;
DROP INDEX IF EXISTS public.commissions_supplier_id_63abfe1e;
DROP INDEX IF EXISTS public.categories_slug_9bedfe6b_like;
DROP INDEX IF EXISTS public.categories_parent_id_fc02df82;
DROP INDEX IF EXISTS public.cart_items_variant_id_6e25bb33;
DROP INDEX IF EXISTS public.cart_items_product_id_9398bb89;
DROP INDEX IF EXISTS public.cart_items_buyer_id_fd91efa0;
DROP INDEX IF EXISTS public.banners_supplier_id_56a381c8;
DROP INDEX IF EXISTS public.auth_permission_content_type_id_2f476e4b;
DROP INDEX IF EXISTS public.auth_group_permissions_permission_id_84c5c92e;
DROP INDEX IF EXISTS public.auth_group_permissions_group_id_b120cbf9;
DROP INDEX IF EXISTS public.auth_group_name_a6ea08ec_like;
ALTER TABLE IF EXISTS ONLY public.wishlists DROP CONSTRAINT IF EXISTS wishlists_pkey;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_user_id_permission_id_3b86cbdf_uniq;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_user_id_group_id_fc7788e8_uniq;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_email_key;
ALTER TABLE IF EXISTS ONLY public.user_spins DROP CONSTRAINT IF EXISTS user_spins_video_ref_key;
ALTER TABLE IF EXISTS ONLY public.user_spins DROP CONSTRAINT IF EXISTS user_spins_pkey;
ALTER TABLE IF EXISTS ONLY public.wishlists DROP CONSTRAINT IF EXISTS unique_wishlist_supplier;
ALTER TABLE IF EXISTS ONLY public.wishlists DROP CONSTRAINT IF EXISTS unique_wishlist_product;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS unique_review_supplier;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS unique_review_product;
ALTER TABLE IF EXISTS ONLY public.conversations DROP CONSTRAINT IF EXISTS unique_conversation;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_outstandingtoken DROP CONSTRAINT IF EXISTS token_blacklist_outstandingtoken_pkey;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_outstandingtoken DROP CONSTRAINT IF EXISTS token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_blacklistedtoken DROP CONSTRAINT IF EXISTS token_blacklist_blacklistedtoken_token_id_key;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_blacklistedtoken DROP CONSTRAINT IF EXISTS token_blacklist_blacklistedtoken_pkey;
ALTER TABLE IF EXISTS ONLY public.supplier_subscriptions DROP CONSTRAINT IF EXISTS supplier_subscriptions_pkey;
ALTER TABLE IF EXISTS ONLY public.supplier_store DROP CONSTRAINT IF EXISTS supplier_store_supplier_id_key;
ALTER TABLE IF EXISTS ONLY public.supplier_store DROP CONSTRAINT IF EXISTS supplier_store_pkey;
ALTER TABLE IF EXISTS ONLY public.supplier_profiles DROP CONSTRAINT IF EXISTS supplier_profiles_user_id_key;
ALTER TABLE IF EXISTS ONLY public.supplier_profiles DROP CONSTRAINT IF EXISTS supplier_profiles_slug_key;
ALTER TABLE IF EXISTS ONLY public.supplier_profiles DROP CONSTRAINT IF EXISTS supplier_profiles_pkey;
ALTER TABLE IF EXISTS ONLY public.supplier_documents DROP CONSTRAINT IF EXISTS supplier_documents_pkey;
ALTER TABLE IF EXISTS ONLY public.subscription_plans DROP CONSTRAINT IF EXISTS subscription_plans_pkey;
ALTER TABLE IF EXISTS ONLY public.sub_orders DROP CONSTRAINT IF EXISTS sub_orders_pkey;
ALTER TABLE IF EXISTS ONLY public.spin_prizes DROP CONSTRAINT IF EXISTS spin_prizes_pkey;
ALTER TABLE IF EXISTS ONLY public.search_history DROP CONSTRAINT IF EXISTS search_history_pkey;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS reviews_pkey;
ALTER TABLE IF EXISTS ONLY public.review_photos DROP CONSTRAINT IF EXISTS review_photos_pkey;
ALTER TABLE IF EXISTS ONLY public.quotes DROP CONSTRAINT IF EXISTS quotes_pkey;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_slug_key;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_pkey;
ALTER TABLE IF EXISTS ONLY public.product_variants DROP CONSTRAINT IF EXISTS product_variants_pkey;
ALTER TABLE IF EXISTS ONLY public.product_price_tiers DROP CONSTRAINT IF EXISTS product_price_tiers_pkey;
ALTER TABLE IF EXISTS ONLY public.product_interactions DROP CONSTRAINT IF EXISTS product_interactions_pkey;
ALTER TABLE IF EXISTS ONLY public.product_images DROP CONSTRAINT IF EXISTS product_images_pkey;
ALTER TABLE IF EXISTS ONLY public.orders DROP CONSTRAINT IF EXISTS orders_pkey;
ALTER TABLE IF EXISTS ONLY public.order_items DROP CONSTRAINT IF EXISTS order_items_pkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_pkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_pkey;
ALTER TABLE IF EXISTS ONLY public.django_session DROP CONSTRAINT IF EXISTS django_session_pkey;
ALTER TABLE IF EXISTS ONLY public.django_migrations DROP CONSTRAINT IF EXISTS django_migrations_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_app_label_model_76bd3d3b_uniq;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_pkey;
ALTER TABLE IF EXISTS ONLY public.coupons DROP CONSTRAINT IF EXISTS coupons_pkey;
ALTER TABLE IF EXISTS ONLY public.coupons DROP CONSTRAINT IF EXISTS coupons_code_key;
ALTER TABLE IF EXISTS ONLY public.conversations DROP CONSTRAINT IF EXISTS conversations_pkey;
ALTER TABLE IF EXISTS ONLY public.commissions DROP CONSTRAINT IF EXISTS commissions_sub_order_id_key;
ALTER TABLE IF EXISTS ONLY public.commissions DROP CONSTRAINT IF EXISTS commissions_pkey;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_slug_key;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_pkey;
ALTER TABLE IF EXISTS ONLY public.cart_items DROP CONSTRAINT IF EXISTS cart_items_pkey;
ALTER TABLE IF EXISTS ONLY public.cart_items DROP CONSTRAINT IF EXISTS cart_items_buyer_id_product_id_variant_id_250b8b19_uniq;
ALTER TABLE IF EXISTS ONLY public.buyer_profiles DROP CONSTRAINT IF EXISTS buyer_profiles_user_id_key;
ALTER TABLE IF EXISTS ONLY public.buyer_profiles DROP CONSTRAINT IF EXISTS buyer_profiles_pkey;
ALTER TABLE IF EXISTS ONLY public.banners DROP CONSTRAINT IF EXISTS banners_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_codename_01ab375a_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_name_key;
DROP TABLE IF EXISTS public.wishlists;
DROP TABLE IF EXISTS public.users_user_permissions;
DROP TABLE IF EXISTS public.users_groups;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.user_spins;
DROP TABLE IF EXISTS public.token_blacklist_outstandingtoken;
DROP TABLE IF EXISTS public.token_blacklist_blacklistedtoken;
DROP TABLE IF EXISTS public.supplier_subscriptions;
DROP TABLE IF EXISTS public.supplier_store;
DROP TABLE IF EXISTS public.supplier_profiles;
DROP TABLE IF EXISTS public.supplier_documents;
DROP TABLE IF EXISTS public.subscription_plans;
DROP TABLE IF EXISTS public.sub_orders;
DROP TABLE IF EXISTS public.spin_prizes;
DROP TABLE IF EXISTS public.search_history;
DROP TABLE IF EXISTS public.reviews;
DROP TABLE IF EXISTS public.review_photos;
DROP TABLE IF EXISTS public.quotes;
DROP TABLE IF EXISTS public.products;
DROP TABLE IF EXISTS public.product_variants;
DROP TABLE IF EXISTS public.product_price_tiers;
DROP TABLE IF EXISTS public.product_interactions;
DROP TABLE IF EXISTS public.product_images;
DROP TABLE IF EXISTS public.orders;
DROP TABLE IF EXISTS public.order_items;
DROP TABLE IF EXISTS public.notifications;
DROP TABLE IF EXISTS public.messages;
DROP TABLE IF EXISTS public.django_session;
DROP TABLE IF EXISTS public.django_migrations;
DROP TABLE IF EXISTS public.django_content_type;
DROP TABLE IF EXISTS public.django_admin_log;
DROP TABLE IF EXISTS public.coupons;
DROP TABLE IF EXISTS public.conversations;
DROP TABLE IF EXISTS public.commissions;
DROP TABLE IF EXISTS public.categories;
DROP TABLE IF EXISTS public.cart_items;
DROP TABLE IF EXISTS public.buyer_profiles;
DROP TABLE IF EXISTS public.banners;
DROP TABLE IF EXISTS public.auth_permission;
DROP TABLE IF EXISTS public.auth_group_permissions;
DROP TABLE IF EXISTS public.auth_group;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: banners; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.banners (
    id uuid NOT NULL,
    image_url text NOT NULL,
    link_url text NOT NULL,
    slot character varying(30) NOT NULL,
    starts_at timestamp with time zone,
    ends_at timestamp with time zone,
    price_tnd numeric(10,3),
    impressions integer NOT NULL,
    clicks integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    supplier_id uuid NOT NULL
);


--
-- Name: buyer_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.buyer_profiles (
    id uuid NOT NULL,
    company_name character varying(200) NOT NULL,
    trade_type character varying(30) NOT NULL,
    rc_number character varying(100) NOT NULL,
    city character varying(100) NOT NULL,
    wilaya character varying(100) NOT NULL,
    phone_pro character varying(20) NOT NULL,
    total_orders integer NOT NULL,
    total_spent_tnd numeric(14,3) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    user_id uuid NOT NULL
);


--
-- Name: cart_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cart_items (
    id uuid NOT NULL,
    quantity integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    buyer_id uuid NOT NULL,
    product_id uuid NOT NULL,
    variant_id uuid,
    CONSTRAINT cart_items_quantity_check CHECK ((quantity >= 0))
);


--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    id uuid NOT NULL,
    name character varying(150) NOT NULL,
    slug character varying(200) NOT NULL,
    icon_name character varying(100) NOT NULL,
    image_url text NOT NULL,
    is_hot boolean NOT NULL,
    is_new boolean NOT NULL,
    sort_order integer NOT NULL,
    is_active boolean NOT NULL,
    parent_id uuid
);


--
-- Name: commissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.commissions (
    id uuid NOT NULL,
    commission_pct numeric(5,2) NOT NULL,
    subtotal_tnd numeric(12,3) NOT NULL,
    commission_tnd numeric(12,3) NOT NULL,
    supplier_net_tnd numeric(12,3) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    sub_order_id uuid NOT NULL,
    supplier_id uuid NOT NULL
);


--
-- Name: conversations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conversations (
    id uuid NOT NULL,
    last_msg_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    buyer_id uuid NOT NULL,
    product_id uuid,
    supplier_id uuid NOT NULL
);


--
-- Name: coupons; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.coupons (
    id uuid NOT NULL,
    code character varying(50) NOT NULL,
    amount_tnd numeric(10,3) NOT NULL,
    source character varying(20) NOT NULL,
    is_used boolean NOT NULL,
    used_at timestamp with time zone,
    expires_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    user_id uuid
);


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id uuid NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


--
-- Name: messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.messages (
    id uuid NOT NULL,
    content text NOT NULL,
    attachment_url text NOT NULL,
    is_read boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    conversation_id uuid NOT NULL,
    sender_id uuid NOT NULL
);


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id uuid NOT NULL,
    type character varying(50) NOT NULL,
    title character varying(200) NOT NULL,
    body text NOT NULL,
    data jsonb NOT NULL,
    channel character varying(20) NOT NULL,
    is_read boolean NOT NULL,
    sent_at timestamp with time zone NOT NULL,
    user_id uuid NOT NULL
);


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.order_items (
    id uuid NOT NULL,
    quantity integer NOT NULL,
    unit_price_tnd numeric(10,3) NOT NULL,
    total_tnd numeric(12,3) NOT NULL,
    product_id uuid NOT NULL,
    sub_order_id uuid NOT NULL
);


--
-- Name: orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orders (
    id uuid NOT NULL,
    status character varying(30) NOT NULL,
    payment_status character varying(20) NOT NULL,
    payment_method character varying(20) NOT NULL,
    total_tnd numeric(12,3) NOT NULL,
    discount_tnd numeric(10,3) NOT NULL,
    shipping_address text NOT NULL,
    notes text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    buyer_id uuid NOT NULL
);


--
-- Name: product_images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_images (
    id uuid NOT NULL,
    url text NOT NULL,
    is_primary boolean NOT NULL,
    sort_order integer NOT NULL,
    product_id uuid NOT NULL
);


--
-- Name: product_interactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_interactions (
    id uuid NOT NULL,
    event_type character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    product_id uuid NOT NULL,
    user_id uuid NOT NULL
);


--
-- Name: product_price_tiers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_price_tiers (
    id uuid NOT NULL,
    min_qty integer NOT NULL,
    max_qty integer,
    price_tnd numeric(10,3) NOT NULL,
    product_id uuid NOT NULL
);


--
-- Name: product_variants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_variants (
    id uuid NOT NULL,
    name character varying(50) NOT NULL,
    image_url text NOT NULL,
    sort_order integer NOT NULL,
    product_id uuid NOT NULL
);


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    id uuid NOT NULL,
    name character varying(300) NOT NULL,
    slug character varying(350) NOT NULL,
    description text NOT NULL,
    sku character varying(100) NOT NULL,
    unit character varying(50) NOT NULL,
    moq integer NOT NULL,
    base_price_tnd numeric(10,3) NOT NULL,
    video_url text NOT NULL,
    stock_qty integer NOT NULL,
    sold_count integer NOT NULL,
    view_count integer NOT NULL,
    rating_avg numeric(3,2) NOT NULL,
    rating_count integer NOT NULL,
    status character varying(20) NOT NULL,
    badge_choice boolean NOT NULL,
    badge_flash boolean NOT NULL,
    badge_flash_end timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    category_id uuid,
    supplier_id uuid NOT NULL,
    is_free_shipping boolean NOT NULL,
    old_price_tnd numeric(10,3),
    brand character varying(100) NOT NULL,
    pack_size integer NOT NULL,
    reference character varying(100) NOT NULL,
    specs_raw text NOT NULL,
    delivery_days integer NOT NULL,
    shipping_price_tnd numeric(10,3) NOT NULL,
    CONSTRAINT products_delivery_days_check CHECK ((delivery_days >= 0)),
    CONSTRAINT products_pack_size_check CHECK ((pack_size >= 0))
);


--
-- Name: quotes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quotes (
    id uuid NOT NULL,
    quantity integer NOT NULL,
    message text NOT NULL,
    status character varying(20) NOT NULL,
    quote_tnd numeric(12,3),
    valid_until timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    buyer_id uuid NOT NULL,
    product_id uuid,
    supplier_id uuid NOT NULL
);


--
-- Name: review_photos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.review_photos (
    id uuid NOT NULL,
    url text NOT NULL,
    sort_order integer NOT NULL,
    review_id uuid NOT NULL
);


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reviews (
    id uuid NOT NULL,
    rating smallint NOT NULL,
    comment text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    order_id uuid,
    product_id uuid,
    reviewer_id uuid NOT NULL,
    supplier_id uuid,
    variant_id uuid
);


--
-- Name: search_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_history (
    id uuid NOT NULL,
    query character varying(300) NOT NULL,
    result_count integer NOT NULL,
    searched_at timestamp with time zone NOT NULL,
    user_id uuid NOT NULL
);


--
-- Name: spin_prizes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spin_prizes (
    id uuid NOT NULL,
    label character varying(150) NOT NULL,
    prize_type character varying(20) NOT NULL,
    value_tnd numeric(10,3),
    probability numeric(5,4) NOT NULL,
    color_hex character varying(7) NOT NULL,
    is_active boolean NOT NULL
);


--
-- Name: sub_orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sub_orders (
    id uuid NOT NULL,
    status character varying(30) NOT NULL,
    subtotal_tnd numeric(12,3) NOT NULL,
    delivery_type character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    order_id uuid NOT NULL,
    supplier_id uuid NOT NULL
);


--
-- Name: subscription_plans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subscription_plans (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    price_tnd numeric(10,3) NOT NULL,
    commission_pct numeric(5,2) NOT NULL,
    max_products integer,
    features jsonb NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: supplier_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.supplier_documents (
    id uuid NOT NULL,
    doc_type character varying(50) NOT NULL,
    file_url text NOT NULL,
    status character varying(20) NOT NULL,
    uploaded_at timestamp with time zone NOT NULL,
    supplier_id uuid NOT NULL
);


--
-- Name: supplier_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.supplier_profiles (
    id uuid NOT NULL,
    company_name character varying(200) NOT NULL,
    slug character varying(200) NOT NULL,
    rc_number character varying(100) NOT NULL,
    tax_number character varying(100) NOT NULL,
    address text NOT NULL,
    city character varying(100) NOT NULL,
    wilaya character varying(100) NOT NULL,
    min_order_tnd numeric(10,3),
    verified_at timestamp with time zone,
    verification_status character varying(20) NOT NULL,
    rating_avg numeric(3,2) NOT NULL,
    rating_count integer NOT NULL,
    followers_count integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    user_id uuid NOT NULL
);


--
-- Name: supplier_store; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.supplier_store (
    id uuid NOT NULL,
    logo_url text NOT NULL,
    banner_url text NOT NULL,
    description text NOT NULL,
    certifications text NOT NULL,
    page_views integer NOT NULL,
    response_rate numeric(5,2) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    supplier_id uuid NOT NULL,
    founded_year integer,
    response_time_hrs integer
);


--
-- Name: supplier_subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.supplier_subscriptions (
    id uuid NOT NULL,
    status character varying(20) NOT NULL,
    started_at timestamp with time zone NOT NULL,
    expires_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    changed_by_id uuid,
    plan_id uuid NOT NULL,
    supplier_id uuid NOT NULL
);


--
-- Name: token_blacklist_blacklistedtoken; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.token_blacklist_blacklistedtoken (
    id bigint NOT NULL,
    blacklisted_at timestamp with time zone NOT NULL,
    token_id bigint NOT NULL
);


--
-- Name: token_blacklist_blacklistedtoken_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.token_blacklist_blacklistedtoken ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.token_blacklist_blacklistedtoken_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: token_blacklist_outstandingtoken; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.token_blacklist_outstandingtoken (
    id bigint NOT NULL,
    token text NOT NULL,
    created_at timestamp with time zone,
    expires_at timestamp with time zone NOT NULL,
    user_id uuid,
    jti character varying(255) CONSTRAINT token_blacklist_outstandingtoken_jti_hex_not_null NOT NULL
);


--
-- Name: token_blacklist_outstandingtoken_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.token_blacklist_outstandingtoken ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.token_blacklist_outstandingtoken_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: user_spins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_spins (
    id uuid NOT NULL,
    video_ref character varying(200) NOT NULL,
    spun_at timestamp with time zone NOT NULL,
    coupon_id uuid,
    prize_id uuid,
    user_id uuid NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    id uuid NOT NULL,
    email character varying(254) NOT NULL,
    phone character varying(20) NOT NULL,
    full_name character varying(150) NOT NULL,
    avatar_url text NOT NULL,
    role character varying(20) NOT NULL,
    is_verified boolean NOT NULL,
    is_active boolean NOT NULL,
    is_staff boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    last_seen timestamp with time zone
);


--
-- Name: users_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users_groups (
    id bigint NOT NULL,
    user_id uuid NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: users_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users_user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users_user_permissions (
    id bigint NOT NULL,
    user_id uuid NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: users_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: wishlists; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wishlists (
    id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    product_id uuid,
    supplier_id uuid,
    user_id uuid NOT NULL
);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add user	6	add_user
22	Can change user	6	change_user
23	Can delete user	6	delete_user
24	Can view user	6	view_user
25	Can add buyer profile	7	add_buyerprofile
26	Can change buyer profile	7	change_buyerprofile
27	Can delete buyer profile	7	delete_buyerprofile
28	Can view buyer profile	7	view_buyerprofile
29	Can add supplier profile	8	add_supplierprofile
30	Can change supplier profile	8	change_supplierprofile
31	Can delete supplier profile	8	delete_supplierprofile
32	Can view supplier profile	8	view_supplierprofile
33	Can add supplier store	9	add_supplierstore
34	Can change supplier store	9	change_supplierstore
35	Can delete supplier store	9	delete_supplierstore
36	Can view supplier store	9	view_supplierstore
37	Can add category	10	add_category
38	Can change category	10	change_category
39	Can delete category	10	delete_category
40	Can view category	10	view_category
41	Can add product	11	add_product
42	Can change product	11	change_product
43	Can delete product	11	delete_product
44	Can view product	11	view_product
45	Can add product image	12	add_productimage
46	Can change product image	12	change_productimage
47	Can delete product image	12	delete_productimage
48	Can view product image	12	view_productimage
49	Can add product price tier	13	add_productpricetier
50	Can change product price tier	13	change_productpricetier
51	Can delete product price tier	13	delete_productpricetier
52	Can view product price tier	13	view_productpricetier
53	Can add sub order	14	add_suborder
54	Can change sub order	14	change_suborder
55	Can delete sub order	14	delete_suborder
56	Can view sub order	14	view_suborder
57	Can add order	15	add_order
58	Can change order	15	change_order
59	Can delete order	15	delete_order
60	Can view order	15	view_order
61	Can add order item	16	add_orderitem
62	Can change order item	16	change_orderitem
63	Can delete order item	16	delete_orderitem
64	Can view order item	16	view_orderitem
65	Can add notification	17	add_notification
66	Can change notification	17	change_notification
67	Can delete notification	17	delete_notification
68	Can view notification	17	view_notification
69	Can add conversation	18	add_conversation
70	Can change conversation	18	change_conversation
71	Can delete conversation	18	delete_conversation
72	Can view conversation	18	view_conversation
73	Can add message	19	add_message
74	Can change message	19	change_message
75	Can delete message	19	delete_message
76	Can view message	19	view_message
77	Can add review	20	add_review
78	Can change review	20	change_review
79	Can delete review	20	delete_review
80	Can view review	20	view_review
81	Can add spin prize	21	add_spinprize
82	Can change spin prize	21	change_spinprize
83	Can delete spin prize	21	delete_spinprize
84	Can view spin prize	21	view_spinprize
85	Can add user spin	22	add_userspin
86	Can change user spin	22	change_userspin
87	Can delete user spin	22	delete_userspin
88	Can view user spin	22	view_userspin
89	Can add coupon	23	add_coupon
90	Can change coupon	23	change_coupon
91	Can delete coupon	23	delete_coupon
92	Can view coupon	23	view_coupon
93	Can add supplier subscription	24	add_suppliersubscription
94	Can change supplier subscription	24	change_suppliersubscription
95	Can delete supplier subscription	24	delete_suppliersubscription
96	Can view supplier subscription	24	view_suppliersubscription
97	Can add quote	25	add_quote
98	Can change quote	25	change_quote
99	Can delete quote	25	delete_quote
100	Can view quote	25	view_quote
101	Can add subscription plan	26	add_subscriptionplan
102	Can change subscription plan	26	change_subscriptionplan
103	Can delete subscription plan	26	delete_subscriptionplan
104	Can view subscription plan	26	view_subscriptionplan
105	Can add banner	27	add_banner
106	Can change banner	27	change_banner
107	Can delete banner	27	delete_banner
108	Can view banner	27	view_banner
109	Can add wishlist	28	add_wishlist
110	Can change wishlist	28	change_wishlist
111	Can delete wishlist	28	delete_wishlist
112	Can view wishlist	28	view_wishlist
113	Can add commission	29	add_commission
114	Can change commission	29	change_commission
115	Can delete commission	29	delete_commission
116	Can view commission	29	view_commission
117	Can add supplier document	30	add_supplierdocument
118	Can change supplier document	30	change_supplierdocument
119	Can delete supplier document	30	delete_supplierdocument
120	Can view supplier document	30	view_supplierdocument
121	Can add product interaction	31	add_productinteraction
122	Can change product interaction	31	change_productinteraction
123	Can delete product interaction	31	delete_productinteraction
124	Can view product interaction	31	view_productinteraction
125	Can add search history	32	add_searchhistory
126	Can change search history	32	change_searchhistory
127	Can delete search history	32	delete_searchhistory
128	Can view search history	32	view_searchhistory
147	Can add Blacklisted Token	54	add_blacklistedtoken
148	Can change Blacklisted Token	54	change_blacklistedtoken
149	Can delete Blacklisted Token	54	delete_blacklistedtoken
150	Can view Blacklisted Token	54	view_blacklistedtoken
151	Can add Outstanding Token	55	add_outstandingtoken
152	Can change Outstanding Token	55	change_outstandingtoken
153	Can delete Outstanding Token	55	delete_outstandingtoken
154	Can view Outstanding Token	55	view_outstandingtoken
155	Can add product variant	56	add_productvariant
156	Can change product variant	56	change_productvariant
157	Can delete product variant	56	delete_productvariant
158	Can view product variant	56	view_productvariant
159	Can add review photo	57	add_reviewphoto
160	Can change review photo	57	change_reviewphoto
161	Can delete review photo	57	delete_reviewphoto
162	Can view review photo	57	view_reviewphoto
163	Can add cart item	58	add_cartitem
164	Can change cart item	58	change_cartitem
165	Can delete cart item	58	delete_cartitem
166	Can view cart item	58	view_cartitem
\.


--
-- Data for Name: banners; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.banners (id, image_url, link_url, slot, starts_at, ends_at, price_tnd, impressions, clicks, is_active, created_at, supplier_id) FROM stdin;
\.


--
-- Data for Name: buyer_profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.buyer_profiles (id, company_name, trade_type, rc_number, city, wilaya, phone_pro, total_orders, total_spent_tnd, created_at, user_id) FROM stdin;
3e2273ae-c688-4d33-bb48-c63b68946a31							0	0.000	2026-06-11 19:08:10.59635+01	d5ec6043-f93f-46d7-b500-240bafa964b8
10ea8543-c139-4da0-8012-11ecae23d8aa							0	0.000	2026-06-14 20:43:18.751121+01	39277626-4717-4ab2-9f1b-180c1d3c84f1
\.


--
-- Data for Name: cart_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cart_items (id, quantity, created_at, updated_at, buyer_id, product_id, variant_id) FROM stdin;
977b4df2-68bc-4799-a82c-d01ceefc40a6	111	2026-06-26 04:32:00.896738+01	2026-06-26 04:36:49.890301+01	a53de944-cff5-411a-8da5-cf68296311ef	90ac3559-cd27-446a-9d10-e88de14053e5	\N
0a89d6a3-1f0c-4423-b95b-94f6df046ff3	43	2026-06-26 04:32:19.932748+01	2026-06-26 14:10:13.193887+01	a53de944-cff5-411a-8da5-cf68296311ef	3378bc0d-8c6f-4fff-8b0e-be5f3f7309d4	\N
52e7d6cb-65c8-4f9a-8efb-c7f81e70f559	104	2026-06-26 14:10:32.341331+01	2026-06-26 14:10:53.129511+01	a53de944-cff5-411a-8da5-cf68296311ef	4d754241-9ff6-4027-a2a5-b8a82c98a424	\N
9392e6c5-db81-4347-ba7a-112df81b4441	50	2026-06-30 13:53:55.988098+01	2026-06-30 13:53:55.989442+01	a53de944-cff5-411a-8da5-cf68296311ef	ec1782fa-3cd9-454d-a6e5-b81b8d920db1	\N
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.categories (id, name, slug, icon_name, image_url, is_hot, is_new, sort_order, is_active, parent_id) FROM stdin;
9f2bba15-be85-4c8c-bf01-3d353bd63d13	Textile	textile	Shirt		f	f	1	t	\N
a1b2c3d4-0001-0001-0001-000000000001	Électronique	electronique	Cpu		f	f	2	t	\N
a1b2c3d4-0002-0002-0002-000000000002	Alimentaire	alimentaire	Apple		t	f	3	t	\N
a1b2c3d4-0003-0003-0003-000000000003	Hygiène	hygiene	Sparkles		f	t	4	t	\N
a1b2c3d4-0004-0004-0004-000000000004	Mobilier	mobilier	Armchair		f	f	5	t	\N
a1b2c3d4-0005-0005-0005-000000000005	Beauté	beaute	Sparkles		t	t	6	t	\N
a1b2c3d4-0006-0006-0006-000000000006	Sport	sport	Dumbbell		f	t	7	t	\N
a1b2c3d4-0007-0007-0007-000000000007	Cuisine	cuisine	ChefHat		t	f	8	t	\N
a1b2c3d4-0008-0008-0008-000000000008	Papeterie	papeterie	PenLine		f	f	9	t	\N
a1b2c3d4-0009-0009-0009-000000000009	Jouets	jouets	Gamepad2		t	f	10	t	\N
95738ed9-1211-4b5e-afe9-c2ddf79e8c26	T-shirts	textile-t-shirts		https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400	t	f	0	t	9f2bba15-be85-4c8c-bf01-3d353bd63d13
ccfda88d-e22f-49e2-805a-5faaf40bf1ec	Jeans	textile-jeans		https://images.unsplash.com/photo-1542272604-787c3835535d?w=400	f	f	1	t	9f2bba15-be85-4c8c-bf01-3d353bd63d13
4a4a69a5-0d32-48b3-9709-350017f9b9de	Robes	textile-robes		https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400	f	t	2	t	9f2bba15-be85-4c8c-bf01-3d353bd63d13
6302c9e9-88bd-410b-972e-c65c1ea3045f	Vestes	textile-vestes		https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400	f	f	3	t	9f2bba15-be85-4c8c-bf01-3d353bd63d13
33c269f9-7369-4f24-9c32-6a55f4851902	Sous-vetements	textile-sous-vetements		https://images.unsplash.com/photo-1571513722275-4b41940f54b8?w=400	f	f	4	t	9f2bba15-be85-4c8c-bf01-3d353bd63d13
5e862e54-f39e-488e-943d-b8edd4b48462	Chaussures	textile-chaussures		https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400	t	f	5	t	9f2bba15-be85-4c8c-bf01-3d353bd63d13
9953f5bd-7645-45d5-9824-c060df7c8f71	Sacs	textile-sacs		https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400	f	f	6	t	9f2bba15-be85-4c8c-bf01-3d353bd63d13
8443cb92-1116-4423-a9a3-18f94580130a	Smartphones	electronique-smartphones		https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400	t	f	0	t	a1b2c3d4-0001-0001-0001-000000000001
fbc5663f-aec1-4575-8797-401090ee51e3	Accessoires	electronique-accessoires		https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400	f	f	1	t	a1b2c3d4-0001-0001-0001-000000000001
235b05c0-39f9-404d-be11-874f0454f6e0	Audio	electronique-audio		https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400	f	f	2	t	a1b2c3d4-0001-0001-0001-000000000001
12ad4b9c-6918-48d2-ae75-7ee37a28892d	Ordinateurs	electronique-ordinateurs		https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400	f	f	3	t	a1b2c3d4-0001-0001-0001-000000000001
5c574a4e-434d-480a-b3cd-393a6c8f6c1f	TV et Video	electronique-tv-et-video		https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400	f	f	4	t	a1b2c3d4-0001-0001-0001-000000000001
111787bd-4b0a-4b71-98f9-75709f347250	Petits electros	electronique-petits-electros		https://images.unsplash.com/photo-1574269909862-7e1d70bb892a?w=400	f	t	5	t	a1b2c3d4-0001-0001-0001-000000000001
1ed517bf-932f-4d2a-89b5-f8efa5579ec4	Epicerie	alimentaire-epicerie		https://images.unsplash.com/photo-1542838132-92c53300491e?w=400	f	f	0	t	a1b2c3d4-0002-0002-0002-000000000002
6c6edfe2-9246-47f8-ac86-1e295918faa9	Boissons	alimentaire-boissons		https://images.unsplash.com/photo-1543253687-c931c8e01820?w=400	f	f	1	t	a1b2c3d4-0002-0002-0002-000000000002
99de5358-67fd-4e00-8c9f-a8149172968d	Conserves	alimentaire-conserves		https://images.unsplash.com/photo-1584473457409-ce95a9c00018?w=400	f	f	2	t	a1b2c3d4-0002-0002-0002-000000000002
7e2b8b92-5b52-44a6-8ff2-368b299a0be9	Snacks	alimentaire-snacks		https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400	t	f	3	t	a1b2c3d4-0002-0002-0002-000000000002
92c33391-b275-413a-ac12-e878ea106750	Surgeles	alimentaire-surgeles		https://images.unsplash.com/photo-1574326830054-fab2cfae73c0?w=400	f	f	4	t	a1b2c3d4-0002-0002-0002-000000000002
1be14387-5100-4037-9623-ef9ac102fba4	Soins du corps	hygiene-soins-du-corps		https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400	f	f	0	t	a1b2c3d4-0003-0003-0003-000000000003
45ae44d9-8abd-46b3-97fa-a4f809327e13	Hygiene dentaire	hygiene-hygiene-dentaire		https://images.unsplash.com/photo-1559591935-c6c92c6bdd1f?w=400	f	f	1	t	a1b2c3d4-0003-0003-0003-000000000003
2c001dde-7cb2-4e87-9cb8-9c6a4e405b70	Bebe	hygiene-bebe		https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=400	f	t	2	t	a1b2c3d4-0003-0003-0003-000000000003
97f08dd4-648e-4ef5-9266-d2bc4db37b13	Detergents	hygiene-detergents		https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=400	f	f	3	t	a1b2c3d4-0003-0003-0003-000000000003
e4e615d6-a85e-46d1-a4a0-fdf3802a343f	Papier	hygiene-papier		https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=400	f	f	4	t	a1b2c3d4-0003-0003-0003-000000000003
ae2dc758-998e-43b7-9dcd-025e796d1f9f	Salon	mobilier-salon		https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400	f	f	0	t	a1b2c3d4-0004-0004-0004-000000000004
0f28acec-e6c5-4abb-89d6-439513aac895	Chambre	mobilier-chambre		https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=400	f	f	1	t	a1b2c3d4-0004-0004-0004-000000000004
af86248f-aa32-4c14-a0e4-0710d2eb84b0	Cuisine	mobilier-cuisine		https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400	f	f	2	t	a1b2c3d4-0004-0004-0004-000000000004
b6ebac57-d05d-4fe7-878f-8377490e6945	Bureau	mobilier-bureau		https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=400	f	t	3	t	a1b2c3d4-0004-0004-0004-000000000004
13b52024-a64f-4738-b015-93408d477dc6	Decoration	mobilier-decoration		https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=400	f	f	4	t	a1b2c3d4-0004-0004-0004-000000000004
6ed03fba-6bcc-4698-93ca-147da83ab44c	Maquillage	beaute-maquillage		https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400	t	f	0	t	a1b2c3d4-0005-0005-0005-000000000005
83b98b86-6ee6-4ffe-9004-6ec7f0b10111	Parfums	beaute-parfums		https://images.unsplash.com/photo-1541643600914-78b084683601?w=400	f	f	1	t	a1b2c3d4-0005-0005-0005-000000000005
3c3f123e-3e0b-4127-a274-e1bc3f29347c	Soins visage	beaute-soins-visage		https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=400	f	f	2	t	a1b2c3d4-0005-0005-0005-000000000005
bcfb22a7-4050-45a5-a6c6-6e8dee7236a1	Cheveux	beaute-cheveux		https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400	f	f	3	t	a1b2c3d4-0005-0005-0005-000000000005
de02a5eb-5525-4147-af4f-fa9e454bc276	Ongles	beaute-ongles		https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400	f	f	4	t	a1b2c3d4-0005-0005-0005-000000000005
889872ce-ff11-4764-bb50-d25ff8ef7225	Fitness	sport-fitness		https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400	t	f	0	t	a1b2c3d4-0006-0006-0006-000000000006
30cfe886-560f-4745-96f9-7f74a8ff2534	Football	sport-football		https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=400	f	f	1	t	a1b2c3d4-0006-0006-0006-000000000006
ca9c21c9-5063-4626-8fdf-26fd14554ede	Cyclisme	sport-cyclisme		https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=400	f	f	2	t	a1b2c3d4-0006-0006-0006-000000000006
43824f2a-20b3-4350-bdf6-b8e569d2d67b	Natation	sport-natation		https://images.unsplash.com/photo-1530549387789-4c1017266635?w=400	f	f	3	t	a1b2c3d4-0006-0006-0006-000000000006
2b662a17-d44e-481c-89bc-98f01355c93f	Outdoor	sport-outdoor		https://images.unsplash.com/photo-1551632811-561732d1e306?w=400	f	t	4	t	a1b2c3d4-0006-0006-0006-000000000006
23b97140-8f1c-44f2-8542-e9e5873c3faa	Ustensiles	cuisine-ustensiles		https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400	f	f	0	t	a1b2c3d4-0007-0007-0007-000000000007
226cd121-80e2-4080-944e-324c9a392e78	Vaisselle	cuisine-vaisselle		https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=400	f	f	1	t	a1b2c3d4-0007-0007-0007-000000000007
e8b7c249-e340-4a96-b190-1dadebcade0c	Casseroles	cuisine-casseroles		https://images.unsplash.com/photo-1584990347449-a4d4e1b80b5c?w=400	f	f	2	t	a1b2c3d4-0007-0007-0007-000000000007
f3128077-a711-4ab1-9c68-0db12c3ae18e	Petit electro	cuisine-petit-electro		https://images.unsplash.com/photo-1574269909862-7e1d70bb892a?w=400	f	f	3	t	a1b2c3d4-0007-0007-0007-000000000007
80294232-19a7-48bf-b32f-5b74de9e981a	Ecriture	papeterie-ecriture		https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400	f	f	0	t	a1b2c3d4-0008-0008-0008-000000000008
cf20eb30-4164-414a-af3d-495978f9bb13	Cahiers	papeterie-cahiers		https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=400	f	f	1	t	a1b2c3d4-0008-0008-0008-000000000008
7357aed6-3950-493a-902c-6bd1066ccbe5	Cartables	papeterie-cartables		https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400	t	f	2	t	a1b2c3d4-0008-0008-0008-000000000008
1dee7c7c-f287-48f7-b6f8-489992c1407e	Bureautique	papeterie-bureautique		https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?w=400	f	f	3	t	a1b2c3d4-0008-0008-0008-000000000008
9f155bfb-509f-4704-85e8-0bb6adc7665a	Peluches	jouets-peluches		https://images.unsplash.com/photo-1559454403-b8fb88521f0e?w=400	f	f	0	t	a1b2c3d4-0009-0009-0009-000000000009
a29811fb-0b1f-455e-98fe-41c166d85762	Jeux educatifs	jouets-jeux-educatifs		https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400	f	t	1	t	a1b2c3d4-0009-0009-0009-000000000009
4248e49f-011d-44fb-81a3-98608c68d7d8	Voitures	jouets-voitures		https://images.unsplash.com/photo-1594787318286-3d835c1d207f?w=400	f	f	2	t	a1b2c3d4-0009-0009-0009-000000000009
9e4f4931-f5ad-4dca-9334-5f1010a60526	Poupees	jouets-poupees		https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400	f	f	3	t	a1b2c3d4-0009-0009-0009-000000000009
be19befa-a0fb-4a7a-8e4e-5ec12c3557f2	Plein air	jouets-plein-air		https://images.unsplash.com/photo-1597149083691-2a01b6e1bcad?w=400	f	f	4	t	a1b2c3d4-0009-0009-0009-000000000009
\.


--
-- Data for Name: commissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.commissions (id, commission_pct, subtotal_tnd, commission_tnd, supplier_net_tnd, created_at, sub_order_id, supplier_id) FROM stdin;
\.


--
-- Data for Name: conversations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.conversations (id, last_msg_at, created_at, buyer_id, product_id, supplier_id) FROM stdin;
0fb8205c-f32d-47eb-9c2e-9c96c709c886	2026-06-26 16:27:01.83998+01	2026-06-26 16:26:57.429681+01	a53de944-cff5-411a-8da5-cf68296311ef	4d754241-9ff6-4027-a2a5-b8a82c98a424	b591f07a-6bbd-4d4e-83ef-a47e256d48a0
6ce2dd02-7fd9-45f0-8cf4-3c6fa485c6d8	2026-06-26 16:34:00.70051+01	2026-06-26 16:27:16.615482+01	a53de944-cff5-411a-8da5-cf68296311ef	90ac3559-cd27-446a-9d10-e88de14053e5	b591f07a-6bbd-4d4e-83ef-a47e256d48a0
e65ef6bf-2c66-445b-9e94-79286b1c9c19	2026-06-26 16:35:31.14132+01	2026-06-26 16:35:27.529579+01	a53de944-cff5-411a-8da5-cf68296311ef	ec1782fa-3cd9-454d-a6e5-b81b8d920db1	b591f07a-6bbd-4d4e-83ef-a47e256d48a0
\.


--
-- Data for Name: coupons; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.coupons (id, code, amount_tnd, source, is_used, used_at, expires_at, created_at, user_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	sessions	session
6	users	user
7	users	buyerprofile
8	users	supplierprofile
9	users	supplierstore
10	products	category
11	products	product
12	products	productimage
13	products	productpricetier
14	orders	suborder
15	orders	order
16	orders	orderitem
17	notifications	notification
18	messaging	conversation
19	messaging	message
20	products	review
21	gamification	spinprize
22	gamification	userspin
23	gamification	coupon
24	store	suppliersubscription
25	store	quote
26	store	subscriptionplan
27	store	banner
28	store	wishlist
29	store	commission
30	store	supplierdocument
31	store	productinteraction
32	store	searchhistory
54	token_blacklist	blacklistedtoken
55	token_blacklist	outstandingtoken
56	products	productvariant
57	products	reviewphoto
58	orders	cartitem
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2026-06-04 20:56:43.439033+01
2	contenttypes	0002_remove_content_type_name	2026-06-04 20:56:43.448261+01
3	auth	0001_initial	2026-06-04 20:56:43.506137+01
4	auth	0002_alter_permission_name_max_length	2026-06-04 20:56:43.513259+01
5	auth	0003_alter_user_email_max_length	2026-06-04 20:56:43.519375+01
6	auth	0004_alter_user_username_opts	2026-06-04 20:56:43.525683+01
7	auth	0005_alter_user_last_login_null	2026-06-04 20:56:43.533153+01
8	auth	0006_require_contenttypes_0002	2026-06-04 20:56:43.535424+01
9	auth	0007_alter_validators_add_error_messages	2026-06-04 20:56:43.541444+01
10	auth	0008_alter_user_username_max_length	2026-06-04 20:56:43.547751+01
11	auth	0009_alter_user_last_name_max_length	2026-06-04 20:56:43.556129+01
12	auth	0010_alter_group_name_max_length	2026-06-04 20:56:43.564634+01
13	auth	0011_update_proxy_permissions	2026-06-04 20:56:43.573635+01
14	auth	0012_alter_user_first_name_max_length	2026-06-04 20:56:43.580101+01
15	users	0001_initial	2026-06-04 20:56:43.709864+01
16	admin	0001_initial	2026-06-04 20:56:43.74321+01
17	admin	0002_logentry_remove_auto_add	2026-06-04 20:56:43.754805+01
18	admin	0003_logentry_add_action_flag_choices	2026-06-04 20:56:43.767143+01
19	sessions	0001_initial	2026-06-04 20:56:43.781275+01
20	users	0002_supplierstore_founded_year_and_more	2026-06-04 22:34:47.827246+01
21	products	0001_initial	2026-06-04 22:55:29.832555+01
22	orders	0001_initial	2026-06-04 23:26:01.563821+01
23	notifications	0001_initial	2026-06-04 23:31:02.038897+01
24	messaging	0001_initial	2026-06-05 00:28:50.341866+01
25	messaging	0002_remove_message_content_raw_and_more	2026-06-05 00:51:53.995192+01
26	products	0002_review	2026-06-11 03:26:27.889058+01
27	gamification	0001_initial	2026-06-11 03:28:51.482452+01
28	store	0001_initial	2026-06-11 03:30:25.041029+01
60	token_blacklist	0001_initial	2026-06-11 18:19:45.289965+01
61	token_blacklist	0002_outstandingtoken_jti_hex	2026-06-11 18:19:45.321055+01
62	token_blacklist	0003_auto_20171017_2007	2026-06-11 18:19:45.365207+01
63	token_blacklist	0004_auto_20171017_2013	2026-06-11 18:19:45.420699+01
64	token_blacklist	0005_remove_outstandingtoken_jti	2026-06-11 18:19:45.472131+01
65	token_blacklist	0006_auto_20171017_2113	2026-06-11 18:19:45.503118+01
66	token_blacklist	0007_auto_20171017_2214	2026-06-11 18:19:45.703423+01
67	token_blacklist	0008_migrate_to_bigautofield	2026-06-11 18:19:45.816419+01
68	token_blacklist	0010_fix_migrate_to_bigautofield	2026-06-11 18:19:45.915664+01
69	token_blacklist	0011_linearizes_history	2026-06-11 18:19:45.918063+01
70	token_blacklist	0012_alter_outstandingtoken_user	2026-06-11 18:19:45.964208+01
71	token_blacklist	0013_alter_blacklistedtoken_options_and_more	2026-06-11 18:19:45.995988+01
72	products	0003_product_is_free_shipping_product_old_price_tnd	2026-06-12 01:40:21.297647+01
73	products	0004_product_brand_product_pack_size_product_reference_and_more	2026-06-20 02:14:10.334677+01
74	products	0005_product_specs_raw	2026-06-20 02:22:58.405275+01
75	products	0006_product_delivery_days_product_shipping_price_tnd	2026-06-20 22:07:14.704086+01
76	products	0007_reviewphoto	2026-06-20 23:00:47.368803+01
77	orders	0002_cartitem	2026-06-26 04:30:13.522702+01
78	orders	0003_alter_cartitem_options	2026-06-27 01:26:27.125493+01
79	users	0003_user_last_seen	2026-06-27 01:26:27.195432+01
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.messages (id, content, attachment_url, is_read, created_at, conversation_id, sender_id) FROM stdin;
0f37f892-2196-4523-9cc0-8427021cb560	Asleeema		f	2026-06-26 16:27:01.830586+01	0fb8205c-f32d-47eb-9c2e-9c96c709c886	a53de944-cff5-411a-8da5-cf68296311ef
678de4f5-58da-4786-8c56-b998de7973a3	Asleema		f	2026-06-26 16:27:20.385611+01	6ce2dd02-7fd9-45f0-8cf4-3c6fa485c6d8	a53de944-cff5-411a-8da5-cf68296311ef
4cbbf571-a730-48a3-9b0f-d9b869b93c71	Cc		f	2026-06-26 16:34:00.69546+01	6ce2dd02-7fd9-45f0-8cf4-3c6fa485c6d8	a53de944-cff5-411a-8da5-cf68296311ef
e7ab2731-7511-408c-8c72-0d2bf69ddd9c	Coucou		f	2026-06-26 16:35:31.137561+01	e65ef6bf-2c66-445b-9e94-79286b1c9c19	a53de944-cff5-411a-8da5-cf68296311ef
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notifications (id, type, title, body, data, channel, is_read, sent_at, user_id) FROM stdin;
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.order_items (id, quantity, unit_price_tnd, total_tnd, product_id, sub_order_id) FROM stdin;
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orders (id, status, payment_status, payment_method, total_tnd, discount_tnd, shipping_address, notes, created_at, updated_at, buyer_id) FROM stdin;
\.


--
-- Data for Name: product_images; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product_images (id, url, is_primary, sort_order, product_id) FROM stdin;
ee1f106d-9926-4cac-aedd-6dc6ef417366	https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&q=80	t	1	e6eb1b81-d3ac-473e-9d18-b66ecc9fc6d2
c98432c4-9f20-4546-a410-e10fe62c7961	https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=600&q=80	f	2	e6eb1b81-d3ac-473e-9d18-b66ecc9fc6d2
71417a9b-a943-481d-bf36-ffcb8cc00499	https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=600&q=80	f	3	e6eb1b81-d3ac-473e-9d18-b66ecc9fc6d2
ac215b9e-bce0-490b-98d5-8d03de4371b0	https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=600&q=80	t	1	3378bc0d-8c6f-4fff-8b0e-be5f3f7309d4
f99472db-d59d-4b98-a2e5-dbc32c320735	https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&q=80	f	2	3378bc0d-8c6f-4fff-8b0e-be5f3f7309d4
cb4955e5-6400-4de1-89dc-b9f600ce6af3	https://images.unsplash.com/photo-1511920170033-f8396924c348?w=600&q=80	f	3	3378bc0d-8c6f-4fff-8b0e-be5f3f7309d4
0004652a-bf49-4058-8f63-14158c27a119	https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80	t	1	ee163980-a0ff-4c27-994f-4bbcd5efa85a
bcdab872-1174-4913-9ee3-a736c01a67ca	https://images.unsplash.com/photo-1484704849700-f032a568e944?w=600&q=80	f	2	ee163980-a0ff-4c27-994f-4bbcd5efa85a
73f94c13-2c37-467a-bda9-141c499f3823	https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=600&q=80	f	3	ee163980-a0ff-4c27-994f-4bbcd5efa85a
ee8cc34b-6b20-48b5-8a8d-1466d44b42a1	https://images.unsplash.com/photo-1607006344380-b6775a0824a7?w=600&q=80	t	1	637623a1-d8af-4fc5-a62d-b05e184f08a8
b231e78e-a626-4aa5-889e-d9f0b3cd8b78	https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&q=80	f	2	637623a1-d8af-4fc5-a62d-b05e184f08a8
c94e2f5c-60a2-47ef-ba98-f785698b683f	https://images.unsplash.com/photo-1620756236308-65c3ef5d25f3?w=600&q=80	f	3	637623a1-d8af-4fc5-a62d-b05e184f08a8
36724fbb-9b51-4db2-8dd7-a0f6a41f0d9c	https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&q=80	t	1	8a7e67ad-5a36-4ba0-afdf-a6e475dd357d
99047406-9960-4a33-91c2-db0156982b4e	https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600&q=80	f	2	8a7e67ad-5a36-4ba0-afdf-a6e475dd357d
45055efb-4ab6-49bd-b1ba-d0bf107f51d4	https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600&q=80	t	1	87e973ef-65a0-4f50-8667-49a5cf02087b
b7a9c8f3-4036-49ae-9cbb-7481ebbc8e3a	https://images.unsplash.com/photo-1583623025817-d180a2221d0a?w=600&q=80	f	2	87e973ef-65a0-4f50-8667-49a5cf02087b
fde90053-b7c6-4c65-bcf4-1ffd4e3c0f1b	https://images.unsplash.com/photo-1526947425960-945c6e72858f?w=600&q=80	t	1	bfb9ce0c-14fe-4106-986d-8d208ab47e78
d35c8683-bc48-4028-b259-215ab9d34e4d	https://images.unsplash.com/photo-1585751119414-ef2636f8aede?w=600&q=80	f	2	bfb9ce0c-14fe-4106-986d-8d208ab47e78
36cb799e-4bd8-4598-a658-3c44a4f18e1d	https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80	t	1	9e06fd4e-7238-4d3a-8845-b85de7cb8118
2a34b0f0-3439-44a6-b1e5-a55c014a5d3d	https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=600&q=80	f	2	9e06fd4e-7238-4d3a-8845-b85de7cb8118
fb883444-fbc8-4cfc-967c-dd5bf6399d11	https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=600&q=80	t	1	65be765e-5ae8-4779-ac8a-13ad49afaa50
46c83e8a-323f-4136-bdab-31b008e033ab	https://images.unsplash.com/photo-1503602642458-232111445657?w=600&q=80	f	2	65be765e-5ae8-4779-ac8a-13ad49afaa50
e9332505-1bf4-43f7-b969-427e9aee5b95	https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&q=80	t	1	e71933ea-6a63-4693-8782-d2eb54ac73f0
b7f4bc66-a310-430c-be85-2f770802c0ff	https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&q=80	f	2	e71933ea-6a63-4693-8782-d2eb54ac73f0
3c3d8713-0782-43f1-b6ec-6a555936fc2d	https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&q=80	t	1	ec1782fa-3cd9-454d-a6e5-b81b8d920db1
22d8e64d-0e65-4ddf-bcbd-b9d5ad1e516f	https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600&q=80	f	2	ec1782fa-3cd9-454d-a6e5-b81b8d920db1
2809461e-fa48-458f-a513-04e6b9bb63d1	https://images.unsplash.com/photo-1609780447631-05b93e5a3e48?w=600&q=80	t	1	aab28161-86d1-4d13-8b10-817204428d94
017f8a57-edf2-4659-a78c-c2786a32639b	https://images.unsplash.com/photo-1548848221-0c2e497ed557?w=600&q=80	f	2	aab28161-86d1-4d13-8b10-817204428d94
5b73d0cc-5529-4359-a787-b5cd21609026	https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&q=80	t	1	8dc49f35-b8bc-43af-980e-42103095575b
807614c0-bb48-422d-a8d7-484969a9b095	https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=600&q=80	f	2	8dc49f35-b8bc-43af-980e-42103095575b
1af6d8f6-c7e5-4476-90ad-964063d77366	https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&q=80	t	1	e76526d9-ad5a-4fbe-bb26-6716ece7b75b
7166f91b-64cb-4bf2-add4-a8fa0727b95e	https://images.unsplash.com/photo-1523362628745-0c100150b504?w=600&q=80	f	2	e76526d9-ad5a-4fbe-bb26-6716ece7b75b
e82fb33f-3a8f-4de0-bd3e-a1b20a4fdb71	https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600&q=80	t	1	9546c507-7b6b-48fa-8815-538a1639c010
83a157a9-2aa2-46b5-af06-bfdba3ac9517	https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&q=80	f	2	9546c507-7b6b-48fa-8815-538a1639c010
0c8afab3-8dfd-4fb9-826b-6e9d35d6991c	https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&q=80	t	1	a5938b3e-b357-4d35-9677-b4cc1278ec94
3600b534-2c7a-4248-8f54-5af3e6e9cc3d	https://images.unsplash.com/photo-1583947581924-860bda6a26df?w=600&q=80	f	2	a5938b3e-b357-4d35-9677-b4cc1278ec94
8e6a4cc1-302c-49e7-82ec-ead06aa14c46	https://images.unsplash.com/photo-1583339793403-3d9b001b6008?w=600&q=80	t	1	90ac3559-cd27-446a-9d10-e88de14053e5
4989f914-9282-4e69-91f5-d32b1165ec79	https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=600&q=80	f	2	90ac3559-cd27-446a-9d10-e88de14053e5
289f8bc3-be2f-442e-93ec-ddef6c4cf8fb	https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=600&q=80	t	1	dd386452-bd16-411b-b93e-58c1cab21ec8
306dc1fa-793f-4ca8-8c96-012cd63b1d32	https://images.unsplash.com/photo-1598032895397-b9472444bf93?w=600&q=80	f	2	dd386452-bd16-411b-b93e-58c1cab21ec8
7b8edde8-1358-4d6c-8997-5738e2e5110c	https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80	t	1	b2b669bf-2de5-452b-bd5c-3a67ad3fbfc6
3e7d629f-e2b0-4403-9e40-86922d51e11c	https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=600&q=80	f	2	b2b669bf-2de5-452b-bd5c-3a67ad3fbfc6
ba2eb32d-c6f1-418e-986c-fd681d236920	https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&q=80	t	0	4d754241-9ff6-4027-a2a5-b8a82c98a424
1e8a0ee8-c50b-462d-a0fb-cad52ea24101	https://images.unsplash.com/photo-1591290619762-c2e9c8de9d09?w=600&q=80	f	1	4d754241-9ff6-4027-a2a5-b8a82c98a424
7bad7827-386f-47f3-a08a-9532c340b68b	https://images.unsplash.com/photo-1622957461293-1cfb0b1d4c79?w=600&q=80	f	2	4d754241-9ff6-4027-a2a5-b8a82c98a424
\.


--
-- Data for Name: product_interactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product_interactions (id, event_type, created_at, product_id, user_id) FROM stdin;
5e3fb7ae-932e-4f1d-9254-a2ff8dfbccc2	view	2026-06-20 02:58:12.226194+01	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	0d8aca23-b2b0-459b-bf8c-43bfd268b430
540724ec-6a1b-461e-b9d9-a66b9e671e81	view	2026-06-20 02:58:12.482271+01	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	0d8aca23-b2b0-459b-bf8c-43bfd268b430
abbf262a-996c-4ff5-bdf4-2ea51ca39e24	view	2026-06-20 21:32:50.327479+01	ec1782fa-3cd9-454d-a6e5-b81b8d920db1	0d8aca23-b2b0-459b-bf8c-43bfd268b430
0b2a315f-c2cc-4f51-b5a3-cb7139062bfc	view	2026-06-20 21:32:50.557539+01	ec1782fa-3cd9-454d-a6e5-b81b8d920db1	0d8aca23-b2b0-459b-bf8c-43bfd268b430
0f64881c-86e5-4471-a4ef-0533b98817f4	view	2026-06-20 21:40:14.814635+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
de6c82d2-659b-48ed-b52c-7fa30ca72d3e	view	2026-06-20 21:40:15.111377+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
13d20fd8-7afe-42f0-a8da-37ac918a1413	view	2026-06-20 22:08:29.45197+01	ec1782fa-3cd9-454d-a6e5-b81b8d920db1	0d8aca23-b2b0-459b-bf8c-43bfd268b430
5399768a-fd76-402a-8312-c1f25a699e65	view	2026-06-20 22:08:29.709422+01	ec1782fa-3cd9-454d-a6e5-b81b8d920db1	0d8aca23-b2b0-459b-bf8c-43bfd268b430
de3f6304-6bd9-4fe5-93df-98f8fd5367b9	view	2026-06-20 22:08:35.805659+01	ec1782fa-3cd9-454d-a6e5-b81b8d920db1	0d8aca23-b2b0-459b-bf8c-43bfd268b430
87a7de37-26b5-4f46-ab86-96cbff0a58c8	view	2026-06-20 22:08:35.976598+01	ec1782fa-3cd9-454d-a6e5-b81b8d920db1	0d8aca23-b2b0-459b-bf8c-43bfd268b430
a554d9be-e58e-453b-a496-5864f1f5d590	view	2026-06-20 22:09:04.447112+01	ec1782fa-3cd9-454d-a6e5-b81b8d920db1	0d8aca23-b2b0-459b-bf8c-43bfd268b430
9f1da189-4519-4668-867c-624d52f0a406	view	2026-06-20 22:09:04.635794+01	ec1782fa-3cd9-454d-a6e5-b81b8d920db1	0d8aca23-b2b0-459b-bf8c-43bfd268b430
5d5eb29d-9743-49b9-b699-82191f9bbffd	view	2026-06-20 22:09:30.922424+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
dd7be254-b0cb-4e0a-b866-ae756ef6a1b0	view	2026-06-20 22:09:31.065903+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
9e3ad2dd-e5c4-4ddd-a830-d6daefc53aa7	view	2026-06-20 22:09:54.06864+01	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	0d8aca23-b2b0-459b-bf8c-43bfd268b430
a1a924ba-3298-4097-8486-fafd2afa09b7	view	2026-06-20 22:09:54.209379+01	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	0d8aca23-b2b0-459b-bf8c-43bfd268b430
e5a0d5af-7f70-4d3e-b786-577276cb08f7	view	2026-06-20 22:12:23.222869+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
41606f55-3358-4eb6-9099-672e82d5ddb8	view	2026-06-20 22:12:23.312348+01	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	0d8aca23-b2b0-459b-bf8c-43bfd268b430
16771af2-abf7-4ae2-8f13-750ccd2913eb	view	2026-06-20 22:12:23.482141+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
a0485d57-4d93-46e6-9af0-a8b9dc7cfc77	view	2026-06-20 22:12:23.513733+01	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	0d8aca23-b2b0-459b-bf8c-43bfd268b430
5e8b7903-f6ec-4795-b490-cc503d07aecb	view	2026-06-20 22:12:30.858528+01	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	0d8aca23-b2b0-459b-bf8c-43bfd268b430
68200ae4-ef70-473e-bc40-eb510a17bef8	view	2026-06-20 22:12:31.091672+01	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	0d8aca23-b2b0-459b-bf8c-43bfd268b430
23e27031-6c75-4ee0-9884-1237c65c0e42	view	2026-06-20 22:13:18.691318+01	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	0d8aca23-b2b0-459b-bf8c-43bfd268b430
1511c10e-9f8d-41bf-a40f-e7b4f9374e63	view	2026-06-20 22:13:18.966353+01	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	0d8aca23-b2b0-459b-bf8c-43bfd268b430
c27985c0-ad18-4270-9341-1e2538e1652c	view	2026-06-20 23:17:58.34544+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
fec1f8d6-6879-44a5-9c33-7efd994e1014	view	2026-06-20 23:17:58.522222+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
6f17b2ea-72da-4ebd-aeb8-d029974cce25	view	2026-06-20 23:24:19.494424+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
abeaac78-9ef8-41b8-abb4-2beb07dc6b8c	view	2026-06-20 23:24:19.648773+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
9be258a5-9e32-43e5-9fd4-17432bc5b9e6	view	2026-06-20 23:33:39.346319+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
3de21027-a2d7-4934-a5d1-337b1ccdf15b	view	2026-06-20 23:33:39.592884+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
33216d4a-cdda-4832-8f17-5467a5a23b3c	view	2026-06-20 23:34:14.859464+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
7602d492-6460-4142-8de2-899c1fc5b399	view	2026-06-20 23:34:15.005762+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
0ba1d3b9-4604-4846-b510-a0619129bc30	view	2026-06-20 23:37:44.294175+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
05496255-b99b-49b3-b76d-d8026983609d	view	2026-06-20 23:37:44.312654+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
a61ac54d-659a-4e82-8720-ada4d11e0be2	view	2026-06-20 23:37:44.589489+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
d3cce6e4-174a-4389-90dd-da4f25a71f8b	view	2026-06-20 23:37:44.604697+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
16dd3af0-38cf-4a80-8b15-578e1321a2d5	view	2026-06-20 23:37:49.553502+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
99d7cfb6-82b0-461e-99b6-02ea1392cb8f	view	2026-06-20 23:37:49.726854+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
323f91d2-a969-48d2-9214-d0cc80a8c1c4	view	2026-06-20 23:38:10.362477+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
1cc364d9-df40-4c26-8ec4-76a1768c4df9	view	2026-06-20 23:38:10.591407+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
3aeb45b1-018b-477d-88a2-de4b4ac72283	view	2026-06-20 23:38:15.069701+01	b2b669bf-2de5-452b-bd5c-3a67ad3fbfc6	0d8aca23-b2b0-459b-bf8c-43bfd268b430
9c9c85de-0e4a-4a9f-a0a2-bb50dffc8e2d	view	2026-06-20 23:38:15.293881+01	b2b669bf-2de5-452b-bd5c-3a67ad3fbfc6	0d8aca23-b2b0-459b-bf8c-43bfd268b430
c7b07315-7ca9-498e-951f-b483cc7d8044	view	2026-06-23 20:56:37.819304+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	a53de944-cff5-411a-8da5-cf68296311ef
e9e44e28-7f52-4f2d-9d84-79781ca97601	view	2026-06-23 20:56:38.086055+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	a53de944-cff5-411a-8da5-cf68296311ef
95816c7f-8581-436b-bcee-5f6e29051100	view	2026-06-23 20:56:48.042711+01	90ac3559-cd27-446a-9d10-e88de14053e5	a53de944-cff5-411a-8da5-cf68296311ef
6c84056d-97ee-4432-affb-f57e6cf8ace0	view	2026-06-23 20:56:48.188124+01	90ac3559-cd27-446a-9d10-e88de14053e5	a53de944-cff5-411a-8da5-cf68296311ef
c6ed55b3-934d-401b-8223-6998bbeae729	view	2026-07-07 02:05:22.156911+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
433e53de-b5a7-4c21-a9f5-da45eb909373	view	2026-07-07 02:05:22.428217+01	ee163980-a0ff-4c27-994f-4bbcd5efa85a	0d8aca23-b2b0-459b-bf8c-43bfd268b430
a26521d0-3a13-45cc-ace7-4fae08572788	view	2026-07-09 15:51:30.087527+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	0d8aca23-b2b0-459b-bf8c-43bfd268b430
cbea5d92-e008-4756-acf8-160288e4dfcc	view	2026-07-11 16:25:04.806588+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	a53de944-cff5-411a-8da5-cf68296311ef
acba3d7f-bb8e-4660-b4b8-754c0740bf0c	view	2026-07-11 16:25:05.004257+01	4d754241-9ff6-4027-a2a5-b8a82c98a424	a53de944-cff5-411a-8da5-cf68296311ef
\.


--
-- Data for Name: product_price_tiers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product_price_tiers (id, min_qty, max_qty, price_tnd, product_id) FROM stdin;
bf2cdecf-a908-4754-83c0-8a798f797877	50	99	18.500	4d754241-9ff6-4027-a2a5-b8a82c98a424
a9deec7d-4b2e-47a3-8081-6c91f2d0298a	100	299	16.900	4d754241-9ff6-4027-a2a5-b8a82c98a424
ffd39d60-812f-4d9c-a6b2-04b4bbba1404	300	\N	14.750	4d754241-9ff6-4027-a2a5-b8a82c98a424
\.


--
-- Data for Name: product_variants; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product_variants (id, name, image_url, sort_order, product_id) FROM stdin;
ca4d9e5e-f49f-49af-8717-65277391bede	Blanc		0	4d754241-9ff6-4027-a2a5-b8a82c98a424
3b777590-e74f-4366-b8e2-4cf1852d2247	Noir		1	4d754241-9ff6-4027-a2a5-b8a82c98a424
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.products (id, name, slug, description, sku, unit, moq, base_price_tnd, video_url, stock_qty, sold_count, view_count, rating_avg, rating_count, status, badge_choice, badge_flash, badge_flash_end, created_at, updated_at, category_id, supplier_id, is_free_shipping, old_price_tnd, brand, pack_size, reference, specs_raw, delivery_days, shipping_price_tnd) FROM stdin;
a5938b3e-b357-4d35-9677-b4cc1278ec94	Gel hydroalcoolique 500ml · carton x48	gel-hydroalcoolique-500ml	Gel hydroalcoolique 70% d alcool. Formule enrichie en aloe vera. Parfum neutre.	GEL-001	unité	48	3.200		1200	4500	9	5.00	1	approved	f	f	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0003-0003-0003-000000000003	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	t	5.500		1			3	0.000
8dc49f35-b8bc-43af-980e-42103095575b	Crème hydratante visage 50ml · carton x36	creme-hydratante-50ml	Crème hydratante enrichie en aloe vera et vitamine E. Tous types de peau. Sans paraben.	CRM-001	unité	36	5.900		700	890	0	5.00	1	approved	f	f	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0005-0005-0005-000000000005	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	f	9.000		1			3	0.000
8a7e67ad-5a36-4ba0-afdf-a6e475dd357d	Tapis de yoga antidérapant · lot x10	tapis-yoga-antiderapant	Tapis de yoga en TPE écologique 6mm. Surface antidérapante double face. 183x61cm.	TAP-001	pièce	10	18.500		250	480	5	4.50	2	approved	t	f	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0006-0006-0006-000000000006	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	f	28.000		1			3	0.000
637623a1-d8af-4fc5-a62d-b05e184f08a8	Savon surgras karité 100g · carton x48	savon-surgras-karite	Savon naturel surgras au beurre de karité. Sans paraben. Idéal peaux sensibles.	SAV-003	pièce	48	2.800		600	1800	0	3.00	1	approved	t	f	\N	2026-06-12 01:51:09.819609+01	2026-06-12 01:51:09.819609+01	a1b2c3d4-0003-0003-0003-000000000003	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	t	4.500		1			3	0.000
87e973ef-65a0-4f50-8667-49a5cf02087b	Harissa traditionnelle 200g · carton x24	harissa-traditionnelle-200g	Harissa tunisienne traditionnelle préparée selon recette artisanale. Piments rouges sélectionnés.	HAR-001	pot	24	3.500		800	2700	1	4.50	2	approved	t	f	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0002-0002-0002-000000000002	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	t	\N		1			3	0.000
ee163980-a0ff-4c27-994f-4bbcd5efa85a	Écouteurs Bluetooth 5.0 · lot x20	ecouteurs-bluetooth-5	Écouteurs sans fil avec réduction de bruit active. Autonomie 8h. Compatible iOS et Android.	ECO-002	pièce	20	12.500		150	980	15	4.50	2	approved	f	t	\N	2026-06-12 01:51:09.819609+01	2026-06-12 01:51:09.819609+01	a1b2c3d4-0001-0001-0001-000000000001	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	f	18.000		1			3	0.000
aab28161-86d1-4d13-8b10-817204428d94	Dattes Deglet Nour 1kg · carton x24	dattes-deglet-nour-1kg	Dattes Deglet Nour premium de Tozeur. Calibre extra. Conditionnement sous vide.	DAT-001	kg	24	14.500		500	3100	0	4.00	1	approved	t	f	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0002-0002-0002-000000000002	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	t	\N		1			3	0.000
e76526d9-ad5a-4fbe-bb26-6716ece7b75b	Bouteille sport inox 750ml · lot x24	bouteille-sport-inox-750ml	Bouteille isotherme en acier inoxydable 750ml. Maintient chaud 12h froid 24h.	BTL-001	pièce	24	9.800		350	670	10	4.00	2	approved	f	t	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0006-0006-0006-000000000006	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	f	15.000		1			3	0.000
9546c507-7b6b-48fa-8815-538a1639c010	Poêle antiadhésive 28cm · lot x12	poele-antiadhesive-28cm	Poêle antiadhésive en aluminium forgé. Revêtement PFOA free. Compatible induction.	POE-001	pièce	12	22.000		200	430	0	4.00	1	approved	f	f	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0007-0007-0007-000000000007	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	t	34.000		1			3	0.000
ec1782fa-3cd9-454d-a6e5-b81b8d920db1	Chargeur rapide USB-C 65W · lot x50	chargeur-usb-c-65w	Chargeur rapide 65W compatible tous appareils USB-C. Câble inclus. Certifié CE.	CHG-001	pièce	50	7.200		800	2200	22	3.00	1	approved	t	t	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0001-0001-0001-000000000001	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	t	12.000		1			3	0.000
dd386452-bd16-411b-b93e-58c1cab21ec8	Polo homme coton piqué · lot x24	polo-homme-coton-pique	Polo homme 100% coton piqué 220g. Col boutonné. Coloris variés. Tailles S-3XL.	PLO-001	pièce	24	6.800		600	1200	0	4.00	1	approved	t	f	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	9f2bba15-be85-4c8c-bf01-3d353bd63d13	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	f	11.000		1			3	0.000
b2b669bf-2de5-452b-bd5c-3a67ad3fbfc6	Montre connectée sport · lot x10	montre-connectee-sport	Montre connectée étanche IP68. Suivi activité cardiaque sommeil GPS. Autonomie 7 jours.	MON-001	pièce	10	45.000		120	340	2	4.00	2	approved	t	t	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0001-0001-0001-000000000001	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	f	68.000		1			3	0.000
90ac3559-cd27-446a-9d10-e88de14053e5	Stylos bille bleu · boîte x100	stylos-bille-bleu-x100	Stylos bille écriture fluide. Encre bleue longue durée. Grip antidérapant.	STY-001	pièce	100	0.450		5000	8900	25	5.00	2	approved	f	f	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0008-0008-0008-000000000008	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	f	\N		1			3	0.000
bfb9ce0c-14fe-4106-986d-8d208ab47e78	Shampoing argan 400ml · carton x24	shampoing-argan-400ml	Shampoing à l huile d argan du Maroc. Nourrit et répare les cheveux abîmés.	SHA-001	unité	24	7.500		450	760	6	5.00	1	approved	f	t	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0005-0005-0005-000000000005	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	f	11.000		1			3	0.000
9e06fd4e-7238-4d3a-8845-b85de7cb8118	Voiture télécommandée · lot x6	voiture-telecommandee-lot	Voiture télécommandée 4x4 tout terrain. Portée 50m. Autonomie 30min. Dès 6 ans.	JOU-001	pièce	6	28.000		80	190	0	4.50	2	approved	f	f	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0009-0009-0009-000000000009	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	f	42.000		1			3	0.000
65be765e-5ae8-4779-ac8a-13ad49afaa50	Chaise plastique empilable · lot x20	chaise-plastique-empilable	Chaise en polypropylène résistante UV. Empilable. Usage intérieur et extérieur. 150kg max.	CHA-001	pièce	20	12.000		300	520	0	5.00	2	approved	f	f	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	a1b2c3d4-0004-0004-0004-000000000004	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	t	\N		1			3	0.000
4d754241-9ff6-4027-a2a5-b8a82c98a424	Chargeur rapide USB-C 65W	chargeur-rapide-usb-c-65w-lot-x50	Chargeur rapide USB-C 65W compatible avec la majorité des smartphones, tablettes et laptops compacts. Technologie GaN pour une charge rapide et un encombrement réduit. Vendu en lot de 50 unités, idéal pour revendeurs et boutiques d'accessoires.	CHG-USBC-65W	pièce	50	18.500		850	1240	52	5.00	1	approved	t	f	\N	2026-06-20 21:38:49.705104+01	2026-06-20 21:38:49.706205+01	a1b2c3d4-0001-0001-0001-000000000001	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	t	22.000	PowerMax	50	PM-GAN65-2026	Puissance: 65W\nTechnologie: GaN (Gallium Nitride)\nPorts: 1x USB-C PD\nCompatibilité: Smartphones, tablettes, laptops compacts\nEntrée: 100-240V ~50/60Hz\nSortie: 5V/3A · 9V/3A · 12V/3A · 15V/3A · 20V/3.25A\nProtection: Surchauffe, surtension, court-circuit\nGarantie: 12 mois	3	0.000
3378bc0d-8c6f-4fff-8b0e-be5f3f7309d4	Café arabica torréfié 1kg · carton x12	cafe-arabica-1kg	Café arabica 100% tunisien torréfié artisanalement. Arômes intenses et corsés.	CAF-001	kg	12	18.900		300	2400	5	4.00	1	approved	t	f	\N	2026-06-12 01:51:09.819609+01	2026-06-12 01:51:09.819609+01	a1b2c3d4-0002-0002-0002-000000000002	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	t	26.000		1			3	0.000
e6eb1b81-d3ac-473e-9d18-b66ecc9fc6d2	T-shirt coton 180g	t-shirt-coton-180g	T-shirt coton de qualité supérieure	TSH-001	pièce	50	4.200		500	150	0	5.00	2	approved	f	f	\N	2026-06-11 19:52:40.039647+01	2026-06-11 19:52:40.039647+01	9f2bba15-be85-4c8c-bf01-3d353bd63d13	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	f	\N		1			3	0.000
e71933ea-6a63-4693-8782-d2eb54ac73f0	Jeans slim coton stretch · lot x30	jeans-slim-coton-x30	Jeans slim stretch 98% coton 2% elasthanne. Tailles 38-48. Coloris bleu indigo.	JNS-001	pièce	30	8.500		400	1500	3	3.00	1	approved	t	f	\N	2026-06-12 02:17:00.222362+01	2026-06-12 02:17:00.222362+01	9f2bba15-be85-4c8c-bf01-3d353bd63d13	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	f	14.000		1			3	0.000
\.


--
-- Data for Name: quotes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quotes (id, quantity, message, status, quote_tnd, valid_until, created_at, buyer_id, product_id, supplier_id) FROM stdin;
\.


--
-- Data for Name: review_photos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.review_photos (id, url, sort_order, review_id) FROM stdin;
c0b6be4b-ba14-4b09-b4f3-241c7c3edd04	https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=400&q=70	0	0f83bbc1-e656-4cce-a57a-f2afebe237a8
947cebc9-b28e-4e2d-9c4c-b4db8f565c8b	https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=70	1	0f83bbc1-e656-4cce-a57a-f2afebe237a8
a0c773b0-fa7c-4a2c-ac26-af2af23dc765	https://images.unsplash.com/photo-1622957461293-1cfb0b1d4c79?w=400&q=70	2	0f83bbc1-e656-4cce-a57a-f2afebe237a8
6cffa397-ec44-4092-8bc0-aa74acb2069a	https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=70	0	8b4697e2-3745-40d4-8623-efb91c1cb986
5291f9b4-6fe1-46c0-b571-7ea7cf95d351	https://images.unsplash.com/photo-1591290619762-c2e9c8de9d09?w=400&q=70	0	92154cc1-7787-4809-84e3-1852bdbe5721
8f0ebf67-0d56-407a-a795-d74ed139d99a	https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=70	1	92154cc1-7787-4809-84e3-1852bdbe5721
634b07ed-f6cc-4b9f-b2c8-2f16384b6075	https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=70	0	e5ebc52d-dcac-47b1-a291-89bc5afb8570
29b30bc3-6443-49e0-86f9-ad6f976c8881	https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=400&q=70	1	e5ebc52d-dcac-47b1-a291-89bc5afb8570
8cdbcb12-313e-47c2-a214-8bd152707830	https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=70	2	e5ebc52d-dcac-47b1-a291-89bc5afb8570
15b1f9a7-60a4-43eb-ae91-9ce0d6fe3770	https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=70	0	d35bd387-0b2f-48fb-8031-1f80d046213e
b19a35a1-56eb-4c21-a166-fca9d6cd5828	https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=70	1	d35bd387-0b2f-48fb-8031-1f80d046213e
d21f0ef8-db49-4d77-a158-1543ac2e31d1	https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=400&q=70	0	25ea55fb-33d0-49ed-9067-90ed23113506
a97ab3cc-8ad6-4118-a9bf-f9c68fec1fc2	https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=400&q=70	0	f5ee91ad-2b6f-4ed5-bad7-8378d71d2313
2230d688-6088-4a01-868d-f3b26f3ad1d0	https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=400&q=70	0	ec64a192-fd61-441f-8b79-db215cf1d69d
443a84f4-dfad-4391-88d1-0e23580e5a0a	https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=70	1	ec64a192-fd61-441f-8b79-db215cf1d69d
0b7770f8-b6ca-4a5b-8763-82fb6ad5444c	https://images.unsplash.com/photo-1591290619762-c2e9c8de9d09?w=400&q=70	2	ec64a192-fd61-441f-8b79-db215cf1d69d
87c60744-358d-4ea2-9de6-d06c5ce8ca2d	https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=70	0	28044fa5-f63b-4173-a016-9aaeb446a605
7b42367c-c378-4165-acba-63c02f8157bf	https://images.unsplash.com/photo-1591290619762-c2e9c8de9d09?w=400&q=70	0	0221557a-d1ae-4690-8c7e-848601352ef4
3b4ddda1-2cb0-4428-a169-cc26ea5705b8	https://images.unsplash.com/photo-1591290619762-c2e9c8de9d09?w=400&q=70	0	e8f11262-38ec-4565-8674-f60110934e58
5294c96b-180d-43ef-82c4-5c4cc4710dc5	https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=70	1	e8f11262-38ec-4565-8674-f60110934e58
d6c8a585-d777-459c-986d-f41cfc2a287a	https://images.unsplash.com/photo-1622957461293-1cfb0b1d4c79?w=400&q=70	2	e8f11262-38ec-4565-8674-f60110934e58
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reviews (id, rating, comment, created_at, order_id, product_id, reviewer_id, supplier_id, variant_id) FROM stdin;
0f83bbc1-e656-4cce-a57a-f2afebe237a8	5	Excellent produit, exactement comme dÃ©crit. Livraison rapide et emballage soignÃ©. Je recommande vivement ce fournisseur.	2026-06-20 23:06:49.611805+01	\N	e6eb1b81-d3ac-473e-9d18-b66ecc9fc6d2	a53de944-cff5-411a-8da5-cf68296311ef	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	\N
8087e54e-7af5-44a6-ad2d-83b301f6038d	5	Parfait pour mon commerce, j'en ai commandÃ© plusieurs fois dÃ©jÃ . QualitÃ© constante, fournisseur sÃ©rieux.	2026-06-20 23:33:13.817468+01	\N	e6eb1b81-d3ac-473e-9d18-b66ecc9fc6d2	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
ef219062-c7c5-4a2b-9dd8-1ea1726f2df5	4	Bon rapport qualitÃ©-prix. Quelques jours de dÃ©lai en plus que prÃ©vu mais le rÃ©sultat en vaut la peine.	2026-06-20 23:33:13.824994+01	\N	3378bc0d-8c6f-4fff-8b0e-be5f3f7309d4	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
38c40057-a5fe-4c14-9515-94ff1cc1bf52	5	TrÃ¨s satisfait de mon achat. La qualitÃ© est au rendez-vous et le service client a Ã©tÃ© rÃ©actif tout au long du processus.	2026-06-20 23:33:13.828039+01	\N	8dc49f35-b8bc-43af-980e-42103095575b	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
8b4697e2-3745-40d4-8623-efb91c1cb986	4	Bon rapport qualitÃ©-prix. Quelques jours de dÃ©lai en plus que prÃ©vu mais le rÃ©sultat en vaut la peine.	2026-06-20 23:33:13.831078+01	\N	ee163980-a0ff-4c27-994f-4bbcd5efa85a	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
01438b39-e03c-4aaa-a6da-d4f6a0ee3c91	5	Excellent produit, exactement comme dÃ©crit. Livraison rapide et emballage soignÃ©. Je recommande vivement ce fournisseur.	2026-06-20 23:33:13.835329+01	\N	ee163980-a0ff-4c27-994f-4bbcd5efa85a	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
92154cc1-7787-4809-84e3-1852bdbe5721	3	Correct sans plus. Le produit fait le travail mais j'attendais un peu mieux niveau finition pour ce prix.	2026-06-20 23:33:13.838572+01	\N	637623a1-d8af-4fc5-a62d-b05e184f08a8	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
e5ebc52d-dcac-47b1-a291-89bc5afb8570	3	Correct sans plus. Le produit fait le travail mais j'attendais un peu mieux niveau finition pour ce prix.	2026-06-20 23:33:13.840592+01	\N	e71933ea-6a63-4693-8782-d2eb54ac73f0	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
d35bd387-0b2f-48fb-8031-1f80d046213e	3	Correct sans plus. Le produit fait le travail mais j'attendais un peu mieux niveau finition pour ce prix.	2026-06-20 23:33:13.843654+01	\N	ec1782fa-3cd9-454d-a6e5-b81b8d920db1	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
716d8052-65f7-4e91-be48-5da2a128ac36	4	Conforme Ã  la description, bon emballage. Je recommande pour les commandes en volume.	2026-06-20 23:33:13.847158+01	\N	aab28161-86d1-4d13-8b10-817204428d94	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
f35c1b93-b500-4b71-bffe-384aebad1471	3	Correct sans plus. Le produit fait le travail mais j'attendais un peu mieux niveau finition pour ce prix.	2026-06-20 23:33:13.850273+01	\N	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
d36d09c3-a2a9-4848-9555-7a989bd143e4	5	TrÃ¨s satisfait de mon achat. La qualitÃ© est au rendez-vous et le service client a Ã©tÃ© rÃ©actif tout au long du processus.	2026-06-20 23:33:13.853561+01	\N	e76526d9-ad5a-4fbe-bb26-6716ece7b75b	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
b206ed38-5183-42ba-bf42-3a1b6627dc43	4	Bon rapport qualitÃ©-prix. Quelques jours de dÃ©lai en plus que prÃ©vu mais le rÃ©sultat en vaut la peine.	2026-06-20 23:33:13.855587+01	\N	9546c507-7b6b-48fa-8815-538a1639c010	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
25ea55fb-33d0-49ed-9067-90ed23113506	5	Excellent produit, exactement comme dÃ©crit. Livraison rapide et emballage soignÃ©. Je recommande vivement ce fournisseur.	2026-06-20 23:33:13.858644+01	\N	a5938b3e-b357-4d35-9677-b4cc1278ec94	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
3fa901aa-65f9-4b53-b644-525936cb4a49	4	Bon rapport qualitÃ©-prix. Quelques jours de dÃ©lai en plus que prÃ©vu mais le rÃ©sultat en vaut la peine.	2026-06-20 23:33:13.861819+01	\N	dd386452-bd16-411b-b93e-58c1cab21ec8	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
1ec64c0e-8a74-475d-b42c-1f8a00902fc1	4	Bon rapport qualitÃ©-prix. Quelques jours de dÃ©lai en plus que prÃ©vu mais le rÃ©sultat en vaut la peine.	2026-06-20 23:33:13.864017+01	\N	b2b669bf-2de5-452b-bd5c-3a67ad3fbfc6	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
cab0ca8b-2c9b-462f-b048-d155004960ac	4	Bon rapport qualitÃ©-prix. Quelques jours de dÃ©lai en plus que prÃ©vu mais le rÃ©sultat en vaut la peine.	2026-06-20 23:33:13.867267+01	\N	b2b669bf-2de5-452b-bd5c-3a67ad3fbfc6	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
f5ee91ad-2b6f-4ed5-bad7-8378d71d2313	5	TrÃ¨s satisfait de mon achat. La qualitÃ© est au rendez-vous et le service client a Ã©tÃ© rÃ©actif tout au long du processus.	2026-06-20 23:33:13.870354+01	\N	87e973ef-65a0-4f50-8667-49a5cf02087b	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
ec64a192-fd61-441f-8b79-db215cf1d69d	4	Bon rapport qualitÃ©-prix. Quelques jours de dÃ©lai en plus que prÃ©vu mais le rÃ©sultat en vaut la peine.	2026-06-20 23:33:13.873755+01	\N	87e973ef-65a0-4f50-8667-49a5cf02087b	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
d24c87fe-4f59-4f9b-9f52-3b0a7a6c14c5	5	TrÃ¨s satisfait de mon achat. La qualitÃ© est au rendez-vous et le service client a Ã©tÃ© rÃ©actif tout au long du processus.	2026-06-20 23:33:13.876846+01	\N	bfb9ce0c-14fe-4106-986d-8d208ab47e78	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
cb2cc66a-f69c-4e3e-8689-84103f53ae50	4	Bon rapport qualitÃ©-prix. Quelques jours de dÃ©lai en plus que prÃ©vu mais le rÃ©sultat en vaut la peine.	2026-06-20 23:33:13.880102+01	\N	9e06fd4e-7238-4d3a-8845-b85de7cb8118	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
cdd32749-848d-47e3-86eb-803354ba9bf5	5	TrÃ¨s satisfait de mon achat. La qualitÃ© est au rendez-vous et le service client a Ã©tÃ© rÃ©actif tout au long du processus.	2026-06-20 23:33:13.882305+01	\N	9e06fd4e-7238-4d3a-8845-b85de7cb8118	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
1ba390ed-6e68-4518-81d7-dba613a051d1	5	Excellent produit, exactement comme dÃ©crit. Livraison rapide et emballage soignÃ©. Je recommande vivement ce fournisseur.	2026-06-20 23:33:13.885422+01	\N	65be765e-5ae8-4779-ac8a-13ad49afaa50	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
417963fc-acb7-4630-b868-1024db7e743c	5	Parfait pour mon commerce, j'en ai commandÃ© plusieurs fois dÃ©jÃ . QualitÃ© constante, fournisseur sÃ©rieux.	2026-06-20 23:33:13.890634+01	\N	65be765e-5ae8-4779-ac8a-13ad49afaa50	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
e12eee0a-9d4d-4cf9-8d3b-dfa9a1d6110c	5	Parfait pour mon commerce, j'en ai commandÃ© plusieurs fois dÃ©jÃ . QualitÃ© constante, fournisseur sÃ©rieux.	2026-06-20 23:33:13.895765+01	\N	8a7e67ad-5a36-4ba0-afdf-a6e475dd357d	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
28044fa5-f63b-4173-a016-9aaeb446a605	4	Bon rapport qualitÃ©-prix. Quelques jours de dÃ©lai en plus que prÃ©vu mais le rÃ©sultat en vaut la peine.	2026-06-20 23:33:13.900015+01	\N	8a7e67ad-5a36-4ba0-afdf-a6e475dd357d	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
568d7136-3013-4d6f-9ebb-c1bc9296f122	5	TrÃ¨s satisfait de mon achat. La qualitÃ© est au rendez-vous et le service client a Ã©tÃ© rÃ©actif tout au long du processus.	2026-06-20 23:33:13.90306+01	\N	4d754241-9ff6-4027-a2a5-b8a82c98a424	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
0221557a-d1ae-4690-8c7e-848601352ef4	5	Excellent produit, exactement comme dÃ©crit. Livraison rapide et emballage soignÃ©. Je recommande vivement ce fournisseur.	2026-06-20 23:33:13.905087+01	\N	90ac3559-cd27-446a-9d10-e88de14053e5	c2ccbfb5-283a-427d-a251-5595e80c60f9	\N	\N
e8f11262-38ec-4565-8674-f60110934e58	5	Excellent produit, exactement comme dÃ©crit. Livraison rapide et emballage soignÃ©. Je recommande vivement ce fournisseur.	2026-06-20 23:33:13.908139+01	\N	90ac3559-cd27-446a-9d10-e88de14053e5	a53de944-cff5-411a-8da5-cf68296311ef	\N	\N
\.


--
-- Data for Name: search_history; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.search_history (id, query, result_count, searched_at, user_id) FROM stdin;
\.


--
-- Data for Name: spin_prizes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.spin_prizes (id, label, prize_type, value_tnd, probability, color_hex, is_active) FROM stdin;
\.


--
-- Data for Name: sub_orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sub_orders (id, status, subtotal_tnd, delivery_type, created_at, updated_at, order_id, supplier_id) FROM stdin;
\.


--
-- Data for Name: subscription_plans; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.subscription_plans (id, name, price_tnd, commission_pct, max_products, features, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: supplier_documents; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.supplier_documents (id, doc_type, file_url, status, uploaded_at, supplier_id) FROM stdin;
\.


--
-- Data for Name: supplier_profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.supplier_profiles (id, company_name, slug, rc_number, tax_number, address, city, wilaya, min_order_tnd, verified_at, verification_status, rating_avg, rating_count, followers_count, created_at, user_id) FROM stdin;
b591f07a-6bbd-4d4e-83ef-a47e256d48a0	Sfax Textile Co.	sfax-textile-co				Sfax	Sfax	\N	\N	approved	4.50	10	50	2026-06-11 19:50:35.787437+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430
\.


--
-- Data for Name: supplier_store; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.supplier_store (id, logo_url, banner_url, description, certifications, page_views, response_rate, created_at, updated_at, supplier_id, founded_year, response_time_hrs) FROM stdin;
aa470c73-e8ae-4ef4-ad16-d5a17e724abe					0	0.00	2026-06-19 17:01:12.114236+01	2026-06-19 17:01:12.114236+01	b591f07a-6bbd-4d4e-83ef-a47e256d48a0	2018	\N
\.


--
-- Data for Name: supplier_subscriptions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.supplier_subscriptions (id, status, started_at, expires_at, created_at, changed_by_id, plan_id, supplier_id) FROM stdin;
\.


--
-- Data for Name: token_blacklist_blacklistedtoken; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.token_blacklist_blacklistedtoken (id, blacklisted_at, token_id) FROM stdin;
\.


--
-- Data for Name: token_blacklist_outstandingtoken; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.token_blacklist_outstandingtoken (id, token, created_at, expires_at, user_id, jti) FROM stdin;
1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4Mzc5MzI5MCwiaWF0IjoxNzgxMjAxMjkwLCJqdGkiOiI3ZmQ1YTM0OWE3N2E0YzFkYTZjM2Y5NjA3NDQ4MTkyZiIsInVzZXJfaWQiOiJkNWVjNjA0My1mOTNmLTQ2ZDctYjUwMC0yNDBiYWZhOTY0YjgifQ.L3BVLSOOIG72CIkf_Mn3f4fBekpMRKYts8b6CNKuOGM	2026-06-11 19:08:10.611133+01	2026-07-11 19:08:10+01	d5ec6043-f93f-46d7-b500-240bafa964b8	7fd5a349a77a4c1da6c3f9607448192f
2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA1MzIwNCwiaWF0IjoxNzgxNDQ4NDA0LCJqdGkiOiJjODEyNmU3NjJjMWY0YmNiOWNhMmNhZTE0OTYwOTY2NiIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.M2DB4AJbGJKnBA0bzHrWlUSUEde2whY1SbQMrJ9aSqs	2026-06-14 15:46:44.007133+01	2026-06-21 15:46:44+01	a53de944-cff5-411a-8da5-cf68296311ef	c8126e762c1f4bcb9ca2cae149609666
3	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA1MzY3MSwiaWF0IjoxNzgxNDQ4ODcxLCJqdGkiOiI3OWU2NTNiYmIzZWI0OTQ5OTgxYWNiMjI4NDlmMDBhOCIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.2P7kiO96_4ji53YEx-DUzAEZajE7_jL71K8SEDd3vys	2026-06-14 15:54:31.032989+01	2026-06-21 15:54:31+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	79e653bbb3eb4949981acb22849f00a8
4	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA1NjUzMCwiaWF0IjoxNzgxNDUxNzMwLCJqdGkiOiJjZjVhM2NlZGI3Y2E0MDIwYWUwOTQ4MmY4NjI4ZDNmZSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.Dd2nHSs7FihWn1zi2pFcsF7iur_2TZ6VgRBlD9cHbI0	2026-06-14 16:42:10.889171+01	2026-06-21 16:42:10+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	cf5a3cedb7ca4020ae09482f8628d3fe
5	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA1NjUzNSwiaWF0IjoxNzgxNDUxNzM1LCJqdGkiOiI0YzUxNzM5Y2FlMmE0MDJkOWY4YzMzNDkwOTIwMDcyNiIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.zo2BTr9Ef686YR4lLagGBIsNEZsFx2i4BolTeOq4Blc	2026-06-14 16:42:15.551575+01	2026-06-21 16:42:15+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	4c51739cae2a402d9f8c334909200726
6	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA1NjYwMiwiaWF0IjoxNzgxNDUxODAyLCJqdGkiOiI4NzkwYjAxZDU4YjU0OGM2YWNlNTU0Y2MxNjQ2MTI5OCIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.EiHwALe50ryuRaVwfQSalIs-Djt8RjP_p-5qJT-XFaI	2026-06-14 16:43:22.820294+01	2026-06-21 16:43:22+01	a53de944-cff5-411a-8da5-cf68296311ef	8790b01d58b548c6ace554cc16461298
7	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA1NzM4NSwiaWF0IjoxNzgxNDUyNTg1LCJqdGkiOiJkZWI2NDI0NGQ0NzQ0ZTgwYTZmZmFhY2U0OGFlNzk5ZiIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.n85Ark7X3WEa1RGtYxOFHhc-yys0-Wzz_UpKd98uvgI	2026-06-14 16:56:25.488075+01	2026-06-21 16:56:25+01	a53de944-cff5-411a-8da5-cf68296311ef	deb64244d4744e80a6ffaace48ae799f
8	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA3MDk5OCwiaWF0IjoxNzgxNDY2MTk4LCJqdGkiOiJmMzY0MjVhNDJlNzE0NTU3ODRiOTg5YWNhYTVlN2FjMiIsInVzZXJfaWQiOiIzOTI3NzYyNi00NzE3LTRhYjItOWYxYi0xODBjMWQzYzg0ZjEifQ.6zL5zQakXjoemT97R3VF-_5ToHQg22c05NcsRJXf1H8	2026-06-14 20:43:18.762354+01	2026-06-21 20:43:18+01	39277626-4717-4ab2-9f1b-180c1d3c84f1	f36425a42e71455784b989acaa5e7ac2
9	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA3MTUxMywiaWF0IjoxNzgxNDY2NzEzLCJqdGkiOiI1MGM2ZWJlNTNjOTY0ZTEzYTgzZGZjYWJjYjI5ZTAwNSIsInVzZXJfaWQiOiIzOTI3NzYyNi00NzE3LTRhYjItOWYxYi0xODBjMWQzYzg0ZjEifQ.kvHcjM8HH9QwQGSaZeiqm9OXrSv80TX6p_Az3leKdjU	2026-06-14 20:51:53.763503+01	2026-06-21 20:51:53+01	39277626-4717-4ab2-9f1b-180c1d3c84f1	50c6ebe53c964e13a83dfcabcb29e005
10	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA3MTY5MCwiaWF0IjoxNzgxNDY2ODkwLCJqdGkiOiI5M2FkNzQwYjcyMWM0NWQ1OGViY2Q2MDhiZmI5NjAxNiIsInVzZXJfaWQiOiIzOTI3NzYyNi00NzE3LTRhYjItOWYxYi0xODBjMWQzYzg0ZjEifQ.HCBldNWC-jOg3k5OFqncidNoGk09dt-Xr_nRDkvLtvQ	2026-06-14 20:54:50.657808+01	2026-06-21 20:54:50+01	39277626-4717-4ab2-9f1b-180c1d3c84f1	93ad740b721c45d58ebcd608bfb96016
11	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA3MTcxNywiaWF0IjoxNzgxNDY2OTE3LCJqdGkiOiJmNTFmZGYyYmIyMTc0ZjVkYmQyZjU3NGYxMTI2NjM2YyIsInVzZXJfaWQiOiIzOTI3NzYyNi00NzE3LTRhYjItOWYxYi0xODBjMWQzYzg0ZjEifQ.-ohCFfwDuxpg848YTsINFSkHgpEFqitvOg3F6KgTo0Q	2026-06-14 20:55:17.884297+01	2026-06-21 20:55:17+01	39277626-4717-4ab2-9f1b-180c1d3c84f1	f51fdf2bb2174f5dbd2f574f1126636c
12	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4NzY2NywiaWF0IjoxNzgxNDgyODY3LCJqdGkiOiJhOWE2ZjFmZWYzZjM0NjExYWJiMzZmYmE2ZGI3YjgzNSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.pGb3cz9MrUq_D2jZt40GOncqdRxhoDUXLEp22q0xmC0	2026-06-15 01:21:07.616783+01	2026-06-22 01:21:07+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	a9a6f1fef3f34611abb36fba6db7b835
13	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4NzcwNiwiaWF0IjoxNzgxNDgyOTA2LCJqdGkiOiI2ZDUxMDc4ZmQ5ZDY0Njc0YWU5NTRmOTRhNDNkNTY2NyIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.FQBsgMCOlG4CRGoW-h5Q6MYeNFjABRabyILYbomLoMI	2026-06-15 01:21:46.705699+01	2026-06-22 01:21:46+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	6d51078fd9d64674ae954f94a43d5667
14	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4Nzc5MCwiaWF0IjoxNzgxNDgyOTkwLCJqdGkiOiJhYjQ2ODBiNGIyZDA0Yzk2ODZkMjk3NTFiNzZhNTExMyIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.PT7ZxTySWkVzAGahpTuiA_3HJldpZVFWnn-xeIfwPTU	2026-06-15 01:23:10.043545+01	2026-06-22 01:23:10+01	a53de944-cff5-411a-8da5-cf68296311ef	ab4680b4b2d04c9686d29751b76a5113
15	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4Nzc5MiwiaWF0IjoxNzgxNDgyOTkyLCJqdGkiOiIzZjM4YmUzN2IxY2E0NDQxODBkMjVmYTgwMzBlYzFlNyIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.8yEPxSWMPbbT4Kg8m5nO89Xkvs4hXhop9UysU_I4KwQ	2026-06-15 01:23:12.957208+01	2026-06-22 01:23:12+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	3f38be37b1ca444180d25fa8030ec1e7
16	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4Nzc5NCwiaWF0IjoxNzgxNDgyOTk0LCJqdGkiOiJkNzhlOTBhNjZkNmY0NDNiOWRlMzljN2JmZjA2OTkwNiIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.xDBNGJH6JaaLh2KEzgHfVG3MKmBRa-J82bdt-jR6NqA	2026-06-15 01:23:14.542338+01	2026-06-22 01:23:14+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	d78e90a66d6f443b9de39c7bff069906
17	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4Nzc5NywiaWF0IjoxNzgxNDgyOTk3LCJqdGkiOiJjYmExNzVkYzk2MzA0MmRmYmNmN2Q3NWI5OTI3NjE2YSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.LCSEtcQo0i0k5Ld5f0zm_6SXejVuKYxYOILH1W6YsYA	2026-06-15 01:23:17.652583+01	2026-06-22 01:23:17+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	cba175dc963042dfbcf7d75b9927616a
18	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4ODA5NSwiaWF0IjoxNzgxNDgzMjk1LCJqdGkiOiJmOTE1ZTZjOTA5NGU0OTFhYWZkYTI4MDg2NDZiYTdhYSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.LsZf0CkMtQDPdS3A45HMTcrcE3RQxFqR_f1ISdIgZh0	2026-06-15 01:28:15.060287+01	2026-06-22 01:28:15+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	f915e6c9094e491aafda2808646ba7aa
19	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4ODA5NywiaWF0IjoxNzgxNDgzMjk3LCJqdGkiOiIyYmUwOTcxYzdlYzU0ZjIxYmExM2M2MDdlNGY0YmU0ZCIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.gHSYUTHIxHbaI3dVsrYoMFfer_19KrE5c7Rf1WBst00	2026-06-15 01:28:17.67749+01	2026-06-22 01:28:17+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	2be0971c7ec54f21ba13c607e4f4be4d
20	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4ODEyOSwiaWF0IjoxNzgxNDgzMzI5LCJqdGkiOiIyNDEwM2RlZWI0M2Q0YTU4YjllY2Y0M2YwMTQ0ODFlZSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.l3VVX_CMISml1-CNBi2d1CYQf2WJE-shQaWIUnWeR-o	2026-06-15 01:28:49.681407+01	2026-06-22 01:28:49+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	24103deeb43d4a58b9ecf43f014481ee
21	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4ODM0OSwiaWF0IjoxNzgxNDgzNTQ5LCJqdGkiOiI2MjA5MzE4ZTFhZTQ0YzMwYjIyM2IyODM1NDgwNTZmNSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.KgkQRJTlNWEIyIIdjILm--t67vm_U7ZCgjCyZxfhJqM	2026-06-15 01:32:29.246327+01	2026-06-22 01:32:29+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	6209318e1ae44c30b223b283548056f5
22	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4ODUxMCwiaWF0IjoxNzgxNDgzNzEwLCJqdGkiOiI3NjkyYmY3MTIzYzc0YzhlYWFlMWNkOGRjYjU2ZTdjNSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.N3bRFl0p33C8TOqf12bUfFfMPB7xyGaGyPMsHGjdpj8	2026-06-15 01:35:10.021234+01	2026-06-22 01:35:10+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	7692bf7123c74c8eaae1cd8dcb56e7c5
23	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4ODUxOSwiaWF0IjoxNzgxNDgzNzE5LCJqdGkiOiIzOGYzZDA5ZWU5ZjY0MWIxOTkwMjgxMmUyZWIwN2RhZSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.SPgH33XgwCBifGrf4rgwMik1SPzSKjzj3DQBKad-f1g	2026-06-15 01:35:19.100045+01	2026-06-22 01:35:19+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	38f3d09ee9f641b19902812e2eb07dae
24	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjA4ODc2MSwiaWF0IjoxNzgxNDgzOTYxLCJqdGkiOiJjODc3NGQ0ZTY2Njk0NjEyYmU0MzFjZTE5MTQxNWY5NiIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.q-DBQ10oPWGftgspbJnOM_puZ-lXYsRqfR8pOEZljVY	2026-06-15 01:39:21.943493+01	2026-06-22 01:39:21+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	c8774d4e66694612be431ce191415f96
25	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjMwNDU5NiwiaWF0IjoxNzgxNjk5Nzk2LCJqdGkiOiI1YTk0ZDM0NWY1MDE0MTdiOTQ3NjE2ZDdiMDdkZmExMSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.neYKjFl9goCodio06w31gt7fgVToYlE52fp7WEkpczY	2026-06-17 13:36:36.720883+01	2026-06-24 13:36:36+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	5a94d345f501417b947616d7b07dfa11
26	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjM5NDU4MSwiaWF0IjoxNzgxNzg5NzgxLCJqdGkiOiI0ZDg3MWQ3YmUwNDc0MTQ2OGIzNDY5NDhiYmI2YWNhZSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.VBMsLKRp2kApL7nR8kj8YKfkwC73fmK6eJxEBq-ZmJ8	2026-06-18 14:36:21.785086+01	2026-06-25 14:36:21+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	4d871d7be04741468b346948bbb6acae
27	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MjYwMDc4OSwiaWF0IjoxNzgxOTk1OTg5LCJqdGkiOiJjZWU3OTkxODZmZmU0MjhiYjJmNzhiNzI5ODRmNmYzMiIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.q-JT_ssjOWfiwnOBqn5OGUSSL5IbO3zGhADb6DRYGBg	2026-06-20 23:53:09.027829+01	2026-06-27 23:53:09+01	a53de944-cff5-411a-8da5-cf68296311ef	cee799186ffe428bb2f78b72984f6f32
28	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4Mjg0ODcxMiwiaWF0IjoxNzgyMjQzOTEyLCJqdGkiOiIyYTE3YzZjZmViMmQ0MjRmYjFkYjliNzJjYmFjMGMxMyIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.Vnqp1VnpIQKmhCesl62byYynS2L-zlelAUAmAD6GOoM	2026-06-23 20:45:12.078735+01	2026-06-30 20:45:12+01	a53de944-cff5-411a-8da5-cf68296311ef	2a17c6cfeb2d424fb1db9b72cbac0c13
29	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4Mjg0ODczNCwiaWF0IjoxNzgyMjQzOTM0LCJqdGkiOiIxN2FkZWRjOTQzNGI0M2VhOTk2MDJhNmJjZjc1NTI0ZSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.a66dUFTZAWmbUc3VIoprvgBJnbkMduaSX7lbqBrFjn4	2026-06-23 20:45:34.69698+01	2026-06-30 20:45:34+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	17adedc9434b43ea99602a6bcf75524e
30	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4Mjg0ODc1MiwiaWF0IjoxNzgyMjQzOTUyLCJqdGkiOiI3ZTEyOTgyYjQxZDM0NTQwODlmMGNmZjE5NzhlZmU5OCIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.Key7pkln3I9kXEtAK5hs0SPkd0fID0IcYEIp9tLdjvo	2026-06-23 20:45:52.039601+01	2026-06-30 20:45:52+01	a53de944-cff5-411a-8da5-cf68296311ef	7e12982b41d3454089f0cff1978efe98
31	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4Mjg0OTMzNywiaWF0IjoxNzgyMjQ0NTM3LCJqdGkiOiI4MzMyODBkOGM4YzU0ODMwOGFkYTJlOGY0MTMzNmY5OSIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.Iz-lywP-bCTkwojTIDcqf6Lq3Hebtg7Kelc0QAuZ2mE	2026-06-23 20:55:37.413326+01	2026-06-30 20:55:37+01	a53de944-cff5-411a-8da5-cf68296311ef	833280d8c8c548308ada2e8f41336f99
32	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4Mjg2NTUzMCwiaWF0IjoxNzgyMjYwNzMwLCJqdGkiOiI2Mzk3NzcyNWI2YTU0N2YzYTM4MTc3MGU4OGVhZDliNSIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.QMbuoOKfy_LbfG3g0XulwxSqpSs-dTtsUwgcckXEWVQ	2026-06-24 01:25:30.610451+01	2026-07-01 01:25:30+01	a53de944-cff5-411a-8da5-cf68296311ef	63977725b6a547f3a381770e88ead9b5
33	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzA0NzU5NywiaWF0IjoxNzgyNDQyNzk3LCJqdGkiOiJmOTdiMDUzOTE0ZTc0ODlkYTIyZGVkMDhkZjJlMjM0YiIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.P6Gi5jEn0Jf5kiyW3XML8Co_rXoCa3RiHcEKNRX3f0I	2026-06-26 03:59:57.746283+01	2026-07-03 03:59:57+01	a53de944-cff5-411a-8da5-cf68296311ef	f97b053914e7489da22ded08df2e234b
34	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzA0OTUxNywiaWF0IjoxNzgyNDQ0NzE3LCJqdGkiOiJkM2I0ZjUyMGY3OWE0YmJlYWI1MGI4ZTg5MjczZDk3MyIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.lfl9Kp5jwewS9oy0wbKRn45Zcn6rtwASf6JhOiUn2Vw	2026-06-26 04:31:57.2897+01	2026-07-03 04:31:57+01	a53de944-cff5-411a-8da5-cf68296311ef	d3b4f520f79a4bbeab50b8e89273d973
35	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzA4NDE5MywiaWF0IjoxNzgyNDc5MzkzLCJqdGkiOiJjZGVjZjgxY2I1Nzk0NDM2YjAxMWJlYWVlMDQzOTE5ZCIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.hiDbMNZk6IGg40_g2P_9rBLx-zkBOIKnUCO1rMOCFPQ	2026-06-26 14:09:53.851658+01	2026-07-03 14:09:53+01	a53de944-cff5-411a-8da5-cf68296311ef	cdecf81cb5794436b011beaee043919d
36	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzEyMjgyMiwiaWF0IjoxNzgyNTE4MDIyLCJqdGkiOiI3NGVmYzE1MzhlYTA0ZjQ0OTUzYjI5NTBmZjRmZjI3MSIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.z0LMC89Yn5YjxsuEeT26Fcz_XTeLZDBqAJJsSlHBk5U	2026-06-27 00:53:42.646722+01	2026-07-04 00:53:42+01	a53de944-cff5-411a-8da5-cf68296311ef	74efc1538ea04f44953b2950ff4ff271
37	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzE3NzI4MSwiaWF0IjoxNzgyNTcyNDgxLCJqdGkiOiJlMWRkZmJkNDFmOWY0NGJjYTQ3NTU2NDA2MGJiMTkzNSIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.9qxQYbvQ7ritFHN6MXkeQtTgaDXZNKu0zXhPWhbks5A	2026-06-27 16:01:21.147394+01	2026-07-04 16:01:21+01	a53de944-cff5-411a-8da5-cf68296311ef	e1ddfbd41f9f44bca475564060bb1935
38	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzE3ODYyOSwiaWF0IjoxNzgyNTczODI5LCJqdGkiOiIxMjlmOWEyNzUyNjc0NjI0ODE4YjdkZWQ2M2FiYmFlYiIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.v1XMfQPKouKtikCZyXdsMlWGqR6iFBfkItklSJ0NU4k	2026-06-27 16:23:49.325466+01	2026-07-04 16:23:49+01	a53de944-cff5-411a-8da5-cf68296311ef	129f9a2752674624818b7ded63abbaeb
39	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzIwOTU4OSwiaWF0IjoxNzgyNjA0Nzg5LCJqdGkiOiIyNGE3Njk4YTcwOTU0ZGM2ODJhNjdmNTYzMTg5MmJhMiIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.f-p-Ucz6Tdsw3iLYnOZNGR6vzBrO2K2NhmAy6maWqtc	2026-06-28 00:59:49.716531+01	2026-07-05 00:59:49+01	a53de944-cff5-411a-8da5-cf68296311ef	24a7698a70954dc682a67f5631892ba2
40	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzM1MzQ5OCwiaWF0IjoxNzgyNzQ4Njk4LCJqdGkiOiJjODQyMGM5OWFiZTY0NjhiODIwMGQ5N2IyNDIwNTA2NiIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.zV_xkd50B2RE3rxiOIWM9ViF8CinZaAQSxsJZfMWaQ0	2026-06-29 16:58:18.01331+01	2026-07-06 16:58:18+01	a53de944-cff5-411a-8da5-cf68296311ef	c8420c99abe6468b8200d97b24205066
41	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzU1MTY1MywiaWF0IjoxNzgyOTQ2ODUzLCJqdGkiOiIyZDkxNjgxNTllOTE0ODc3YjM2OTU0N2RkOWQwZmJkYSIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.hMM0CqDBHdZgL0kP4PQOGzHGIyVNRE2H717S2FMQww8	2026-07-02 00:00:53.583158+01	2026-07-09 00:00:53+01	a53de944-cff5-411a-8da5-cf68296311ef	2d9168159e914877b369547dd9d0fbda
42	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzgzNTEzMiwiaWF0IjoxNzgzMjMwMzMyLCJqdGkiOiJjZGZiMzc2M2E0MmQ0OGMwOGUxZGNjMjBmNTBlYWQ0MCIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.T8RJkAwr1_4GadsduIsNN8vntTBu2y0WxCXEDjWR6cc	2026-07-05 06:45:32.069307+01	2026-07-12 06:45:32+01	a53de944-cff5-411a-8da5-cf68296311ef	cdfb3763a42d48c08e1dcc20f50ead40
43	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzgzNTE0NCwiaWF0IjoxNzgzMjMwMzQ0LCJqdGkiOiJjMDUwNzEyMzdmYWE0NjhhOGY2YTVkNjhlYjhmNzQwOCIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.edo0RNE88CCHEHYND_7Hq2F0SHI0BRFuiMyHqwadCzE	2026-07-05 06:45:44.920325+01	2026-07-12 06:45:44+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	c05071237faa468a8f6a5d68eb8f7408
44	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MzkxMzMyMSwiaWF0IjoxNzgzMzA4NTIxLCJqdGkiOiJjOWUyNjYwODBmM2E0NDkzYWM3MDNmYWJkNjIwZTE2ZiIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.h2o_FNj4qnyVzTUo5OfQV-qCifhu32W3u6QDVwxpE5Q	2026-07-06 04:28:41.581671+01	2026-07-13 04:28:41+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	c9e266080f3a4493ac703fabd620e16f
45	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4NDA4MTA4NywiaWF0IjoxNzgzNDc2Mjg3LCJqdGkiOiJlNmFiNWQ1MDNiYjM0Nzg1OGU5MDgzOTFkYWQ5YmRhZSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.vPVSaJd1plvIZZ4xGr4hachPoiczyZaYSuXQJ9diuhI	2026-07-08 03:04:47.030942+01	2026-07-15 03:04:47+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	e6ab5d503bb347858e908391dad9bdae
46	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4NDE2ODk4NSwiaWF0IjoxNzgzNTY0MTg1LCJqdGkiOiI4MmYzNDM2MGYwM2Q0ZjM4YjdmZjE1MzgzOGU4NmNiNyIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.b91wD-mceD_b5L9ADdvN9-gxxNukBnfgwM3UAMAQDDM	2026-07-09 03:29:45.63471+01	2026-07-16 03:29:45+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	82f34360f03d4f38b7ff153838e86cb7
47	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4NDIxMzA1OCwiaWF0IjoxNzgzNjA4MjU4LCJqdGkiOiJhZGYxMTU4MTBkMTM0ODBkOTVjNDUxMzgzM2I3NWVlMiIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.C6WccHV0SQhpVscDFMbEvGFS_t26BBVCmz5RflL7R8c	2026-07-09 15:44:18.233721+01	2026-07-16 15:44:18+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	adf115810d13480d95c4513833b75ee2
48	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4NDM4ODA1OSwiaWF0IjoxNzgzNzgzMjU5LCJqdGkiOiIwMjk3YjA4NjMxZDA0ZTI5OTc4MmJmNTdmNjA1MGQ4YiIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.9m2gsTDBeXr0qbe5uWazST2oTc-U5nR25LIf_LXOPhc	2026-07-11 16:20:59.524764+01	2026-07-18 16:20:59+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	0297b08631d04e299782bf57f6050d8b
49	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4NDM4ODI0MywiaWF0IjoxNzgzNzgzNDQzLCJqdGkiOiJlZmM0MDQyOWRhOTk0YWZkYWI5OGVkYmNlYWQ5ZTU4YSIsInVzZXJfaWQiOiIwZDhhY2EyMy1iMmIwLTQ1OWItYmY4Yy00M2JmZDI2OGI0MzAifQ.Yw-fhCZgTMU0M3M1CN194cAyRobc-_7EkmuQI1iMoMQ	2026-07-11 16:24:03.233825+01	2026-07-18 16:24:03+01	0d8aca23-b2b0-459b-bf8c-43bfd268b430	efc40429da994afdab98edbcead9e58a
50	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4NDM4ODI5MiwiaWF0IjoxNzgzNzgzNDkyLCJqdGkiOiI2MGM0ZmEyYTdkN2I0OTdkYjFmN2Y1NjYzZGM0ZGU3NyIsInVzZXJfaWQiOiJhNTNkZTk0NC1jZmY1LTQxMWEtOGRhNS1jZjY4Mjk2MzExZWYifQ.ONHagLBPQSdhrsBmRyp0uD6GIY0X1bFSgEAxOFwJX_g	2026-07-11 16:24:52.804859+01	2026-07-18 16:24:52+01	a53de944-cff5-411a-8da5-cf68296311ef	60c4fa2a7d7b497db1f7f5663dc4de77
\.


--
-- Data for Name: user_spins; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_spins (id, video_ref, spun_at, coupon_id, prize_id, user_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (password, last_login, is_superuser, id, email, phone, full_name, avatar_url, role, is_verified, is_active, is_staff, created_at, updated_at, last_seen) FROM stdin;
pbkdf2_sha256$1000000$PzMYAwPSL4KIrohl5LrbtB$V50ce/ufYIycvgIUQ76xlmV6YKap3eIKh5BP/t8fXE0=	\N	f	d5ec6043-f93f-46d7-b500-240bafa964b8	test@groshop.tn	20123456	Mohamed Aziz		buyer	f	t	f	2026-06-11 19:08:10.581358+01	2026-06-11 19:08:10.581358+01	\N
argon2$argon2id$v=19$m=102400,t=2,p=8$WDRJa3pmS2tPaDdBQlZkM3U5TXhmdg$7TiwzUiLfLBWR34sy79EKL+4cwrImMIuAgM7SfdXSKs	\N	f	a53de944-cff5-411a-8da5-cf68296311ef	buyer@test.tn		Ahmed Ben Ali		buyer	t	t	f	2026-06-14 15:44:10.747677+01	2026-06-14 15:44:10.788719+01	\N
argon2$argon2id$v=19$m=102400,t=2,p=8$NlJXMnpWaTB2NzN2cXRmcmcwQzRBeg$QHBlPD8/uUqZSWCCipjxznxgUaA8NneDzBgb7NF/g/s	\N	f	0d8aca23-b2b0-459b-bf8c-43bfd268b430	supplier@test.tn	20123456	Sfax Textile Co.		supplier	t	t	f	2026-06-11 19:48:07.651356+01	2026-06-14 15:44:59.650621+01	\N
!G58O3rorINwcM5nnS9xBCGR1Ogu7i3RKtbSrOp92	\N	f	39277626-4717-4ab2-9f1b-180c1d3c84f1	groshop.dev@gmail.com		Gros Hop		buyer	t	t	f	2026-06-14 20:43:18.740075+01	2026-06-14 20:43:18.740075+01	\N
argon2$argon2id$v=19$m=102400,t=2,p=8$WU9hMjdaejd3OHZnemk0UHlSdHgxcQ$BQya4x3sBck1f/MP/fyho8/ZwOsk/EY4VPeVJ22zD7E	\N	f	c2ccbfb5-283a-427d-a251-5595e80c60f9	buyer2@test.tn		Amira Khelifi		buyer	t	t	f	2026-06-20 23:01:16.853644+01	2026-06-20 23:01:16.979366+01	\N
\.


--
-- Data for Name: users_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: users_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: wishlists; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.wishlists (id, created_at, product_id, supplier_id, user_id) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 166, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 58, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 79, true);


--
-- Name: token_blacklist_blacklistedtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.token_blacklist_blacklistedtoken_id_seq', 1, false);


--
-- Name: token_blacklist_outstandingtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.token_blacklist_outstandingtoken_id_seq', 50, true);


--
-- Name: users_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_groups_id_seq', 1, false);


--
-- Name: users_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_permissions_id_seq', 1, false);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: banners banners_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.banners
    ADD CONSTRAINT banners_pkey PRIMARY KEY (id);


--
-- Name: buyer_profiles buyer_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.buyer_profiles
    ADD CONSTRAINT buyer_profiles_pkey PRIMARY KEY (id);


--
-- Name: buyer_profiles buyer_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.buyer_profiles
    ADD CONSTRAINT buyer_profiles_user_id_key UNIQUE (user_id);


--
-- Name: cart_items cart_items_buyer_id_product_id_variant_id_250b8b19_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cart_items
    ADD CONSTRAINT cart_items_buyer_id_product_id_variant_id_250b8b19_uniq UNIQUE (buyer_id, product_id, variant_id);


--
-- Name: cart_items cart_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cart_items
    ADD CONSTRAINT cart_items_pkey PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: categories categories_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_slug_key UNIQUE (slug);


--
-- Name: commissions commissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commissions
    ADD CONSTRAINT commissions_pkey PRIMARY KEY (id);


--
-- Name: commissions commissions_sub_order_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commissions
    ADD CONSTRAINT commissions_sub_order_id_key UNIQUE (sub_order_id);


--
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- Name: coupons coupons_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.coupons
    ADD CONSTRAINT coupons_code_key UNIQUE (code);


--
-- Name: coupons coupons_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.coupons
    ADD CONSTRAINT coupons_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: product_images product_images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_pkey PRIMARY KEY (id);


--
-- Name: product_interactions product_interactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_interactions
    ADD CONSTRAINT product_interactions_pkey PRIMARY KEY (id);


--
-- Name: product_price_tiers product_price_tiers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_price_tiers
    ADD CONSTRAINT product_price_tiers_pkey PRIMARY KEY (id);


--
-- Name: product_variants product_variants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_variants
    ADD CONSTRAINT product_variants_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: products products_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_slug_key UNIQUE (slug);


--
-- Name: quotes quotes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT quotes_pkey PRIMARY KEY (id);


--
-- Name: review_photos review_photos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_photos
    ADD CONSTRAINT review_photos_pkey PRIMARY KEY (id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- Name: search_history search_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_history
    ADD CONSTRAINT search_history_pkey PRIMARY KEY (id);


--
-- Name: spin_prizes spin_prizes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spin_prizes
    ADD CONSTRAINT spin_prizes_pkey PRIMARY KEY (id);


--
-- Name: sub_orders sub_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_orders
    ADD CONSTRAINT sub_orders_pkey PRIMARY KEY (id);


--
-- Name: subscription_plans subscription_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_plans
    ADD CONSTRAINT subscription_plans_pkey PRIMARY KEY (id);


--
-- Name: supplier_documents supplier_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_documents
    ADD CONSTRAINT supplier_documents_pkey PRIMARY KEY (id);


--
-- Name: supplier_profiles supplier_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_profiles
    ADD CONSTRAINT supplier_profiles_pkey PRIMARY KEY (id);


--
-- Name: supplier_profiles supplier_profiles_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_profiles
    ADD CONSTRAINT supplier_profiles_slug_key UNIQUE (slug);


--
-- Name: supplier_profiles supplier_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_profiles
    ADD CONSTRAINT supplier_profiles_user_id_key UNIQUE (user_id);


--
-- Name: supplier_store supplier_store_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_store
    ADD CONSTRAINT supplier_store_pkey PRIMARY KEY (id);


--
-- Name: supplier_store supplier_store_supplier_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_store
    ADD CONSTRAINT supplier_store_supplier_id_key UNIQUE (supplier_id);


--
-- Name: supplier_subscriptions supplier_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_subscriptions
    ADD CONSTRAINT supplier_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: token_blacklist_blacklistedtoken token_blacklist_blacklistedtoken_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_blacklistedtoken
    ADD CONSTRAINT token_blacklist_blacklistedtoken_pkey PRIMARY KEY (id);


--
-- Name: token_blacklist_blacklistedtoken token_blacklist_blacklistedtoken_token_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_blacklistedtoken
    ADD CONSTRAINT token_blacklist_blacklistedtoken_token_id_key UNIQUE (token_id);


--
-- Name: token_blacklist_outstandingtoken token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_outstandingtoken
    ADD CONSTRAINT token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq UNIQUE (jti);


--
-- Name: token_blacklist_outstandingtoken token_blacklist_outstandingtoken_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_outstandingtoken
    ADD CONSTRAINT token_blacklist_outstandingtoken_pkey PRIMARY KEY (id);


--
-- Name: conversations unique_conversation; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT unique_conversation UNIQUE (buyer_id, supplier_id, product_id);


--
-- Name: reviews unique_review_product; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT unique_review_product UNIQUE (reviewer_id, product_id);


--
-- Name: reviews unique_review_supplier; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT unique_review_supplier UNIQUE (reviewer_id, supplier_id);


--
-- Name: wishlists unique_wishlist_product; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wishlists
    ADD CONSTRAINT unique_wishlist_product UNIQUE (user_id, product_id);


--
-- Name: wishlists unique_wishlist_supplier; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wishlists
    ADD CONSTRAINT unique_wishlist_supplier UNIQUE (user_id, supplier_id);


--
-- Name: user_spins user_spins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_spins
    ADD CONSTRAINT user_spins_pkey PRIMARY KEY (id);


--
-- Name: user_spins user_spins_video_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_spins
    ADD CONSTRAINT user_spins_video_ref_key UNIQUE (video_ref);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users_groups users_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_pkey PRIMARY KEY (id);


--
-- Name: users_groups users_groups_user_id_group_id_fc7788e8_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_user_id_group_id_fc7788e8_uniq UNIQUE (user_id, group_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users_user_permissions users_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: users_user_permissions users_user_permissions_user_id_permission_id_3b86cbdf_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_user_id_permission_id_3b86cbdf_uniq UNIQUE (user_id, permission_id);


--
-- Name: wishlists wishlists_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wishlists
    ADD CONSTRAINT wishlists_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: banners_supplier_id_56a381c8; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX banners_supplier_id_56a381c8 ON public.banners USING btree (supplier_id);


--
-- Name: cart_items_buyer_id_fd91efa0; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX cart_items_buyer_id_fd91efa0 ON public.cart_items USING btree (buyer_id);


--
-- Name: cart_items_product_id_9398bb89; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX cart_items_product_id_9398bb89 ON public.cart_items USING btree (product_id);


--
-- Name: cart_items_variant_id_6e25bb33; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX cart_items_variant_id_6e25bb33 ON public.cart_items USING btree (variant_id);


--
-- Name: categories_parent_id_fc02df82; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX categories_parent_id_fc02df82 ON public.categories USING btree (parent_id);


--
-- Name: categories_slug_9bedfe6b_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX categories_slug_9bedfe6b_like ON public.categories USING btree (slug varchar_pattern_ops);


--
-- Name: commissions_supplier_id_63abfe1e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX commissions_supplier_id_63abfe1e ON public.commissions USING btree (supplier_id);


--
-- Name: conversations_buyer_id_d99807d5; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX conversations_buyer_id_d99807d5 ON public.conversations USING btree (buyer_id);


--
-- Name: conversations_product_id_c2c693e3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX conversations_product_id_c2c693e3 ON public.conversations USING btree (product_id);


--
-- Name: conversations_supplier_id_b1a02e5b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX conversations_supplier_id_b1a02e5b ON public.conversations USING btree (supplier_id);


--
-- Name: coupons_code_ca4a2ab4_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX coupons_code_ca4a2ab4_like ON public.coupons USING btree (code varchar_pattern_ops);


--
-- Name: coupons_user_id_bee5d0f0; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX coupons_user_id_bee5d0f0 ON public.coupons USING btree (user_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: messages_conversation_id_5ef638db; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX messages_conversation_id_5ef638db ON public.messages USING btree (conversation_id);


--
-- Name: messages_sender_id_dc5a0bbd; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX messages_sender_id_dc5a0bbd ON public.messages USING btree (sender_id);


--
-- Name: notificatio_user_id_a4dd5c_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notificatio_user_id_a4dd5c_idx ON public.notifications USING btree (user_id, is_read);


--
-- Name: notifications_user_id_468e288d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notifications_user_id_468e288d ON public.notifications USING btree (user_id);


--
-- Name: order_items_product_id_dd557d5a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX order_items_product_id_dd557d5a ON public.order_items USING btree (product_id);


--
-- Name: order_items_sub_order_id_402616ff; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX order_items_sub_order_id_402616ff ON public.order_items USING btree (sub_order_id);


--
-- Name: orders_buyer_id_3d1f9476; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX orders_buyer_id_3d1f9476 ON public.orders USING btree (buyer_id);


--
-- Name: product_images_product_id_28ebf5f0; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX product_images_product_id_28ebf5f0 ON public.product_images USING btree (product_id);


--
-- Name: product_int_product_877230_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX product_int_product_877230_idx ON public.product_interactions USING btree (product_id, event_type);


--
-- Name: product_int_user_id_300aa7_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX product_int_user_id_300aa7_idx ON public.product_interactions USING btree (user_id, created_at);


--
-- Name: product_interactions_product_id_3b05e327; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX product_interactions_product_id_3b05e327 ON public.product_interactions USING btree (product_id);


--
-- Name: product_interactions_user_id_7d8a05fd; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX product_interactions_user_id_7d8a05fd ON public.product_interactions USING btree (user_id);


--
-- Name: product_price_tiers_product_id_0b11ff1b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX product_price_tiers_product_id_0b11ff1b ON public.product_price_tiers USING btree (product_id);


--
-- Name: product_variants_product_id_019d9f04; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX product_variants_product_id_019d9f04 ON public.product_variants USING btree (product_id);


--
-- Name: products_categor_4083ff_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX products_categor_4083ff_idx ON public.products USING btree (category_id);


--
-- Name: products_category_id_a7a3a156; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX products_category_id_a7a3a156 ON public.products USING btree (category_id);


--
-- Name: products_slug_8f20884e_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX products_slug_8f20884e_like ON public.products USING btree (slug varchar_pattern_ops);


--
-- Name: products_sold_co_e478bd_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX products_sold_co_e478bd_idx ON public.products USING btree (sold_count);


--
-- Name: products_status_a30e64_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX products_status_a30e64_idx ON public.products USING btree (status);


--
-- Name: products_supplie_1396c7_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX products_supplie_1396c7_idx ON public.products USING btree (supplier_id);


--
-- Name: products_supplier_id_ae23c972; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX products_supplier_id_ae23c972 ON public.products USING btree (supplier_id);


--
-- Name: quotes_buyer_id_22f5da77; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX quotes_buyer_id_22f5da77 ON public.quotes USING btree (buyer_id);


--
-- Name: quotes_product_id_1acb7bad; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX quotes_product_id_1acb7bad ON public.quotes USING btree (product_id);


--
-- Name: quotes_supplier_id_4f28ef00; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX quotes_supplier_id_4f28ef00 ON public.quotes USING btree (supplier_id);


--
-- Name: review_photos_review_id_e79d7d0f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX review_photos_review_id_e79d7d0f ON public.review_photos USING btree (review_id);


--
-- Name: reviews_order_id_35d02b74; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_order_id_35d02b74 ON public.reviews USING btree (order_id);


--
-- Name: reviews_product_id_d4b78cfe; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_product_id_d4b78cfe ON public.reviews USING btree (product_id);


--
-- Name: reviews_reviewer_id_dbb954a8; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_reviewer_id_dbb954a8 ON public.reviews USING btree (reviewer_id);


--
-- Name: reviews_supplier_id_38f37b3e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_supplier_id_38f37b3e ON public.reviews USING btree (supplier_id);


--
-- Name: reviews_variant_id_6f6b041c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_variant_id_6f6b041c ON public.reviews USING btree (variant_id);


--
-- Name: search_hist_user_id_f49661_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX search_hist_user_id_f49661_idx ON public.search_history USING btree (user_id, searched_at);


--
-- Name: search_history_user_id_b2c466f7; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX search_history_user_id_b2c466f7 ON public.search_history USING btree (user_id);


--
-- Name: sub_orders_order_id_24b9bae3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX sub_orders_order_id_24b9bae3 ON public.sub_orders USING btree (order_id);


--
-- Name: sub_orders_supplier_id_da7f0756; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX sub_orders_supplier_id_da7f0756 ON public.sub_orders USING btree (supplier_id);


--
-- Name: supplier_documents_supplier_id_b4c40cf4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX supplier_documents_supplier_id_b4c40cf4 ON public.supplier_documents USING btree (supplier_id);


--
-- Name: supplier_profiles_slug_e553b94a_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX supplier_profiles_slug_e553b94a_like ON public.supplier_profiles USING btree (slug varchar_pattern_ops);


--
-- Name: supplier_subscriptions_changed_by_id_d22b0a7c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX supplier_subscriptions_changed_by_id_d22b0a7c ON public.supplier_subscriptions USING btree (changed_by_id);


--
-- Name: supplier_subscriptions_plan_id_a6b37853; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX supplier_subscriptions_plan_id_a6b37853 ON public.supplier_subscriptions USING btree (plan_id);


--
-- Name: supplier_subscriptions_supplier_id_84f377c6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX supplier_subscriptions_supplier_id_84f377c6 ON public.supplier_subscriptions USING btree (supplier_id);


--
-- Name: token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_like ON public.token_blacklist_outstandingtoken USING btree (jti varchar_pattern_ops);


--
-- Name: token_blacklist_outstandingtoken_user_id_83bc629a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX token_blacklist_outstandingtoken_user_id_83bc629a ON public.token_blacklist_outstandingtoken USING btree (user_id);


--
-- Name: user_spins_coupon_id_2fb21a5e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX user_spins_coupon_id_2fb21a5e ON public.user_spins USING btree (coupon_id);


--
-- Name: user_spins_prize_id_40b20cae; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX user_spins_prize_id_40b20cae ON public.user_spins USING btree (prize_id);


--
-- Name: user_spins_user_id_a7d8ee45; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX user_spins_user_id_a7d8ee45 ON public.user_spins USING btree (user_id);


--
-- Name: user_spins_video_ref_9a4a7a6d_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX user_spins_video_ref_9a4a7a6d_like ON public.user_spins USING btree (video_ref varchar_pattern_ops);


--
-- Name: users_email_0ea73cca_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_email_0ea73cca_like ON public.users USING btree (email varchar_pattern_ops);


--
-- Name: users_groups_group_id_2f3517aa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_groups_group_id_2f3517aa ON public.users_groups USING btree (group_id);


--
-- Name: users_groups_user_id_f500bee5; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_groups_user_id_f500bee5 ON public.users_groups USING btree (user_id);


--
-- Name: users_user_permissions_permission_id_6d08dcd2; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_user_permissions_permission_id_6d08dcd2 ON public.users_user_permissions USING btree (permission_id);


--
-- Name: users_user_permissions_user_id_92473840; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_user_permissions_user_id_92473840 ON public.users_user_permissions USING btree (user_id);


--
-- Name: wishlists_product_id_6f2a0dee; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX wishlists_product_id_6f2a0dee ON public.wishlists USING btree (product_id);


--
-- Name: wishlists_supplier_id_e4aaf659; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX wishlists_supplier_id_e4aaf659 ON public.wishlists USING btree (supplier_id);


--
-- Name: wishlists_user_id_6280b16e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX wishlists_user_id_6280b16e ON public.wishlists USING btree (user_id);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: banners banners_supplier_id_56a381c8_fk_supplier_profiles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.banners
    ADD CONSTRAINT banners_supplier_id_56a381c8_fk_supplier_profiles_id FOREIGN KEY (supplier_id) REFERENCES public.supplier_profiles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: buyer_profiles buyer_profiles_user_id_405ef80f_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.buyer_profiles
    ADD CONSTRAINT buyer_profiles_user_id_405ef80f_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cart_items cart_items_buyer_id_fd91efa0_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cart_items
    ADD CONSTRAINT cart_items_buyer_id_fd91efa0_fk_users_id FOREIGN KEY (buyer_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cart_items cart_items_product_id_9398bb89_fk_products_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cart_items
    ADD CONSTRAINT cart_items_product_id_9398bb89_fk_products_id FOREIGN KEY (product_id) REFERENCES public.products(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cart_items cart_items_variant_id_6e25bb33_fk_product_variants_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cart_items
    ADD CONSTRAINT cart_items_variant_id_6e25bb33_fk_product_variants_id FOREIGN KEY (variant_id) REFERENCES public.product_variants(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: categories categories_parent_id_fc02df82_fk_categories_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_parent_id_fc02df82_fk_categories_id FOREIGN KEY (parent_id) REFERENCES public.categories(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: commissions commissions_sub_order_id_e9e09e8b_fk_sub_orders_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commissions
    ADD CONSTRAINT commissions_sub_order_id_e9e09e8b_fk_sub_orders_id FOREIGN KEY (sub_order_id) REFERENCES public.sub_orders(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: commissions commissions_supplier_id_63abfe1e_fk_supplier_profiles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commissions
    ADD CONSTRAINT commissions_supplier_id_63abfe1e_fk_supplier_profiles_id FOREIGN KEY (supplier_id) REFERENCES public.supplier_profiles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: conversations conversations_buyer_id_d99807d5_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_buyer_id_d99807d5_fk_users_id FOREIGN KEY (buyer_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: conversations conversations_product_id_c2c693e3_fk_products_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_product_id_c2c693e3_fk_products_id FOREIGN KEY (product_id) REFERENCES public.products(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: conversations conversations_supplier_id_b1a02e5b_fk_supplier_profiles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_supplier_id_b1a02e5b_fk_supplier_profiles_id FOREIGN KEY (supplier_id) REFERENCES public.supplier_profiles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: coupons coupons_user_id_bee5d0f0_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.coupons
    ADD CONSTRAINT coupons_user_id_bee5d0f0_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: messages messages_conversation_id_5ef638db_fk_conversations_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_conversation_id_5ef638db_fk_conversations_id FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: messages messages_sender_id_dc5a0bbd_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_sender_id_dc5a0bbd_fk_users_id FOREIGN KEY (sender_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: notifications notifications_user_id_468e288d_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_468e288d_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: order_items order_items_product_id_dd557d5a_fk_products_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_dd557d5a_fk_products_id FOREIGN KEY (product_id) REFERENCES public.products(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: order_items order_items_sub_order_id_402616ff_fk_sub_orders_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_sub_order_id_402616ff_fk_sub_orders_id FOREIGN KEY (sub_order_id) REFERENCES public.sub_orders(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: orders orders_buyer_id_3d1f9476_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_buyer_id_3d1f9476_fk_users_id FOREIGN KEY (buyer_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: product_images product_images_product_id_28ebf5f0_fk_products_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_product_id_28ebf5f0_fk_products_id FOREIGN KEY (product_id) REFERENCES public.products(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: product_interactions product_interactions_product_id_3b05e327_fk_products_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_interactions
    ADD CONSTRAINT product_interactions_product_id_3b05e327_fk_products_id FOREIGN KEY (product_id) REFERENCES public.products(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: product_interactions product_interactions_user_id_7d8a05fd_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_interactions
    ADD CONSTRAINT product_interactions_user_id_7d8a05fd_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: product_price_tiers product_price_tiers_product_id_0b11ff1b_fk_products_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_price_tiers
    ADD CONSTRAINT product_price_tiers_product_id_0b11ff1b_fk_products_id FOREIGN KEY (product_id) REFERENCES public.products(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: product_variants product_variants_product_id_019d9f04_fk_products_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_variants
    ADD CONSTRAINT product_variants_product_id_019d9f04_fk_products_id FOREIGN KEY (product_id) REFERENCES public.products(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: products products_category_id_a7a3a156_fk_categories_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_a7a3a156_fk_categories_id FOREIGN KEY (category_id) REFERENCES public.categories(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: products products_supplier_id_ae23c972_fk_supplier_profiles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_supplier_id_ae23c972_fk_supplier_profiles_id FOREIGN KEY (supplier_id) REFERENCES public.supplier_profiles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quotes quotes_buyer_id_22f5da77_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT quotes_buyer_id_22f5da77_fk_users_id FOREIGN KEY (buyer_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quotes quotes_product_id_1acb7bad_fk_products_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT quotes_product_id_1acb7bad_fk_products_id FOREIGN KEY (product_id) REFERENCES public.products(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quotes quotes_supplier_id_4f28ef00_fk_supplier_profiles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT quotes_supplier_id_4f28ef00_fk_supplier_profiles_id FOREIGN KEY (supplier_id) REFERENCES public.supplier_profiles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: review_photos review_photos_review_id_e79d7d0f_fk_reviews_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_photos
    ADD CONSTRAINT review_photos_review_id_e79d7d0f_fk_reviews_id FOREIGN KEY (review_id) REFERENCES public.reviews(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reviews reviews_order_id_35d02b74_fk_orders_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_order_id_35d02b74_fk_orders_id FOREIGN KEY (order_id) REFERENCES public.orders(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reviews reviews_product_id_d4b78cfe_fk_products_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_product_id_d4b78cfe_fk_products_id FOREIGN KEY (product_id) REFERENCES public.products(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reviews reviews_reviewer_id_dbb954a8_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_reviewer_id_dbb954a8_fk_users_id FOREIGN KEY (reviewer_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reviews reviews_supplier_id_38f37b3e_fk_supplier_profiles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_supplier_id_38f37b3e_fk_supplier_profiles_id FOREIGN KEY (supplier_id) REFERENCES public.supplier_profiles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reviews reviews_variant_id_6f6b041c_fk_product_variants_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_variant_id_6f6b041c_fk_product_variants_id FOREIGN KEY (variant_id) REFERENCES public.product_variants(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: search_history search_history_user_id_b2c466f7_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.search_history
    ADD CONSTRAINT search_history_user_id_b2c466f7_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sub_orders sub_orders_order_id_24b9bae3_fk_orders_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_orders
    ADD CONSTRAINT sub_orders_order_id_24b9bae3_fk_orders_id FOREIGN KEY (order_id) REFERENCES public.orders(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sub_orders sub_orders_supplier_id_da7f0756_fk_supplier_profiles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_orders
    ADD CONSTRAINT sub_orders_supplier_id_da7f0756_fk_supplier_profiles_id FOREIGN KEY (supplier_id) REFERENCES public.supplier_profiles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: supplier_documents supplier_documents_supplier_id_b4c40cf4_fk_supplier_profiles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_documents
    ADD CONSTRAINT supplier_documents_supplier_id_b4c40cf4_fk_supplier_profiles_id FOREIGN KEY (supplier_id) REFERENCES public.supplier_profiles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: supplier_profiles supplier_profiles_user_id_c7ab43fb_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_profiles
    ADD CONSTRAINT supplier_profiles_user_id_c7ab43fb_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: supplier_store supplier_store_supplier_id_d7bbffc3_fk_supplier_profiles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_store
    ADD CONSTRAINT supplier_store_supplier_id_d7bbffc3_fk_supplier_profiles_id FOREIGN KEY (supplier_id) REFERENCES public.supplier_profiles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: supplier_subscriptions supplier_subscriptio_plan_id_a6b37853_fk_subscript; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_subscriptions
    ADD CONSTRAINT supplier_subscriptio_plan_id_a6b37853_fk_subscript FOREIGN KEY (plan_id) REFERENCES public.subscription_plans(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: supplier_subscriptions supplier_subscriptio_supplier_id_84f377c6_fk_supplier_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_subscriptions
    ADD CONSTRAINT supplier_subscriptio_supplier_id_84f377c6_fk_supplier_ FOREIGN KEY (supplier_id) REFERENCES public.supplier_profiles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: supplier_subscriptions supplier_subscriptions_changed_by_id_d22b0a7c_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supplier_subscriptions
    ADD CONSTRAINT supplier_subscriptions_changed_by_id_d22b0a7c_fk_users_id FOREIGN KEY (changed_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: token_blacklist_blacklistedtoken token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_blacklistedtoken
    ADD CONSTRAINT token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk FOREIGN KEY (token_id) REFERENCES public.token_blacklist_outstandingtoken(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: token_blacklist_outstandingtoken token_blacklist_outstandingtoken_user_id_83bc629a_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_outstandingtoken
    ADD CONSTRAINT token_blacklist_outstandingtoken_user_id_83bc629a_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_spins user_spins_coupon_id_2fb21a5e_fk_coupons_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_spins
    ADD CONSTRAINT user_spins_coupon_id_2fb21a5e_fk_coupons_id FOREIGN KEY (coupon_id) REFERENCES public.coupons(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_spins user_spins_prize_id_40b20cae_fk_spin_prizes_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_spins
    ADD CONSTRAINT user_spins_prize_id_40b20cae_fk_spin_prizes_id FOREIGN KEY (prize_id) REFERENCES public.spin_prizes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_spins user_spins_user_id_a7d8ee45_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_spins
    ADD CONSTRAINT user_spins_user_id_a7d8ee45_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_groups users_groups_group_id_2f3517aa_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_group_id_2f3517aa_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_groups users_groups_user_id_f500bee5_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_user_id_f500bee5_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_permissions users_user_permissio_permission_id_6d08dcd2_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissio_permission_id_6d08dcd2_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_permissions users_user_permissions_user_id_92473840_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_user_id_92473840_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: wishlists wishlists_product_id_6f2a0dee_fk_products_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wishlists
    ADD CONSTRAINT wishlists_product_id_6f2a0dee_fk_products_id FOREIGN KEY (product_id) REFERENCES public.products(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: wishlists wishlists_supplier_id_e4aaf659_fk_supplier_profiles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wishlists
    ADD CONSTRAINT wishlists_supplier_id_e4aaf659_fk_supplier_profiles_id FOREIGN KEY (supplier_id) REFERENCES public.supplier_profiles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: wishlists wishlists_user_id_6280b16e_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wishlists
    ADD CONSTRAINT wishlists_user_id_6280b16e_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

\unrestrict 2uth1l2s65Dw7no5kuQrZlAJ5cbqDug9CShjfSwQFtyVruxTwOx8xe9N8RzcOxq

