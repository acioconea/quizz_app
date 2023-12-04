from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseModelForm
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from quiz.models import Question, Category
from .forms import QuestionForm, QuizForm, ChoiceFormSet
from .models import Quiz


class QuizView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = 'quiz/quiz_index.html'
    # context_object_name = 'quizzes'
    paginate_by = 5


class NewQuizView(LoginRequiredMixin, CreateView):
    model = Quiz
    fields = ['title', 'category', 'start_time', 'end_time', 'duration_minutes', 'max_score',
              'nr_of_questions']
    template_name = 'forms.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse('quiz:lista_quizuri')
        return success_url


# class UpdateQuizView(LoginRequiredMixin, UpdateView):
#     model = Quiz
#     form_class = QuizForm
#     template_name = 'quiz/update_quiz.html'
#     success_url = reverse_lazy('quiz:lista_quizuri')
#
#     def get_form_kwargs(self):
#         data = super(UpdateQuizView, self).get_form_kwargs()
#         data.update({"pk": self.kwargs['pk']})
#         return data
#
#     def get_success_url(self):
#         return reverse('quiz:lista_quizuri')


class UpdateQuizView(LoginRequiredMixin, UpdateView):

    model = Quiz
    template_name = 'quiz/update_quiz.html'
    form_class = QuizForm
    success_url = reverse_lazy('quiz:lista_quizuri')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.get_questions()
        return context

    def get_form_kwargs(self):
        data = super(UpdateQuizView, self).get_form_kwargs()
        data.update({"pk": self.kwargs['pk']})
        return data


class UpdateQuestionView(LoginRequiredMixin, UpdateView):
    model = Question
    template_name = 'quiz/update_question.html'
    form_class = QuestionForm
    success_url = reverse_lazy('quiz:update_quiz')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()
        context['choices'] = question.get_choices()
        return context

    def get_form_kwargs(self):
        data = super(UpdateQuestionView, self).get_form_kwargs()
        data.update({"pk": self.kwargs['pk']})
        return data


class AddQuestionView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'quiz/add_question.html'
    success_url = reverse_lazy('quiz:lista_quizuri')

    def form_valid(self, form):
        form.instance.quiz_id = self.kwargs['quiz_id']
        context = self.get_context_data()
        choices = context['choice_formset']

        # Ensure each form in the formset has the question_id set
        for choice_form in choices:
            choice_form.instance.question = self.object

        if form.is_valid() and choices.is_valid():
            self.object = form.save()
            choices.instance = self.object
            choices.save()

            return redirect(self.get_success_url())

        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['choice_formset'] = ChoiceFormSet(self.request.POST)
        else:
            data['choice_formset'] = ChoiceFormSet(instance=self.object)
        return data


class NewCategoryView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name']
    template_name = 'forms.html'

    def get_success_url(self):
        return reverse('quiz:categorie_noua')
