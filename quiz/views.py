from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ChoicesFormSet
from .models import Exam, Question, Result


class ExamListView(ListView):
    model = Exam
    template_name = 'exams/list.html'
    context_object_name = 'exams'


class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    template_name = 'exams/details.html'
    context_object_name = 'exam'
    pk_url_kwarg = 'uuid'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')

        return self.model.objects.get(uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result_list'] = Result.objects.filter(
            exam=self.get_object(),
            user=self.request.user
        ).order_by('state', '-create_timestamp')

        return context


class ExamResultCreateView(LoginRequiredMixin, CreateView):
    def post(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        result = Result.objects.create(
            user=request.user,
            exam=Exam.objects.get(uuid=uuid),
            state=Result.STATE.NEW,
            current_order_number=0
        )

        result.save()

        return HttpResponseRedirect(
            reverse(
                'quiz:question',
                kwargs={
                    'uuid': uuid,
                    'res_uuid': result.uuid,
                    'order_num': 1
                }
            )
        )


class ExamResultQuestionView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        order_num = kwargs.get('order_num')
        question = Question.objects.get(
            exam__uuid=uuid,
            order_num=order_num
        )

        choices = ChoicesFormSet(queryset=question.choices.all())

        return render(request, 'exams/question.html', context={'question': question, 'choices': choices})

    def post(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        res_uuid = kwargs.get('res_uuid')
        order_num = kwargs.get('order_num')

        question = Question.objects.get(
            exam__uuid=uuid,
            order_num=order_num
        )
        choices = ChoicesFormSet(data=request.POST)
        selected_choices = ['is_selected' in form.changed_data for form in choices.forms]
        result = Result.objects.get(uuid=res_uuid)
        result.update_result(order_num, question, selected_choices)

        if result.state == Result.STATE.FINISHED:
            return HttpResponseRedirect(
                reverse(
                    'quiz:result_details',
                    kwargs={
                        'uuid': uuid,
                        'res_uuid': result.uuid
                    }
                )
            )

        return HttpResponseRedirect(
            reverse(
                'quiz:question',
                kwargs={
                    'uuid': uuid,
                    'res_uuid': res_uuid,
                    'order_num': order_num + 1
                }
            )
        )


class ExamResultDetailView(LoginRequiredMixin, DetailView):
    model = Result
    template_name = 'results/details.html'
    context_object_name = 'result'
    pk_url_kwarg = 'uuid'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('res_uuid')

        return self.get_queryset().get(uuid=uuid)


class ExamResultUpdateView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        res_uuid = kwargs.get('res_uuid')
        user = request.user

        result = Result.objects.get(
            user=user,
            uuid=res_uuid,
            exam__uuid=uuid,
        )

        return HttpResponseRedirect(
            reverse(
                'quiz:question',
                kwargs={
                    'uuid': uuid,
                    'res_uuid': result.uuid,
                    'order_num': result.current_order_number + 1
                }
            )
        )


# class ExamResultDeleteView(LoginRequiredMixin, DeleteView):
#     pass
