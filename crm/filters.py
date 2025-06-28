import django_filters
from .models import Product, Customer, Order

class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')

    #filters customers created after a certain date. gte means greater than or equal to
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')

    #filters customers created after a certain date. lte means less than or equal to
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    phone =django_filters.CharFilter(method='filter_by_phone')

    def filter_by_phone(self, queryset, name, value):
        if value:
            return queryset.filter(phone__startswith=value)
        return queryset

    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at']

class ProductFilter(django_filters.FilterSet):
    name = name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock = django_filters.NumberFilter(field_name='stock', lookup_expr='icontains')
    stock__gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock__lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']

class OrderFilter(django_filters.FilterSet):
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date_gte = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')
    product_id = django_filters.CharFilter(field_name='products__id', lookup_expr='exact')

    class Meta:
        model = Order
        fields = ['total_amount', 'order_date']
