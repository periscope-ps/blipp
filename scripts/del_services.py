from blipp.unis_client import UNISInstance

unis = UNISInstance({"unis_url":"http://dev.incntre.iu.edu"})
s = unis.get("/services?name=blipp&properties.configurations.hostname=hikerbear")
s = s if s else []
s2 = unis.get("/services?name=blipp&runningOn.href=http://dev.incntre.iu.edu/nodes/510b3492e77989124500008f")
s2 = s2 if s2 else []

s.extend(s2)

for serv in s:
    unis.delete("/services/" + serv["id"])



