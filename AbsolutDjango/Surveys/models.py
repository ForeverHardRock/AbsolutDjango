from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from unidecode import unidecode

answer_types = (
    ('select', 'Пункты'),
    ('input', 'Ввод'),
    ('choice', 'Выбор'),
)
question_variables = (
    ('independent', 'Самостоятельный'),
    ('simple', 'Для группы'),
)


# модель для группы вопросов
class AnswerGroup(models.Model):
    group_title = models.CharField(max_length=100, verbose_name='Название блока')
    questions = models.ManyToManyField('Question', verbose_name='Вопросы',
                                       limit_choices_to={'question_type': 'simple'})

    class Meta:
        verbose_name = 'блок'
        verbose_name_plural = 'блоки'

    def __str__(self):
        return self.group_title


# модель для инлайновых ответов к вопросам
class QuestionInline(models.Model):
    question_object = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='inline_question')
    answer = models.CharField(max_length=255, verbose_name='Ответ', null=True, blank=True)

    class Meta:
        verbose_name = 'вариант ответа'
        verbose_name_plural = 'варианты ответа'

    def __str__(self):
        return self.question_object.text


# модель вопросов
class Question(models.Model):
    text = models.CharField(max_length=200, verbose_name='Вопрос')
    answer_type = models.CharField(max_length=10, choices=answer_types, default='choice', verbose_name='Тип ответа')
    not_null = models.BooleanField(default=True, verbose_name='Ответ обязателен')
    question_type = models.CharField(max_length=15, default='independent', choices=question_variables,
                                     verbose_name='Тип вопроса')

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self):
        return self.text


# модель опроса
class Answer(MPTTModel):
    text = models.CharField(max_length=200, verbose_name='Ответ', null=True, blank=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, verbose_name='Вопрос',
                                 limit_choices_to={'question_type': 'independent'}, null=True, blank=True)
    group = models.ForeignKey('AnswerGroup', on_delete=models.CASCADE, verbose_name='Группа вопросов',
                              null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                            verbose_name='Предыдущий ответ')
    q_a = models.TextField(verbose_name='Вопрос - ответ')
    slug = models.CharField(max_length=200, unique=True, verbose_name='URL', null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['text']

    class Meta:
        verbose_name = 'вопрос - ответ'
        verbose_name_plural = 'опросы'

    def __str__(self):
        return self.q_a

    def clean(self):
        super().clean()
        if not self.parent:
            if not self.question:
                raise ValidationError({'question': 'Это обязательное поле.'})
            if self.question.answer_type != 'choice':
                raise ValidationError({'question': 'Тип вопроса должен быть "Выбор".'})
            if not self.text:
                raise ValidationError({'text': 'Это обязательное поле.'})

        if not self.question and not self.group:
            raise ValidationError({'question': 'Одно из полей должно быть заполнено.',
                                   'group': 'Одно из полей должно быть заполнено.'})

        if self.question:
            if self.question.answer_type == 'choice':
                if not self.text:
                    raise ValidationError({'text': 'Это обязательное поле.'})

            if self.question.answer_type == 'select':
                if self.parent.get_descendant_count() > 0 and self.pk is None:
                    raise ValidationError(
                        'У вопросов с выбором пунктов может быть только один ответ с множеством вариантов ответов')

    def save(self, *args, **kwargs):
        if not self.parent:
            self.slug = slugify(unidecode(self.text))
        super().save(*args, **kwargs)
        if self.question:
            if self.question.answer_type == 'select':
                try:
                    inlines = QuestionInline.objects.filter(question_object=self.question)
                except:
                    inlines = None
                if inlines:
                    self.text = ', '.join(list(inlines.values_list('answer', flat=True)))

            elif self.question.answer_type == 'input':
                self.text = 'Ввод'

            self.q_a = f'{self.question} - {self.text}'
        if self.group:
            if self.question:
                self.q_a += f' + {self.group.group_title}'
            else:
                self.q_a = self.group.group_title
        super().save(*args, **kwargs)


# модель для хранения пройденных опросов
class UserData(models.Model):
    user = models.CharField(max_length=100, verbose_name='Пользователь', default='test')
    data = models.JSONField(verbose_name='Данные опроса')

    class Meta:
        verbose_name = 'результат опроса'
        verbose_name_plural = 'результаты опроса'

    def __str__(self):
        return self.user