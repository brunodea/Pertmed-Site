from pertmed_site.md_manager.models import Doctor, Item, Field, PhoneNumber
from pertmed_site.md_manager.forms import ProfileForm
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from pertmed_site.md_manager.macros import informations          

def index(request):
    """ For now, this is the index page of PERTMED's site. """
    return render_to_response("basic/base.html")

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
    new_request = request.POST.copy()

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
        if not item.field_set.all():
            item.delete()
        #mesmo que para os campos, so que relacionado aos itens.
#        if item.name in new_request:
#            del new_request[item.name]
#        else:
#            item.delete()
    doc_phones = doctor.phonenumber_set.all()
    phone_number = ''
    for phone in doc_phones:
        phone_number = str(phone.region) + str(phone.phone)
        deleted_phone = True
        for i in range(0, 100):
            phn = 'Phone_' + str(i)
            if not phn in new_request:
                break
            if phone_number == new_request[phn]:
                del new_request[phn]
                deleted_phone = False
                break
        if deleted_phone:
            phone.delete()

    #Adiciona um campo e/ou um item caso o medico tenha-os
    #marcado no formulario.
    for elem in new_request:
        part = elem.partition('_')
        if part[2] and part[0] != 'Phone':
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
        elif part[0] == 'Phone':
            phone = new_request[elem]
            if not phone.isdigit():
                continue

            region = int(phone[:2])
            number = int(phone[2:])
            doc_phone = doctor.phonenumber_set.filter(region=region, phone=number)   
            if not doc_phone:
                new_phone = PhoneNumber(region=region, phone=number, doctor=doctor)
                new_phone.save()
                doctor.phonenumber_set.add(new_phone)
                doctor.save()


def profile(request, object_id, template_name='md_manager/md_profile.html'):
    """ Shows the doctor's profile. """
    doctor = get_object_or_404(Doctor, pk=object_id)

    return render_to_response(template_name, {'object': doctor})


def checkPhoneForm(request):
    new_request = request.POST.copy()

    for i in range(0, 100):
        phn = 'Phone_' + str(i)
        if not phn in request.POST:
            break

        if not request.POST[phn].isdigit() or len(request.POST[phn]) != 10:
            del new_request[phn]

    return new_request
    
def profile_change(request, object_id, template_name='md_manager/md_profile_form.html'):
    #medico em questao.
    doctor = get_object_or_404(Doctor, pk=object_id)
    changed = False

    dic_form = {}
    doc_phones = doctor.phonenumber_set.all()
    
    #verifica se o formulario enviado pelo usuario eh valido e faz as acoes necessarias.
    if request.method == 'POST':
        forms = ProfileForm(checkPhoneForm(request))
        if 'addphone' in request.POST:
            forms.add_phoneNumber()

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
        i = 0
        for phone in doc_phones:
            phone_number = str(phone.region) + str(phone.phone)
            dic_form['Phone_' + str(i)] = phone_number
            i += 1
        if not doc_phones:
            dic_form['Phone_0'] = 'Phone Num'
        
        forms = ProfileForm(dic_form)

    forms.add_phoneNumber(howmany=len(doc_phones) - 1)

        

    info_forms = []
    #atualiza a lista 'info_forms' para que a forma como o formulario eh apresentado
    #seja mais maleavel no template.
    for item, fields in informations:
        f_list = []
        for field in fields:
            f = field + '_' + item
            f_list.append((field, forms[f]))
        info_forms.append(([(item, forms[item])], f_list))

    phone_forms = []
    for i in range(0, len(forms.phone_list)):
        phn = 'Phone_' + str(i)
        phone_forms.append(forms[phn])

    return render_to_response(template_name, {'object': doctor, 'forms': forms, 'info_forms': info_forms,
                              'phone_forms': phone_forms, 'changed': changed},
                              context_instance = RequestContext(request))






