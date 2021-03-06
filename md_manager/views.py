# Lida com os templates e seus formularios.


######## Importacoes necessarias #############

from pertmed_site.md_manager.models import Doctor, Item, ItemField, Notifications, PhoneNumber
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
    #deve ter como ver isso direto no banco, dunno
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

    #TODO: passar a responsabilidade de verificacao para o banco
def verifyNameAndEmail(user, email, name):
    """ Verifica se o nome e email passados como parametro ja existem no BD.
        Retorna uma tupla com o nome do campo incorreto e a mensagem do erro. """

    user_email = ''
    user_name = ''

    if user.is_authenticated():
        user_email = user.email
        user_name = user.get_full_name()

    error = ''
    if user_email != email and email in [umails.email for umails in User.objects.all()]: #PROBLEMA: estamos passando HORRORES de dados pra memoria RAM -> desnecessario
        error = ('email', 'Email already registered.')

    elif user_name != name and name in [dname.name for dname in Doctor.objects.all()]: #mesmo acima
        error = ('name', 'Name already registered.')

    return error

#funcao que, apos tudo ser validado, altera as informacoes acerca do medico.
def profilePOSTHandler(request, doctor, forms):
    """ Lida com as informacoes do request.POST enviadas via formulario 
        para alteracao do perfil do usuario """
    user = request.user
    user.first_name = request.POST['first_name'] 
    user.last_name  = request.POST['last_name']
    user.email = request.POST['email']
    user.save() #salva os novos nome e email do usuario.

    doctor.name = user.get_full_name()

    #Deleta os itens e campos que devem ser deletados por terem sido desmarcados
    #pelo medico.
    doc_itens = doctor.sorted_itens_fields()
    last_title = ''

    title = []
    alert = []

    for item, fields in doc_itens:
        for field in fields:
            name = 'itemfield_' + str(item.id) + '_' + str(field.id)
            if not name in request.POST:
                notif = Notifications.objects.get(doctor=doctor, field=field)
                notif.delete()

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
        if part[0] == 'itemfield':
            sub_part = part[2].partition('_')
            field_id = int(sub_part[2])
            field = ItemField.objects.get(id=field_id)
            doc_item = doctor.notifications_set.filter(field=field)
            if not doc_item: #se o medico ja nao tem tal field.
                notification = Notifications(doctor=doctor, field=field)
                notification.save()

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


@login_required
def profile(request, template_name='md_manager/md_profile.html'): #ACHO QUE SERIA CONVENIENTE DIVIDIR EM FUNCOES MENORES, FICARIA MAIS FACIL DE DAR MANUTENCAO
    """ Mostra o perfil do medico e permite sua alteracao. """
    user = request.user
  
    doctor =  user.doctor_set.get()
    doctor = get_object_or_404(Doctor, pk=doctor.id)

    changed = False

    dic_form                = {}
    name_email_error        = []
    phonef_error_messages   = []  
    phonef_success_messages = []


    doctor_itens_fields = []
    
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

        name = request.POST['first_name'] + ' ' + request.POST['last_name']
        email = request.POST['email']
        name_email_error = verifyNameAndEmail(request.user, email, name)

        if not phonef_error_messages and not name_email_error and forms.is_valid():
            profilePOSTHandler(request, doctor, forms)
            changed = True

        doctor_itens_fields = doctor.sorted_itens_fields()
    else:
        dic_form = {}

        
        doctor_itens_fields = doctor.sorted_itens_fields()
        #o dicionario 'dic_form' eh atualizado para que as opcoes ja relacionadas
        #ao medico estejam marcadas no formulario.
        for item, fields in doctor_itens_fields:
            for field in fields:
                name = 'itemfield_' + str(item.id) + '_' + str(field.id)
                dic_form[name] = [u'on']

        i = 0
        for phone in doctor.phonenumber_set.all():
            phone_number = phone.region + phone.phone
            dic_form['Phone_' + str(i)] = phone_number
            i += 1

        forms = ProfileForm(dic_form)
    
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

    for item in Item.objects.all():
        f_list = []
        for field in item.itemfield_set.all():
            f = 'itemfield_' + str(item.id) + '_' + str(field.id)
            f_list.append((field, forms[f]))
        info_forms.append((item, sorted(f_list, key=lambda elem: elem[0].name)))

    info_forms = sorted(info_forms, key=lambda elem: elem[0].name)

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
                              'object_itens_fields': doctor_itens_fields, 
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
        
        #ao invez disso, usar um bloco try/except para pegar a excessao que sera jogada. (violacao de unicidade: email, first name e last name devem sem campos unique)
        regist_form_errors = verifyNameAndEmail(request.user, request.POST['email'],
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

def login(request): pass #necessaria para visualizacao da pagina do admin.

def pageNotFound(request):
    return render_to_response('404.html', context_instance = RequestContext(request))


