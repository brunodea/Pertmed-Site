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

    new_request = {}
    #copia os elementos do dicionario(imutavel) request.POST para um dicionario
    #mutavel.
    new_request = request.POST.copy()

    #Salva o novo nome do medico.
    doctor.name = new_request['name']
    doctor.save()  

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
            try:
                del new_request[f]
            except KeyError:
                field.delete()

        if not item.field_set.all():
            item.delete()

    doc_phones = doctor.phonenumber_set.all()

    phone_number = ''

    #remove do dicionario "new_request" os formularios cujo numero do telefone
    #ja esteja no BD com o medico (Evitando duplicacoes).
    #E caso o telefone ja estava no BD soh que nao esta no "new_request", significa
    #que ele foi deletado. Entao, ele eh deletado do BD.

    for phone in doc_phones:
        phone_number = phone.region + phone.phone
        deleted_phone = True

        for elem in new_request:
            if elem.startswith('Phone_') and phone_number == new_request[elem]:
                del new_request[elem] 
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

def checkPhoneForm(request):
    """ Verifica se as informacoes sobre os telefones no formulario estao corretas 
        e retorna uma lista com os possiveis erros """
    error_messages = []
    success_messages = []

    #Se tiver mais de 30 campos para telefones as verificacoes do excedente nao sao feitas.
    for i in range(0, 30):
        phn = 'Phone_' + str(i)
        try:
            if request.POST[phn] == '':
                error_messages.append((phn, 'Can\'t be empty.'))

            elif not request.POST[phn].isdigit():
                error_messages.append((phn, 'Please, only digits.'))

            elif len(request.POST[phn]) != 10:
                error_messages.append((phn, 'Must be exact 10 digits.'))
        
            elif request.POST.values().count(request.POST[phn]) >= 2:
                error_messages.append((phn, 'Phone number repeated.'))        
            else:              
                success_messages.append(phn)

        except KeyError:
            continue

    return (error_messages, success_messages)

def profile(request, object_id, template_name='md_manager/md_profile.html'):
    """ Mostra o perfil do medico e permite sua alteracao. """
    doctor = get_object_or_404(Doctor, pk=object_id)
    changed = False

    dic_form = {}

    phonef_error_messages = []  
    phonef_success_messages = []
    
    if request.method == 'POST':   
        messages =  checkPhoneForm(request)     
        phonef_error_messages = messages[0]
        phonef_success_messages = messages[1]

        new_request = {}
        phone_elems = []
        
        for elem in request.POST:
            if not elem.startswith('Phone_'):
                new_request[elem] = request.POST[elem]
            else:
                phone_elems.append((request.POST[elem], int(elem.partition('_')[2])))

        phone_elems = sorted(phone_elems, key=lambda e: e[1])
        for i in range(0, len(phone_elems)):
            new_request['Phone_' + str(i)] = phone_elems[i][0]
             
        forms = ProfileForm(new_request)

        if not phonef_error_messages and forms.is_valid():
            profilePOSTHandler(request, doctor, forms)
            changed = True
    else:
        dic_form = {'name': doctor.name}
        #o dicionario 'dic_form' eh atualizado para que as opcoes ja relacionadas
        #ao medico em questao estejam marcadas no formulario.

        for item in doctor.item_set.all():
            for field in item.field_set.all():
                name = field.name + '_' + item.name
                dic_form[name] = [u'on']

        i = 0
        for phone in doctor.phonenumber_set.all():
            phone_number = phone.region + phone.phone
            dic_form['Phone_' + str(i)] = phone_number
            i += 1
        
        forms = ProfileForm(dic_form)
    
    doc_itens_fields = doctor.sorted_itens_fields()

    #phonef_error_messages soh tem elementos se entrou no if anterior. Com isso,
    #o metodo do request com certeza eh post.
    if phonef_error_messages: #and request.method == 'POST'
        num_phonef = len(phone_elems)
    else:
        num_phonef = len(doctor.phonenumber_set.all())  
    forms.add_phoneNumber(howmany=num_phonef)

    info_forms = []
    #atualiza a lista 'info_forms' para que a forma como o formulario eh apresentado
    #seja mais maleavel no template.
    for item, fields in informations:
        f_list = []
        for field in fields:
            f = field + '_' + item
            f_list.append((field, forms[f]))
        info_forms.append((item, f_list))
    phone_forms = []

    for phonef in forms.phone_list:
        phone_forms.append(forms[phonef.label])

    return render_to_response(template_name, {'object': doctor, 'forms': forms, 'info_forms': info_forms,
                              'phone_forms': phone_forms, 'changed': changed,
                              'phoneform_errors': phonef_error_messages,
                              'phoneform_success': phonef_success_messages,
                              'object_itens_fields': doc_itens_fields},
                              context_instance = RequestContext(request))


###################TODO CADASTRO DE NOVOS MEDICOS.####################################




