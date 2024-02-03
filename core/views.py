from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .classes import *
from .forms import AndamentoForm
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .data import *

@login_required(login_url='/login/')
def logout_user(request):
    
    logout(request)
    return redirect('/login/')    

def login_user(request):

    #return  render(request,'login.html')   
    return redirect('/accounts/login')

@csrf_protect
def submit_login(request):
    if request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                messages.error(request, 'Dados não conferem')
    
    return redirect('/login')
   
@login_required(login_url='/login/')
def mudar_senha(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Senha atualizada com sucesso!')
            return redirect('/')
        else:
            for erro in form.error_messages:            
                messages.error(request, form.error_messages[erro])
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'c-mudarsenha.html', {'form': form})


def about(request):
    return  render(request,'sobre.html')

@login_required(login_url='/login/')
def pagina_inicial(request):
    return render(request,'inicial.html')

@login_required(login_url='/login/')
def demandas_listar(request):
    
    urlent      = request.path
    ambiente    = CriaObjetoAmbiente(request, 'demandas', None)    
    cliente     = GetClienteByUser(request.user)
    
    if urlent.find('/todas/')>0:        
        demandas = Demanda.objects.filter(cliente=cliente).order_by('-dtatualizado')

    if urlent.find('/pendente/')>0 and ambiente.is_dev:        
        demandas = GetDemandasPendentes(request)    

    if urlent.find('/pendente/')>0:
        demandas = Demanda.objects.filter(cliente=cliente).order_by('dtatualizado')   
        for dem in demandas:
            if dem.status.id == 2:
                dem.listar = False    
    
    for dem in demandas:
        dem.seguindo = GetStatusSeekDemanda(request.user, dem.id)
    
    return render(request,'demandas.html', {'demandas':demandas,'ambiente':ambiente})

@login_required(login_url='/login/')
def demandas_listar_usuario(request):
    
    demandas = Demanda.objects.filter(usuario=request.user).order_by('-dtatualizado')
    for dem in demandas:
        dem.seguindo = GetStatusSeekDemanda(request.user, dem.id)

    ambiente = CriaObjetoAmbiente(request,'demandas',demandas)
    return render(request,'demandas.html', {'demandas':demandas,'ambiente':ambiente})

@login_required(login_url='/login/')
def demandas_listar_seguindo(request):

    demandas = Demanda.objects.filter(usuario=request.user).order_by('-dtatualizado')
    for dem in demandas:
        dem.seguindo = GetStatusSeekDemanda(request.user, dem.id)
        if dem.seguindo == 'N':
            dem.listar = False
    ambiente = CriaObjetoAmbiente(request,'demandas',demandas)
    return render(request,'demandas.html', {'demandas':demandas,'ambiente':ambiente})

@login_required(login_url='/login/')
def demandas_registrar(request):
    
    tipos       = Tipo.objects.filter()
    setores     = Setor.objects.filter()
    statuss     = Status.objects.filter()

    demanda_id = request.GET.get('id')
    ambiente = CriaObjetoAmbiente(request,'empty', None)
    if demanda_id:
        demanda = Demanda.objects.get(id=demanda_id)
        ambiente = CriaObjetoAmbiente(request,'demanda', demanda)
        if ambiente.pode_alterar:
           return render(request, 'demanda-nova.html', {'demanda':demanda,'tipos':tipos ,'setores':setores,'statuss':statuss,'ambiente':ambiente})    
    
    return render(request,'demanda-nova.html', {'tipos':tipos,'setores':setores,'statuss':statuss})    

@login_required(login_url='/login/')
def demandas_gravar(request):

    demanda_id  = request.POST.get('demandaid')
    tipo        = request.POST.get('tipo')
    setor       = request.POST.get('setor')
    assunto     = request.POST.get('assunto')
    descricao   = request.POST.get('descricao')
    status      = request.POST.get('status')
    atividade   = '|Nova Demanda| ' + assunto 

    tipo    = Tipo.objects.get(id=tipo) 
    setor   = Setor.objects.get(id=setor)         
    cliente = GetClienteByUser(request.user)

    if demanda_id:
        status  = Status.objects.get(id=status)
        demanda = Demanda.objects.get(id=demanda_id)        
        oldstatus           = demanda.status
        demanda.assunto     = assunto
        demanda.tipo        = tipo
        demanda.setor       = setor
        demanda.status      = status
        demanda.descricao   = descricao
        demanda.cor         = status.cor
        demanda.cliente     = cliente
        demanda.save()
        atividade   = '|Alterações na Demanda| ' + assunto
    else:
        status  = Status.objects.get(id=1)   
        demanda = Demanda.objects.create(
            assunto=assunto,        
            descricao=descricao,
            status=status,
            tipo=tipo,        
            setor=setor, 
            usuario=request.user, 
            cliente=cliente,          
            cor="table-primary"
            ) 
        oldstatus = status

        #adicionar o senhor se estiver criando
        GravaSeekDemanda(request.user, demanda, 'S')

    AtividadeDemanda(demanda, '', atividade, demanda.descricao, request.user, oldstatus)

    url = "/demandas/demanda/{}".format(demanda.id)
    return redirect(url)   

@login_required(login_url='/login/')
def demandas_item(request, id):

    demanda = Demanda.objects.get(id=id)
    andamentos = Andamento.objects.filter(demanda=demanda).order_by('-dtatualizado')
    usuario_demanda = False
    try:
        usuario_demanda = UsuarioDemanda.objects.get(usuario=request.user, demanda=demanda)
    except:
        usuario_demanda = UsuarioDemanda.objects.none()
        usuario_demanda.status = 'N'

    ambiente = CriaObjetoAmbiente(request,'demanda', demanda)
    return render(request,'demanda.html', {'demanda':demanda,'andamentos':andamentos,'usuario_demanda':usuario_demanda,'ambiente':ambiente})


@login_required(login_url='/login/')
def andamento_gravar(request):
    
    andamento_id    = request.POST.get('andamentoid')
    demanda         = request.POST.get('demandaid')   
    tipo            = request.POST.get('tipo')
    descricao       = request.POST.get('descricao')  
    tipo            = TipoAndamento.objects.get(id=tipo)     
    demanda         = Demanda.objects.get(id=demanda) 
    atividade       = '|Andamento na Demanda| ' + demanda.assunto

    if andamento_id:
        andamento = Andamento.objects.get(id=andamento_id)        
        andamento.tipo        = tipo
        andamento.demanda     = demanda
        andamento.descricao   = descricao
        andamento.usuario     = request.user
        andamento.save()

    else:

        andamento = Andamento.objects.create(
            descricao=descricao,
            tipo=tipo,        
            usuario=request.user,           
            demanda=demanda
            )
        
        AndamentoAfetaDemanda(demanda, andamento)        

    AtividadeDemanda(demanda, andamento, atividade, andamento.descricao, request.user, '')

    url = "/demandas/demanda/{}".format(demanda.id)
    return redirect(url)   

def andamento_item_remover(request, id):
    andamento   = Andamento.objects.get(id=id)
    
    andamento.delete()
    
    url = "/andamento/item/" +str(id)
    return redirect(url)   

def andamento_item(request, id):

    andamento   = ''
    demanda     = ''
    ambiente    = ''
    
    try:
        andamento   = Andamento.objects.get(id=id)
        demanda     = Demanda.objects.get(id=str(andamento.demanda))
        ambiente    = CriaObjetoAmbiente(request,'andamento',andamento) 
    except Andamento.DoesNotExist:
        messages.error(request, "User doesnot exist")            

    return render(request,'andamento.html', {'andamento':andamento,'demanda':demanda,'ambiente':ambiente})


@login_required(login_url='/login/')
def andamento_registrar(request):
    tipos           = TipoAndamento.objects.all()
    tiposh          = TipoHora.objects.all()
    
    if request.method == 'POST':
        form = AndamentoForm(request.POST)
        if form.is_valid():
            demanda     = request.POST.get('demandaid') 
            demanda     = Demanda.objects.get(id=demanda) 
            tipo        = request.POST.get('tipo')
            tipo        = TipoAndamento.objects.get(id=tipo) 
            andamento = form.save(commit=False)
            andamento.tipo        = tipo
            andamento.demanda     = demanda
            andamento.usuario     = request.user
            andamento.save()
            atividade = '|Andamento na Demanda| ' + demanda.assunto

            AtividadeDemanda(demanda, andamento, atividade, andamento.descricao, request.user, '')
            AndamentoAfetaDemanda(demanda, andamento)        
            url = "/demandas/demanda/{}".format(demanda.id)
            return redirect(url)
    else:
        demanda_id = request.GET.get('demandaid')
        demanda = Demanda.objects.get(id=demanda_id)  
        ambiente = CriaObjetoAmbiente(request,'demanda',demanda)          
        return render(request, 'andamento-novo.html',{'demanda':demanda,'tipos':tipos,'tiposh':tiposh, 'ambiente':ambiente})     

@login_required(login_url='/login/')
def andamento_registrar2(request):
    tipos           = TipoAndamento.objects.all()
    tiposh          = TipoHora.objects.all()

    if request.method == 'POST':
        form = AndamentoForm(request.POST)
        if form.is_valid():
            andamento = form.save(commit=False)
            demanda = request.POST.get('demandaid') 
            demanda = Demanda.objects.get(id=demanda) 
            
            tipo    = request.POST.get('tipo')
            tipo    = TipoAndamento.objects.get(id=tipo) 

            hora     = request.POST.get('hora')  
            tipohora = request.POST.get('tipo_hora')  
            if tipohora:
                tipohora = TipoHora.objects.get(id=tipohora)
                andamento.tipo_hora = tipohora
            if hora:
                andamento.hora     = hora                                        
            
            andamento.tipo        = tipo
            andamento.demanda     = demanda
            andamento.usuario     = request.user
            andamento.save()

            atividade = '|Andamento na Demanda| ' + demanda.assunto
            # Bolar uma renderização para a descrição, colocando uma url ou dados que possam auxiliar no detalhamento
            AtividadeDemanda(demanda, andamento, atividade, andamento.descricao, request.user, '')
            AndamentoAfetaDemanda(demanda, andamento)        
            url = "/demandas/demanda/{}".format(demanda.id)
            return redirect(url)
    else:
           demanda_id = request.GET.get('demandaid')
           demanda = Demanda.objects.get(id=demanda_id) 
           form = AndamentoForm()
           ambiente = CriaObjetoAmbiente(request,'demanda',demanda)
           return render(request, 'andamento-novo.html',{'form':form,'demanda':demanda,'tipos':tipos,'tiposh':tiposh,'ambiente':ambiente})     

def error_500(request):
    return render(request, '500.html')

def error_404(request, *args, **argv):
   return redirect('')  

@login_required(login_url='/login/')
def demanda_seguir(request, id):

    demanda = Demanda.objects.get(id=id)
    urlent = request.path
    
    if urlent.find('/nao/')<1:
        GravaSeekDemanda(request.user, demanda, 'S')        
    else:
        GravaSeekDemanda(request.user, demanda, 'N')        

    url = "/demandas/demanda/" + str(id)
    
    return redirect(url)


@login_required(login_url='/login/')
def demanda_retornarorcamento(request, id):

    andamento   = Andamento.objects.get(id=id)
    demanda     = Demanda.objects.get(id=str(andamento.demanda))
    urlent = request.path
    
    if urlent.find('/aprovado/')>0:
        GravaRespostaAndamento(request.user, demanda, andamento,  'A')        
    
    if urlent.find('/rejeitado/')>0:
        GravaRespostaAndamento(request.user, demanda, andamento, 'R')

    if urlent.find('/analise/')>0:
        GravaRespostaAndamento(request.user, demanda, andamento, 'N')    

    url = "/demandas/demanda/" + str(demanda.id)
    
    return redirect(url)    

@login_required(login_url='/login/')
def painel_gestor(request):
    
    ambiente = CriaObjetoAmbiente(request,'painel', None)

    if ambiente.is_manager:
        return render(request,'painel-gestor.html', {'ambiente':ambiente})
    else:
        return redirect("/")

@login_required(login_url='/login/')
def pacote_horas(request):

    ambiente    = CriaObjetoAmbiente(request,'painel', None)
    
    if ambiente.is_manager:
        return render(request,'painel-horas.html', {'ambiente':ambiente})            
    else:
       return redirect("/")    
    

@login_required(login_url='/login/')
def pacote_horas_result(request):
    
    urlent   = request.path
    ambiente = CriaObjetoAmbiente(request,'painel', None)
    if not ambiente.is_manager:
        return redirect("/")        

    datai = request.POST.get('data_i')
    dataf = request.POST.get('data_f')
    
    msgs = messages.get_messages(request)
    for message in msgs:
        print(message)

    if not datai:
        messages.error(request, 'Informe a data inicial')
        return redirect('/gestor/pacote/')

    if not dataf:        
        messages.error(request, 'Informe a data final')
        return redirect('/gestor/pacote/')
    
    datai = datetime.strptime(datai, '%Y-%m-%d')
    dataf = datetime.strptime(dataf, '%Y-%m-%d')

    if datai > dataf:
        messages.error(request, 'Data inicial não pode ser maior que a final')
        return redirect('/gestor/pacote/')        

    if datai.strftime('%Y') !=  dataf.strftime('%Y'):
        messages.error(request, 'Ano da data inicial e final precisa ser o mesmo')
        return redirect('/gestor/pacote/')        
        
    ano         = int(datai.strftime('%Y'))
    valores     = ConsultaConsumoHorasPorPeriodo(ambiente.cliente, datai, dataf, 0)
    consumomin  = ConsultaConsumoHorasPorPeriodo(ambiente.cliente, datai, dataf, 1)
    totais      = Totais()
    cliente     = ambiente.cliente
    
    try:
        pacote = Pacote.objects.get(cliente=cliente, ano=ano)
    except:
        pacote = Pacote.objects.none()
        pacote.horas = 0    
    
    setattr(totais, 'pacote', pacote.horas)
    setattr(totais, 'consumo', minutostohorasstr(consumomin))
    setattr(totais, 'saldo', totais.pacote - int(consumomin/60))
    setattr(totais, 'listar', True)

    if valores is None:
        totais.listar = False

    ambiente.ano = str(ano)
    
    if not urlent.find('/listagem/')>0:
        return render(request,'painel-horas-resultado.html', {'ambiente':ambiente,'valores':valores,'totais':totais})

    # segue aqui para a listagem
    csql = GetSqlAndamentosPacote(ambiente.cliente, datai, dataf)
    andamentos = Andamento.objects.raw(csql)
    return render(request, 'painel-horas-listagem.html', {'ambiente':ambiente,'valores':valores,'totais':totais, 'andamentos':andamentos})

@login_required(login_url='/login/')
def testes(request):

    log = '<b>Registros:</b><br><br>' 

    minutos     = horatominutos('100:05')
    log         += 'Minutos: ' + str(minutos) + "<br>"
    horas       = minutostohoras(minutos)
    log         += 'Horas: ' + horas + "<br>"
    
    return render(request,'testes.html',{'log':log})

@login_required(login_url='/login/')
def painel_dev(request):
    
    ambiente = CriaObjetoAmbiente(request,'painel', None)

    if ambiente.is_dev:
        return render(request,'painel-dev.html', {'ambiente':ambiente})
    else:
        return redirect("/")    
    