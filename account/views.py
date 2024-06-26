from decimal import Decimal

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Account, Transaction
from .serializers import AccountSerializer, AccountCreateSerializer


# Create your views here.
@api_view(['GET', 'POST'])
def list_account(request):
    if request.method == 'GET':
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = AccountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'GET':
        serializer = AccountSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = AccountCreateSerializer(account, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        serializer = AccountCreateSerializer(account, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        account.delete()
        return Response("Deleted successful", status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def deposit(request):
    account_number = request.data['account_number']
    amount = request.data['amount']
    description = request.data['description']
    account = get_object_or_404(Account, pk=account_number)
    account.account_balance += Decimal(amount)
    account.save()
    Transaction.objects.create(
        account=account,
        amount=amount,
        description=description

    )
    return Response(data={"message": "Transaction successful"}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def withdraw(request):
    account_number = request.data['account_number']
    amount = request.data['amount']
    pin = request.data['pin']
    description = request.data['description']
    account = get_object_or_404(Account, pk=account_number)
    if account.pin != pin:
        return Response({"message": "Invalid pin number"}, status=status.HTTP_400_BAD_REQUEST)
    if amount > account.account_balance:
        return Response({"message": "Not enough money"}, status=status.HTTP_400_BAD_REQUEST)
    if amount <= 0:
        return Response({"message": "Amount must be positive"}, status=status.HTTP_400_BAD_REQUEST)
    account.account_balance -= amount
    account.save()
    Transaction.objects.create(
        account=account,
        transaction_type="DEB",
        amount=amount,
        description=description
    )
    return Response(data={"message": "Transaction successful"}, status=status.HTTP_201_CREATED)

    # try:
    #     account = Account.objects.get(pk=pk)
    #     serializer = AccountSerializer(account)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    #
    # except Account.DoesNotExist:
    #     return Response({"message": "Account does not exist"}, status=status.HTTP_404_NOT_FOUND)
    #
