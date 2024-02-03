from .models import *
from django.template import loader
from datetime import datetime, date, timedelta
from .data import *

class Totais:
    id = 0

class itemCol:
    def __init__(self, mes, minutos, horas):
        
        self.mes     = mes
        self.minutos = minutos
        self.horas   = horas

class Ambiente():
    usuario         = ''
    nome_usuario    = ''
    is_dev          = False
    url             = ''
    pode_alterar    = False
    is_manager      = False
    datai           = ''
    dataf           = ''
    cliente         = 0
    ano             = ''

def GetSeekerCliente(cliente):
    csql = GetSqlSeekerCliente(cliente)
    usuario_demanda = UsuarioDemanda.objects.raw(csql)

    for usu_dem in usuario_demanda:
        username = usu_dem.usuario_id
        usuario = User.objects.get(id=username)
    
    return usuario.email

def GetClienteByUser(user):

    grupo_usuario   = GrupoUsuario.objects.get(usuario=user)
    idgrupo = str(grupo_usuario.grupo)
    grupo = Grupo.objects.get(id=idgrupo)
    
    return str(grupo.cliente)

def GravaSeekDemanda(user, demanda, status):

    usuario_demanda = False
    try:
        usuario_demanda = UsuarioDemanda.objects.get(usuario=user, demanda=demanda)
        usuario_demanda.status = status
        usuario_demanda.save()
    except:
        usuario_demanda = UsuarioDemanda.objects.create(
            usuario=user,
            demanda=demanda,
            status=status
            )  

def GravaRespostaAndamento(user, demanda, andamento, opcao):
    
    descricao   = '|AUTOM| Orçamento apresentado no andamento ' + str(andamento.id) + ' da demanda "' + demanda.assunto + '" '
    
    if opcao == 'A':
        tipo        = TipoAndamento.objects.get(nome = 'Aprovação')
        descricao   += 'está <b>aprovado</b>.'
    
    if opcao == 'R':
        tipo         = TipoAndamento.objects.get(nome = 'Retorno')
        descricao   += 'está <b>rejeitado</b>.'

    if opcao == 'N':
        tipo         = TipoAndamento.objects.get(nome = 'Retorno')
        descricao   += 'está sob <b>análise</b>, e estaremos retornando mais tarde. '

    novo_andamento = Andamento.objects.create(
        usuario=user,
        demanda=demanda,
        tipo=tipo,
        descricao=descricao
        ) 
    
    atividade       = '|Retorno de Orçamento na Demanda| ' + demanda.assunto
    AtividadeDemanda(demanda, novo_andamento, atividade, novo_andamento.descricao, user, '')
    AndamentoAfetaDemanda(demanda, novo_andamento)

def AtividadeDemanda(demanda, andamento, assunto, descricao, user, oldstatus):
    
    mensagem = GeraCorpoMensagemAtividade(demanda, andamento, assunto, descricao, user, oldstatus)
    mensagem + '<br><br>' + descricao
    seekers_demanda = UsuarioDemanda.objects.filter(demanda=demanda)
    for seeker in seekers_demanda:
        usuario = User.objects.get(username=seeker.usuario)
        enviarEmail(usuario.email, assunto, mensagem, 5007, None)

    seek_cliente = GetSeekerCliente(GetClienteByUser(user))    

    if seek_cliente is not None:
       enviarEmail(seek_cliente, assunto, mensagem, 5007, None) 

def enviarEmail(email, assunto, descricao, tipo, anexo):

    anexo   = None
    assunto = assunto[:99]

    fila_email = Fila_Email.objects.create(
        tipo=tipo,
        email=email,
        assunto=assunto,
        descricao=descricao,
        anexo=anexo
    )
    

def GetStatusSeekDemanda(user, demanda):

    try:
        usuario_demanda = UsuarioDemanda.objects.get(usuario=user,demanda=demanda)
    except:
        usuario_demanda = UsuarioDemanda.objects.none()
        usuario_demanda.status = 'N'  
  
    
    return usuario_demanda.status

def GeraCorpoMensagemAtividade(demanda, andamento, assunto, descricao, user, oldstatus):

    usuario = User.objects.get(username=user)
    mensagem = ''
    if type(andamento).__name__=='str':
        mensagem = 'O usuário ' + str(usuario.email) + ' realizou alteração nos dados básicos da demanda.'
    else:
        mensagem = 'O usuário ' + str(usuario.email) + ' registrou novo andamento para a demanda.'

    if type(oldstatus).__name__!='str' and oldstatus != demanda.status:
        mensagem = 'O usuário ' + str(usuario.email) + ' alterou o status de "'
        mensagem += str(oldstatus) + '" para "' + str(demanda.status) + '" na demanda.' 
                
    print(' type(oldstatus).__name__: ', type(oldstatus).__name__)
    htmlmsg = loader.render_to_string('atividade.html', {'demanda':demanda,'andamento':andamento,'assunto':assunto,'mensagem':mensagem,'descricao':descricao})
    
    return  htmlmsg

def GetGrupoByUser(user):
    
    try:
        grupo_usuario = GrupoUsuario.objects.get(usuario=user)
    except:
        grupo_usuario = GrupoUsuario.objects.none()

    if grupo_usuario is None:
        return Grupo.objects.none()

    idgrupo = str(grupo_usuario.grupo)
    try:
        grupo = Grupo.objects.get(id=idgrupo)
    except:
        grupo = Grupo.objects.none()
        
    return grupo        


def UserIsDev(user):
    
    grupo = GetGrupoByUser(user)
   
    if grupo is None:
        return False

    if grupo.tipo is None:
        return False
    if grupo.tipo == 0:        
        return True

    return False  

def UserIsManager(user):
    
    grupo = GetGrupoByUser(user)
   
    if grupo is None:
        return False

    if grupo.tipo is None:
        return False
    if grupo.tipo == 1:        
        return True

    return False

def CriaObjetoAmbiente(request, opcao, objeto):

    ambiente = Ambiente() 
    ambiente.is_dev     = UserIsDev(request.user)  
    ambiente.cliente    = GetClienteByUser(request.user)
    
    if opcao == 'demanda':
        if request.user == objeto.usuario:
            ambiente.pode_alterar = True
        if ambiente.is_dev:
            ambiente.pode_alterar = True


    if opcao == 'painel':
       ambiente.is_manager = UserIsManager(request.user)
       if not ambiente.is_manager:
           ambiente.is_manager = ambiente.is_dev

       datai = boy(datetime.now())
       dataf = datetime.now()

       ambiente.datai = str(datai.strftime('%Y-%m-%d'))
       ambiente.dataf = str(dataf.strftime('%Y-%m-%d'))

    return ambiente

def boy(date):
    ano = str(date.strftime('%Y'))
    return date.strptime('01/01/'+ano, '%d/%m/%Y')
def eoy(date):    
    ano = str(date.strftime('%Y'))
    return date.strptime('13/12/'+ano, '%d/%m/%Y')

def ConsultaConsumoHorasPorPeriodo(cliente, datai, dataf, opcao):

    csql = GetSqlConsultaConsumoHorasPorPeriodo(cliente, datai, dataf)
    andamentos = Andamento.objects.raw(csql)
    tempo       = 0
    minutos     = 0
    currmes     = 'XX'
    lnt         = 0
    mycoll      = None
    for andamento in andamentos:
        if andamento.tipo_hora is not None:
                if andamento.tipo_hora.faturavel == 'SIM':
                    
                    dataregistro = andamento.dtgerado
                    mesregistro  = str(dataregistro.strftime('%m'))
                    currano      = str(dataregistro.strftime('%Y'))
                    tempo       += horatominutos(andamento.hora)

                    if currmes=='XX':
                        currmes =  mesregistro
                    
                    #Se trocou o mês, insere item e reinicia a contagem
                    if mesregistro != currmes:
                        lnt += 1
                        item = itemCol(currmes + '/' + currano, minutos, minutostohorasstr(minutos))
                        if lnt == 1:
                            mycoll = [item]
                        else:
                            mycoll.append(item)                        
                        
                        #reiniciada contagem de horas para o mes novo
                        minutos  = horatominutos(andamento.hora)
                        currmes = mesregistro                        
                    else:
                        minutos += horatominutos(andamento.hora)
                        
    #appenda saldo de minutos
    if minutos > 0:
        currano = str(dataregistro.strftime('%Y'))
        item = itemCol(currmes + '/' + currano, minutos, minutostohorasstr(minutos))
        
        if lnt == 0:
             mycoll = [item]
        else:
            mycoll.append(item)
    
    if opcao == 0:
        return mycoll
    if opcao == 1:
        return tempo
    

def horatominutos(hora):
   idx1     = hora.rfind(':') 
   chora    = hora[:idx1]
   cminu    = hora[idx1+1:]
   
   minutos = int(cminu) + (int(chora)*60)

   return minutos

def minutostohoras(minutos):
    
    if minutos < 60:
        horas = 0
    else:        
        horas = int(minutos / 60)

    smin  =  minutos - (horas * 60)       
    chora = str(horas)
    cmin  = str(smin)

    return chora.zfill(3) + ':' + cmin.zfill(2)


def minutostohorasstr(minutos):
    hora     = minutostohoras(minutos)
    idx1     = hora.rfind(':') 
    nhora    = int(hora[:idx1])
    nminu    = int(hora[idx1+1:])
    
    if nhora == 0:
        horasstr = ""
    else:
        if nhora == 1:
            horasstr = str(nhora) + " hora "
        else:
            horasstr = str(nhora) + " horas "

    if nminu > 0:
        horasstr += str(nminu) + " minutos "                

    return horasstr

def GetDemandasPendentes(request):

    demandas = Demanda.objects.all().order_by('dtatualizado')
    for dem in demandas:
        if dem.status.id == 2:
            dem.listar = False 

    return demandas

def AndamentoAfetaDemanda(demanda, andamento):

    if str(andamento.tipo) == 'Aprovação':
        status = Status.objects.get(nome='Em andamento')
        demanda.status  = status
        demanda.cor     = status.cor
        demanda.save()

    if str(andamento.tipo) == 'Análise' and str(andamento.tipo_hora) == 'Orçamento':
        status = Status.objects.get(nome='Aguardando Aprovação')
        demanda.status = status
        demanda.cor     = status.cor        
        demanda.save()

    if str(andamento.tipo) == 'Programação':
        status = Status.objects.get(nome='Aguardando Cliente')
        demanda.status = status
        demanda.cor     = status.cor        
        demanda.save()

    if str(andamento.tipo) == 'Suporte':
        status = Status.objects.get(nome='Aguardando Cliente')
        demanda.status = status
        demanda.cor     = status.cor        
        demanda.save()    