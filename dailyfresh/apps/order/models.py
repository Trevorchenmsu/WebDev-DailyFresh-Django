# -*-coding:utf-8-*-
from django.db import models
from db.base_model import BaseModel

'''
This application has two tables: 
(1) order information; (2) goods detail information in a specific order 
'''
class OrderInfo(BaseModel):
    """ Order Model Class """
    PAY_METHODS = {
        '1': "Pay On Delivery",
        '2': "Pay By Wechat",
        '3': "Pay By AliPay",
        '4': 'Pay by UnionPay'
    }

    PAY_METHODS_ENUM = {
        "CASH": 1,
        "ALIPAY": 2
    }

    ORDER_STATUS = {
        1: 'Unpaid',
        2: 'BackOrder',
        3: 'Unreceived',
        4: 'Unreviewed',
        5: 'Completed'
    }

    PAY_METHOD_CHOICES = (
        (1, 'Pay On Delivery'),
        (2, 'Pay By Wechat'),
        (3, 'Pay By AliPay'),
        (4, 'Pay by UnionPay')
    )

    ORDER_STATUS_CHOICES = (
        (1, 'Unpaid'),
        (2, 'BackOrder'),
        (3, 'Unreceived'),
        (4, 'Unreviewed'),
        (5, 'Completed')
    )
    '''
    An user can have several orders and an user can have different orders to different address.
    Thus, user and address are foreign keys here. Becasue User and Address are in different application
    directories, we need to refer their directories, so we have "user. Address" and "user.User"
    '''
    order_id = models.CharField(max_length=128, primary_key=True, verbose_name='OrderID')
    addr = models.ForeignKey('user.Address', on_delete=models.CASCADE, verbose_name='Address')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='User')
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=3, verbose_name='PayMethod')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Subtotal')
    total_count = models.IntegerField(default=1, verbose_name='TotalCount')
    transit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='TransmitFee')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='OrderStatus')
    trade_no = models.CharField(max_length=128, default='', verbose_name='TradeNumber')

    class Meta:
        db_table = 'df_order_info'
        verbose_name = 'Order'
        verbose_name_plural = verbose_name

''' This class is used to store the detailed goods information in an order.
    Since an order can have several goods info, OrderInfo is a foreign key here. 
    Same as Goods SKU. 
'''
class OrderGoods(BaseModel):
    """Order Goods Model Class """
    order = models.ForeignKey('OrderInfo', on_delete=models.CASCADE, verbose_name='Order')
    sku = models.ForeignKey('goods.GoodsSKU', on_delete=models.CASCADE, verbose_name='GoodsSKU')
    count = models.IntegerField(default=1, verbose_name='GoodsCount')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price')  # total price
    comment = models.CharField(max_length=256, default='', verbose_name='Review')

    class Meta:
        db_table = 'df_order_goods'
        verbose_name = 'OrderGoods'
        verbose_name_plural = verbose_name



