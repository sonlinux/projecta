# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Merchants(models.Model):
    firstname = models.CharField(max_length=50)
    merchantid = models.CharField(max_length=50)


class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    merchant_id = models.CharField(max_length=50)


class Charges(models.Model):
    #Needed to conduct refunds and disputes
    charge_stripe_id = models.CharField(max_length=50)
    merchant_stripe_id = models.CharField(max_length=50)
    customer_stripe_id = models.CharField(max_length=50)
    charge_amount = models.DecimalField(
        help_text=_('Amount charged on account in dollars'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        default=0
    )
    project_id = models.CharField(max_length=50)
    user_id = models.CharField(max_length=50)
    date = models.DateTimeField()