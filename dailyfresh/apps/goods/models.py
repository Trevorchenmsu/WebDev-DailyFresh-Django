# -*-coding:utf-8-*-
from django.db import models
from db.base_model import BaseModel
from tinymce.models import HTMLField

'''
1. There are seven tables related to goods:
    (1) Goods type; (2) Goods SKU; (3) Goods (SPU);
    (4) Goods Image; (5) Goods banner display; 
    (6) Goods type banner display; (7) Promotion activity display
    Image storage: type, banner, goods. We don't actually use these places to store the images.
    we will use FastDFS to store images instead.
'''

'''
(1) Goods type: stores goods' category name, a small logo next to the name, an image 
    represents this kind of goods;
'''
class GoodsType(BaseModel):
    """Goods Type Model Class"""
    name = models.CharField(max_length=20, verbose_name='TypeName')
    logo = models.CharField(max_length=20, verbose_name='Logo')
    image = models.ImageField(upload_to='type', verbose_name='TypeImage')

    class Meta:
        db_table = 'df_goods_type'
        verbose_name = 'GoodsType'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

'''
(2) Goods SKU: SKU = Stock Keeping Unit. It is a specific type of a product. For example,
    iPhone X with 32G storage, white. Thus, it should has many attributes describing the goods.
    OnSale or OffSale represents the status whether the goods is still on the sale or off the sale.
    Sine one type of goods can have many goods SKU, goods type is a foreign key here.
    A goods SPU can have several goods SKU, so goods SPU is a foreign key here. 
'''
class GoodsSKU(BaseModel):
    """Goods SKU Model Class"""
    status_choices = (
        (0, 'OnSale'),
        (1, 'OffSale')
    )
    name = models.CharField(max_length=20, verbose_name='GoodsName')
    desc = models.CharField(max_length=256, verbose_name='GoodsDescription')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price')
    unite = models.CharField(max_length=20, verbose_name='Units')
    type = models.ForeignKey('GoodsType', on_delete=models.CASCADE, verbose_name='GoodsType')
    stock = models.IntegerField(default=1, verbose_name='Stocks')
    image = models.ImageField(upload_to='goods', verbose_name='Images')
    status = models.SmallIntegerField(default=1, choices=status_choices, verbose_name='Status')
    goods = models.ForeignKey('Goods', on_delete=models.CASCADE, verbose_name='GoodsSPU')
    sales = models.IntegerField(default=0, verbose_name='Sales')

    class Meta:
        db_table = 'df_goods_sku'
        verbose_name = 'Goods'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    # def __repr__(self):
    #     return self.name

'''
(3) Goods (SPU): SPU = Standard Product Unit. It is general concept to represent a product, 
    but it is not related to any specific details of that product. Normally, the products 
    with same attributes and features can be classified as a SPU. For example, iPhone X
    is a SPU. It has nothing to do with the color or storage. So goods SPU has fewer info
    than goods SKU.
    Here we use rich-text to define the detail of the goods. it is easier for adminstrator to
    manipulate in the backend. 
'''
class Goods(BaseModel):
    """Goods SPU Model Class"""
    name = models.CharField(max_length=20, verbose_name='GoodsSPUName')
    # Rich-text type：text with certain format
    detail = HTMLField(blank=True, verbose_name='GoodsDescription')

    class Meta:
        db_table = 'df_goods'
        verbose_name = 'GoodsSPU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

'''
(4) Goods Image: this class is used to define each image related to a specific goods SKU.
    As a goods SKU can have several images to represent it, goods SKU is a foreign key here.
'''
class GoodsImage(BaseModel):
    """ Goods Image Model Class """
    sku = models.ForeignKey('GoodsSKU', on_delete=models.CASCADE, verbose_name='GoodsSKU')
    image = models.ImageField(upload_to='goods', verbose_name='ImagePath')

    class Meta:
        db_table = 'df_goods_image'
        verbose_name = 'GoodsImage'
        verbose_name_plural = verbose_name

'''
(5) Goods Banner: this class is used to display 4-5 goods SKU images, like an ad in the homepage.
    Goods SKU is a foreign key here. Index is used to display the images in order.
'''
class IndexGoodsBanner(BaseModel):
    """ Homepage Carousel Goods Display Model Class """
    sku = models.ForeignKey('GoodsSKU', on_delete=models.CASCADE, verbose_name='GoodsSKU')
    image = models.ImageField(upload_to='banner', verbose_name='Image')
    index = models.SmallIntegerField(default=0, verbose_name='DisplayOrder')

    class Meta:
        db_table = 'df_index_banner'
        verbose_name = 'HomepageCarouselGoods'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku.name

'''
(6) Goods Type Banner: this class is used to display the goods types. Goods type and SKU are
    both the foreign keys here. 
    The display has two types: one is to display the title of the goods, the other is to display
    the image of the goods. The index is used to display the images or titles in order. 
'''
class IndexTypeGoodsBanner(BaseModel):
    """HomePage Type Goods Display Model Class"""
    DISPLAY_TYPE_CHOICES = (
        (0, 'Title'),
        (1, 'Image')
    )

    type = models.ForeignKey('GoodsType', on_delete=models.CASCADE, verbose_name='GoodsType')
    sku = models.ForeignKey('GoodsSKU', on_delete=models.CASCADE, verbose_name='GoodsSKU')
    display_type = models.SmallIntegerField(default=1, choices=DISPLAY_TYPE_CHOICES, verbose_name='DisplayType')
    index = models.SmallIntegerField(default=1, verbose_name='DisplayOrder')

    class Meta:
        db_table = 'df_index_type_goods'
        verbose_name = 'HomePageTypeGoodsDisplay'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku.name

'''
(7) Promotion Banner: this class is used to display the promotion activities. Thus,
    it has the link which connects to the specific activity page. It also displays 
    different activities with different images in order. 
'''
class IndexPromotionBanner(BaseModel):
    """ Homepage Promotion Activity Model Class """
    name = models.CharField(max_length=20, verbose_name='ActivityName')
    url = models.URLField(verbose_name='ActivityURL')
    image = models.ImageField(upload_to='banner', verbose_name='ActivityImage')
    index = models.SmallIntegerField(default=0, verbose_name='DisplayOrder')

    class Meta:
        db_table = 'df_index_promotion'
        verbose_name = 'HomepagePromotionActivity'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
