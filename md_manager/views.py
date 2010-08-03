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

def profilePOSTHandler(request, doctor, forms):
    """ Lida com as informacoes do request.POST enviadas via formulario 
        do perfil do usuario """

    #Salva o novo nome do medico.
    doctor.name = request.POST['name']
    doctor.save()  

    new_request = {}

    #copia os elementos do dicionario(imutavel) request.POST para um dicionario
    #mutavel.
    new_request = checkPhoneForm(request)[0]

    #Deleta os itens e campos que devem ser deletados por terem sido desmarcados
    #pelo medico.
    doc_itens = doctor.item_set.all()
    for item in doc_itens:  
        for field in item.field_set.all():
            f = field.name + '_' + item.name
            #caso o campo em questao esteja marcado no formulario e como medico ja 
            #tinha previamente ele, este campo eh deletado do dicionario
            #(para evitar duplicacoes e aumentar levemente a velocidade do algoritmo). Se nao,
            #este campo eh deletado do Banco de Dados, pois pressupoe-se que o 
            #medico tenha desmarcado esta opcao no formulario.
            if f in new_request:
                del new_request[f]
            else:
                field.delete()
        if not item.field_set.all():
            item.delete()

    doc_phones = doctor.phonenumber_set.all()
    phone_number = ''
    #faz uma copia de "forms.phone_list".
    phone_list = list(forms.phone_list) 

    #remove do dicionario "new_request" os formularios cujo numero do telefone
    #ja esteja no BD com o medico (Evitando duplicacoes).
    #E caso o telefone ja estava no BD soh que nao esta no "new_request", significa
    #que ele foi deletado. Entao, ele eh deletado do BD.
    for phone in doc_phones:
        phone_number = phone.region + phone.phone
        deleted_phone = True

        for phone_form in phone_list:
            if phone_number == new_request[phone_form.label]:
                del new_request[phone_form.label] 
                phone_list.remove(phone_form) #para aumento de desempenho
                deleted_phone = False
                break
        if deleted_phone:
            phone.delete()

    #Adiciona ao BD as informacoes adicionadas pelo medico.
    for elem in new_request:
        part = elem.partition('_')
        #Faz a lida com os itens e campos.
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
        #Faz a lida com os numeros de telefone.
        elif part[0] == 'Phone':
            phone = new_request[elem]

            region = phone[:2]
            number = phone[2:]

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
    """ Verifica se as informacoes sobre os telefones no formulario estao corretas
        Caso nao, aquele item eh removido do Request """
    new_request = request.POST.copy()

    error_messages = []

    #Se tiver mais de 10 campos para telefones as verificacoes nao sao feitas.
    for i in range(0, 10):
        phn = 'Phone_' + str(i)
        if not phn in request.POST:
            break
        if new_request[phn] == '':
            del new_request[phn]    
            continue

        if not new_request[phn].isdigit():
 #           del new_request[phn]
            error_messages.append((phn, 'Please, only digits.'))

        elif len(new_request[phn]) != 10:
#            del new_request[phn]
            error_messages.append((phn, 'Must be exact 10 digits.'))

    return (new_request, error_messages)

def profile_change(request, object_id, template_name='md_manager/md_profile_form.html'):
    #medico em questao.
    doctor = get_object_or_404(Doctor, pk=object_id)
    changed = False

    dic_form = {}
    doc_phones = doctor.phonenumber_set.all()
    num_phonef = len(doc_phones) - 1
    phonef_error_messages = []
    
    if request.method == 'POST':
        check_phoneforms = checkPhoneForm(request)
        new_request = check_phoneforms[0]
        phonef_error_messages = check_phoneforms[1]

        forms = ProfileForm(new_request)

        if not phonef_error_messages and forms.is_valid():
            profilePOSTHandler(request, doctor, forms)
            if 'addphone' in request.POST:
                forms.add_phoneNumber()
            changed = True
        if not 'addphone' in request.POST:
            num_phonef += len(forms.phone_list)
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
            phone_number = phone.region + phone.phone
            dic_form['Phone_' + str(i)] = phone_number
            i += 1
        if not doc_phones:
            dic_form['Phone_0'] = '----------'
        
        forms = ProfileForm(dic_form)

    forms.add_phoneNumber(howmany=num_phonef)

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

    for phonef in forms.phone_list:
        phone_forms.append(forms[phonef.label])

    return render_to_response(template_name, {'object': doctor, 'forms': forms, 'info_forms': info_forms,
                              'phone_forms': phone_forms, 'changed': changed,
                              'phoneform_errors': phonef_error_messages},
                              context_instance = RequestContext(request))






