import graphene
from graphene-django import DjangoObjectType
from .models import Customer, Product, Order
from django.core,exceptions import ValidationError
from django_core.validators import validate_email
import re
from django.db import transaction

#validating phone number format
def validate_phone(phone):
    if not phone:
        return True
    pattern = re.compile(r'^(\+\d{10}|\d{3}-\d{3}-\d{4})$')
    return bool(pattern.match(phone))

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

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
    message = graphene.string()

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

class BulkCreateCustomers:
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
