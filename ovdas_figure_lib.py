import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from math import cos, radians
import numpy as np
from matplotlib.ticker import FormatStrFormatter,MaxNLocator
from netCDF4 import Dataset
from mpl_toolkits.basemap import Basemap, shiftgrid, cm
from matplotlib.colors import LightSource
import matplotlib.colors as colors
import matplotlib.patches as patches
import pandas as pd
from simplekml import (Kml, OverlayXY, ScreenXY, Units, RotationXY,
                       AltitudeMode, Camera)
import ovdas_getfromdb_lib as gdb 
def plot_map(a,stadata,fechas,anch=80,ms=3,sel='all',op=''):
    print("NUEVA VERSIÓN, AHORA EN LA CARPETA DE TRABAJO SE GUARDA ARCHIVO KMZ CON LOCALIZACION(ES)")
    print("QUIZAS (LO MAS PROBABLE) SEA NECESARIO INSTALAR LIBRERIA KML, EN EL PROMPT EJECUTAR")
    print("conda install -c conda-forge simplekml")
    print("SI SALE EL ERROR 'NO MODULE NAME SIMPLEKML'\n\n\n\n\n")
    kml = Kml()
    #a = pd.DataFrame.from_dict(a, orient='index')
    #stadata = pd.DataFrame.from_dict(stadata, orient='index')
    if op=='REAV':
        zona=a.iloc[0]['zona_id']
        cod=a.iloc[0]['vol_cod']
        latv=float(a.iloc[0]['vol_lat'])
        lonv=float(a.iloc[0]['vol_lon'])
        nref=float(a.iloc[0]['vol_alt'])
        t_deg = anch/(111.320*cos(radians(latv)))
        ancho = haversine(float(lonv), float(latv), float(lonv)+float(t_deg), float(latv))
        ancho = int(round(ancho))
        factorlatlon=param_volcan(zona,cod)[0]  
        londelta = float(t_deg/2); latdelta = float(londelta*factorlatlon)
        tiev,late,lone,profe,ML=[],[],[],[],[]
        for i in range(0,len(a)):
            tiev.append(a.iloc[0]['ev_tipoev']) 
            late.append(a.iloc[0]['ev_lat'])  
            lone.append(a.iloc[0]['ev_lon'])  
            profe.append(a.iloc[0]['ev_prof'])  
            ML.append(a.iloc[0]['ev_ml'])  
    else:
        zona = a.zona_id;cod=a.vol_cod;latv=float(a.vol_lat);lonv=float(a.vol_lon);nref=a.vol_alt
        tiev = a.ev_tipoev
        late= a.ev_lat  
        lone= a.ev_lon 
        profe = a.ev_prof  
        ML = a.ev_ml  
        t_deg = anch/(111.320*cos(radians(latv[0])))
        ancho = haversine(float(lonv[0]), float(latv[0]), float(lonv[0])+float(t_deg), float(latv[0]))
        ancho = int(round(ancho))
        factorlatlon=param_volcan(zona[0],cod[0])[0]  
        londelta = float(t_deg/2); latdelta = float(londelta*factorlatlon)
    gs = gen_fig_topo()
    x,y='prof','lat' #Latitud vs prof (x,y,datos_x,datos_y,nref)
    subfig_prof(x,y,profe,late,nref,gs,latv,lonv,latdelta,londelta,tiev,'hypo',ms,ML)
    gs,m= gen_fig_map(nref,latv,lonv,latdelta,londelta,zona,cod,gs,factorlatlon,ancho/4,t_deg,op,fechas)
    if op!='reav':
        #plot_esta(m,stadata,kml,ms)
        print(sel)
        from matplotlib.lines import Line2D
        legend_elements = [Line2D([], [], marker='o', color='k', label='ML=1',lw=0, markersize=ms*1,markerfacecolor='none'),
           Line2D([], [], marker='o', color='k', label='ML=2',lw=0, markersize=ms*2,markerfacecolor='none'),
           Line2D([], [], marker='o', color='k', label='ML=3',lw=0, markersize=ms*3,markerfacecolor='none'),
           Line2D([], [], marker='^', color='k', label='Est. Sísmica',lw=0,markerfacecolor='k', markersize=ms*2)
           ]
        if sel=='all':
             legend_elements.extend([Line2D([], [], marker='o', color='k', label='VT',lw=0,markerfacecolor='r', markersize=ms*3),
           Line2D([], [], marker='o', color='k', label='LP',lw=0,markerfacecolor='y', markersize=ms*3)])
        else:
            if sel=='VT':color='r'
            elif sel=='LP':color='y'
            legend_elements.extend([Line2D([], [], marker='o', color='k', label=sel,lw=0,markerfacecolor=color, markersize=ms*3),
           Line2D([], [], marker='o', color='none', label='',lw=0,markerfacecolor='none', markersize=ms*3)])            
        #legend = plt.gca().legend(ncol=2,title='Leyenda',handles=legend_elements, loc='lower right', fontsize=ms*3)
        #plt.setp(legend.get_title(),fontsize=ms*3)
    plot_sis(late,lone,latv,lonv,latdelta,londelta,m,tiev,'hypo',ms,ML) #MAPA
    x,y='lon','prof'
    subfig_prof(x,y,lone,profe,nref,gs,latv,lonv,latdelta,londelta,tiev,'hypo',ms,ML)
    path = save_fig_vol(zona,cod)
    
    #evs = pd.DataFrame.from_dict(a).T
    fol01 = kml.newfolder(name='ML 0-1')
    fol12 = kml.newfolder(name='ML 1-2')
    fol23 = kml.newfolder(name='ML 2-3')
    fol39 = kml.newfolder(name='ML >3')
    for index,row in a.iterrows():
        if row['ev_ml']>0 and row['ev_ml']<1.1:
            pnt = fol01.newpoint()
        elif row['ev_ml']>1 and row['ev_ml']<2.1:
            pnt = fol12.newpoint()
        elif row['ev_ml']>2 and row['ev_ml']<3.1:
            pnt = fol23.newpoint()
        elif row['ev_ml']>3:
            pnt = fol39.newpoint()
        if row['ev_tipoev']=='VT':
            pnt.style.iconstyle.color = 'ff0000ff'
        elif row['ev_tipoev']=='LP': 
            pnt.style.iconstyle.color = 'ff00ffff'
        elif row['ev_tipoev']=='VD': 
            pnt.style.iconstyle.color = 'ffff00ff'
        lat = row['ev_lat']
        lon = row['ev_lon']
        pnt.coords = [(lon,lat)]
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png'
    kml.savekmz(str(zona)+str(cod)+".kmz")

    return path
def plot_esta(m,stadata,kml,ms):
    folesta = kml.newfolder(name='sta')
    for index,row in stadata.iterrows():
        pnt = folesta.newpoint()
        x=float(row['longitud']);y=float(row['latitud'])
        pnt.name =row['codcorto']
        pnt.coords = [(x,y)]
        pnt.style.iconstyle.color = 'ff000000'
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/triangle.png'
        x,y=m(x,y)
        plt.plot(x,y,"^",color='k',ms=ms*2)
    
def plot_sis(lat,lon,lat_vol,lon_vol,latdelta,londelta,m,ev,loc,tam,ML):
	#DATOS A PLOTEAR
	lats = lat
	lons = lon 
	x,y = m(lons,lats)
	vx,vy = m(lon_vol,lat_vol)
	vxx,vyy = m(lon_vol-londelta+0.09,lat_vol-latdelta+0.03)
	m.plot(vx,vy,'*',mfc=(1,1,1),ms=10)
	#estax,estay=m(lon_esta,lat_esta)
	#m.plot(x,y,20,marker='o',color='r',)

	#m.plot(x,y,fig,ms=4*tam,alpha=0.7,mew=0.4,mfc=col)
	def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    		new_cmap = colors.LinearSegmentedColormap.from_list(
        	'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        	cmap(np.linspace(minval, maxval, n)))
    		return new_cmap	
	cmap2 = plt.get_cmap('RdYlGn_r')
	#cmap2 = plt.get_cmap('copper')
	cmap2 = truncate_colormap(cmap2, 0.0, 1)
	#plt.hexbin(x, y, mincnt=1, bins=25)
	tam = float(tam)

	#l1 = plt.scatter([],[], facecolor=col,alpha=0.7,lw=0.4,s=tam*10, edgecolors='k')
	#l2 = plt.scatter([],[], facecolor=col,alpha=0.7,lw=0.4,s=tam*2*10, edgecolors='k')
	#l3 = plt.scatter([],[], facecolor=col,alpha=0.7,lw=0.4,s=tam*3*10, edgecolors='k')
	#l4 = plt.scatter([],[], facecolor=col,alpha=0.7,lw=0.4,s=tam*4*10, edgecolors='k')

	
	try:
		for n in range(0,len(lat)):
		    if ev[n]=='VT':	
		        col=(1,0,0)
		    elif ev[n]=='VD':
		        col=(1,0,1)	
		    elif ev[n]=='HB':
		        col=(1,0.5,0)	
		    elif ev[n]=='LP':
		        col=(1,1,0)		
		    elif ev[n]=='IC':
		        col=(0,1,0)	
		    elif ev[n]=='LV':
		        col=(0.5,0.5,0)	
		    elif ev[n]=='TO':
		        col=(0.3,0.3,0)	
		    if loc=='hypo':
		        fig = 'o'
		    elif loc=='ate':
		        col=(0.5,0.5,0.5)
		        fig = 's'
		    if loc=="hypo":
		        m.plot(x[n],y[n],fig,ms=tam*ML[n],alpha=0.7,mew=1,mfc=col, mec='k')
		    elif loc=="ate":
		        m.plot(x[n],y[n],fig,ms=tam*1,alpha=0.7,mew=1,mfc=col, mec='k')
		#leg = plt.legend([l1, l2, l3, l4], ["1","2","3","4"], ncol=2, frameon=True, fontsize=12, loc = 'lower right', borderpad = 0.2,handletextpad=0.5, title='ML',scatterpoints=1)
	except:
		if loc=="hypo":
			m.plot(x,y,fig,ms=tam*3,alpha=0.7,mew=1,mfc=col, mec='k')
		elif loc=="ate":
			m.plot(x,y,fig,ms=tam*3,alpha=0.7,mew=1,mfc=col, mec='k')	

			
def gen_fig_topo():
    m = plt.figure()
    gs = gridspec.GridSpec(2, 2,width_ratios=[1,9], height_ratios=[9,1])
    gs.update(left=0.08, right=0.95,top=0.95,bottom=0.07, wspace=0.03, hspace=0.03)
    return gs
	
def save_fig_vol(zona,cod):
    plt.subplots_adjust(hspace=0.1)
    path=str(zona)+str(cod)+'.png'
    plt.savefig(path,dpi=300)
    plt.close("all")
    return path
	
def subfig_prof(x,y,datx,daty,nivel_ref,gs,lat_vol,lon_vol,latdelta,londelta,ev,loc,tam,ML):
    tam = float(tam)
    if x =='prof':
        ax4 = plt.subplot(gs[0])
        datx = datx-(np.float32(nivel_ref)/1000)
        plt.locator_params(axis = 'x', nbins = 4)
        plt.xlim(10,-6.4)
        ax4 = plt.subplot(gs[0])
        plt.xlabel('km')
        ax4.tick_params(labelsize=8)
    elif x=='lat' or x=='lon':
        datx = datx
    else:
        print('no se reconoce opcion para graficar (lat,lon,prof)')
    if y =='prof':
        ax4 = plt.subplot(gs[3])
        daty = daty-(np.float32(nivel_ref)/1000)
        plt.ylim(10,-6.4)
        plt.locator_params(axis = 'y', nbins = 4)
        ax4.yaxis.tick_right()
        ax4.tick_params(labelsize=8)
    elif y=='lat' or y=='lon':
        daty = daty
    else:
        print('no se reconoce opcion para graficar (lat,lon,prof)')
    if y=='lat':
        plt.ylim(lat_vol-latdelta,lat_vol+latdelta)
        plt.axvline(x=-5, ymin=0, ymax=1, color='gray',ls='dashed',alpha=0.5)
        plt.axvline(x=0, ymin=0, ymax=1, color='gray',ls='dashed',alpha=0.5)
        plt.axvline(x=5, ymin=0, ymax=1, color='gray',ls='dashed',alpha=0.5)
        ax4.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    if x=='lon':
        plt.xlim(lon_vol-londelta,lon_vol+londelta)
        plt.axhline(y=-5, xmin=0, xmax=1, color='gray',ls='dashed',alpha=0.5)
        plt.axhline(y=0,  xmin=0, xmax=1, color='gray',ls='dashed',alpha=0.5)
        plt.axhline(y=5,  xmin=0, xmax=1, color='gray',ls='dashed',alpha=0.5)
        ax4.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    for n in range(0,len(ML)):
        if ev[n]=='VT':    
            col=(1,0,0)
        elif ev[n]=='VD':
            col=(1,0,1)    
        elif ev[n]=='HB':
            col=(1,0.5,0)    
        elif ev[n]=='LP':
            col=(1,1,0)        
        elif ev[n]=='IC':
            col=(0,1,0)    
        elif ev[n]=='LV':
            col=(0.5,0.5,0)    
        elif ev[n]=='TO':
            col=(0.3,0.3,0)    
        if loc=='hypo':
            fig = 'o'
        elif loc=='ate':
            col=(0.5,0.5,0.5)
            fig = 's'
        else:
            "error"
        plt.plot(datx[n],daty[n],fig,ms=tam*ML[n],alpha=0.6,mec="k",mfc=col, mew=1)

def gen_fig_map(nivel_ref,lat_vol,lon_vol,latdelta,londelta,zona,cod,gs,factorlatlon,km,test_deg,op,fechas):
	##CREACION DE MAPA
	ax2 = plt.subplot(gs[1])
	url = "C:/nc/" + str(zona) + "/" + cod+  ".nc"
	etopodata = Dataset(url)
	try:
		topoin = etopodata.variables['z'][:] ; lons = etopodata.variables['x'][:] ; lats = etopodata.variables['y'][:]
	except:
		topoin = etopodata.variables['z_range'][:] ; lons = etopodata.variables['x_range'][:] ; lats = etopodata.variables['y_range'][:]
	m = Basemap(projection='merc',llcrnrlat=lat_vol-latdelta,urcrnrlat=lat_vol+latdelta,  llcrnrlon=lon_vol-londelta,urcrnrlon=lon_vol+londelta,lat_ts=(max(lats)+min(lats))/2,resolution='i')

	#LUZ
	ls = LightSource(azdeg = 180, altdeg = 60)
	# transform to nx x ny regularly spaced 5km native projection grid
	nx = int((m.xmax-m.xmin)/50.)+1; ny = int((m.ymax-m.ymin)/50.)+1
	topodat,x,y = m.transform_scalar(topoin,lons,lats,nx,ny,returnxy=True)
	cmap = plt.get_cmap('gist_earth')
	def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    		new_cmap = colors.LinearSegmentedColormap.from_list(
        	'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        	cmap(np.linspace(minval, maxval, n)))
    		return new_cmap
	new_cmap = truncate_colormap(cmap, 0.1, 0.7)
	# plot image over map with imshow.
	#im = m.imshow(topodat,cmap='gist_earth')
	rgb = ls.shade(topodat, new_cmap)
	#PLOTEO DE MAPA
	im = m.imshow(rgb, alpha=0.6)
	plt.gca().add_patch(patches.Rectangle((0,0),km*1250, km*370,facecolor="#ffffff"))
	m.drawmapscale(lon_vol-(test_deg*0.35),lat_vol-(latdelta*0.875),lon_vol,lat_vol,km,barstyle='fancy',format='%.1f')
	if op=='reav':
		()
	else:
		plt.text(0.02,0.95,str(fechas[0])+" - " +str(fechas[1]),fontsize=8,color='k',ha='left',bbox=dict(facecolor='111111', alpha=0.85,pad=2),transform = plt.gca().transAxes)
	return gs,m
	
def haversine(lon1, lat1, lon2, lat2):
    from math import radians, cos, sin, asin, sqrt
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def param_volcan(zona,cod):
    zona=str(zona)
    if zona=='1':
        if cod=='C':factor=0.700 ;id=1;
        if cod=='A':factor=0.690 ;id=2;
        if cod=='P':factor=0.700 ;id=3;
        if cod=='G':factor=0.700 ;id=4;
        if cod=='S':factor=0.685 ;id=5;
        if cod=='8':factor=0.700 ;id=6;
        if cod=='I':factor=0.690 ;id=7;
        if cod=='O':factor=0.690 ;id=8;
        if cod=='E':factor=0.620 ;id=9;
        if cod=='R':factor=0.680 ;id=10;
        if cod=='L':factor=0.675 ;id=11;
        if cod=='T':factor=0.618 ;id=12;
        if cod=='J':factor=0.610 ;id=13;
        if cod=='N':factor=0.608 ;id=14;
    if zona=='2':
        if cod=='P': factor=0.600 ;id=15;
    #PELLADO               ;id=16;                          
        if cod=='D': factor=0.545 ;id=17;
        if cod=='I': factor=0.600 ;id=18;        
        if cod=='M': factor=0.600 ;id=19;
        if cod=='6': factor=0.590 ;id=20;
        if cod=='9': factor=0.537 ;id=21;
        if cod=='N': factor=0.582 ;id=22;
        if cod=='G': factor=0.535 ;id=23;
        if cod=='Z': factor=0.580 ;id=24;
        if cod=='Q': factor=0.580 ;id=25;
    if zona=='3':
        if cod=='L': factor=0.574 ;id=26;
        if cod=='S': factor=0.570 ;id=27;
        if cod=='V': factor=0.571 ;id=28;
        if cod=='Q': factor=0.570 ;id=29;
        if cod=='N': factor=0.570 ;id=30;
        if cod=='H': factor=0.560 ;id=31;
        if cod=='K': factor=0.560 ;id=32;    
        if cod=='E': factor=0.515 ;id=33;        
        if cod=='A': factor=0.560 ;id=34;
    #PUNTIAGUDO-LOS CENIZOS      ;id=35;    
    if zona=='4':
        if cod=='O':factor=0.554 ;id=36;
        if cod=='B':factor=0.510 ;id=37;
        if cod=='1':factor=0.548 ;id=38;
        if cod=='H':factor=0.544 ;id=39;        
        if cod=='C':factor=0.542 ;id=40;        
        if cod=='2':factor=0.540 ;id=41;
        if cod=='7':factor=0.490 ;id=42;
        if cod=='Y':factor=0.527 ;id=43;
        if cod=='4':factor=0.525 ;id=44;
        if cod=='W':factor=0.518 ;id=45;
        if cod=='K':factor=0.518 ;id=48;
        if cod=='U':factor=0.515 ;id=46;        
    return factor,id

    
def plot_apri(evs,evs_loc,fechas,vol,ar='wide'):
    evs_c = gdb.count_evs(evs) #contar eventos
    evs.set_index('ev_fecha',inplace=True)
    plt.style.use('seaborn-darkgrid')
    if len(evs_c.columns)==0:
        raise Exception("Sin eventos para el periodo "+str(fechas))
    if ar=='wide':
        size=[10,1*len(evs_c.columns)]
    elif ar=='portrait':
        size=[8.5,1*len(evs_c.columns)]
    fig, axs = plt.subplots(len(evs_c.columns)*2, 1, sharex=True,figsize=size)
    fig.subplots_adjust(hspace=0)
    fig.suptitle('Conteo de eventos - '+vol,y=1)
    if len(evs_c.columns)>1:
        i=0
        for series in evs_c.columns:
            tievstr=series[-2:]
            color=colores_cla(tievstr)
            axs[i].bar(evs_c.index,evs_c[series],edgecolor='k',rasterized=True)
            axs[i].yaxis.set_major_locator(MaxNLocator(integer=True))
            axs[i].set_ylim(0,max(evs_c[series])*1.1)
            axs[i].set(xlabel='fecha', ylabel='ev/día')
            axs[i].yaxis.get_major_ticks()[0].label1.set_visible(False)
            axs[i].locator_params(axis='y',nbins=4)
            #extrae VT y VD de los localizados
            evs_loc_fil= evs_loc[evs_loc.ev_tipoev == tievstr]
            evs_loc_fil.set_index('ev_fecha',inplace=True)
            if tievstr=='VT' or tievstr=='VD':
                axs[i+1].plot(evs_loc_fil.index,evs_loc_fil['ev_ml'],'o',ms=3,alpha=0.7)
                axs[i+1].set_ylim(0,max(evs_loc_fil['ev_ml'])*1.1)
                texto='ML'
            else:
                evs_fil= evs[evs.ev_tipoev == tievstr]
                axs[i+1].plot(evs_fil.index,evs_fil['ev_DR'],'o',ms=3,alpha=0.7)
                axs[i+1].set_ylim(0,max(evs_fil['ev_DR'])*1.1)
                axs[i+1].set(ylabel='cm*cm')  
                texto='DR'                
            if tievstr=='LV':tievstr='VLP'
            axs[i].text(0.02,0.8,tievstr,
            {'color': 'k','ha': 'left', 'va': 'center',
             'bbox': dict(boxstyle="round", fc=color, ec="black", pad=0.2,alpha=0.5)},
                        transform=axs[i].transAxes,rasterized=True)
            axs[i+1].text(0.02,0.8,texto,
            {'color': 'k','ha': 'left', 'va': 'center',
             'bbox': dict(boxstyle="round", fc=color, ec="black", pad=0.2,alpha=0.1)},fontsize=8,
                        transform=axs[i+1].transAxes,rasterized=True)
            axs[i+1].locator_params(axis='y',nbins=5)
            axs[i+1].yaxis.get_major_ticks()[0].label1.set_visible(False)
            i=i+2
    elif len(evs_c.columns)==1:
        for series in evs_c.columns:
            color=colores_cla(series[-2:])
            axs.bar(evs_c.index,evs[series],color=color,edgecolor='k')
            axs.yaxis.set_major_locator(MaxNLocator(integer=True))
            axs.set_ylim(0,max(evs_c[series])*1.1)
            axs.yaxis.get_major_ticks()[0].label1.set_visible(False)
            axs.set_xlim(fechas)
            
    plt.tight_layout()
    fig.subplots_adjust(hspace=0.1)  
    print('figura guardada en carpeta de trabajo')
    plt.savefig(vol+'_resumen.png', dpi=300)
    

def colores_cla(tipoev):
    DICT_COL={
        'VT': (1.00,0.00,0.00),
        'VD': (1.00,0.00,1.00),
        'LP': (1.00,1.00,0.00),
        'LV': (0.67,0.67,0.00),
        'TR': (0.00,1.00,1.00),
        'TO': (0.39,0.39,0.00),
        'HB': (1.00,0.55,0.00),
        'AV': (0.59,1.00,0.59),
        'IC': (0.00,1.00,0.00),
        'RY': (0.00,0.69,0.00),
        'EX': (0.00,0.39,0.00),
        'MI': (0.71,0.00,0.80),
        'BG': (0.00,0.00,1.00),
        'VA': (0.39,0.39,0.39),
        'RE': (0.69,0.69,0.69),
        'ZZ': (1.00,0.39,0.39),
        'MF': (1.00,0.75,0.00)
        }
    color= DICT_COL[tipoev]
    return color
    