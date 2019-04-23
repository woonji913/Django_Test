# from django.test import TestCase
from test_plus.test import TestCase
from django.conf import settings
from django.urls import reverse
from .models import Board
from .forms import BoardForm

#1. settings test
class SettingsTest(TestCase):
    def test_01_settings(self):
        self.assertEqual(settings.USE_I18N, True)
        self.assertEqual(settings.USE_TZ, False)
        self.assertEqual(settings.LANGUAGE_CODE, 'ko-kr')
        self.assertEqual(settings.TIME_ZONE, 'Asia/Seoul')
        
#2. Model test + ModelForm test
class BoardModelTest(TestCase):
    def test_01_model(self):
        # board = Board.objects.create(title='test title', content='test content')
        board = Board.objects.create(title='test title', content='test content', user_id=1)
        self.assertEqual(str(board), f'Board{board.pk}', msg='출력값이 일치하지 않음')
    
    def test_02_boardform(self):
        # given
        data = {'title':'제목', 'content':'내용'}
        # when then
        self.assertEqual(BoardForm(data).is_valid(), True)
    
    def test_03_boardform_without_title(self):
        # given
        data = {'content':'내용'}
        self.assertEqual(BoardForm(data).is_valid(), False)
        
    def test_04_boardform_without_content(self):
        data ={'title':'제목'}
        self.assertEqual(BoardForm(data).is_valid(), False)
    
        
#3. View test
class BoardViewTest(TestCase):
    # 반복되기 떄문에 먼저 셋업해준다.
    # 공통적인 given 상황을 구성하기 유용하다.
    def setUp(self):
        self.user = self.make_user(username='test', password='qawsdrf!')
    
    # create test 에서의 포인트는 form을 제대로 주느냐이다. 
    # 가장 기본은 get_check_200
    def test_01_get_create(self):
        # given
        # user = self.make_user(username='test', password='qawsdrf!') # 유저를 만듦(회원가입)
        # when
        with self.login(username='test', password='qawsdrf!'): # login상태 유지하게 잡아주는 것
            response = self.get_check_200('boards:create')
            # self.assertContains(response, '<form') #1)
            # then
            self.assertIsInstance(response.context['form'], BoardForm) #2) 이게 더 정확한 코드
    
    def test_02_get_create_login_required(self):
        self.assertLoginRequired('boards:create')
    
    def test_03_post_create(self):
        # given : 사용자와 작성한 글 데이터
        # user = self.make_user(username='test', password='qawsdrf!')
        data = {'title': 'test title', 'content': 'test content'}
        # when : 로그인을 해서 post요청으로 해당 url로 요청 보낸 경우
        with self.login(username='test', password='qawsdrf!'):
        # then : 글이 작성되고, 페이지가 detail로 redirect된다.
            self.post('boards:create', data=data)
    
    def test_04_board_create_without_content(self):
        # given
        data = {'title':'test title'}
        # when
        with self.login(username='test', password='qawsdrf!'):
        # then
            response = self.post('boards:create', data=data)
            self.assertContains(response, '')
            # form.is_valid()를 통과하지 못해서 튕겨져 나옴.
    # detail 페이지가 제대로 출력되는지 확인
    def test_05_detail_contains(self):
        # given
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        # board = Board.objects.create(title='제목', content='내용', user_id=1)
        # when 
        self.get_check_200('boards:detail', board_pk=board.pk)
        # then
        self.assertResponseContains(board.title, html=False)
        self.assertResponseContains(board.content, html=False)
    
    def test_06_detail_template(self):
        # given
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        # when 
        response = self.get_check_200('boards:detail', board_pk=board.pk)
        # then
        self.assertTemplateUsed(response, 'boards/detail.html')
    
    def test_07_get_index(self):
        # given when then
        self.get_check_200('boards:index')
    
    def test_08_index_template(self):
        # when then
        response = self.get_check_200('boards:index')
        self.assertTemplateUsed(response, 'boards/index.html')
    
    def test_09_index_queryset(self):
        # given - 글 2개 작성
        Board.objects.create(title='제목', content='내용', user=self.user)
        Board.objects.create(title='제목', content='내용', user=self.user)
        boards = Board.objects.order_by('-pk')
        #when
        response = self.get_check_200('boards:index')
        #then
        self.assertQuerysetEqual(response.context['boards'], map(repr, boards))
    
    def test_10_delete_get(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='qawsdrf!'):
            self.get_check_200('boards:delete', board_pk=board.pk)
    
    def test_11_delete_post(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='qawsdrf!'):
            self.post('boards:delete', board_pk=board.pk)
            self.assertEqual(Board.objects.count(), 0)
    
    def test_12_delete_redirect(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='qawsdrf!'):
            response = self.post('boards:delete', board_pk=board.pk)
            # then
            self.assertRedirect(response, reverse('boards:index'))
    
    def test_13_get_update(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='qawsdrf!'):
            response = self.get_check_200('boards:update', board.pk)
            self.assertEqual(response.context['form'].instance.pk, board.pk)
    
    def test_14_get_update_login_required(self):
        self.assertRequired('boards:update', board_pk=1)