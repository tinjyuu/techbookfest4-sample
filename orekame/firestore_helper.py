import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import threading
import logging

logger = logging.getLogger(__name__)
cred = credentials.Certificate('/home/pi/orekame/sa.json')
firebase_admin.initialize_app(cred, {
    'projectId': "replace-your-id",
})
db = firestore.client()
doc_ref = db.collection(u'robots').document(u'orekame')


class FireStoreHelper(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.command = ""
        self.status = ""
        self.running = True

    def update_command(self):
        try:
            doc = doc_ref.get()
            d = doc.to_dict()
            self.command = d.get("command")
        except Exception as e:
            logger.error(u'No such document! {}'.format(e))

    def run(self):
        while self.running:
            self.update_command()
            self.update_status()

    def update_status(self):
        try:
            doc = doc_ref.get()
            d = doc.to_dict()
            self.status = d.get("status")
        except Exception as e:
            logger.error(u'No such document! {}'.format(e))
