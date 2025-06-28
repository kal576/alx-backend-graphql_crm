import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from graphene_filters import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from django.db import transaction
from datetime import datetime

#validating phone number format
def validate_phone(phone):
    if not phone:
        return True
    pattern = re.compile(r'^(\+\d{10}|\d{3}-\d{3}-\d{4})$')
    return bool(pattern.match(phone))

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

#filter inputs
class CustomerFilterInput(graphene.InputObjectType):
    name = graphene.String()
    email = graphene.String()
    created_at_gte = graphene.Date()
    created_at_lte = graphene.Date()
    phone_pattern = graphene.String()


class ProductFilterInput(graphene.InputObjectType):
    name = graphene.String()
    price_gte = graphene.Float()
    price_lte = graphene.Float()
    stock_gte = graphene.Int()
    stock_lte = graphene.Int()


class OrderFilterInput(graphene.InputObjectType):
    total_amount_gte = graphene.Float()
    total_amount_lte = graphene.Float()
    order_date_gte = graphene.Date()
    order_date_lte = graphene.Date()
    customer_name = graphene.String()
    product_name = graphene.String()
    product_id = graphene.ID()

#inputs
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customerId = graphene.ID(required=True)
    productIds = graphene.List(graphene.ID, required=True)
    orderDate = graphene.Date()

#create mutation classes
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(root, info, input):
        try:
            #check of the email exists
            validate_email(email)
            if Customer.objects.filter(email=email).exists():
                raise Exception("A customer with this email already exists")
            #create a new customer and save to database

            #the ** unpacks the dictionary into keyword arguments, and _asdict returns a python dictionary
            customer = Customer(**input._asdict())
            customer.save()
            return CreateCustomer(customer=customer, message="Customer created successfully")

        except ValidationError as e:
            raise Exception(f"Validation error: {ve}")
        except Exception as e:
            raise Exception(str(e))

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers: graphene.List(CustomerType)
    errors: graphene.List(graphene.String)

    def mutate(root, info, input):
        #validates the email and phone number of customers, then returns the validated list
        customers = []
        error = []

        for idx, data in enumertare(input):
            try:
                validate_email(data.email)
                if Customer.objects.filter(email=email).exists():
                    errors.append(ErrorType(field=f"email_{idx}", message="Email already exists"))
                    continue
                if data.phone and not validate_phone(data.phone):
                    errors.append(ErrorType(field=f"phone_{idx}", message="Invalid phone number format"))

                # Create and save customer
                customers.append(Customer(**data._asdict()))
                customer.save()
            except ValidationError as ve:
                errors.append(ErrorType(field=f"customer_{idx}", message=str(ve)))

        with transaction.atomic():
            created_customers = Customer.objects.bulk_create(customers)

        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    @staticmethod
    def mutate(root, info, input):
        if input.price < 0:
            raise Exception ("Price cannot be negative")
        if input.stock < 0:
            raise Exception ("Stock cannot be negative")

        Product(**input._asdict()).save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    @staticmethod
    def mutate(root, info, input):
        try:
            customers = Customer.objects.get(pk=input.customerId)
        except Customer.DoesNotExist:
            raise Exception("Customer does not exist")

        product_ids = input.productIds
        if not product_ids:
            raise Exception("At least one product is required")

        products = list(Product.objects.filter(id__in=product_ids))
        if len(products) != len(product_ids):
            missing = set(product_ids) - set(str(p.id) for p in products)
            raise Exception(f"Invalid product IDs: {missing}")

        total_amount = sum(p.price for p in products)
        order = Order.objects.create(
                customer=customer,
            total_amount=total_amount,
            order_date=input.orderDate
            )

        order.products.set(order)
        order.save

        return order

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    hello = graphene.String()

    #simple list queries
    customers = graphene.List(CustomerType)
    producs = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    #filtered connection queries to handle filter requests faster
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, filter_input_type=CustomerFilterInput)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, filter_input_type=ProductFilterInput)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, filter_input_type=OrderFilterInput)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()


