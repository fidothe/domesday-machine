from django.template import Library, Node

register = Library()

def field_errors(field):
    return {'errors': field.errors}

register.inclusion_tag('domes/templatetags/field_errors.html')(field_errors)

def form_errors(form):

    has_field_errors = False
    
    #Any field errors?
    for field in form:
        if field.errors:
            has_field_errors = True
            break
    
    return {'has_field_errors': has_field_errors, 'form': form}

register.inclusion_tag('domes/templatetags/form_errors.html')(form_errors)