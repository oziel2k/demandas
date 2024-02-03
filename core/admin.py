from django.contrib import admin
from .models import Fila_Email, Tipo, Setor, Status, Demanda, TipoAndamento, Andamento, Cliente, Grupo, GrupoUsuario, TipoHora, UsuarioDemanda, Pacote

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ['id','nome']

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ['id','nome']

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id','nome']

@admin.register(Demanda)
class DemandaAdmin(admin.ModelAdmin):
    list_display = ['id','setor','assunto', 'status']

@admin.register(TipoAndamento)
class TipoAndamentoAdmin(admin.ModelAdmin):
    list_display = ['id','nome', 'tipo']

@admin.register(Andamento)
class AndamentoAdmin(admin.ModelAdmin):
    list_display = ['id','demanda','descricao', 'tipo']      

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id','nome','numero']      

@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ['id','nome','descricao', 'cliente','tipo']       

@admin.register(GrupoUsuario)
class GrupoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['id','grupo','usuario']


@admin.register(Fila_Email)
class Fila_EmailAdmin(admin.ModelAdmin):
    list_display = ['id','email','assunto','data']    


@admin.register(UsuarioDemanda)
class UsuarioDemandaAdmin(admin.ModelAdmin):
    list_display = ['id','usuario','demanda','status']    

@admin.register(TipoHora)
class TipoHoraAdmin(admin.ModelAdmin):
    list_display = ['id','nome','faturavel']        


@admin.register(Pacote)
class PacoteAdmin(admin.ModelAdmin):
    list_display = ['id','cliente','ano','horas']     

