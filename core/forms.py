from django.forms import ModelForm, fields
from .models import Andamento, Demanda, Tipo

class AndamentoForm(ModelForm):
    class Meta:
        model = Andamento
        fields = ['descricao']

    def __init__(self, *args, **kwargs):
        super(AndamentoForm, self).__init__(*args, **kwargs)
        self.fields['descricao'].label = ""        
        
