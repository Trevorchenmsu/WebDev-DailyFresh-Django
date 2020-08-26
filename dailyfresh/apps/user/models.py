# -*-coding:utf-8-*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel

'''
1. BaseModel is defined in db directory. It is a class including create time, update time, and
delete flag. This class is inherited by all the model classes since we need to keep track of these
three information for all the model classes.  
2. AbstractUser is inherited by User class. AbstractUser is a default user class in Django. It
includes the basic definition, like user name, password, email, etc. Thus, as long as we inherit
this class, we don't need to define these parameters in User class, which makes it concise. 
3. All the Meta classes defined in each class are used to keep the database tables name from changing
the project's name or something else. For example, in User class, the table name will always be "df_user_user".
'''
class User(AbstractUser, BaseModel):
    """ User Model Class"""

    class Meta:
        db_table = 'df_user'
        verbose_name = 'user'
        verbose_name_plural = verbose_name


class AddressManager(models.Manager):
    """ Address Management Model Class """
    # 1. change query results set: all()
    # 2. encapsulation: tables corresponding to user operation model class
    #    (add, delete, query, change)

    def get_default_address(self, user):
        # Get the user's default shipping address
        try:
            address = self.get(user=user, is_default=True)
        except self.model.DoesNotExist:
            address = None  # default address does not exit

        return address

'''
1. User-Address is a one to multiple relation, thus user is a foreign key in address table. 
2. The function of __str__ is to display the user name when it displays the table in database. 
'''
class Address(BaseModel):
    """ Address Model Class """
    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='User')
    receiver = models.CharField(max_length=20, verbose_name='Receiver')
    addr = models.CharField(max_length=256, verbose_name='Address')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='ZipCode')
    phone = models.CharField(max_length=11, verbose_name='Phone')
    is_default = models.BooleanField(default=False, verbose_name='DefaultFlag')

    # Define an address manager
    objects = AddressManager()

    class Meta:
        db_table = 'df_address'
        verbose_name = 'address'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username
