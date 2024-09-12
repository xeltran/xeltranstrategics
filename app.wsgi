import sys
sys.path.insert(0, '/var/www/xeltranstrategics')

activate_this = '/root/.local/share/virtualenvs/xeltranstrategics-E2THiQfu/bin/activate_this.py'
with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

from app import app as application