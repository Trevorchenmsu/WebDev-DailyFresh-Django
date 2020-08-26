# -*-coding:utf-8-*-
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
#
from apps.user.models import User, Address
# from apps.goods.models import GoodsSKU
# from apps.order.models import OrderInfo, OrderGoods
#
from celery_tasks.tasks import send_register_active_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection
import re
import time

# /user/register
# def register(request):
#     """ Register """
#     if request.method == 'GET':
#         return render(request, 'register.html')  # Display register page
#     else:
#         """ Register processing """
#         # Receive data
#         username = request.POST.get('user_name')
#         password = request.POST.get('pwd')
#         email = request.POST.get('email')
#         allow = request.POST.get('allow')
#
#         # Data verification
#         if not all([username, password, email]):
#             # Incomplete date
#             return render(request, 'register.html', {'errmsg': 'Incomplete Data'})
#
#         # Email Verification
#         if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#             return render(request, 'register.html', {'errmsg': 'Incorrect Email Format'})
#
#         if allow != 'on':
#             return render(request, 'register.html', {'errmsg': 'Please Check Agreement'})
#
#         # Detect duplicate user name
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             # user name do not exit
#             user = None
#
#         if user:
#             return render(request, 'register.html', {'errmsg': 'User Name Exists'})
#
#         # User registration and store the data to database
#         user = User.objects.create_user(username, email, password)
#         user.is_active = 0
#         user.save()
#
#         # Return response and redirect to homepage
#         return redirect(reverse('goods:index'))

# def register_handle(request):
#     '''进行注册处理'''
#     # 接收数据
#     username = request.POST.get('user_name')
#     password = request.POST.get('pwd')
#     email = request.POST.get('email')
#     allow = request.POST.get('allow')
#
#     # 进行数据校验
#     if not all([username, password, email]):
#         # 数据不完整
#         return render(request, 'register.html', {'errmsg':'数据不完整'})
#
#     # 校验邮箱
#     if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#         return render(request, 'register.html', {'errmsg':'邮箱格式不正确'})
#
#     if allow != 'on':
#         return render(request, 'register.html', {'errmsg':'请同意协议'})
#
#     # 校验用户名是否重复
#     try:
#         user = User.objects.get(username=username)
#     except User.DoesNotExist:
#         # 用户名不存在
#         user = None
#
#     if user:
#         # 用户名已存在
#         return render(request, 'register.html', {'errmsg': '用户名已存在'})
#
#     # 进行业务处理: 进行用户注册
#     user = User.objects.create_user(username, email, password)
#     user.is_active = 0
#     user.save()
#
#     # 返回应答, 跳转到首页
#     return redirect(reverse('goods:index'))



# class view
# /user/register


class RegisterView(View):
    ''' Register'''
    def get(self, request):
        ''' Display register page'''
        return render(request, 'register.html')

    def post(self, request):
        """ Register processing """
        # Receive data
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # Data verification
        if not all([username, password, email]):
            # Incomplete date
            return render(request, 'register.html', {'errmsg': 'Incomplete Data'})

        # Email Verification
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': 'Incorrect Email Format'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': 'Please Check Agreement'})

        # Detect duplicate user name
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # user name do not exit
            user = None

        if user:
            return render(request, 'register.html', {'errmsg': 'User Name Exists'})

        # User registration and store the data to database
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # Return response and redirect to homepage
        # return redirect(reverse('goods:index'))

        # send activation email, including activation link: http://127.0.0.1:8000/user/active/3
        # user's info should be included in the activation link, and encrypted.

        # encrypt user info and generate activation token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info) # bytes
        token_decode = token.decode()

        # subject = 'Daily Fresh Welcome'
        # message = 'for trial'
        # sender = settings.EMAIL_FROM
        # receiver = [email]
        # send_mail(subject, message, sender, receiver)
        # msg = '<a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (token, token)
        # send_mail(subject, message, sender, receiver, html_message=msg)

        # send email
        send_register_active_email.delay(email, username, token_decode)

        # return response and redirect to homepage
        return redirect(reverse('goods:index'))



class ActiveView(View):
    ''' User Activation '''
    def get(self, request, token):
        ''' Activation Process '''
        # get the user info for activation
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # get the user id
            user_id = info['confirm']

            # get the user info based on user id
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # redirect to login page
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # activation link expires
            return HttpResponse('Activation has expired')

# /user/login
class LoginView(View):
    ''' login '''
    def get(self, request):
        ''' login page '''
        # determine whether user name is remembered
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        # use template
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        ''' login verification '''
        # receive data
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # data verification
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg':'incomplete data'})

        # processing: login verification
        user = authenticate(username=username, password=password)
        if user is not None:
            # correct user name and password
            if user.is_active:
                # activated user
                # remember login state
                login(request, user)

                # get the redirect webpage after login, default=homepage
                next_url = request.GET.get('next', reverse('goods:index'))

                # redirect to next_url
                response = redirect(next_url) # HttpResponseRedirect

                # check whether to remember user name
                remember = request.POST.get('remember')

                if remember == 'on':
                    # remember user name
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')

                # return response
                return response
            else:
                # inactivated user
                return render(request, 'login.html', {'errmsg':'Account needs to be activated'})
        else:
            # incorrect user name or password
            return render(request, 'login.html', {'errmsg':'incorrect user name or password'})

# /user/logout
class LogoutView(View):
    ''' logout '''
    def get(self, request):
        ''' logout '''
        # clear user session
        logout(request)

        # redirect to homepage
        return redirect(reverse('goods:index'))


# /user
class UserInfoView(LoginRequiredMixin, View):
    """用户中心-信息页"""
    def get(self, request):
        return render(request, 'user_center_info.html', {'page': 'user'})
        # # 获取个人信息
        # user = request.user
        # address = Address.objects.get_default_address(user)
        #
        # # 获取用户的历史浏览记录
        # # from redis import StrictRedis
        # # sr = StrictRedis(host='127.0.0.1', port='6379', db=9)
        # con = get_redis_connection('default')
        #
        # history_key = 'history_%d' % user.id
        #
        # # 获取用户最新历史浏览记录的5个商品id
        # sku_ids = con.lrange(history_key, 0, 4)
        #
        # # 从数据库中查询用户浏览商品的具体信息
        # # goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        # #
        # # goods_res = []
        # # for a_id in sku_ids:
        # #     for goods in goods_li:
        # #         goods_res.append(goods)
        #
        # # 遍历获取用户浏览的历史商品信息
        # goods_list = []
        # for id in sku_ids:
        #     goods = GoodsSKU.objects.get(id=id)
        #     goods_list.append(goods)
        #
        # # 组织上下文
        # context = {'page': 'user',
        #            'address': address,
        #            'goods_list': goods_list}
        #
        # return render(request, 'df_user/user_center_info.html', context)


# /user/order
class UserOrderView(LoginRequiredMixin, View):
    """用户中心-订单页"""
    def get(self, request, page):
        return render(request, 'user_center_order.html', {'page': 'order'})

        # # 获取用户的订单信息
        # user = request.user
        # orders = OrderInfo.objects.filter(user=user).order_by('-create_time')
        #
        # # 遍历获取订单商品信息
        # for order in orders:
        #     # 根据order_id查询订单商品信息
        #     order_skus = OrderGoods.objects.filter(order_id=order.order_id)
        #
        #     # 遍历Order_skus计算商品的小计
        #     for order_sku in order_skus:
        #         amount = order_sku.count * order_sku.price
        #         # 动态给order_sku增加属性amount,保存订单商品小计
        #         order_sku.amount = amount
        #
        #     # 动态给order增加属性, 保存订单状态标题
        #     order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
        #     order.order_skus = order_skus
        #
        # # 分页
        # paginator = Paginator(orders, 2)  # 单页显示数目2
        #
        # try:
        #     page = int(page)
        # except Exception as e:
        #     page = 1
        #
        # if page > paginator.num_pages or page <= 0:
        #     page = 1
        #
        # # 获取第page页的Page实例对象
        # order_page = paginator.page(page)
        #
        # # todo: 进行页码的控制，页面上最多显示5个页码
        # # 1. 总数不足5页，显示全部
        # # 2. 如当前页是前3页，显示1-5页
        # # 3. 如当前页是后3页，显示后5页
        # # 4. 其他情况，显示当前页的前2页，当前页，当前页的后2页
        # num_pages = paginator.num_pages
        # if num_pages < 5:
        #     pages = range(1, num_pages)
        # elif page <= 3:
        #     pages = range(1, 6)
        # elif num_pages - page <= 2:
        #     pages = range(num_pages-4, num_pages+1)
        # else:
        #     pages = range(page-2, page+3)
        #
        # # 组织上下文
        # context = {'order_page': order_page,
        #            'pages': pages,  # 页面范围控制
        #            'page': 'order'}
        #
        # return render(request, 'df_user/user_center_order.html', context)


# /user/address
class AddressView(LoginRequiredMixin, View):
    """用户中心-地址页"""
    def get(self, request):
        return render(request, 'user_center_site.html', {'page': 'address'})

    #     # django框架会给request对象添加一个属性user
    #     # 如果用户已登录，user的类型User
    #     # 如果用户没登录，user的类型AnonymousUser
    #     # 除了我们给django传递的模板变量，django还会把user传递给模板文件
    #
    #     # 获取用户的默认地址
    #     # 获取登录用户对应User对象
    #     user = request.user
    #
    #     # try:
    #     #     address = Address.objects.get(user=user, is_default=True)
    #     # except Address.DoesNotExist:
    #     #     address = None  # 不存在默认地址
    #     address = Address.objects.get_default_address(user)
    #
    #     return render(request, 'df_user/user_center_site.html', {'title': '用户中心-收货地址', 'page': 'address', 'address': address})
    #
    # def post(self, request):
    #     # 地址添加
    #     receiver = request.POST.get('receiver')
    #     addr = request.POST.get('addr')
    #     zip_code = request.POST.get('zip_code')
    #     phone = request.POST.get('phone')
    #
    #     # 业务处理：地址添加
    #     # 如果用户没存在默认地址，则添加的地址作为默认收获地址
    #     user = request.user
    #
    #     # try:
    #     #     address = Address.objects.get(user=user, is_default=True)
    #     # except Address.DoesNotExist:
    #     #     address = None  # 不存在默认地址
    #     address = Address.objects.get_default_address(user)
    #
    #     if address:
    #         is_default = False
    #     else:
    #         is_default = True
    #
    #     # 数据校验
    #     if not all([receiver, addr, phone]):
    #         return render(request, 'df_user/user_center_site.html',
    #                       {'page': 'address',
    #                        'address': address,
    #                        'errmsg': '数据不完整'})
    #
    #     # 校验手机号
    #     if not re.match(r'^1([3-8][0-9]|5[189]|8[6789])[0-9]{8}$', phone):
    #         return render(request, 'df_user/user_center_site.html',
    #                       {'page': 'address',
    #                        'address': address,
    #                        'errmsg': '手机号格式不合法'})
    #
    #     # 添加
    #     Address.objects.create(user=user,
    #                            receiver=receiver,
    #                            addr=addr,
    #                            zip_code=zip_code,
    #                            phone=phone,
    #                            is_default=is_default)
    #
    #     # 返回应答
    #     return redirect(reverse('user:address'))  # get的请求方式

