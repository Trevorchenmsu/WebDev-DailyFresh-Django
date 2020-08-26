#!usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author: Jisheng Chen
@file:base_model.py
@time: 08/21/2020
"""
from django.db import models


class BaseModel(models.Model):
    """ Model abstract base class """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='CreateTime')
    update_time = models.DateTimeField(auto_now=True, verbose_name='UpdateTime')
    is_delete = models.BooleanField(default=False, verbose_name='DeleteFlag')

    class Meta:
        abstract = True  # Claim it is an abstract class
