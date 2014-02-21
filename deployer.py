import subprocess, logging, config, time, local


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
            post_data = jsonS.encode('utf-8')
            #print(jsonS)
            request = urllib.request.Request(self.host+':'+self.port+self.url, data=post_data, headers=headers)
            body = urllib.request.urlopen(request)
        except Exception as e:
            #print(e)
            f = open(config.params["log_error_file"]+'.dead', 'a')
            f.write(time.strftime('%d/%m/%Y %H:%M:%S')+' # CONNECTION ERROR # '+self.host+':'+self.port+self.url+'\n')
            f.close()



def setLogs():

    formatStr = '[%(asctime)s # %(lineno)d # %(levelname)s] %(message)s'
        
    # SE CREA EL HANDLER QUE ENVIARA MENSAJES AL API, SIEMPRE A PARTIR DEL NIVEL INFO PARA NO SOBRECARGAR LA RED
    rh = RESTHandler(config.params["url"],config.params["port"],config.params["errors"])
    rh.setLevel(logging.INFO)

    logging.basicConfig(level='DEBUG',handlers=[rh],format=formatStr)



setLogs()

orgn = subprocess.check_output(["git","-C","../totones","rev-parse","HEAD"],universal_newlines=True,stderr=subprocess.STDOUT)
rmte = subprocess.check_output(["git","-C","../totones","ls-remote","git://github.com/lealtag/test-mf.git","HEAD"],universal_newlines=True,stderr=subprocess.STDOUT)

orgn = orgn.strip(' \t\n\r')
rmte = rmte.split("\t")[0].strip(' \t\n\r')


if orgn != rmte:

	subprocess.check_output(["git","-C","../totones","fetch","--all"],universal_newlines=True,stderr=subprocess.STDOUT)
	subprocess.check_output(["git","-C","../totones","reset","--hard","origin/master"],universal_newlines=True,stderr=subprocess.STDOUT)
	logging.info("DEPLOYER UPDATED FROM HEAD %s TO %s",orgn,rmte)





