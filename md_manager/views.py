# Lida com os templates e seus formularios.


######## Importacoes necessarias #############

from pertmed_site.md_manager.models import Doctor, Item, Field, PhoneNumber
from pertmed_site.md_manager.macros import informations, info_itens    
from pertmed_site.md_manager.forms import ProfileForm, SignupForm, UserCreationFormExtended
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth

###############################################


def index(request):
    """ Renderiza a pagina inicial do site. """

    #Se o usuario estiver logado, ao inves de aparecer a opcao de login no menu,
    #seu nome eh mostrado.
    user = request.user
    if user.is_authenticated():
        try:
            doctor = Doctor.objects.get(name=user.get_full_name())
        except Doctor.DoesNotExist:
            pass
    else:
        doctor = []

    return render_to_response("basic/base.html", {'object': user}, context_instance = RequestContext(request))

def profilePOSTHandler(request, doctor, forms):
    """ Lida com as informacoes do request.POST enviadas via formulario 
        para alteracao do perfil do usuario """
    user = request.user
    user.first_name = request.POST['first_name'] 
    user.last_name  = request.POST['last_name']
    user.email = request.POST['email']
    user.save() #salva os novos nome e email do usuario.

    #Deleta os itens e campos que devem ser deletados por terem sido desmarcados
    #pelo medico.
    doc_itens = doctor.item_set.all()
    for item in doc_itens:  
        for field in item.field_set.all():
            f = field.name + '_' + item.name
            #caso o campo 'f' nao esteja marcado no formulario, ele eh deletado do BD.
            if not f in request.POST:
                field.delete()
        #caso o item em questao nao tenha nenhum campo associado a ele, este eh deletado.
        if not item.field_set.all():
            item.delete()

    doc_phones = doctor.phonenumber_set.all()

    phone_number = ''

    #caso o telefone em questao nao esta presente no request, significa que ele
    #foi descartado pelo medico, entao eh deletado do BD.
    for phone in doc_phones:
        phone_number = phone.region + phone.phone
        deleted_phone = True

        for elem in request.POST:
            if elem.startswith('Phone_') and phone_number == request.POST[elem]:
                deleted_phone = False
                break
        if deleted_phone:
            phone.delete()

    #Adiciona ao BD as informacoes adicionadas pelo medico.
    for elem in request.POST:
        part = elem.partition('_')
        #se o terceiro elemento da tripla "part" existir e constar na lista
        #de 'itens' do CCR, significa que se trata de um 'field'.
        if part[2] and part[2] in info_itens:
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
        #Se o primeiro elemento da tripla 'part' for "Phone", significa que se trata
        #de um telefone.
        elif part[0] == 'Phone':
            phone = request.POST[elem]

            #como o telefone passado eh um numero de 10digitos, os dois primeiros
            #representam o numero da regiao e o resto o numero do telefone propriamente dito.
            region = phone[:2]
            number = phone[2:]

            doc_phone = doctor.phonenumber_set.filter(region=region, phone=number)   
            if not doc_phone:
                new_phone = PhoneNumber(region=region, phone=number, doctor=doctor)
                new_phone.save()
                doctor.phonenumber_set.add(new_phone)
                doctor.save()

def phoneFormErrors(label, phone_number):
    """ Realiza alguns testes verificando se o campo do formulario de um telefone
        nao contem erros. Erros possiveis:
        1)Ser vazio; 2)Nao conter apenas numeros e 3)Ter um numero de digitos diferente de 10.
        Se tudo estiver certo, uma string vazia eh retornada. Se nao, uma tupla com o rotulo daquele
        campo do formulario e a mensagem de erro eh retornada."""
    error_message = ''    

    if phone_number == '':
        error_message = (label, 'Can\'t be empty.')

    elif not phone_number.isdigit():
        error_message = (label, 'Please, only digits.')

    elif len(phone_number) != 10:
        error_message = (label, 'Must be exact 10 digits.')
  
    return error_message


def checkPhoneForm(request):
    """ Verifica se as informacoes sobre os telefones no formulario estao corretas 
        e retorna uma lista com os possiveis erros """
    error_messages = []
    success_messages = []

    if request.method != 'POST':
        return (error_messages, success_messages)

    #Se tiver mais de 30 campos para telefones as verificacoes do excedente nao sao feitas.
    for i in range(0, 30):
        phn = 'Phone_' + str(i)
        try:
            message = phoneFormErrors(phn, request.POST[phn])
            if message:
                error_messages.append(message)

            elif request.POST.values().count(request.POST[phn]) >= 2:
                error_messages.append((phn, 'Phone number repeated.'))   

        except KeyError:
            continue

    return (error_messages, success_messages)

def verifyNameAndEmail(email, name):
    """ Verifica se o nome e email passados como parametro ja existem no BD.
        Retorna uma tupla com o nome do campo incorreto e a mensagem do erro. """

    error = ''
    if email in [umails.email for umails in User.objects.all()]:
        error = ('email', 'Email already registered.')

    elif name in [dname.name for dname in Doctor.objects.all()]:
        error = ('name', 'Name already registered.')

    return error

@login_required
def profile(request, template_name='md_manager/md_profile.html'):
    """ Mostra o perfil do medico e permite sua alteracao. """
    user = request.user
  
    doctor =  user.doctor_set.get()
    doctor = get_object_or_404(Doctor, pk=doctor.id)

    changed = False

    dic_form                = {}
    name_email_error        = []
    phonef_error_messages   = []  
    phonef_success_messages = []
    
    if request.method == 'POST':   
        messages = checkPhoneForm(request)     
        phonef_error_messages = messages[0]
        phonef_success_messages = messages[1]

        new_request = {}
        phone_elems = []
        
        #gera uma lista de tuplas com o numero do telefone e o valor da label que o identifica.
        #Os elementos que vao para essa lista nao sao adicionados ao new_request.
        for elem in request.POST:
            if not elem.startswith('Phone_'):
                new_request[elem] = request.POST[elem]
            else:
                phone_elems.append((request.POST[elem], int(elem.partition('_')[2])))

        #essa lista eh entao ordenada de acordo com o valor do seguno elemento das tuplas.
        phone_elems = sorted(phone_elems, key=lambda e: e[1])
        #entao os elementos ordenados dessa lista sao adicionados ao new_request,
        #com seu label modificado para a sua posicao na lista.
        for i in range(0, len(phone_elems)):
            new_request['Phone_' + str(i)] = phone_elems[i][0]
             
        forms = ProfileForm(new_request)

        if not request.POST['first_name'] + ' ' + request.POST['last_name'] == request.user.get_full_name() or not request.POST['email'] == request.user.email:
            name_email_error = verifyNameAndEmail(request.POST, request.POST['email'],
                request.POST['first_name'] + ' ' + request.POST['last_name']) 

        if not phonef_error_messages and not name_email_error and forms.is_valid():
            profilePOSTHandler(request, doctor, forms)
            changed = True
    else:
        dic_form = {}
        #o dicionario 'dic_form' eh atualizado para que as opcoes ja relacionadas
        #ao medico estejam marcadas no formulario.
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
    #adiciona o numero adequado de campos para telefone ao formulario.
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
    #lista com os campos do formulario para os telefones.
    for phonef in forms.phone_list:
        phone_forms.append(forms[phonef.label])
    
    user_form = UserCreationFormExtended(
        {'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name})

    return render_to_response(template_name, 
                             {
                              'object': doctor, 
                              'forms': forms, 
                              'info_forms': info_forms,
                              'phone_forms': phone_forms, 'changed': changed,
                              'phoneform_errors': phonef_error_messages,
                              'phoneform_success': phonef_success_messages,
                              'object_itens_fields': doc_itens_fields, 
                              'user_form': user_form,
                              'name_email_error': name_email_error
                             }, context_instance = RequestContext(request))

def registerPOSTHandler(post_request, new_user):
    """ Salva um novo medico relacionado a um novo usuario. """    


    doctor_name = post_request['first_name'] + ' ' + post_request['last_name']

    doctor = Doctor(name=doctor_name, user=new_user)
    doctor.save()

    phone_number = post_request['phone']
    region = phone_number[:2] 
    number = phone_number[2:]
    phone  = PhoneNumber(doctor=doctor, region=region, phone=number)

    phone.save()

    return doctor

def register(request, template_name='registration/register.html'):
    """ Lida com o cadastro de um usuario. """
    
    phonef_error_message = []
    namef_error_message  = []
    new_doctor           = []
    regist_form_errors   = []

    if request.method == 'POST':

        phonef_error_message = phoneFormErrors('', request.POST['phone'])

        #inicializa os formularios com as informacoes obtidas do request.POST.
        signup_form = SignupForm(request.POST)
        regis_form = UserCreationFormExtended(request.POST)

        regist_form_errors = verifyNameAndEmail(request.POST['email'],
            request.POST['first_name'] + ' ' + request.POST['last_name'])

        #caso esteja tudo ok, um novo usuario eh criado.
        if not phonef_error_message and not regist_form_errors and signup_form.is_valid() and regis_form.is_valid():
            new_user = regis_form.save(request.POST)
            new_doctor = registerPOSTHandler(request.POST, new_user)
        elif phonef_error_message:
            phonef_error_message = phonef_error_message[1]
    else:
        signup_form = SignupForm()
        regis_form = UserCreationFormExtended()

    return render_to_response(template_name, 
                             {
                              'object': new_doctor,
                              'signup_form': signup_form,
                              'regis_form': regis_form,
                              'regist_form_error': regist_form_errors,
                              'phoneform_error': phonef_error_message,
                              'regist_form_errors': regist_form_errors
                             }, context_instance = RequestContext(request))

def login(request): pass

