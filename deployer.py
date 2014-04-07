import subprocess,__main__,os,pprint,math,json,signal, pyodbc, local, decimal, calendar, datetime, config, urllib.request, urllib.error, sys, logging, logging.handlers, time
#import __main__, os , datetime ,pprint,sys,subprocess, logging, logging.handlers, config, time, local, calendar


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)

        return super(DecimalEncoder, self).default(o)


class RESTHandler(logging.Handler):
    """
    A handler class which sends log strings to a wx object
    """
    def __init__(self,host,port,url):
        """
        Initialize the handler
        @param wxDest: the destination object to post the event to 
        @type wxDest: wx.Window
        """
        logging.Handler.__init__(self)
        self.host = host
        self.port = port
        self.url = url

    def flush(self):
        """
        does nothing for this handler
        """


    def emit(self, record):
        """
        Emit a record.


        """
        try:

            data = {'level': record.levelname, 'message': record.getMessage(), "date":record.asctime, "local":local.local['name']}
            jsonS = json.dumps(data, cls=DecimalEncoder)
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            headersD = {'X-COIN':'h4kun4m4t4t4k4p15c4bul','ID':local.local['id']}
            headers.update(headersD)
            post_data = jsonS.encode('utf-8')
            #print(jsonS)
            request = urllib.request.Request(self.host+':'+self.port+self.url, data=post_data, headers=headers)
            body = urllib.request.urlopen(request)
        except Exception as e:
            #print(e)

            ster = getRealPath()
            f = open(ster + '\\' + config.params["log_error_file"]+'.dead', 'a')
            f.write(time.strftime('%d/%m/%Y %H:%M:%S')+' # CONNECTION ERROR # '+self.host+':'+self.port+self.url+'\n')
            f.close()




def getRealPath():

    try:
        if hasattr(sys, 'frozen'):    
            aux = sys.executable.split("\\")
            aux.pop()
            ster = "\\".join(aux)
        else:
            ster=os.path.dirname(os.path.abspath(getattr(__main__,'__file__','__main__.py')))

        return ster
    except Exception as e:
        logging.error("SOMETHING WENT WRONG ON getRealPath, EXCEPTION : [%s]",e)
        sys.exit(-1)   



def setConfiguration():

    try:
        ster = getRealPath()
        
        pp = pprint.PrettyPrinter(indent=4)
        f= open(ster +'\\config.py','w')
        ppaux = pp.pformat(config.params)
        f.write('params =' +ppaux+'\n')
        ppaux = pp.pformat(config.local)
        f.write('local ='+ppaux+'\n')
        f.close()
        f= open(ster + '\\local.py','w')
        ppaux = pp.pformat(local.local)
        f.write('local ='+ppaux+'\n')
        f.close()
        logging.debug("CONFIGURATION WAS SAVED")
    except Exception as e:
        logging.error("SOMETHING WENT WRONG ON setConfiguration, EXCEPTION : [%s]",e)
        sys.exit(-1)   



def setLogs():

    try:
        ster = getRealPath()
        formatStr = '[%(asctime)s # %(lineno)d # %(levelname)s] %(message)s'
            
        # SE CREA EL HANDLER QUE ESCRIBIRA LA INFORMACION DE FUNCIONAMIENTO DEL PROGRAMA, Y 
        # DE SER EL CASO LOS MENSAJES DE DEBUG
        size = int(config.params['log_size']) * 1048576
        fh = logging.handlers.RotatingFileHandler(ster + '\\' +config.params['log_file'], maxBytes=size, backupCount=7)
        
        # SE CREA EL HANDLER QUE ENVIARA MENSAJES AL API, SIEMPRE A PARTIR DEL NIVEL INFO PARA NO SOBRECARGAR LA RED
        rh = RESTHandler(config.params["url"],config.params["port"],config.params["errors"])
        rh.setLevel(logging.INFO)

        # SE CREA EL HANDLER QUE ESCRIBIRA EN UN ARCHIVO ROTATORIO CUALQUIER LOG DE ERRORES
        efh = logging.handlers.RotatingFileHandler(ster +'\\'+ config.params['log_error_file'], maxBytes=size, backupCount=7)
        efh.setLevel(logging.ERROR)    

        logging.basicConfig(level='DEBUG',handlers=[fh,rh,efh],format=formatStr)
    except Exception as e:
        logging.error("SOMETHING WENT WRONG ON setLogs, EXCEPTION : [%s]",e)
        sys.exit(-1)           
   



try:

    ster = getRealPath()

    
    setLogs()

    spo = open(ster + '\\' + config.params['subprocess_o'],'w')
    spe = open(ster + '\\' + config.params['subprocess_e'],'w')

    print("1")

    if config.params['init']:
        subprocess.call(["git","clone",config.params['repo'],ster + '\\' +config.local['path']],universal_newlines=True,stderr=spe, stdout=spo)
        subprocess.call(["git","-C",ster + '\\' +config.local['path'],"fetch","origin",config.local['branch']],universal_newlines=True,stderr=spe, stdout=spo)
        result = subprocess.call(["git","-C",ster + '\\' +config.local['path'],"checkout",config.local['branch']],universal_newlines=True,stderr=spe, stdout=spo)
        print("2")

        if result == 0:
            config.params['init'] = 0
            setConfiguration()
            logging.info("LOADER INSTALLED ON CLIENT")
            spo.close()
            spe.close()
            sys.exit(0)
        else: 
            logging.error("LOADER INSTALLATION FAILED")
            spo.close()
            spe.close()
            sys.exit(-1)

    else:

        orgn = subprocess.check_output(["git","-C",ster + '\\' +config.local['path'],"rev-parse","HEAD"],universal_newlines=True,stderr=spe)
        rmte = subprocess.check_output(["git","-C",ster + '\\' +config.local['path'],"ls-remote",config.params['repo'],config.local['branch']],universal_newlines=True,stderr=spe)

        orgn = orgn.strip(' \t\n\r')
        rmte = rmte.split("\t")[0].strip(' \t\n\r')


        if orgn != rmte:

            subprocess.call(["git","-C",ster + '\\' +config.local['path'],"fetch","--all"],universal_newlines=True,stderr=spe,stdout=spo)
            subprocess.call(["git","-C",ster + '\\' +config.local['path'],"reset","--hard","origin/"+config.local['branch']],universal_newlines=True,stderr=spe, stdout=spo)
            logging.info("DEPLOYER UPDATED FROM HEAD %s TO %s",orgn,rmte)

        spo.close()
        spe.close()
        sys.exit(0)

    
except Exception as e:
    logging.error("SOMETHING WENT WRONG on main, EXCEPTION : [%s]",e)
    spo.close()
    spe.close()
    sys.exit(-1)


