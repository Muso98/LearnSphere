from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from core.models import Class, School
from .models import Conversation, Message, OnlineMeeting
from django.utils import timezone

class CommunicationTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher_test', password='password123', role='teacher')
        self.parent = User.objects.create_user(username='parent_test', password='password123', role='parent')
        self.student = User.objects.create_user(username='student_test', password='password123', role='student')
        
        self.school = School.objects.create(name='Test School', address='123 Test St')
        self.class_obj = Class.objects.create(name='10-A', school=self.school)
        self.student.student_class = self.class_obj
        self.student.save()
        self.parent.children.add(self.student)

    def test_start_chat_creates_conversation(self):
        self.client.login(username='teacher_test', password='password123')
        response = self.client.get(reverse('start_chat', args=[self.parent.id]))
        
        self.assertEqual(Conversation.objects.count(), 1)
        conversation = Conversation.objects.first()
        self.assertIn(self.teacher, conversation.participants.all())
        self.assertIn(self.parent, conversation.participants.all())
        self.assertRedirects(response, reverse('chat_detail', args=[conversation.id]))

    def test_send_message(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.teacher, self.parent)
        
        self.client.login(username='teacher_test', password='password123')
        response = self.client.post(reverse('chat_detail', args=[conversation.id]), {'content': 'Hello parent'})
        
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().content, 'Hello parent')

    def test_meeting_creation_teacher(self):
        self.client.login(username='teacher_test', password='password123')
        response = self.client.post(reverse('create_meeting'), {
            'title': 'Parents Meeting',
            'class_id': self.class_obj.id,
            'start_time': '2024-12-31T10:00',
            'link': 'https://meet.google.com/abc-defg-hij'
        })
        
        self.assertEqual(OnlineMeeting.objects.count(), 1)
        meeting = OnlineMeeting.objects.first()
        self.assertEqual(meeting.title, 'Parents Meeting')
        self.assertEqual(meeting.class_obj, self.class_obj)

    def test_meeting_visibility_parent(self):
        # Create meeting for 10-A
        OnlineMeeting.objects.create(
            title='10-A Meeting',
            class_obj=self.class_obj,
            organizer=self.teacher,
            start_time=timezone.now(),
            meeting_link='http://example.com'
        )
        
        self.client.login(username='parent_test', password='password123')
        response = self.client.get(reverse('meeting_list'))
        
        self.assertContains(response, '10-A Meeting')
        
    def test_meeting_visibility_student(self):
        # Create meeting for 10-A
        OnlineMeeting.objects.create(
            title='10-A Meeting',
            class_obj=self.class_obj,
            organizer=self.teacher,
            start_time=timezone.now(),
            meeting_link='http://example.com'
        )
        
        self.client.login(username='student_test', password='password123')
        response = self.client.get(reverse('meeting_list'))
        
        self.assertContains(response, '10-A Meeting')
