from django.apps import AppConfig


class SurveysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Surveys'
    verbose_name = 'Опросы'
    ordering = ['Survey', 'QuestionsBlocks', 'Questions', 'Answers']
