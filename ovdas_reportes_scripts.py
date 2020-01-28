import datetime as dt

def gen_REAV(fechas=[dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(hours=24), '%Y-%m-%d %H:%M'),dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M")],ML=">1.5",ms=2,anchomap=40):
    """Genera un REAV semiautomático (guardado en el directorio de trabajo), basándose en la búsqueda de eventos del último día LOCALIZADOS
    
    :param fechas: Par [fecha inicial,fecha final], por defecto busca en las últimas 24 horas
    :type fechas: [str,str], opcional
    :param ML: Magnitud local mínima para la búsqueda de eventos. Por defecto busca eventos con ML>1.5
    	:type ML: float, opcional
    :param ms: Factor de escala para el símbolo (circulito) de la localización, por defecto=4
    :type ms: float, opcional
    :param anchomap: Extensión de ancho del mapa ploteado. Por defecto = 80 km
    :type anchomap: float, opcional
    :returns: Documento .doc
    
    :Ejemplo:
    
    >>> import sys
    >>> sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
    >>> import ovdas_reportes_scripts as reportes
    >>> reportes.gen_REAV(fechas=["2019-12-01T00:00","2019-12-05T00:00"],ML=2.0,ms=3,anchomap=40)
    >>> 
    0 - Tatara, VT con ML: 2.3 (201912020039)
    1 - Nevados de Chillan, LP con ML: 3.4 (201912011618)
    2 - Nevados de Chillan, EX con ML: 3.4 (201912011529)
    Seleccione el evento:
    >>> 1
    Mapa generado, en proceso etapa de generación de DOC
    	
    
    """
    #cargar los eventos del ultimo dia con ML>1.5
    import ovdas_getfromdb_lib as gdb
    import ovdas_figure_lib as ffig
    import ovdas_doc_lib as doc
    import ovdas_formulas_lib as formu
    import pandas as pd
    a = gdb.extraer_eventos(inicio=fechas[0],final=fechas[1],ML=ML,volcan='*')

    volcanes_data = gdb.volc_metadata(volc='all')
    #permitir seleccionar uno
    i=0
    a = pd.DataFrame(a)
    a.reset_index()
    print(a)
    for index,row in a.iterrows():
        print(str(i)+" - "+volcanes_data[volcanes_data.id==row.idvolc].nombre_db.iloc[0])
        i=i+1
    '''
    sel = input('Seleccione el evento: ')  
    a = (a[a.index==int(sel)])
    stadata = gdb.esta_metadata(a.iloc[0]['nombredb'],tipo='net')
    pathmap = ffig.plot_map(a,stadata,fechas='',anch=anchomap,ms=ms,op='REAV')
    print(" ")
    print('Archivo .doc generado en la carpeta de trabajo')
    #calcular DR
    stadata = gdb.esta_metadata(tipo='all')

    dist = stadata.distcrater[stadata.idestacion==a.iloc[0]['ev_esta']]
    sensz= stadata.sensz[stadata.idestacion==a.iloc[0]['ev_esta']]
    amp  = a.iloc[0]['ev_amp']
    freq = a.iloc[0]['ev_freq']  
    amp=amp*sensz
    DR=formu.DRc(amp,freq,dist)
	#generar reporte
    doc.REAV(a,pathmap,DR)
    '''

def gen_mapa(fechas,vol,anch=80,ms=2,tiev="all"):
    """Genera un mapa de localizaciones

    :param fechas: Par [fecha inicial,fecha final], por defecto busca en las últimas 24 horas
    :type fechas: [str,str]
    :param vol: Volcán en particular (nombre segun base de datos)
    :type vl: str
    :param tiev: Tipo de evento a plotear ("VT","LP", etc). Por defecto todos!
    :type tiev: str, opcional
    :param anchp: Extensión de ancho del mapa ploteado. Por defecto = 80 km
    :type anchp: float, opcional
    :param ms: Factor de escala para el símbolo de la localización, por defecto=4
    :type ms: float, opcional
    :returns: Documento .png

    :Ejemplo:
        
    >>> import sys
    >>> sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
    >>> import ovdas_reportes_scripts as reportes
    >>> reportes.gen_mapa(fechas=['2019-10-01T00:00', '2019-12-04T00:00'],vol="NevChillan",anch=80,ms=2)
    >>> 
    Mapa generado en la carpeta de trabajo
    
    """
    import ovdas_getfromdb_lib as gdb
    import ovdas_figure_lib as ffig
    a = gdb.get_evloc(fechas=fechas,vol=vol,tiev=tiev) 
    stadata = gdb.esta_metadata(vol,tipo='net')
    ffig.plot_map(a,stadata,fechas,anch=anch,ms=ms,sel=tiev)
    print(" ")
    print("Mapa guardado en la carpeta de trabajo")
    
def gen_apri(vol,fechas):
    """Genera gráfico de parámetros primarios por volcán

    :param vol: Volcán en particular (nombre segun base de datos)
    :type vl: str
    :param fechas: Par [fecha inicial,fecha final]
    :type fechas: [str,str]
    :returns: Documento .png

    :Ejemplo:
        
    >>> import sys
    >>> sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
    >>> import ovdas_reportes_scripts as reportes
    >>> reportes.plot_resumen_primario(vol,fechas)
    >>> 
    figura guardada en carpeta de trabajo
    
    """
    import ovdas_getfromdb_lib as gdb
    import ovdas_figure_lib as ffig
    evs = gdb.get_evs_todos(fechas=fechas,vol=vol)
    evs_loc = gdb.get_evloc(fechas=fechas,vol=vol)
    ffig.plot_apri(evs,evs_loc,fechas,vol,ar='portrait')