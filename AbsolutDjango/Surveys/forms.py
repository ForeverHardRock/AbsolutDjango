from django import forms
from .models import Answer, QuestionInline


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['question', 'text', 'group', 'parent']
        labels = {
            'question': 'Вопрос',
            'text': 'Ответ',
            'group': 'Группа вопросов',
            'parent': 'Предыдущий ответ',
        }


class QuestionInlineForm(forms.ModelForm):
    class Meta:
        model = QuestionInline
        fields = ['question_object', 'answer']
        labels = {
            'question_object': 'Вопрос',
            'answer': 'Ответ',
        }


