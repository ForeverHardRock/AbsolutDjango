from django.shortcuts import render, redirect
from .models import Answer, QuestionInline, UserData


# домашняя страница
def home_view(request):
    if request.method == 'POST':
        identity = request.POST.get('identity')
        if identity:
            return redirect('survey_list')
    return render(request, 'Surveys/home.html')


# страница с опросами
def survey_list_view(request):
    surveys = Answer.objects.exclude(slug=None).values('slug', 'text')
    context = {
        'surveys': surveys,
    }
    return render(request, 'Surveys/home.html', context=context)


# страница с опросом
def survey_view(request, survey_slug: str):
    survey = Answer.objects.get(slug=survey_slug)  # Объект опроса
    slug = survey.slug  # URL опроса
    success = None

    if request.method == 'POST':
        # print(request.POST.dict())

        # если отправляем заполненную форму
        if 'total_form' in request.POST and 'back' not in request.POST:
            total_form = request.POST.get('total_form')
            total_data = eval(total_form)
            UserData.objects.create(user='test', data=total_data)
            success = 'Результаты опроса сохранены!'
            context = {
                'title': survey.text,
                'slug': slug,
                'success': success,
                'width': 100,
            }
            return render(request, 'Surveys/survey.html', context=context)

        else:

            post_data = request.POST.get('form_data')
            form_data = eval(post_data)

            # если нажали назад
            if 'back' in request.POST:
                post_pk = request.POST.get('back')  # Получение ID предыдущего шага
                survey = Answer.objects.get(pk=post_pk)  # Получение предыдущего шага
                form_data.pop(survey.level+1)

            # если ответили на вопрос
            elif 'answer' in request.POST:
                post_pk = request.POST.get('answer')  # Получение ID вложенного ответа из опроса
                survey = Answer.objects.get(pk=post_pk)  # Получение следующего шага
                post_level = survey.level

                # если на этапе был вопрос, разбираем данные
                if 'question' in request.POST:
                    post_question = request.POST.get('question')
                    post_answer = None
                    if 'choice' in request.POST:
                        post_answer = survey.text

                    elif 'select[]' in request.POST:
                        post_answer = request.POST.getlist('select[]')

                    elif 'input' in request.POST:
                        post_answer = request.POST.get('input')
                    form_data[post_level] = {post_question: post_answer}

                # если на этапе была группа вопросов, разбираем данные
                if 'group_title' in request.POST:
                    post_group_title = request.POST.get('group_title')
                    q_and_a = {}
                    if 'group_choice[]' in request.POST:
                        post_answers = request.POST.getlist('group_choice[]')
                        for post_answer in post_answers:
                            q_a_data = post_answer.split('|')
                            q_and_a.update({q_a_data[0]: q_a_data[1]})

                    if 'group_select[]' in request.POST:
                        post_answers = request.POST.getlist('group_select[]')
                        group_select_answers = []
                        group_select_question = None
                        for post_answer in post_answers:
                            q_a_data = post_answer.split('|')
                            group_select_question = q_a_data[0]
                            group_select_answers.append(q_a_data[1])
                        q_and_a.update({group_select_question: group_select_answers})

                    if 'group_input[]' in request.POST:
                        post_answers = request.POST.getlist('group_input[]')
                        for i in range(int(len(post_answers)/2)):
                            group_question = post_answers[i*2]
                            group_answer = post_answers[i*2+1]
                            q_and_a.update({group_question: group_answer})

                    if 'question' in request.POST:
                        form_data[post_level].update({post_group_title: q_and_a})
                    else:
                        form_data[post_level] = {post_group_title: q_and_a}

    else:
        form_data = {}
    parent = survey.parent
    if parent:
        parent_pk = parent.pk
    else:
        parent_pk = None
    answers = survey.get_children()  # Получение доступных ответов
    answer_pk = None
    question = None
    group = None
    group_title = None
    total_form = None

    # если переход на вопрос, то готовим данные для отображения
    if answers:
        question = answers[0].question  # Текущий вопрос

        answer_pk = answers[0].pk  # ID ответа для следующего уровня
        group = answers[0].group  # Текущая группа
        answer_level = answers[0].level  # Уровень вложенности

        # если на этапе есть вопрос, готовим его данные
        if question:
            answer_type = question.answer_type  # Тип ответа на текущий вопрос

            if answer_type == 'select':
                answers = answers[0].text.split(', ')  # Подготовка ответов для типа select
            if answer_type != 'choice':
                pass

        # если на этапе есть группа, готовим ее данные
        if group:
            group_title = group.group_title  # Название группы
            group = group.questions.all()  # Вопросы группы

            if not question:
                answer_pk = answers[0].pk  # Если группа без основного вопроса, получаем ID следующего уровня

            for group_question in group:  # Подготовка ответов, если в группе есть вопрос с пунктами
                if group_question.answer_type != 'input':
                    answer_inlines = QuestionInline.objects.filter(question_object=group_question.pk).values_list('answer', flat=True)
                    group_question.answer_inlines = list(answer_inlines)

        max_level = max(survey.get_descendants(include_self=False).values_list('level', flat=True))  # Максимальная вовзможная вложенность на текущей ветке
        width = int(100 / (max_level + 1) * answer_level)  # Шкала прогресса

    # если на все вопросы ответили
    else:
        width = 100

        stages = form_data.values()
        total_form = []

        # подготовка данных для отображения в превью
        for stage in stages:
            for que, value in zip(stage.keys(), stage.values()):
                if isinstance(value, dict):
                    value_form = []
                    for val_que, val_value in zip(value.keys(), value.values()):
                        if isinstance(val_value, list):
                            value_form.append({'que': val_que, 'value_list': val_value})
                        else:
                            value_form.append({'que': val_que, 'value': val_value})
                    total_form.append({'que': que, 'value_list': value_form})
                elif isinstance(value, list):
                    total_form.append({'que': que, 'value_list': value})
                else:
                    total_form.append({'que': que, 'value': value})

    context = {
        'title': survey.text,
        'answers': answers,
        'question': question,
        'group': group,
        'group_title': group_title,
        'width': width,
        'slug': slug,
        'pk': answer_pk,
        'parent_pk': parent_pk,
        'form_data': form_data,
        'total_form': total_form,
        'success': success,
    }
    return render(request, 'Surveys/survey.html', context=context)

