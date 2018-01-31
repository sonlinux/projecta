# coding: utf-8
import json
from datetime import datetime

import requests
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from ..models import(
    Project,
    Merchants,
    Customer,
    Charges
)


#Call this method when you want to tranfer available funds from Stripe to merchant bank account

@login_required
@csrf_exempt
def payment_view(request):
    """
    :param request:
    :return:
    To do
    1. Try catch blocks
    2. Link to javascript form
    3. Add webhooks
    """
    logged_user = request.user.username
    stripe_public_key = settings.STRIPE_PUBLISHABLE_KEY
    stripe.api_key = settings.STRIPE_KEY
    our_client_id = settings.OUR_CLIENT_ID
    my_account_id = settings.MY_ACCOUNT_ID

    #merchant_id = create_merchant(request)
    # Customer login cerdential should be unique
    #chargeid = create_charge(request,customerid,merchant_id)
    try:
        dbrequest = Merchants.objects.values_list(
            'merchant_id', flat=True).get(
            firstname=logged_user)
    except BaseException:
        dbrequest = None

    return_id = request.GET.get(
        'code')
    # Payout testing
    merchant_id = settings.MY_ACCOUNT_ID
    balance, b = merchant_payout(merchant_id)
    # platform_payout()
    context = {
        'ourclientid': our_client_id,
        'balance': balance,
        'b': b,
    }
    return render(request, 'payments/pay.html', context)


@login_required
def create_account(request):
    donation_amount = settings.STRIPE_CHARGE_AMOUNT
    charge_currency = settings.STRIPE_CHARGE_CURRENCY

    context = {
        'donation_amount': donation_amount,
        'charge_currency': charge_currency
    }
    return render(request, 'payments/createaccount.html', context)


@login_required
def process_customer_and_charge(request):
    first_name = request.user.username  # Look for logged in user
    customer_id = 0
    merchant_id = 0
    try:
        dbrequest = Customer.objects.values_list(
            'merchant_id', flat=True).get(
            firstname=first_name)
    except BaseException:
        dbrequest = None

    if dbrequest is None:  # The customer does not exist
        # 1. Create user -> Click button
        return redirect(create_account)  # Create charge and account
        # 2. Refresh process_customer_and_charge
    else:
        customer_id = dbrequest
        request.session['customerid'] = customer_id
        # Insert code to specify to whom the payment should go
        # Get list of projects that have connected accounts

        #1.Get list of usernames in merchant database.
        first_names = list(Merchants.objects.values_list('first_name',flat=True))
        first_names_id = list(User.objects.filter(username__in=first_names).values_list('id',flat=True))
        db_merch_req = Project.objects.filter(owner_id__in=first_names_id).values('id','name')
        projects = Project.objects.exclude(owner_id__in=first_names_id).values('id','name')
        length_out = projects.count
        length_in = db_merch_req.count
    context = {
        'customerid': customer_id,
        'merchant_id': merchant_id,
        'dbrequest': dbrequest,
        'dbmerchreq': db_merch_req,
        'lengthin': length_in,
        'lengthout': length_out,
        'projects': projects
    }
    return render(request, 'payments/cust.html', context)


@login_required
def create_merchant(request):  # Call this method after Stripe OAuth
    merchant_id = 0
    return_id = request.GET.get(
        'code')  # token that is sent to retrieve client id to be stored in db
    # POST request to OAUTH
    print("returnid: %s"%return_id)
    if return_id is not None:
        r = requests.post(
            "https://connect.stripe.com/oauth/token",
            data={
                'client_secret': stripe.api_key,
                'code': return_id,
                'grant_type': "authorization_code"})
        temp = json.loads(r.content)
        print(temp)
        if r.status_code == 200:
            print(r.status_code)
            merchant_id = temp['stripe_user_id']
            first_name = request.user.username
            merchant_db = Merchants.objects.create(
                firstname=first_name, merchant_id=merchant_id)
            merchant_db.save()
    else:
        merchant_id = "Not successfull"  # Add warning message to user
    return redirect('home')


@login_required
def create_customer(request):
    global customer_id
    cust_tok = request.form['stripeToken']
    if cust_tok is not None:
        customer = stripe.Customer.create(
            description="This is a customer",
            source=cust_tok
        )
        first_name = request.user.username
        customer_id = customer.id
        customerdb = Customer.objects.create(
            first_name=first_name, merchant_id=customer_id)
    return customer_id


@login_required
@csrf_exempt
def process_view(request):
    stripe.api_key = settings.STRIPE_KEY
    my_account_id = settings.MY_ACCOUNT_ID
    cust_tok = request.POST.get("stripeToken")
    customer = stripe.Customer.create(
        description="This is a customer",
        source=cust_tok,
        stripe_account=my_account_id
    )
    first_name = request.user.username  # Get signed in user_id
    customer_id = customer.id
    request.session['customerid'] = customer_id
    customerdb = Customer.objects.create(
        first_name=first_name, merchant_id=customer_id)
    context = {
        'custtok': cust_tok,
        'customerid': customer_id,
    }
    # return render(request, 'payments/cust.html', context)
    return redirect(process_customer_and_charge)


@login_required
def create_charge(request, merchant_id=None):
    # Connect the customer to the connected accounts
    # if this is a POST request we need to process the form data
    customer_id = request.session.get('customerid')
    # Get the project that the payment is to be made to
    project_id = request.POST.get('projects')
    owner_id = Project.objects.values_list('owner_id',flat=True).get(id=project_id)
    error = "Unknown"
    try:
        dbrequest2 = User.objects.values_list(  # Get the username of the account holder
            'username', flat=True).get(
            id=owner_id)
    except BaseException:
        dbrequest2 = None
    try:
        dbrequest3 = Merchants.objects.values_list(  # Look up the merchant id with th username
            'merchant_id', flat=True).get(
            firstname=dbrequest2)
    except BaseException:
        dbrequest3 = None
        error = "Project does not yet have account set up"
    merchant_id = dbrequest3
    try:
        token = stripe.Token.create(
            customer=customer_id,
            stripe_account=merchant_id,
        )
        charge = stripe.Charge.create(
            amount=settings.STRIPE_CHARGE_AMOUNT,
            currency=settings.STRIPE_CHARGE_CURRENCY,
            source=token.id,
            application_fee=settings.STRIPE_APPLICATION_FEE,
            stripe_account=merchant_id
        )
        # Database information for graphs
        donation_amount = settings.STRIPE_CHARGE_AMOUNT
        charge_stripe_id = charge.id
        merchant_stripe_id = merchant_id
        customer_stripe_id = customer_id
        charge_amount = (charge.amount)/100
        project_id = project_id
        user_id = request.user.id
        date1 = datetime.now()
        date1 = datetime(int(2017),int(5),int(8))
        status = 1
        request.session['customerid'] = 0
        request.session['merchant_id'] = 0
        store_charge = Charges.objects.create(chargestripeID=charge_stripe_id, merchantstripeID=merchant_stripe_id,
                                             customerstripeID=customer_stripe_id, chargeAmount=charge_amount,
                                             projectid=project_id,
                                             userid=user_id, date=date1)
        store_charge.save()
    except BaseException:
        status = 0
    if status == 1:
        return redirect('home')
    else:
        context = {
            'status': status,
        }
        return render(request, 'payments/paid.html', context)


def platform_payout():
    balance = stripe.Balance.retrieve(
        stripe_account=settings.MY_ACCOUNT_ID
    )
    for i in balance.get('available'):
        b = i.get('amount')
    payout_platform = stripe.Payout.create(
        amount=b,
        currency='usd',
        method='instant',
        stripe_account=settings.MY_ACCOUNT_ID
    )


def merchant_payout(merchant_id):
    balance = stripe.Balance.retrieve(
        stripe_account=merchant_id
    )
    for i in balance.get('available'):
        b = i.get('amount')
    '''
    payoutplatform = stripe.Payout.create(
        amount=b,
        currency='usd',
        method='instant',
        stripe_account=merchant_id
    )
    '''
    return balance, b