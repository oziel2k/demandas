from django.contrib import admin
from django.urls import path, include, re_path
from core import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("allauth.urls")),
    path('sobre/', views.about),    
    path('login/', views.login_user),
    path('logout/', views.logout_user),
    path('login/submit', views.submit_login),    
    path('mudarsenha/', views.mudar_senha),  
    path('mudarsenha/submit', views.mudar_senha),  
        
    path('demandas/todas/', views.demandas_listar),
    path('demandas/pendente/', views.demandas_listar),      
    path('demandas/usuario/', views.demandas_listar_usuario),  
    path('demandas/seguindo/', views.demandas_listar_seguindo),      
    path('demandas/registrar/', views.demandas_registrar),    
    path('demandas/demanda/<id>', views.demandas_item),   
    path('demandas/registrar/submit', views.demandas_gravar), 
    path('demandas/seguir/sim/<id>', views.demanda_seguir), 
    path('demandas/seguir/nao/<id>', views.demanda_seguir), 

    path('demandas/acoes/retornarandamento/aprovado/<id>', views.demanda_retornarorcamento), 
    path('demandas/acoes/retornarandamento/rejeitado/<id>', views.demanda_retornarorcamento), 
    path('demandas/acoes/retornarandamento/analise/<id>', views.demanda_retornarorcamento), 
        
    path('andamento/registrar/', views.andamento_registrar2),     
    path('andamento/registrar/submit', views.andamento_registrar2),  
    path('andamento/apagar/<id>', views.andamento_item_remover),         
    path('andamento/item/<id>', views.andamento_item),   

    path('gestor/painel/', views.painel_gestor),
    path('gestor/pacote/', views.pacote_horas),
    path('gestor/pacote/submit', views.pacote_horas_result),
    path('gestor/pacote/listagem/', views.pacote_horas),    
    path('gestor/pacote/listagem/submit', views.pacote_horas_result),    

    path('dev/painel/', views.painel_dev),

    path('teste999666333/', views.testes),
    
    path('', views.pagina_inicial),
    re_path('ckeditor', include('ckeditor_uploader.urls')),
] 

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'

