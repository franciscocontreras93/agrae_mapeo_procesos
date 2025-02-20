import psycopg2
import os


class connectionDriver():
    _BASEDIR_ = os.path.abspath(os.path.dirname(__file__))
    def __init__(self) -> None:
        os.environ['PGSERVICEFILE'] = os.path.join(self._BASEDIR_,'pg_service.conf')

        self.conn = None

        self.local  = True
    

    def connection(self):
        
        if self.local:
            return psycopg2.connect(service='local')
        else :
            return psycopg2.connect(service='production')

        
    

