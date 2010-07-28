from pertmed_site.md_manager.models import Doctor, Item, Field
from pertmed_site.md_manager.forms import ProfileForm
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from pertmed_site.md_manager.macros import informations, info_itens, info_fields                  

def index(request):
    """ For now, this is the index page of PERTMED's site. """
    return HttpResponse("Hello world! - Index of PERTMED's site.")

def login(request):
    """ Login page maybe shouldn't be here... """
    return HttpResponse("Login Page!")

def profilePOSTHandler(request, doctor):
    """ Lida com as informacoes do request.POST enviadas via formulario 
        do perfil do usuario """

    #Salva o novo nome do medico.
    doctor.name = request.POST['name']
    doctor.save()  

    new_request = {}

    #copia os elementos do dicionario(imutavel) request.POST para um dicionario
    #mutavel.
    for elem in request.POST:
        new_request[elem] = request.POST[elem]

    doc_itens = doctor.item_set.all()
    for item in doc_itens:  
        for field in item.field_set.all():
            f = field.name + '_' + item.name
            #caso o campo em questao esteja marcado no formulario e como medico ja 
            #tinha previamente ele, este campo eh deletado do dicionario. Se nao,
            #este campo eh deletado do Banco de Dados, pois pressupoe-se que o 
            #medico tenha desmarcado esta opcao no formulario.
            if f in new_request:
                del new_request[f]
            else:
                field.delete()
        #mesmo que para os campos, so que relacionado aos itens.
        if item.name in new_request:
            del new_request[item.name]
        else:
            item.delete()
    
    #Adiciona um campo e/ou um item caso o medico tenha-os
    #marcado no formulario.
    for elem in new_request:
        part = elem.partition('_')
        if part[2]:
            doc_item = doctor.item_set.filter(name=part[2])
            if not doc_item:
                item = Item(name=part[2], doctor=doctor)
                item.save()
                field = Field(name=part[0], item=item)
                field.save()
                item.field_set.add(field)
                item.save()
                doctor.item_set.add(item)
                doctor.save()
            else:
                item_field = doc_item[0].field_set.filter(name=part[0])
                if not item_field:
                    field = Field(name=part[0], item=doc_item[0])
                    field.save()
                    doc_item[0].field_set.add(field)
                    doc_item[0].save()

def profile(request, object_id, template_name='md_manager/md_profile.html'):
    """ Shows the doctor's profile. """
    doctor = get_object_or_404(Doctor, pk=object_id)
           
    return render_to_response(template_name, {'object': doctor})


def profile_change(request, object_id, template_name='md_manager/md_profile_form.html'):
    #pega-se o medico em questao.
    doctor = get_object_or_404(Doctor, pk=object_id)
    changed = False
    
    #verifica se o formulario enviado pelo usuario eh valido e faz as acoes necessarias.
    if request.method == 'POST':
        forms = ProfileForm(request.POST)
        if forms.is_valid():
            profilePOSTHandler(request, doctor)
            changed = True
    else:
        dic_form = {'name': doctor.name}
        #o dicionario 'dic_form' eh atualizado para que as opcoes ja relacionadas
        #ao medico em questao estejam marcadas no formulario.
        for item in doctor.item_set.all():
            dic_form[item.name] = [u'on']
            for field in item.field_set.all():
                name = field.name + '_' + item.name
                dic_form[name] = [u'on']
        forms = ProfileForm(dic_form)

    info_forms = []
    #atualiza a lista 'info_forms' para que a forma como o formulario eh apresentado
    #seja mais maleavel no template.
    for item, fields in informations:
        #eh uma lista de triplas. O primeiro elemento eh o rotulo, o segundo eh
        #o campo em si, e o terceiro eh um booleano para distinguir entre o que 
        #eh Item e o que nao eh.
        #info_forms.append((item, forms[item], True))
        f_list = []
        for field in fields:
            f = field + '_' + item
            f_list.append((field, forms[f]))
        info_forms.append(([(item, forms[item])], f_list))

    return render_to_response(template_name, {'object': doctor, 'forms': forms, 'info_forms': info_forms,
                              'changed': changed},
                              context_instance = RequestContext(request))






