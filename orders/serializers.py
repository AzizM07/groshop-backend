# orders/serializers.py
from rest_framework import serializers
from .models import Order, SubOrder, OrderItem, CartItem


# ══════════════════════════════════════════════════════════════════
# ORDER ITEM
# ══════════════════════════════════════════════════════════════════
class OrderItemSerializer(serializers.ModelSerializer):

    product_name     = serializers.CharField(source='product.name', read_only=True)
    product_slug     = serializers.CharField(source='product.slug', read_only=True)
    product_category = serializers.CharField(source='product.category.name',
                                             read_only=True, allow_null=True, default=None)
    product_image    = serializers.SerializerMethodField()

    class Meta:
        model  = OrderItem
        fields = ['id', 'product_name', 'product_slug', 'product_category', 'product_image',
                  'quantity', 'unit_price_tnd', 'total_tnd']

    def get_product_image(self, obj):
        # ⚡ .all() → utilise le cache du prefetch (0 requête).
        #    .filter() relancerait une requête SQL par article → N+1.
        images = obj.product.images.all()
        for img in images:
            if img.is_primary:
                return img.url
        return images[0].url if images else None


# ══════════════════════════════════════════════════════════════════
# SUB-ORDER
# ══════════════════════════════════════════════════════════════════
class SubOrderSerializer(serializers.ModelSerializer):

    items         = OrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.company_name', read_only=True)
    supplier_slug = serializers.CharField(source='supplier.slug', read_only=True)

    class Meta:
        model  = SubOrder
        fields = ['id', 'supplier_name', 'supplier_slug',
                  'status', 'subtotal_tnd', 'delivery_type', 'items']


# ══════════════════════════════════════════════════════════════════
# ORDER LIST / DETAIL
# ══════════════════════════════════════════════════════════════════
class OrderListSerializer(serializers.ModelSerializer):

    sub_orders_count = serializers.SerializerMethodField()

    class Meta:
        model  = Order
        fields = ['id', 'status', 'payment_status', 'payment_method',
                  'total_tnd', 'discount_tnd', 'created_at', 'sub_orders_count']

    def get_sub_orders_count(self, obj):
        return len(obj.sub_orders.all())   # ⚡ cache prefetch (voir orders_list)


class OrderDetailSerializer(serializers.ModelSerializer):

    sub_orders = SubOrderSerializer(many=True, read_only=True)

    class Meta:
        model  = Order
        fields = ['id', 'status', 'payment_status', 'payment_method',
                  'total_tnd', 'discount_tnd', 'shipping_address',
                  'notes', 'created_at', 'sub_orders']


class CreateOrderSerializer(serializers.Serializer):

    shipping_address = serializers.CharField()
    payment_method   = serializers.ChoiceField(choices=[
        'cod', 'd17', 'flouci', 'sobflous', 'virement'
    ])
    notes            = serializers.CharField(required=False, allow_blank=True)
    items            = serializers.ListField(child=serializers.DictField())


# ══════════════════════════════════════════════════════════════════
# SUPPLIER SUB-ORDER (espace fournisseur)
# ══════════════════════════════════════════════════════════════════
class SupplierSubOrderSerializer(serializers.ModelSerializer):

    order_id       = serializers.UUIDField(source='order.id', read_only=True)
    buyer_name     = serializers.CharField(source='order.buyer.full_name', read_only=True)
    payment_method = serializers.CharField(source='order.payment_method', read_only=True)
    payment_status = serializers.CharField(source='order.payment_status', read_only=True)
    items          = OrderItemSerializer(many=True, read_only=True)
    items_count    = serializers.SerializerMethodField()
    primary_image  = serializers.SerializerMethodField()

    class Meta:
        model  = SubOrder
        fields = ['id', 'order_id', 'status', 'subtotal_tnd', 'delivery_type',
                  'created_at', 'buyer_name', 'payment_method', 'payment_status',
                  'items', 'items_count', 'primary_image']

    def get_items_count(self, obj):
        return len(obj.items.all())        # ⚡ cache prefetch

    def get_primary_image(self, obj):
        items = obj.items.all()            # ⚡ cache prefetch
        if not items:
            return None
        images = items[0].product.images.all()
        for img in images:
            if img.is_primary:
                return img.url
        return images[0].url if images else None


# ══════════════════════════════════════════════════════════════════
# CART ITEM
# ══════════════════════════════════════════════════════════════════
class CartItemSerializer(serializers.ModelSerializer):

    product         = serializers.SerializerMethodField()
    variant_data    = serializers.SerializerMethodField()
    unit_price_tnd  = serializers.DecimalField(
                          source='unit_price',
                          max_digits=10, decimal_places=3,
                          read_only=True)
    total_price_tnd = serializers.DecimalField(
                          source='total_price',
                          max_digits=12, decimal_places=3,
                          read_only=True)

    class Meta:
        model  = CartItem
        fields = ['id', 'quantity', 'variant', 'variant_data',
                  'unit_price_tnd', 'total_price_tnd',
                  'product', 'created_at', 'updated_at']

    def get_product(self, obj):
        p = obj.product

        # ⚡ Image primaire via le cache du prefetch
        images = p.images.all()
        image_url = None
        for img in images:
            if img.is_primary:
                image_url = img.url
                break
        if image_url is None and images:
            image_url = images[0].url

        # Supplier
        supplier_data = None
        if p.supplier_id:
            s = p.supplier
            supplier_data = {
                'id':       str(s.id),
                'name':     getattr(s, 'company_name', '') or getattr(s, 'name', ''),
                'slug':     getattr(s, 'slug', ''),
                'city':     getattr(s, 'city', '') or '',
                'logo_url': getattr(s, 'logo_url', None),
                'verified': getattr(s, 'verified_status', '') == 'approved',
            }

        # ⚡ .all() puis tri Python → cache prefetch ( .order_by() = nouvelle requête )
        tiers = [{
            'min_qty':   t.min_qty,
            'max_qty':   t.max_qty,
            'price_tnd': str(t.price_tnd),
        } for t in sorted(p.price_tiers.all(), key=lambda t: t.min_qty)]

        return {
            'id':             str(p.id),
            'name':           p.name,
            'slug':           getattr(p, 'slug', ''),
            'image_url':      image_url,
            'base_price_tnd': str(p.base_price_tnd),
            'old_price_tnd':  str(p.old_price_tnd) if getattr(p, 'old_price_tnd', None) else None,
            'moq':            p.moq,
            'unit':           getattr(p, 'unit', 'pièce'),
            'stock_qty':      getattr(p, 'stock_qty', 0),
            'price_tiers':    tiers,
            'supplier':       supplier_data,
        }

    def get_variant_data(self, obj):
        if not obj.variant_id:
            return None
        v = obj.variant
        return {
            'id':   str(v.id),
            'name': getattr(v, 'name', ''),
            'sku':  getattr(v, 'sku', ''),
        }