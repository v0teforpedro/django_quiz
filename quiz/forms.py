from django import forms
from django.core.exceptions import ValidationError

from quiz.models import Choice


class QuestionInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        if not (self.instance.QUESTION_MIN_LIMIT <= len(self.forms) <= self.instance.QUESTION_MAX_LIMIT):
            raise ValidationError(
                f'Кол-во вопросов должно быть в диапазоне '
                f'от {self.instance.QUESTION_MIN_LIMIT} '
                f'до {self.instance.QUESTION_MAX_LIMIT}'
            )

        # излишний валидатор проверки:
        # "максимального значения order_num - должно быть не более максимально допустимого кол-ва вопросов"
        if len(self.forms) > self.instance.QUESTION_MAX_LIMIT:
            raise ValidationError(f'Максимальное количество вопросов {self.instance.QUESTION_MAX_LIMIT}')

        # валидатор проверки:
        # "корректности заполнения order_num(должен быть от 1 до N, и увеличиваться на 1)"
        order_start = 1
        for form in self.forms:
            if form.instance.order_num == order_start:
                order_start += 1
            else:
                raise ValidationError(f'Все вопросы должны идти по порядку')


class ChoiceInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        # lst = []                                                                                option 1
        # for form in self.forms:
        #     if form.cleaned_data['is_correct']:
        #         lst.append(1)
        #     else:
        #         lst.append(0)
        # num_correct_answers = sum(lst)
        #
        # num_correct_answers = sum(1 for form in self.forms if form.cleaned_data['is_correct'])  option 2

        num_correct_answers = sum(form.cleaned_data['is_correct'] for form in self.forms)

        if num_correct_answers == 0:
            raise ValidationError('Необходимо выбрать как минимум 1 вариант.')

        if num_correct_answers == len(self.forms):
            raise ValidationError('НЕ разрешено выбирать все варианты')


class ChoiceForm(forms.ModelForm):
    is_selected = forms.BooleanField(required=False)

    class Meta:
        model = Choice
        fields = ['text']


ChoicesFormSet = forms.modelformset_factory(
    model=Choice,
    form=ChoiceForm,
    extra=0
)
