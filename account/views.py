from decimal import Decimal

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Account, Transaction
from .serializers import (AccountSerializer, AccountCreateSerializer,
                          TransferSerializer, DepositWithdrawSerializer,
                          QueryBalanceSerializer)


# class ListAccount(ListCreateAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountCreateSerializer
#     # def get_queryset(self):
#     #     return Account.objects.all()
#     #
#     # def get_serializer_class(self):
#     #     return AccountCreateSerializer
#
#     # def get(self, request):
#     #     accounts = Account.objects.all()
#     #     serializer = AccountSerializer(accounts, many=True)
#     #     return Response(serializer.data, status=status.HTTP_200_OK)
#     #
#     # def post(self, request):
#     #     serializer = AccountCreateSerializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# # Create your views here.
# # @api_view(['GET', 'POST'])
# # def list_account(request):
# #     if request.method == 'GET':
# #         accounts = Account.objects.all()
# #         serializer = AccountSerializer(accounts, many=True)
# #         return Response(serializer.data, status=status.HTTP_200_OK)
# #     elif request.method == 'POST':
# #         serializer = AccountCreateSerializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         serializer.save()
# #         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
# class AccountDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountCreateSerializer
#
#     # def get(self, request, pk):
#     #     account = get_object_or_404(Account, pk=pk)
#     #     serializer = AccountSerializer(account)
#     #     return Response(serializer.data, status=status.HTTP_200_OK)
#     #
#     # def put(self, request, pk):
#     #     account = get_object_or_404(Account, pk=pk)
#     #     serializer = AccountCreateSerializer(account, data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return Response(serializer.data, status=status.HTTP_200_OK)
#     #
#     # def patch(self, request, pk):
#     #     account = get_object_or_404(Account, pk=pk)
#     #     serializer = AccountCreateSerializer(account, data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return Response(serializer.data, status=status.HTTP_200_OK)
#     #
#     # def delete(self, request, pk):
#     #     account = get_object_or_404(Account, pk=pk)
#     #     account.delete()
#     #     return Response(status=status.HTTP_204_NO_CONTENT)
#
#
# # @api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
# # def account_detail(request, pk):
# #     account = get_object_or_404(Account, pk=pk)
# #     if request.method == 'GET':
# #         serializer = AccountSerializer(account)
# #         return Response(serializer.data, status=status.HTTP_200_OK)
# #     elif request.method == 'PUT':
# #         serializer = AccountCreateSerializer(account, data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         serializer.save()
# #         return Response(serializer.data, status=status.HTTP_200_OK)
# #     elif request.method == 'PATCH':
# #         serializer = AccountCreateSerializer(account, data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         serializer.save()
# #         return Response(serializer.data, status=status.HTTP_200_OK)
# #     elif request.method == 'DELETE':
# #         account.delete()
# #         return Response("Deleted successful", status=status.HTTP_204_NO_CONTENT)

class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountCreateSerializer


class Deposit(APIView):
    def post(self, request):
        serializer = DepositWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_number = serializer.data['account_number']
        amount = Decimal(serializer.data['amount'])
        transaction_details = {}
        account = get_object_or_404(Account, pk=account_number)
        balance = account.account_balance
        balance += amount
        Account.objects.filter(account_number=account_number).update(account_balance=balance)
        Transaction.objects.create(
            account=account,
            amount=amount
        )
        transaction_details['account_number'] = account_number
        transaction_details['amount'] = amount

        return Response(data=transaction_details, status=status.HTTP_201_CREATED)


# @api_view(['POST'])
# def deposit(request):
#     account_number = request.data['account_number']
#     amount = request.data['amount']
#     description = request.data['description']
#     account = get_object_or_404(Account, pk=account_number)
#     account.account_balance += Decimal(amount)
#     account.save()
#     Transaction.objects.create(
#         account=account,
#         amount=amount,
#         description=description
#
#     )
#     return Response(data={"message": "Transaction successful"}, status=status.HTTP_201_CREATED)
#


class Withdraw(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DepositWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_number = serializer.data['account_number']
        amount = Decimal(serializer.data['amount'])
        pin = request.data['pin']
        transaction_details = {}

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
        )
        transaction_details['account_number'] = account_number
        transaction_details['amount'] = amount
        transaction_details['transaction_type'] = 'DEB'

        return Response(data=transaction_details,
                        status=status.HTTP_201_CREATED)


# @api_view(['POST'])
# def withdraw(request):
#     account_number = request.data['account_number']
#     amount = request.data['amount']
#     pin = request.data['pin']
#     description = request.data['description']
#     account = get_object_or_404(Account, pk=account_number)
#     if account.pin != pin:
#         return Response({"message": "Invalid pin number"}, status=status.HTTP_400_BAD_REQUEST)
#     if amount > account.account_balance:
#         return Response({"message": "Not enough money"}, status=status.HTTP_400_BAD_REQUEST)
#     if amount <= 0:
#         return Response({"message": "Amount must be positive"}, status=status.HTTP_400_BAD_REQUEST)
#     account.account_balance -= amount
#     account.save()
#     Transaction.objects.create(
#         account=account,
#         transaction_type="DEB",
#         amount=amount,
#         description=description
#     )
#     return Response(data={"message": "Transaction successful"}, status=status.HTTP_201_CREATED)

# try:
#     account = Account.objects.get(pk=pk)
#     serializer = AccountSerializer(account)
#     return Response(serializer.data, status=status.HTTP_200_OK)
#
# except Account.DoesNotExist:
#     return Response({"message": "Account does not exist"}, status=status.HTTP_404_NOT_FOUND)
#


# class CreateAccount(CreateAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountCreateSerializer


class CheckBalance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = QueryBalanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_number = serializer.data['account_number']
        pin = serializer.data['pin']
        transaction_details = {}
        account = get_object_or_404(Account, account_number=account_number)
        if pin != account.pin:
            raise PermissionDenied
        else:
            balance = account.account_balance
            transaction_details['account_number'] = account_number
            transaction_details['balance'] = balance
            return Response(data=transaction_details, status=status.HTTP_200_OK)


class TransferViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender_account = serializer.data['sender_account']
        receiver_account = serializer.data['receiver_account']
        amount = Decimal(serializer.data['amount'])
        sender_account_from = get_object_or_404(Account, pk=sender_account)
        receiver_account_to = get_object_or_404(Account, pk=receiver_account)
        balance = sender_account_from.account_balance

        transaction_details = {}
        if balance > amount:
            balance -= amount
        else:
            return Response(data={"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            transferred_balance = receiver_account_to.account_balance + amount
            Account.objects.filter(pk=receiver_account).update(account_balance=transferred_balance)
            new_balance = sender_account_from.account_balance - amount
            Account.objects.filter(pk=receiver_account).update(account_balance=new_balance)
        except Account.DoesNotExist:
            return Response(data={"message": "Transaction failed"}, status=status.HTTP_400_BAD_REQUEST)
        Transaction.objects.create(
            account=sender_account_from,
            amount=amount,
            transaction_type='TRANSFER'
        )
        transaction_details['receiver_account'] = receiver_account
        transaction_details['amount'] = amount
        transaction_details['transaction_type'] = 'TRANSFER'
        return Response(data=transaction_details, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        return Response(data="Method not supported", status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        return Response(data="Method not supported", status=status.HTTP_405_METHOD_NOT_ALLOWED)


