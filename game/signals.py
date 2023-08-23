from django.db.models.signals import m2m_changed

from quiz.exceptions import HintTimeConflict

from .models import Question


""" def before_hint_was_add(sender, **kwargs):
    hint_class = kwargs['model']
    
    queryset = hint_class.objects.filter(
        pk__in=kwargs['pk_set'],
        appear_after__gt=kwargs['instance'].time
    )
    
    print(f'quesry set in signal: {queryset}')
    
    if len(queryset) != 0:
        raise HintTimeConflict('''
            Time after which hint should be apper in question (hint.appear_after) field,
            greater then time what this question lasts (question.time) field
        ''')


m2m_changed.connect(before_hint_was_add, sender=Question.hints.through, action='pre_add') """
