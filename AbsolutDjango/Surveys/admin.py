from django.contrib import admin
from .models import AnswerGroup, Question, QuestionInline, Answer, UserData
from django_mptt_admin.admin import DjangoMpttAdmin
from .forms import AnswerForm, QuestionInlineForm


admin.site.register(AnswerGroup, admin.ModelAdmin)
admin.site.register(UserData, admin.ModelAdmin)


class QuestionInlineAdmin(admin.TabularInline):
    form = QuestionInlineForm
    model = QuestionInline
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionInlineAdmin]


@admin.register(Answer)
class AnswerAdmin(DjangoMpttAdmin):
    form = AnswerForm
    list_display = ['q_a', 'question', 'parent']
    list_editable = ['question', 'parent']
    tree_auto_open = False

