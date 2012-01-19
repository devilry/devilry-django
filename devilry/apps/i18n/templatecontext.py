def template_variables(request):
    return {'DEVILRY_I18N_CURRENT_LOCALE': request.currentlocale}
