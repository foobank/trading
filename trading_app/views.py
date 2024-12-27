# trading_app/views.py
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .exchange_upbit import UpbitClient
from .models import TradeOrder
import pandas as pd
import numpy as np
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    """
    메인 페이지: KRW-BTC 현재가 조회, 보유자산 조회
    """
    client = UpbitClient()
    current_price = client.get_ticker("KRW-BTC")  # 현재가
    balances = client.get_balances()  # 보유 자산 정보 (리턴값은 list of dict)

    return render(request, 'home.html', {
        'current_price': current_price,
        'balances': balances
    })


def create_order(request):
    """
    주문 생성 페이지
    GET -> 주문 폼
    POST -> 업비트 API로 주문 전송 + DB 저장
    """
    if request.method == 'POST':
        market = request.POST.get('market')  # KRW-BTC
        side = request.POST.get('side')  # 'bid' or 'ask'
        volume = request.POST.get('volume')  # 예: 0.001
        price = request.POST.get('price')  # 예: 20000000
        order_type = request.POST.get('order_type', 'limit')  # 'limit', 'price'(시장가매수), 'market'(시장가매도)

        # 실제 주문 실행
        client = UpbitClient()
        order_response = client.create_order(
            market=market,
            side=side,
            volume=volume if volume else None,
            price=price if price else None,
            ord_type=order_type
        )

        # 응답 바탕으로 status 결정
        order_status = order_response.get('state', 'requested')

        # DB 저장
        TradeOrder.objects.create(
            market=market,
            side=side,
            volume=volume if volume else None,
            price=price if price else None,
            order_type=order_type,
            status=order_status
        )

        return redirect('orders_list')

    return render(request, 'order_form.html')


def orders_list(request):
    """
    주문 목록 조회
    """
    orders = TradeOrder.objects.all().order_by('-created_at')
    return render(request, 'orders_list.html', {'orders': orders})


def backtest_view(request):
    """
    간단한 백테스트 예시:
    CSV 파일 읽어  전략 성과 계산 후 결과 표시
    """
    # CSV 파일 경로 (시연용으로 미리 준비해둔 파일)
    csv_path = os.path.join(os.path.dirname(__file__), 'example_data.csv')

    if not os.path.exists(csv_path):
        return HttpResponse("백테스트용 CSV 파일이 존재하지 않습니다.")

    df = pd.read_csv(csv_path)
    # df 컬럼: ['date','open','high','low','close','volume'] 라고 가정

    # 단순히 수익률 계산(예: 종가 기준) -> 랜덤 전략 시연
    df['daily_return'] = df['close'].pct_change()
    df['cumulative_return'] = (1 + df['daily_return']).cumprod()

    # 실제론 전략(이평선, RSI 등) 로직 넣어서 수익률 비교
    final_return = df['cumulative_return'].iloc[-1] - 1

    return render(request, 'backtest.html', {
        'final_return_percent': round(final_return * 100, 2),
        'rows': df.tail(5).values  # 최근 5줄만 예시로 보여주기
    })


def user_login(request):
    """
    첫 화면을 로그인 페이지로 쓰고 싶다면,
    프로젝트 urls.py에서 ''(루트) 경로를 이 뷰로 연결하면 됩니다.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Django 기본 User 모델은 'username'으로 authenticate를 수행
        # 여기서는 email -> username 변환 로직을 간단히 시도
        try:
            user = User.objects.get(email=email)
            username = user.username  # email 기반으로 user를 찾아서 username 추출
        except User.DoesNotExist:
            messages.error(request, "해당 이메일 계정이 없습니다.")
            return redirect('login')

        user_auth = authenticate(request, username=username, password=password)
        if user_auth is not None:
            login(request, user_auth)
            return redirect('home')  # 로그인 성공 -> 홈 화면
        else:
            messages.error(request, "비밀번호가 올바르지 않습니다.")
            return redirect('login')
    else:
        # GET 요청 시 login.html 렌더링
        return render(request, 'login.html')


def user_register(request):
    """
    회원가입 뷰
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "비밀번호 확인이 일치하지 않습니다.")
            return redirect('register')

        # username은 email에서 '@' 앞부분을 따거나, 원하는 로직으로 생성
        username = email.split('@')[0]

        if User.objects.filter(email=email).exists():
            messages.error(request, "이미 등록된 이메일입니다.")
            return redirect('register')

        # create_user() -> 비밀번호 해시화 & DB 저장
        new_user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "회원가입이 완료되었습니다. 로그인 해주세요.")
        return redirect('login')
    else:
        # GET 요청 시 register.html 렌더링
        return render(request, 'register.html')


def user_logout(request):
    """
    로그아웃 후 로그인 페이지로 이동
    """
    logout(request)
    messages.success(request, "로그아웃되었습니다.")
    return redirect('login')