from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.utils.html import escape
from unittest import skip

from newspush.models import StudentInfo, News, Academy, NewsComment
import json

class NewsAcquisitionViewTest(TestCase):
    @skip
    def test_can_fetch_news_list_by_time(self):
        academy_ = Academy.objects.create()
        news_ = News.objects.create(academy=academy_,title='Test title',sourceURL='Test sourceURL',picURL_Path='Test picURL_Path',originURL='Test originURL')
        d = str(news_.time.year)+str(news_.time.month)+str(news_.time.day)
        response = self.client.post(
            '/news/%d/%d/' % (news_.id,d),
            data=self.get_test_comment()
        )
        date_time = NewsComment.objects.first().time.isoformat()
        self.assertEqual(response.status_code, 200)
        # print(response.content)
        # print(NewsComment.objects.first().time)
        true_json = {
                        'model': 'newspush.news',
                        'pk': 1,
                        'fileds': {
                            'academy': 1,
                            'title': 'Test title',
                            'time': date_time,
                            'sourceURL': 'Test sourceURL',
                            'picURL_Path': 'Test picURL_Path',
                            'originURL': 'Test originURL',
                            'accessNum': 0
                        }
                    }

        actual_json = json.loads(response.content.decode('utf8'))
    def test_can_fetch_news_list_by_academic(self):
        pass

    def test_can_fetch_news_list_by_search_keys(self):
        pass

    def test_can_fetch_specific_news(self):
        pass

class CommentCommitViewTest(TestCase):
    def get_test_comment(self):
        return {
            'content': 'this is a comment for test.',
            'ip': '8.8.8.8',
        }

    def test_can_commit_and_save_a_comment(self):
        academy_ = Academy.objects.create()
        news_ = News.objects.create(academy=academy_)
        stu_ = StudentInfo.objects.create(studentID='2014141466666')
        response = self.client.post(
            '/comments/commit/%d/%s/' % (news_.id, stu_.studentID),
            data=self.get_test_comment()
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(NewsComment.objects.count(), 1)
        new_comment = NewsComment.objects.first()
        self.assertEqual(new_comment.content, self.get_test_comment()['content'])
        self.assertEqual(new_comment.ip, self.get_test_comment()['ip'])

    def test_cannot_commit_comment_with_wrong_news_id(self):
        stu_ = StudentInfo.objects.create(studentID='2014141466666')
        response = self.client.post(
            '/comments/commit/123/%s/' % (stu_.studentID,),
            data=self.get_test_comment()
        )
        self.assertEqual(response.status_code, 404)

    def test_cannot_commit_comment_with_wrong_student_id(self):
        academy_ = Academy.objects.create()
        news_ = News.objects.create(academy=academy_)
        response = self.client.post(
            '/comments/commit/%d/2014141466666/' % (news_.id, ),
            data=self.get_test_comment()
        )
        self.assertEqual(response.status_code, 403)


class CommentsAcquisitionViewTest(TestCase):
    def test_can_fetch_comments_by_news_id(self):
        academy_ = Academy.objects.create()
        news_ = News.objects.create(academy=academy_)
        stu_ = StudentInfo.objects.create(studentID='2014141466666')

        NewsComment.objects.create(
            news=news_,
            studentInfo=stu_,
            content='Test comment',
            ip='8.8.8.8'
        )
        date_time = NewsComment.objects.first().time.isoformat()

        response = self.client.get('/comments/%d/' % (news_.id, ))
        # print(date_time)
        # print(response.content)
        self.assertEqual(response.status_code, 200)
        # print(response.content)
        # print(NewsComment.objects.first().time)
        true_json = {
                        'model': 'newspush.newscomment',
                        'pk': 1,
                        'fileds': {
                            'news': 1,
                            'studentInfo': '2014141466666',
                            'content': 'Test comment',
                            'ip': '8.8.8.8',
                            'time': date_time,
                            'likes': 0,
                            'dislikes': 0
                        }
                    }

        actual_json = json.loads(response.content.decode('utf8'))
        # del actual_json['fields']['time']
        # for key, value in actual_json:
        #     assertEqual(true_json[key], value)

    def test_cannot_fetch_news_by_wrong_news_id(self):
        response = self.client.get('/comments/123/')
        self.assertEqual(response.status_code, 404)

class AccountViewTest(TestCase):
    @skip
    def test_can_login(self):
        self.client.post(
            '/login/',
            data={
                'scu_id': '2014141462274',
                'password': 'mypassword',
                'nickname': 'xmh',
            }
        )
        self.assertEqual(StudentInfo.objects.count(), 1)
        stud = StudentInfo.objects.first()
        self.assertEqual(stud.name, '谢明浩')
        self.assertEqual(stud.nickname, 'xmh')

    def test_can_logout(self):
        stu_ = StudentInfo.objects.create(studentID='2014141466666')
        self.assertEqual(StudentInfo.objects.count(), 1)
        response = self.client.get('/logout/2014141466666/')
        self.assertEqual(StudentInfo.objects.count(), 0)

class NoticesViewTest(TestCase):
    def test_can_fetch_notices_list_by_time(self):
        pass

class DataUpdateViewTest(TestCase):
    def test_can_receive_a_new_data(self):
        pass
