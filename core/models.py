from django.db.models.deletion import CASCADE
from demandas.settings.config import AUTH_PASSWORD_VALIDATORS
from django.db import models
from django.db.models.fields.related import ForeignObject
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from typing import ContextManager
from django.contrib.sessions.models import Session
from datetime import datetime

class Cliente(models.Model):  
    nome            = models.CharField(max_length=200)
    numero          = models.IntegerField()
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "cliente"

class Pacote(models.Model):
    cliente     = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    dtgerado    = models.DateTimeField(auto_now_add=True) 
    dtinicio    = models.DateTimeField(null=True) 
    dtfim       = models.DateTimeField(null=True) 
    ano         = models.IntegerField()
    horas       = models.IntegerField()

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "pacote"

class Grupo(models.Model):  
    nome            = models.CharField(max_length=200)
    descricao       = models.TextField()
    cliente         = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    tipo            = models.IntegerField(null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "grupo"

class GrupoUsuario(models.Model): 
    grupo    = models.ForeignKey(Grupo, on_delete=models.PROTECT)
    usuario  = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.id)

    def cliente(self):
        
        grupo_usuario   = GrupoUsuario.objects.get(usuario=self.usuario)
        idgrupo = str(grupo_usuario.grupo)
        grupo = Grupo.objects.get(id=idgrupo)
    
        return str(grupo.cliente)

    class Meta:
        db_table = "grupo_usuario"

class TipoHora(models.Model):  
    nome        = models.CharField(max_length=200)
    faturavel   = models.CharField(max_length=3)
    classe      = models.CharField(max_length=20,null=True)

    def __str__(self):
        return str(self.nome)

    class Meta:
        db_table = "tipo_hora"   

class TipoAndamento(models.Model):  
    nome = models.CharField(max_length=60)
    tipo = models.IntegerField(null=True)
    
    def __str__(self):
        return str(self.nome)

    class Meta:
        db_table = "tipo_andamento"

class Tipo(models.Model):
    nome = models.CharField(max_length=60)
    
    def __str__(self):
        return str(self.nome)

    class Meta:
        db_table = "tipo"

class Setor(models.Model):
    nome = models.CharField(max_length=60)
    
    def __str__(self):
        return str(self.nome)

    class Meta:
            db_table = "setor"

class Status(models.Model):
    nome    = models.CharField(max_length=60)
    cor     = models.CharField(max_length=40, null=True)
    
    def __str__(self):
        nome = self.nome
        return nome.strip(' ')

    class Meta:
        db_table = "status"

class Demanda(models.Model):

    tipo            = models.ForeignKey(Tipo, on_delete=models.PROTECT)
    setor           = models.ForeignKey(Setor, on_delete=models.PROTECT)
    status          = models.ForeignKey(Status, on_delete=models.PROTECT)
    assunto         = models.CharField(max_length=200)
    descricao       = models.TextField()
    dtgerado        = models.DateTimeField(auto_now_add=True) 
    dtatualizado    = models.DateTimeField(auto_now=True) 
    usuario         = models.ForeignKey(User,on_delete=models.PROTECT)    
    cliente         = models.IntegerField(null=True)
    cor             = models.CharField(max_length=30,null=True)
    
    def __str__(self):
        return str(self.id)

    def mailusuario(self):
        
        usuario = User.objects.get(username=self.usuario)
        return usuario.email

    def seguindo(self):
        return ''

    def listar(self):
        return True

    def horas(self):

        horas = '00:00'
        andamentos = Andamento.objects.filter(demanda=self)
        for andamento in andamentos:
            if andamento.tipo_hora is not None:
                if andamento.tipo_hora.faturavel == 'SIM':
                    horas  = somahoras(horas, andamento.hora)

        return horas

    class Meta:
            db_table = "demanda"        

class Andamento(models.Model):
    
    demanda         = models.ForeignKey(Demanda, on_delete=models.PROTECT)
    tipo            = models.ForeignKey(TipoAndamento, on_delete=models.PROTECT)
    descricao       = RichTextUploadingField(config_name="default")
    dtgerado        = models.DateTimeField(auto_now_add=True,null=True) 
    dtatualizado    = models.DateTimeField(auto_now=True) 
    usuario         = models.ForeignKey(User,on_delete=models.PROTECT)
    hora            = models.CharField(max_length=5,null=True)
    tipo_hora       = models.ForeignKey(TipoHora, on_delete=models.PROTECT, null=True)         

    def __str__(self):
        return str(self.id)

    def mailusuario(self):
        
        usuario = User.objects.get(username=self.usuario)
        return usuario.email        

    class Meta:
            db_table = "andamento"

class Fila_Email(models.Model):

    tipo        = models.IntegerField(null=True)
    email       = models.CharField(max_length=250)
    assunto     = models.CharField(max_length=100)
    descricao   = models.TextField()
    data        = models.DateTimeField(null=True) 
    anexo       = models.CharField(max_length=300)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "fila_email"


class UsuarioDemanda(models.Model):
    
    demanda     = models.ForeignKey(Demanda, on_delete=models.PROTECT)
    usuario     = models.ForeignKey(User, on_delete=models.PROTECT)
    status      = models.CharField(max_length=1,null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "usuario_demanda"

  
def somahoras(hora1, hora2):
    
    time_zero   = datetime.strptime('00:00:00', '%H:%M:%S')
    hora1       = datetime.strptime(hora1, '%H:%M')
    hora2       = datetime.strptime(hora2, '%H:%M')
    horas       = str((hora1-time_zero+hora2).time())
    return horas[:5]