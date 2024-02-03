
def GetSqlConsultaConsumoHorasPorPeriodo(cliente, datai, dataf):

    csql =  "select * from andamento where dtgerado > '" + str(datai) + "' and dtgerado < '" + str(dataf) + "' and usuario_id in"
    csql += "("
    csql += "   select usuario_id from grupo_usuario where grupo_id in"
    csql += "   (select id from grupo where cliente_id = "+  str(cliente) + ")"
    csql += ") Order By dtgerado"

    return csql

def GetSqlSeekerCliente(cliente):
    csql =  "select * from usuario_demanda where id < 200 and demanda_id in "
    csql += "(select id from demanda where id < 200 and cliente = 0 and assunto = 'Controles') and usuario_id in "
    csql += "("
    csql += "   select usuario_id from grupo_usuario where grupo_id in"
    csql += "   (select id from grupo where cliente_id = " +  str(cliente) + ")"
    csql += ")"       
    return csql


def GetSqlAndamentosPacote(cliente, datai, dataf):
    csql =  "select a.*, d.descricao as descridem, d.assunto from andamento as a "
    csql += "left join tipo_hora as th on th.id = a.tipo_hora_id "
    csql += "left join demanda as d on a.demanda_id = d.id "
    csql += "where a.dtgerado > '" + str(datai) + "' and a.dtgerado < '" + str(dataf) + "' and a.usuario_id in"
    csql += "("
    csql += "   select usuario_id from grupo_usuario where grupo_id in"
    csql += "   (select id from grupo where cliente_id = "+  str(cliente) + ")"
    csql += ") and th.faturavel = 'SIM' Order By a.dtgerado"

    return csql

