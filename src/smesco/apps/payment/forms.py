from django import forms


class PaymentNotificationsForm(forms.Form):
    MerchantCode = forms.CharField(required=False)
    PaymentId = forms.CharField(required=False)
    RefNo = forms.CharField(required=False)
    Amount = forms.CharField(required=False)
    Currency = forms.CharField(required=False)
    Remark = forms.CharField(required=False)
    TransId = forms.CharField(required=False)
    AuthCode = forms.CharField(required=False)
    Status = forms.CharField(required=False)
    ErrDesc = forms.CharField(required=False)
    Signature = forms.CharField(required=False)
    xfield1 = forms.CharField(required=False)
    VirtualAccountAssigned = forms.CharField(required=False)
    ETransactionExpiryDate = forms.CharField(required=False)
