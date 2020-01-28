# -*- coding: utf-8 -*- 
import numpy as np
import datetime as dt
import pandas as pd
ip,user,passw,datab = "172.16.47.17", "sismologia", "Ovdas.,sismo_2020", "db_monitoreo_estaciones"
import mysql.connector #libreria conexion
def esta_metadata(clave='',tipo='single'):
    """Permite obtener la información de cada estación (metadatos)

    :param clave: Clave de búsqueda, puede ser el nombre de 3 letras de una estación (cuando tipo='single') o el de un volcán (tipo='net')
    :type clave: str
    :param tipo: "single" para búsqueda de una estación, "net" para red de un volcán y "all" para toda la red
    :type tipo: str
    :returns: Diccionario  (:ref:`tabla_esta_metadata`) que contiene información disponible en la base de datos.

    :rtype: dict

    :Ejemplo:

    >>> import sys
    >>> sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
    >>> import ovdas_getfromdb_lib as gdb
    >>> stadata = gdb.esta_metadata('Corcovado',tipo='net')
    >>> print(stadata)
    {160: {'nombrevolcan': 'Corcovado', 'nombresitio': 'CORCOVADO', 'cod': 'SCOR', 'distcrater': 4.55, 
    'latitud': Decimal('-43.153019'), 'longitud': Decimal('-72.814029'), 'altitud': 970, 'marcaSism': 'REFTEK', 
    'modSism': '151-30A', 'serieSism': 'CORCOVADO', 'periodo': 30, 'marcaDig': 'REFTEK', 'modDig': '130B', 
    'serieDig': 'CORCOVADO', 'fini': datetime.date(2013, 5, 17), 'ffin': None, 'estadoPar': 4, 'estadoEstacion': 4, 
    'nombre_db': 'Corcovado', 'idestacion': 160, 'idzona': 4, 'codcorto': 'COR', 'sensz': 0.000794, 
    'sensn': 0.000794, 'sense': 0.000794, 'IP': None, 'id_volcan': 42, 'canal': 'HH', 
    'referencia': 1, 'umbral': 0.5, 'server': '172.16.40.198', 'iniEstacion': datetime.date(2013, 5, 16)}, 
    206: {'nombrevolcan': 'Corcovado', 'nombresitio': 'MORRILLO', 'cod': 'SMLL', 'distcrater': 7.59, 
    'latitud': Decimal('-43.205986'), 'longitud': Decimal('-72.880987'), 'altitud': 95, 'marcaSism': 'REFTEK', 
    'modSism': '151-30A', 'serieSism': 'MORRILLO', 'periodo': 30, 'marcaDig': 'REFTEK', 'modDig': '130B', 
    'serieDig': 'MORRILLO', 'fini': datetime.date(2012, 11, 20), 'ffin': None, 'estadoPar': 4, 'estadoEstacion': 4, 
    'nombre_db': 'Corcovado', 'idestacion': 206, 'idzona': 4, 'codcorto': 'MLL', 'sensz': 0.000794, 
    'sensn': 0.000794, 'sense': 0.000794, 'IP': None, 'id_volcan': 42, 'canal': 'HH', 'referencia': 0, 
    'umbral': 1.0, 'server': '172.16.40.198', 'iniEstacion': datetime.date(2012, 11, 19)}}

    .. note:: Los sensores que posean sólo una componente entregarán de todas formas un valor
        = *None* para las componentes no existentes (sensn, sense)
    .. seealso:: :class:`ovdas_WWS_lib.extraer_signal`
    .. todo:: check that arg2 is non zero.

    """

    #Obtener datos de estacion
    db = mysql.connector.connect(user=user,database=datab,host=ip,passwd=passw) #conexion
    if tipo=='all':
        query = ('SELECT * FROM estaciones_sismologicas2') #consulta
        cursor = db.cursor(buffered=True);cursor.execute(query)
        res_query = cursor.fetchall()
        column = cursor.description #nombres de columnas
        metadata={}
        for i in range(0,len(res_query)):
            metadata[res_query[i][21]]={}
            for j in range(0,len(column)):
                metadata[res_query[i][21]][str(column[j][0])] = res_query[i][j]
        metadata = pd.DataFrame.from_dict(metadata, orient='index')
    else: 
        if tipo=="single":
             query = ('SELECT * FROM estaciones_sismologicas2 WHERE codcorto = "'+clave+'"') #consulta
             cursor = db.cursor(buffered=True);cursor.execute(query)
             res_query = cursor.fetchall(); res_query = res_query[0]  
             column = cursor.description #nombres de columnas
             #obtener codigo y zona del volcan donde esta la estacion
             query = ('SELECT cod FROM db_monitoreo_estaciones.ovd_volcan WHERE nombre_db ="'+res_query[18]+'"') #consulta codigo volcan
             cursor = db.cursor(buffered=True); cursor.execute(query)
             cod = cursor.fetchall()
             cursor.close() #cierra cursor
             db.close() #cierra db
             cod = cod[0][0] #obtiene codigo volcan
             metadata={}
             for j in range(0,len(column)):
                 metadata[str(column[j][0])] = res_query[j]
             metadata['codv']=cod
        elif tipo=="net":
             query = ('SELECT * FROM estaciones_sismologicas2 WHERE nombre_db = "'+clave+'" ORDER BY fini ASC') #consulta
             cursor = db.cursor(buffered=True);cursor.execute(query)
             res_query = cursor.fetchall()
             column = cursor.description #nombres de columnas
             metadata={}
             for i in range(0,len(res_query)):
                 metadata[res_query[i][21]]={}
                 for j in range(0,len(column)):
                     metadata[res_query[i][21]][str(column[j][0])] = res_query[i][j]
             metadata = pd.DataFrame.from_dict(metadata, orient='index')
    cursor.close() #cierra cursor
    db.close() #cierra db
    return metadata

def get_evloc(num_ev=18643513841,fechas=[dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(hours=24), '%Y-%m-%dT%H:%M'),dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M")],ML=0,vol="all",tiev="all"):
    """Obtiene un listado de los n últimos eventos clasificados y localizados
    
    :param num_ev: Número de eventos a listar, predeterminado a 18643513841 (todos los eventos)
    :type num_ev: int, optional
    :param fechas: Tuple de [fecha inicial,fecha final], predetermiado a [24 horas atras,ahora]
    :type fechas: tuple[str,str]	
    :param ML: ML mínima a buscar, predeterminada a 0
    :type ML: float	
    :returns: Diccionario de diccionarios, donde cada elemento corresponde a un evento en particular (:ref:`tabla_get_evloc`) que contiene información de cada evento ordenado en orden cronológico descendente.
    :rtype: dict
    
    :Ejemplo:

    >>> import sys
    >>> sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
    >>> import ovdas_getfromdb_lib as gdb
    >>> evs = gdb.get_evloc(2,fechas=['2018-01-01','2019-01-01'])
    >>> evs[1]
    {'nombrevolcan': 'Puyehue-Cordon Caulle',
     'ev_fecha': '201812312321',
     'ev_tipoev': 'VT',
     'ev_ml': 0.4,
     'vol_region': 'DE LOS RIOS',
     'vol_tipo': 'C. V.',
     'ev_lat': -40.525833,
     'ev_lon': -72.1255,
     'ev_prof': 1.3,
     'vol_lat': Decimal('-40.522667'),
     'vol_lon': Decimal('-72.145401'),
     'vol_id': 33,
     'nombredb': 'PuyehueCCaulle',
     'vol_cod': 'E',
     'zona_id': 3,
     'vol_alt': 2200,
     'vol_alerta': 1,
     'loc_erh': 0.8}
    
    .. note:: Se muestran solo eventos clasificados y localizados, con todos sus datos
    .. todo:: check that arg2 is non zero.
    
    """
    if vol=="all":
        volcan=" "
    else:
        volcan=" AND v.nombre_db = '"+ vol+"' "
    if tiev=="all":
        tiev=" "
    else:
        tiev=" AND tipo.descripcion = '"+ tiev+"' "
                
    ini = fechas[0]
    fin = fechas[1]
    db = mysql.connector.connect(user='sismologia',database='db_resultados',
                                 host='172.16.47.17',passwd='Ovdas.,sismo_2020')
    cursor = db.cursor(buffered=True)
    sql = "SET time_zone = '+00:00'"
    cursor.execute(sql)    
    query = ("SELECT v.nombre as nombrevolcan, STR_TO_DATE(from_unixtime(ev.unixtime,'%Y%m%d%H%i'),'%Y%m%d%H%i') as ev_fecha,tipo.descripcion as ev_tipoev, loc.magLocal as ev_ml,"
    "reg.descripcion as vol_region,CONVERT(es.descripcion USING utf8) as vol_tipo, loc.latitud as ev_lat, loc.longitud as ev_lon, "
    "loc.profundidad as ev_prof, v.latitud as vol_lat, v.longitud as vol_lon, v.id as vol_id,v.nombre_db as nombredb,v.cod as vol_cod, z.id as zona_id, v.altitud as vol_alt, "
    "(select a.id from db_resultados.res_volcan_alerta va, db_resultados.res_alerta a "
    "WHERE va.id_volcan=v.id and va.id_alerta=a.id order by va.unixtime desc limit 1) as vol_alerta,loc.erh as loc_erh,ev.amplitud as ev_amp ,ev.frecuencia as ev_freq, "
    "ev.id_estacion as ev_esta "
    "FROM db_monitoreo_estaciones.ovd_volcan v, res_evento_localizacion loc, "
    "res_evento ev, res_tipoEvento tipo, db_monitoreo_estaciones.ovd_region reg,"
    "db_monitoreo_estaciones.ovd_volcan_tipoestructura es, "
    "db_monitoreo_estaciones.ovd_volcan_region vreg, db_monitoreo_estaciones.ovd_zona z, db_monitoreo_estaciones.ovd_zona_ovd_volcan zv "
    "WHERE loc.id_evento=ev.id AND v.id = ev.id_volcan AND ev.id_tipoEvento = tipo.id AND v.id=vreg.id_volcan "
    "AND (ev.unixtime  BETWEEN (UNIX_TIMESTAMP(STR_TO_DATE('"+ini+"', '%Y-%m-%dT%H:%i'))) AND (UNIX_TIMESTAMP(STR_TO_DATE('"+fin+"', '%Y-%m-%dT%H:%i'))) ) "
	"AND loc.magLocal > "+str(ML)+volcan+tiev+
    "AND vreg.id_region=reg.id AND v.id_tipoestructura=es.id AND z.id =zv.id_zona and zv.id_volcan=v.id ORDER BY loc.unixtime DESC LIMIT "+str(num_ev))
    cursor.execute(query)
    results_loc = cursor.fetchall()
    metadata={}
    for i in range(0,len(results_loc)):
        metadata[i]={}
        for j in range(0,len(cursor.description)):
            metadata[i][cursor.description[j][0]]=results_loc[i][j]
    cursor.close()
    db.close()   
    metadata = pd.DataFrame.from_dict(metadata).T
    return metadata

def get_evs_todos(num_ev=18643513841,fechas=[dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(hours=24), '%Y-%m-%dT%H:%M'),dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M")],vol="all",tiev="all"):
    """Obtiene un listado de los n últimos eventos clasificados
    
    :param num_ev: Número de eventos a listar, predeterminado a 18643513841 (todos los eventos)
    :type num_ev: int, optional
    :param fechas: Tuple de [fecha inicial,fecha final], predetermiado a [24 horas atras,ahora]
    :type fechas: tuple[str,str]	
    :param vol: Nombre del volcán según formato de base de datos, "all" para todos los volcanes
    :type vol: str
    :param tiev: Tipo de eventos, predefinido en "all" para todos los volcanes
    :type tiev: str
    :returns: Dataframe con los datos de clasificación para cada evento ordenado en orden cronológico descendente.
    :rtype: dict
    
    :Ejemplo:

    >>> import sys
    >>> sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
    >>> import ovdas_getfromdb_lib as gdb
    >>> evs = gdb.get_evs_todos(2,fechas=['2018-01-01','2019-01-01'])
    >>> evs
    Out[258]: 
                nombrevolcan            ev_fecha ev_tipoev  ...  ev_amp ev_freq ev_esta
    0     Nevados de Chillan 2019-12-18 23:44:00        LP  ...    2408    1.78     176
    1     Nevados de Chillan 2019-12-18 23:40:00        LP  ...    1581    2.61     176
    2     Nevados de Chillan 2019-12-18 23:20:00        LP  ...     438    2.42     176
    3     Nevados de Chillan 2019-12-18 23:11:00        LP  ...    1212   10.03     176
    4     Nevados de Chillan 2019-12-18 22:43:00        LP  ...    2499    2.34     176
                     ...                 ...       ...  ...     ...     ...     ...
    8074  Nevados de Chillan 2019-12-01 00:14:00        LP  ...   39188     1.6     235
    8075  Nevados de Chillan 2019-12-01 00:11:00        LP  ...  104262    3.31     235
    8076  Nevados de Chillan 2019-12-01 00:08:00        TR  ...   15249     2.7     235
    8077  Nevados de Chillan 2019-12-01 00:05:00        LP  ...  272357    1.78     235
    8078  Nevados de Chillan 2019-12-01 00:02:00        TR  ...   18099    1.95     176
    
    [8079 rows x 13 columns]
                
    """
    if vol=="all":
        volcan=" "
    else:
        volcan=" AND v.nombre_db = '"+ vol+"' "
    if tiev=="all":
        tiev=" "
    else:
        tiev=" AND tipo.descripcion = '"+ tiev+"' "
                
    ini = fechas[0]
    fin = fechas[1]
    db = mysql.connector.connect(user='sismologia',database='db_resultados',
                                 host='172.16.47.17',passwd='Ovdas.,sismo_2020')
    cursor = db.cursor(buffered=True)
    sql = "SET time_zone = '+00:00'"
    cursor.execute(sql)    
    query = ("SELECT v.nombre as nombrevolcan, STR_TO_DATE(from_unixtime(ev.unixtime,'%Y%m%d%H%i'),'%Y%m%d%H%i') as ev_fecha,tipo.descripcion as ev_tipoev,"
    "reg.descripcion as vol_region,CONVERT(es.descripcion USING utf8) as vol_tipo, "
    "v.id as vol_id,v.nombre_db as nombredb,v.cod as vol_cod, z.id as zona_id, v.altitud as vol_alt, "
    "ev.amplitud as ev_amp ,ev.frecuencia as ev_freq, "
    "ev.id_estacion as ev_esta "
    "FROM db_monitoreo_estaciones.ovd_volcan v, "
    "res_evento ev, res_tipoEvento tipo, db_monitoreo_estaciones.ovd_region reg,"
    "db_monitoreo_estaciones.ovd_volcan_tipoestructura es, "
    "db_monitoreo_estaciones.ovd_volcan_region vreg, db_monitoreo_estaciones.ovd_zona z, db_monitoreo_estaciones.ovd_zona_ovd_volcan zv "
    "WHERE v.id = ev.id_volcan AND ev.id_tipoEvento = tipo.id AND v.id=vreg.id_volcan "
    "AND (ev.unixtime  BETWEEN (UNIX_TIMESTAMP(STR_TO_DATE('"+ini+"', '%Y-%m-%dT%H:%i'))) AND (UNIX_TIMESTAMP(STR_TO_DATE('"+fin+"', '%Y-%m-%dT%H:%i'))) ) "
    "AND vreg.id_region=reg.id AND v.id_tipoestructura=es.id AND z.id =zv.id_zona and zv.id_volcan=v.id "+volcan+
    "ORDER BY ev.unixtime DESC")
    cursor.execute(query)
    results_loc = cursor.fetchall()
    metadata={}
    for i in range(0,len(results_loc)):
        metadata[i]={}
        for j in range(0,len(cursor.description)):
            metadata[i][cursor.description[j][0]]=results_loc[i][j]
    cursor.close()
    db.close()  
    metadata = pd.DataFrame.from_dict(metadata).T
    import ovdas_formulas_lib as formula
    esta = esta_metadata(vol,tipo='net')
    esta_todas = esta_metadata(tipo='all')
    metadata['ev_DR']=0
    for index,row in metadata.iterrows():
        try:
            DR=formula.DRc(row['ev_amp']*esta.sensz[esta.idestacion==row['ev_esta']], row['ev_freq'], esta.distcrater[esta.idestacion==row['ev_esta']])
            metadata.at[index,'ev_DR']=DR
        except:
            print("Evento guardado en estación : "+str(esta_todas.codcorto[esta_todas.idestacion==row['ev_esta']][0])+", omitido DR")   
    return metadata

def count_evs(evs,periodo='D'):
    #Obtener que tipos de eventos aparecieron
    tipoevs = evs.ev_tipoev.unique()
    #generar listado de eventos segun orden de prioridad
    tiev=[]
    listado_tipoevs=['VT','LP','EX','HB','LV','TO','TR']
    for tipoev in listado_tipoevs:
        if (tipoev in tipoevs)==True:
            print('hay '+tipoev)
            tiev.append(tipoev)
            evs['count'+tipoev]=0
            
    for index,row in evs.iterrows():
        for tipoev in tiev:
            if row['ev_tipoev']==tipoev:
                evs.at[index,'count'+tipoev] = 1
    evs = evs.set_index('ev_fecha')
    evs = evs.drop(evs.iloc[:,0:13],axis=1)
    evs = evs.resample(periodo).sum()  
    return evs
	
def volc_metadata(volc): 
    """Permite obtener la información de cada volcán (metadatos)

    :param volc: Nombre del volcán según formato de base de datos, "all" para todos los volcanes
    :type volc: str
    :returns: Diccionario  (:ref:`tabla_volc_metadata`) que contiene información del volcán en la base de datos.

    :rtype: dict

    :Ejemplo:

    >>> import ovdas_getfromdb_lib as gdb
    >>> voldata = gdb.volc_metadata('NevChillan')
    >>> voldata['id_volcan']
    21

    """
    if volc=="all":
        volcan=" "
    else:
        volcan=" WHERE v.nombre_db = '"+volc+"' "
    #Obtener datos de estacion
    db = mysql.connector.connect(user=user,database=datab,host=ip,passwd=passw) #conexion
    query = ('SELECT * FROM ovd_volcan v join ovd_zona_ovd_volcan vz on vz.id_volcan=v.id '+volcan) #consulta
    cursor = db.cursor(buffered=True);cursor.execute(query)
    res_query = cursor.fetchall(); 
    column = cursor.description #nombres de columnas
    cursor.close() #cierra cursor
    db.close() #cierra db
    metadata={}
    if volc=="all":
        for i in range(0,len(res_query)):
            metadata[i] = {}
            for j in range(0,len(column)):
                metadata[i][str(column[j][0])] = res_query[i][j]		    
        ()
        metadata = pd.DataFrame.from_dict(metadata).T
    else:
        res_query = res_query[0] 
        for j in range(0,len(column)):
            metadata[str(column[j][0])] = res_query[j]
    return metadata
    
	
def getCustomQuery(query='', *argv):
	"""Permite obtener los datos de una consulta mysql personalizada.

	Recibe como parámetro fijo:

	:param query: Consulta mysql completa anteponinedo el nombre de base de datos al nombre de la tabla. Ej: "db_resultados.res_evento"
	:type clave: str

	Recibe parámetros opcionales 

	argv: [host, user, passwd, db]  
	
					
	:param host: IP del servidor de base de datos
	:type host: str
	:param user: nombre de usuario de la conexión a la base de datos
	:type user: str
	:param passwd: contraseña de la conexión a la base de datos
	:type passwd: str
	:param db: nombre de la base de datos a la que se realiza la conexión
	:type db: str
	
	.. note::	Si no se definen estos datos, se utilizarán los siguiente s datos por defecto: \n
		host='172.16.47.17'\n
		user='sololectura'\n
		passwd='sololectura'\n
		db='db_monitoreo_estaciones'\n 
		
		Con esta conexión, se tiene acceso a las bases de datos "db_monitoreo_estaciones" y a "db_resultados" 
		teniendo el cuidado de anteponer al nombre de la tabla el nombre de la base de datos.
		Ej: "db_monitoreo_estaciones.estaciones_sismologicas2" ; "db_resultados.cla_loc"	
	
	:type db: str
	:returns: Vector que contiene cada fila devuelta por la consulta como diccionarios

	:rtype: Array

	:Ejemplo:

	>>> import sys
	>>> sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
	>>> import ovdas_getfromdb_lib as gdb
	>>> data=gdb.getCustomQuery('select nombre_db, latitud, longitud from db_monitoreo_estaciones.ovd_volcan limit 10')
	No se han proporcionado datos de conexión. Se conectó a la base de datos por defecto
	>>> print(data)
	[{'nombre_db': 'Tacora', 'latitud': Decimal('-17.720495'), 'longitud': Decimal('-69.772454')}, 
	{'nombre_db': 'Taapaca', 'latitud': Decimal('-18.110000'), 'longitud': Decimal('-69.510000')}, 
	{'nombre_db': 'Parinacota', 'latitud': Decimal('-18.160000'), 'longitud': Decimal('-69.140000')}, 
	{'nombre_db': 'Guallatiri', 'latitud': Decimal('-18.420421'), 'longitud': Decimal('-69.092928')}, 
	{'nombre_db': 'Isluga', 'latitud': Decimal('-19.160000'), 'longitud': Decimal('-68.820000')}, 
	{'nombre_db': 'Irruputuncu', 'latitud': Decimal('-20.730000'), 'longitud': Decimal('-68.560000')}, 
	{'nombre_db': 'Olca', 'latitud': Decimal('-20.940000'), 'longitud': Decimal('-68.500000')}, 
	{'nombre_db': 'Ollague', 'latitud': Decimal('-21.310000'), 'longitud': Decimal('-68.180000')}, 
	{'nombre_db': 'SanPedro', 'latitud': Decimal('-21.890000'), 'longitud': Decimal('-68.390000')}, 
	{'nombre_db': 'Lascar', 'latitud': Decimal('-23.360000'), 'longitud': Decimal('-67.730000')}]

	.. seealso:: :class:`ovdas_WWS_lib.extraer_signal`
	.. todo:: check that arg2 is non zero.

	"""

	
	from collections import OrderedDict as od
	
	try:
		#Intenta conectar a base de datos entregada"""
		host=argv[0]
		user=argv[1]
		passwd=argv[2]
		db=argv[3]

		db = mysql.connector.connect(host=host, user=user, passwd=passwd, database=db)
		cursor = db.cursor()

	except:
		#Si no se entregaron datos o estaban erróneos, abre la conexión con la BD por defecto
		#print('No se han proporcionado datos de conexión. Se conectó a la base de datos por defecto')
		host='172.16.47.17'
		user='sismologia'
		passwd='Ovdas.,sismo_2020'
		db='db_monitoreo_estaciones'
		db = mysql.connector.connect(host=host, user=user, passwd=passwd, database=db)
		cursor = db.cursor()
	#envía consulta al servidor	
	queryhora=("SET time_zone = '+00:00'")
	cursor.execute(queryhora)
	print(query)
	cursor.execute(query)
	column_names = list(map(lambda x: x.lower(), [d[0] for d in cursor.description]))
    # list of data items
	rows = list(cursor.fetchall())
	

	result = [od(zip(column_names, row)) for row in rows]
	return result

	
def extraer_rsamdr(inicio, final, estacion):
	"""
	Permite obtener los registros almacenados en las tablas rsam_dr por año, en una sola consulta

	Recibe como parámetros:

	:param inicio: Fecha inical de la lectura en formato '2019-01-01'
	:type clave: str
				
	:param final: Fecha final de la lectura en formato '2019-01-02'
	:type host: str
	:param estacion: código de 3 caracteres identificatorio de la estación Ej: FRE
	:type user: str
	
	:returns: Vector que contiene cada registro como un diccionario 

	:rtype: Array

	:Ejemplo:

	>>> import sys; sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/'); import ovdas_getfromdb_lib as gdb
	>>> data=gdb.extraer_rsamdr('2015-12-25','2019-12-17','FRE' )
	Año 2015 - 1959 registros
	Año 2016 - 101701 registros
	Año 2017 - 100497 registros
	Año 2018 - 83953 registros
	Año 2019 - 79556 registros
	Vector total contiene 367703 registros
	>>> print(data[0:2])
	[OrderedDict([('id', 417902204), ('id_estacion', 176), ('rsam', 0.128943), ('unixtime', Decimal('1451012700.00')),
	('frec', 10.7352), ('pot', 5788110000.0), ('dr', 0.126035), ('invrsam', None), ('aux1', None), ('aux2', None), ('aux3', None)]), 
	OrderedDict([('id', 417902205), ('id_estacion', 176), ('rsam', 0.123039), ('unixtime', Decimal('1451013000.00')), 
	('frec', 10.6375), ('pot', 6300750000.0), ('dr', 0.142768), ('invrsam', None), ('aux1', None), ('aux2', None), ('aux3', None)])]
	>>>


	"""
	#obtiene el id de la estacion entregada
	data=getCustomQuery('select id from ovd_estacion where cod="S'+estacion+'";')

	idestacion=data[0]['id']
	
	#pasa las fechas de string a datetime
	ini = dt.datetime.strptime(inicio, '%Y-%m-%d')

	fin = dt.datetime.strptime(final, '%Y-%m-%d')

	#obtiene año inicial y año final para iterar las tablas
	anoIni=ini.year
	anoFin=fin.year

	#itera las tablas mysql segun año
	for i, year in enumerate(range(anoIni, anoFin+1)):
		
		if i==0:
			
			query=('select from_unixtime(r.unixtime) as fecha, r.rsam, r.dr, r.frec, r.pot, r.unixtime from db_resultados.res_rsamdr_'+str(year)+' r where r.id_estacion='+str(idestacion)
			+' and r.unixtime between unix_timestamp("'+inicio+'") and unix_timestamp("'+final+'") order by r.unixtime asc;')
			
			data=getCustomQuery(query)
			print("Año "+str(year)+" - "+str(len(data))+" registros")
			
		elif (i>0 and i<len(range(anoIni, anoFin))):
			
			query=('select from_unixtime(r.unixtime) as fecha, r.rsam, r.dr, r.frec, r.pot, r.unixtime from db_resultados.res_rsamdr_'+str(year)+' r where r.id_estacion='+str(idestacion)
			+' and r.unixtime between unix_timestamp("'+inicio+'") and unix_timestamp("'+final+'") order by r.unixtime asc;')
			a=getCustomQuery(query)
			for x in a:
				data.append(x)
			print("Año "+str(year)+" - "+str(len(a))+" registros")
		else:
			
			query=('select from_unixtime(r.unixtime) as fecha, r.rsam, r.dr, r.frec, r.pot, r.unixtime from db_resultados.res_rsamdr_'+str(year)+' r where r.id_estacion='+str(idestacion)
			+' and r.unixtime between unix_timestamp("'+inicio+'") and unix_timestamp("'+final+'") order by r.unixtime asc;')
			a=getCustomQuery(query)
			for x in a:
				data.append(x)
			print("Año "+str(year)+" - "+str(len(a))+" registros")
			
			

	print("Vector total contiene "+str(len(data))+" registros")

	return data



def extraer_eventos(inicio, final, volcan, **kwargs):
	"""
	Permite obtener los registros almacenados en las tablas cla_loc por año, en una sola consulta

	Recibe como parámetros fijos:

	:param inicio: Fecha inical de la lectura en formato '2019-01-01' o bien '2019-01-01 00:10'
	:type clave: str
				
	:param final: Fecha final de la lectura en formato '2019-01-02' o bien '2019-01-02 00:10'
	:type host: str
	:param volcan: Nombre corto del volcan  Ej: NevChillan. Para extraer todos los volcanes ingresar '*'
	:type user: str
	
	Parámetros variables:
	Dentro de los parámetros variables pueden o no incluirse cualquiera del siguiente listado, estos se agregan a continuación del nombre del volcán separados por coma (,)
	
	Los parámetros que acotan la consulta a un valor exacto se ingresan de la siguiente forma:
		
	:param tipoEvento:  	Ej: tipoevento='LP'
	:param calidad:			Ej: calidad='A1'
	:param tipoloc:			Ej:	tipoloc='1'   (1:hypo71 | 2: Atenuación)
	
	En cambio, los parámetros que acotan la consulta a un subconjunto de valores se ingresan añadiendo el signo '>' o '<' en el valor, como se muestra a continuación 
	
	:param ML:				Ej: ML='>3'
	:param amplitudctas:	Ej: amplitudctas='>1000'
	:param s_p:				Ej: s_p='>2'
	:param frecuencia:		Ej: frecuencia='<10'
	:param duracion:		Ej: duracion='>30'
	:param magDuracion:		Ej:	magDuracion='>30'
	:param energia:			Ej: energia='>100000'
	
	:param latitud:			Ej: latitud='<-37.10'
	:param longitud:		Ej: longitud='>-71.0'
	:param profundidad:		Ej: profundidad='>5'
	:param nFases:			Ej: nFases='>6'
	:param gap:				Ej: gap='<130'
	:param distMedia:		Ej: distMedia='<5'
	:param rms:				Ej: rms='<0.5'
	:param erh:				Ej: erh='<0.5'
	:param erz:				Ej: erz='<0.5'
	:param nEstaciones:		Ej: nEstaciones='>3'
	
	
	:returns: Vector que contiene cada registro como un diccionario 

	:rtype: Array

	:Ejemplo:

	>>> import sys; sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/'); import ovdas_getfromdb_lib as gdb
	>>> data=gdb.extraer_eventos('2015-12-25','2019-12-17','NevChillan', tipoEvento='LP', ML='2' )
	Año 2015 - 0 registros
	Año 2016 - 39 registross
	Año 2017 - 19 registross
	Año 2018 - 49 registross
	Año 2019 - 0 registros
	Vector total contiene 107 registros
	>>> import pandas as pd
	>>> pd.DataFrame(data)
				fecha  zona cod        evento tipoevento  ...     q    dr  tipoloc  idevento  amplitud_ums
	0   2016-01-14 10:38:53.000083     2   9  01141338.9LP         LP  ...  None  None        1        10          None
	1   2016-01-30 07:20:39.000074     2   9  01301020.9LP         LP  ...  None  None        1        10          None
	2   2016-02-06 23:24:01.000017     2   9  02070223.9LP         LP  ...  None  None        1        10          None
	3   2016-02-16 00:43:58.000088     2   9  02160343.9LP         LP  ...  None  None        1        10          None
	4   2016-03-09 09:29:26.000045     2   9  03091229.9LP         LP  ...  None  None        1        10          None
	..                         ...   ...  ..           ...        ...  ...   ...   ...      ...       ...           ...
	102 2018-07-29 18:49:32.000086     2   9  07292249.9LP         LP  ...  None  None        1        10          None
	103 2018-07-29 18:49:32.000098     2   9  07292249.9LP         LP  ...  None  None        1        10          None
	104 2018-08-02 23:07:06.000095     2   9  08030306.9LP         LP  ...  None  None        1        10          None
	105 2018-09-17 04:59:58.000072     2   9  09170759.9LP         LP  ...  None  None        1        10          None
	106 2018-10-08 00:56:57.000072     2   9  10080356.9LP         LP  ...  None  None        1        10          None

	[107 rows x 32 columns]
	>>>
	


	"""
	if (volcan=='*'):
		idvolcan='idvolc'
	else:
		#obtiene el id del volcan entregado
		data=getCustomQuery('select id from ovd_volcan where nombre_db="'+volcan+'";')

		idvolcan=data[0]['id']
	
	#pasa las fechas de string a datetime
	if (len(inicio)<11):
		ini = dt.datetime.strptime(inicio, '%Y-%m-%d')
	else:
		ini = dt.datetime.strptime(inicio, '%Y-%m-%d %H:%M')
	
	if (len(final)<11):
		fin = dt.datetime.strptime(final, '%Y-%m-%d')
	else:
		fin = dt.datetime.strptime(final, '%Y-%m-%d %H:%M')

	#obtiene año inicial y año final para iterar las tablas
	anoIni=ini.year
	anoFin=fin.year

	
	filtros=''
	#itera entre los parámetros variables ingresados y crea los filtro mysql a partir de ellos
	for key, value in kwargs.items():
		if ('>' in value or '<' in value):
			filtros=filtros+' and '+key+value
		else:
			filtros=filtros+' and '+key+'="'+value+'"'
	
	
	#itera las tablas mysql segun año
	for i, year in enumerate(range(anoIni, anoFin+1)):
		
		if i==0:          
			query=('select from_unixtime(c.unixtime) as fecha, c.* from db_resultados.cla_loc_'+str(year)+' c where c.idvolc='+str(idvolcan)+' and '
			+ '(c.unixtime between unix_timestamp("'+inicio+'") and unix_timestamp("'+final+'")) '+filtros+' order by c.unixtime asc;')
			
			data=getCustomQuery(query)
			print("Año "+str(year)+" - "+str(len(data))+" registros")
			
		elif (i>0 and i<len(range(anoIni, anoFin))):
			
			query=('select from_unixtime(c.unixtime) as fecha, c.* from db_resultados.cla_loc_'+str(year)+' c where c.idvolc='+str(idvolcan)+' and '
			+ '(c.unixtime between unix_timestamp("'+inicio+'") and unix_timestamp("'+final+'")) '+filtros+' order by c.unixtime asc;')
			a=getCustomQuery(query)
			for x in a:
				data.append(x)
			print("Año "+str(year)+" - "+str(len(a))+" registross")
		else:
			
			query=('select from_unixtime(c.unixtime) as fecha, c.* from db_resultados.cla_loc_'+str(year)+' c where c.idvolc='+str(idvolcan)+' and '
			+ '(c.unixtime between unix_timestamp("'+inicio+'") and unix_timestamp("'+final+'")) '+filtros+' order by c.unixtime asc;')
			a=getCustomQuery(query)
			for x in a:
				data.append(x)
			print("Año "+str(year)+" - "+str(len(a))+" registros")
			
			

	print("Vector total contiene "+str(len(data))+" registros")

	return data

	

def extraer_eventos_dia(inicio, final, volcan, tipoevento):
	"""
	Permite obtener la cantidad de eventos por volcan y tipo de evento, agrupados por día.
	Esta estructura de datos es usada para crear graficas temporales de números de eventos por día

	Recibe como parámetros fijos:

	:param inicio: Fecha inical de la lectura en formato '2019-01-01'
	:type clave: str
				
	:param final: Fecha final de la lectura en formato '2019-01-02'
	:type host: str
	
	:param volcan: Nombre corto del volcan  Ej: 'NevChillan'.
	:type user: str
	
	:param tipoevento: Abreviación del tipo de evento a extraer  Ej: 'VT'.
	:type user: str
	
		
	:returns: Vector que contiene cada registro como un diccionario 

	:rtype: Array

	:Ejemplo:

	>>> import sys; sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/'); import ovdas_getfromdb_lib as gdb
	>>> data=gdb.extraer_eventos_dia('2016-01-01','2019-06-01','NevChillan','VT')
	Año 2016 - 321 registros
	Año 2017 - 309 registross
	Año 2018 - 284 registross
	Año 2019 - 120 registrosss
	Vector total contiene 1034 registros
	>>> import pandas as pd
	>>> pd.DataFrame(data)
				 dia  eventos          energia
	0     2016-01-01        5     142814098981
	1     2016-01-02       11    1336027888967
	2     2016-01-03        4    1019007167527
	3     2016-01-05        8     465385150488
	4     2016-01-06        3     121150510364
	...          ...      ...              ...
	1029  2019-05-23        3  580638287095038
	1030  2019-05-24        1      12347718406
	1031  2019-05-26        2      57629968759
	1032  2019-05-27        2      57629968759
	1033  2019-05-28        3    3166162044674

	[1034 rows x 3 columns]
	>>>
	


	"""
	#obtiene el id del volcan entregado
	
	try:
		
		idvolcan=int(volcan)
	except:
	
		data=getCustomQuery('select id from ovd_volcan where nombre_db="'+volcan+'";')

		idvolcan=data[0]['id']
		
				
	try:
		
		idtipoevento=int(tipoevento)
	except:
	
		data=getCustomQuery('select id from db_resultados.res_tipoEvento where descripcion="'+tipoevento+'";')

		idtipoevento=data[0]['id']
	
	#pasa las fechas de string a datetime

	ini = dt.datetime.strptime(inicio, '%Y-%m-%d')
	
	
	fin = dt.datetime.strptime(final, '%Y-%m-%d')
	

	#obtiene año inicial y año final para iterar las tablas
	anoIni=ini.year
	anoFin=fin.year


	
	#itera las tablas mysql segun año
	for i, year in enumerate(range(anoIni, anoFin+1)):
		
		if i==0:          
			query=('select CAST(from_unixtime(`unixtime`) AS DATE) as dia, count(id) as eventos , sum(energia) as energia from db_resultados.res_evento_'+str(year)+' where id_tipoEvento='+str(idtipoevento)+' and '
			+ '(unixtime between unix_timestamp("'+inicio+'") and unix_timestamp("'+final+'")) and id_volcan='+str(idvolcan)+' group by  CAST(from_unixtime(`unixtime`) AS DATE);')
			
			data=getCustomQuery(query)
			print("Año "+str(year)+" - "+str(len(data))+" registros")
			
		elif (i>0 and i<len(range(anoIni, anoFin))):
			
			query=('select CAST(from_unixtime(`unixtime`) AS DATE) as dia, count(id) as eventos , sum(energia) as energia from db_resultados.res_evento_'+str(year)+' where id_tipoEvento='+str(idtipoevento)+' and '
			+ '(unixtime between unix_timestamp("'+inicio+'") and unix_timestamp("'+final+'")) and id_volcan='+str(idvolcan)+' group by  CAST(from_unixtime(`unixtime`) AS DATE);')
			
			a=getCustomQuery(query)
			for x in a:
				data.append(x)
			print("Año "+str(year)+" - "+str(len(a))+" registross")
		else:
			
			query=('select CAST(from_unixtime(`unixtime`) AS DATE) as dia, count(id) as eventos , sum(energia) as energia from db_resultados.res_evento_'+str(year)+' where id_tipoEvento='+str(idtipoevento)+' and '
			+ '(unixtime between unix_timestamp("'+inicio+'") and unix_timestamp("'+final+'")) and id_volcan='+str(idvolcan)+' group by  CAST(from_unixtime(`unixtime`) AS DATE);')
			
			a=getCustomQuery(query)
			for x in a:
				data.append(x)
			print("Año "+str(year)+" - "+str(len(a))+" registrosss")
			
			

	print("Vector total contiene "+str(len(data))+" registros")

	return data
	
	
def extraer_energia_acumulada(final, volcan, tipoevento):
	"""
	Permite obtener la cantidad de eventos por volcan y tipo de evento, agrupados por día.
	Esta estructura de datos es usada para crear graficas temporales de números de eventos por día

	Recibe como parámetros fijos:

	:param final: Fecha final de la lectura en formato '2019-01-02'
	:type host: str
	
	:param volcan: Nombre corto del volcan  Ej: 'NevChillan'.
	:type user: str
	
	:param tipoevento: Abreviación del tipo de evento a extraer  Ej: 'VT'.
	:type user: str
	
		
	:returns: Cantidad de energía acumulada desde el inicio del monitoreo hasta la fecha ingresa

	:rtype: int

	:Ejemplo:

	>>> import sys; sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/'); import ovdas_getfromdb_lib as gdb
	>>> data=gdb.extraer_energia_acumulada('2019-06-01','NevChillan','VT')
	>>> data
	Decimal('31191019639645118')
	>>>
	


	"""
	#obtiene el id del volcan entregado
	
	try:
		
		idvolcan=int(volcan)
	except:
	
		data=getCustomQuery('select id from ovd_volcan where nombre_db="'+volcan+'";')

		idvolcan=data[0]['id']
		
				
	try:
		
		idtipoevento=int(tipoevento)
	except:
	
		data=getCustomQuery('select id from db_resultados.res_tipoEvento where descripcion="'+tipoevento+'";')

		idtipoevento=data[0]['id']
	
	#pasa las fechas de string a datetime
	
	inicio='2007-01-01'

	ini = dt.datetime.strptime('2007-01-01', '%Y-%m-%d')
	
	
	fin = dt.datetime.strptime(final, '%Y-%m-%d')
	

	#obtiene año inicial y año final para iterar las tablas
	anoIni=ini.year
	anoFin=fin.year


	energia=0
	#itera las tablas mysql segun año
	for i, year in enumerate(range(anoIni, anoFin+1)):
		
		
			query=('select sum(energia) as energia from db_resultados.res_evento_'+str(year)+' where id_tipoEvento='+str(idtipoevento)+' and '
			+ '(unixtime between unix_timestamp("'+inicio+'") and unix_timestamp("'+final+'")) and id_volcan='+str(idvolcan)+';')
			data=getCustomQuery(query)
			
			if data[0]['energia'] is not None:
				
				#print(data[0]['energia'])
				energia=energia+data[0]['energia']
				
			
	
	return int(energia)