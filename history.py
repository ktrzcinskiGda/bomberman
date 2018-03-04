import xml.dom.minidom
import engine

filename = 'history.xml'
doc = xml.dom.minidom.Document()
r = doc.createElement('history')
counter = 0

def addTimestamp(document=doc, root=r):
    global counter
    timestamp = document.createElement('timestamp')
    timestamp.setAttribute('count', str(counter))
    counter += 1

    tiles = document.createElement('tiles')
    t = engine.world.map.getraw()
    s = ''
    for l in t:
        s += ''.join(l) + '\n'
    tiles.appendChild(document.createTextNode(s))
    timestamp.appendChild(tiles)

    xmlagents = document.createElement('agents')
    for a in engine.world.map.agents:
        xmla = document.createElement('agent')
        xmla.setAttribute('x', str(a.x))
        xmla.setAttribute('y', str(a.y))
        xmla.setAttribute('vx', str(a.vx))
        xmla.setAttribute('vy', str(a.vy))
        xmlagents.appendChild(xmla)
    timestamp.appendChild(xmlagents)

    xmlbombs = document.createElement('bombs')
    for b in engine.world.map.bombs:
        xmlb = document.createElement('bomb')
        xmlb.setAttribute('x', str(b.x))
        xmlb.setAttribute('y', str(b.x))
        xmlbombs.appendChild(xmlb)
    timestamp.appendChild(xmlbombs)

    p = engine.player
    xmlplayer = document.createElement('player')
    xmlplayer.setAttribute('x', str(p.x))
    xmlplayer.setAttribute('y', str(p.y))
    xmlplayer.setAttribute('vx', str(p.vx))
    xmlplayer.setAttribute('vy', str(p.vy))
    timestamp.appendChild(xmlplayer)

    root.appendChild(timestamp)


def laodFile():
    counter = 0
    r = xml.dom.minidom.parse(filename)

def restorestatic(obj, xml):
    obj.x, obj.y = xml.getAttribute("x"), xml.getAttribute("y")

def restoremobile(obj, xml):
    restorestatic(obj, xml)
    obj.vx, obj.vy = xml.getAttribute("vx"), xml.getAttribute("vy")

def restore(i = -1):
    global counter
    if i == -1:
        i = counter
        counter += 1
    hist = r.childNodes[0]
    t = hist.getElementsByTagName("timestamp")[i]
    engine.world.map.tile = t.getElementsByTagName("tiles")
    restoremobile(engine.player, t.getElementsByTagName("player"))
    agents = t.getElementsByTagName("agents")
    engine.world.map.agents.clear()
    for a in agents:
        engine.world.map.agents.append(engine.Agent(0, 0))
        restoremobile(engine.world.map.agents[-1], a)
    engine.world.map.bombs.clear()
    bombs = t.getElementsByTagName("bombs")
    for b in bombs:
        engine.world.map.bombs.append(engine.Bombs(0, 0))
        restorestatic(engine.Bombs[-1], b)

def save():
    doc.appendChild(r)
    with open(filename, 'wb+') as out:
        s = doc.toprettyxml(newl='\n', encoding='utf-8')
        out.write(s)
