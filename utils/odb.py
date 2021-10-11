# Objects DB - Maintain a list of objects and their co-ords
# HanishKVC, 2021
# GPL


import pickle


def initdb():
    return {}


def store(db, sFName):
    f = open(sFName, "wb+")
    pickle.dump(db, f)


def load(sFName):
    f = open(sFName, "rb")
    db = pickle.load(f)
    return db


def _key(lat, lon):
    if type(lat) == str:
        lat = float(lat)
        lon = float(lon)
    k = "{:6.2f}-{:6.2f}".format(lat, lon)
    return k


def set(db, lat, lon, data):
    k = _key(lat, lon)
    db[k] = data


def get(db, lat, lon):
    k = _key(lat, lon)
    try:
        return db[k]
    except:
        return None


