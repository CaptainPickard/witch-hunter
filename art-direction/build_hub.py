
import base64, os
from PIL import Image
import io

artdir = '/workspace/witch-hunter/art-direction'
webdir = artdir + '/web'

def b64f(name):
    return 'data:image/jpeg;base64,' + base64.b64encode(open(webdir + '/' + name + '.jpg','rb').read()).decode()

def png_small(path, max_h=460):
    im = Image.open(path).convert('RGBA')
    w,h = im.size
    if h > max_h:
        im = im.resize((int(w*max_h/h), max_h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

lbase = artdir + '/sprites/noble-knight/layers'
L = {k: png_small(lbase + '/normalized/' + k + '.png') for k in ['body','cloak','chest','helm']}
LF = {k: png_small(lbase + '/normalized/' + k + '.png') for k in ['body-front','piece-cloak','piece-legs','piece-faulds','piece-gorget','piece-gloves','piece-chest','piece-helm']}

def fig(name, title, cap):
    return ('<figure class="panel"><div class="frame"><img src="' + b64f(name) + '"></div>'
            '<figcaption><span class="cap-title">' + title + '</span><span class="cap-body">' + cap + '</span></figcaption></figure>')

def pair(day, night, title, cap):
    return ('<div class="pair"><div class="pair-imgs">'
            '<div class="frame"><img src="' + b64f(day) + '"></div>'
            '<div class="frame"><img src="' + b64f(night) + '"></div></div>'
            '<div class="ptag"><span>day</span><span>night</span></div>'
            '<figcaption style="margin-top:8px"><span class="cap-title" style="display:block;font-variant:small-caps;letter-spacing:0.22em;color:#C9A227;font-size:13.5px;text-align:center">' + title + '</span>'
            '<span class="cap-body" style="display:block;color:#8D93A3;font-size:14.5px;text-align:center">' + cap + '</span></figcaption></div>')

world = (pair('d01-darkwood','c01-darkwood','DARKWOOD FORESTS','Day never truly arrives under the canopy; night belongs to the fog and the lantern is the only law.')
 + pair('d02-moors','c02-moors','MOORS AND HIGHLANDS','Day: long sight-lines and weathered stone. Night: the beacon window is a life-or-death question.')
 + pair('d03-blight','c03-blight','BLIGHTED ZONES','The blight has no honest day. Noon is a burned disc behind ash haze; the red glow never sleeps.')
 + pair('d04-tavern','c04-tavern','THE ROADSIDE TAVERN','Day: timber, thatch, honest light. Night: the amber windows become the point of the whole road.')
 + pair('d05-ambush','c05-ambush','THE MOOR ROAD AMBUSH','Same road, same wolves. By day the fight is readable; by night it is two points of light in the fog.')
 + pair('d06-council','c06-council','THE WAR COUNCIL','Day: cressets unlit, banners vivid. Night: torchlight and gravity. Departure time is the survival decision.')
 + pair('d07-mourning','c07-mourning','THE MOURNING RING','Fourteen cairns. By night, candle flames; by day, threads of smoke. The camp remembers its dead for fourteen days.')
 + pair('d08-veil-spire','c08-veil-spire','THE VEIL SPIRE','The gray noon exposes every spire and somehow makes it worse. Night hides it in fog; both are held breaths.')
 + pair('d09-hearth','c09-hearth','THE SAVE-POINT','Day: embers banking, dust in window light. Night: the hearth is the world.')
 + pair('d10-hunter','c10-hunter','THE HUNTER','Resolve reads in both lights. The archetype does not change with the clock; the world does.'))

cast = (fig('n-handmaiden','THE HANDMAIDEN','The princess\'s servant, candle in a night corridor. The court seen from underneath.')
 + fig('n-thrall','THE THRALL','Orc-camp slave, iron collar. Broken, not finished. Rescuable or recruitable.')
 + fig('n-banner-g','THE BANNERMAN, LIGHT','A trusted man holding a promise in cloth: white-and-gold stag banner over watch coals.')
 + fig('n-banner-d','THE BANNERMAN, DARK','Broken-sun banner, red brazier. Same rank as his mirror, different gravity.')
 + fig('n-bard-g','THE BARD, LIGHT-AFFINITY','Tavern bench, hearth pool. Protection buffs: joy is scarce and this man makes it.')
 + fig('n-bard-d','THE BARD, DARK-AFFINITY','Black lute, veiled courtiers, red cresset. The song is beautiful; the room is a trap.')
 + fig('n-gravedigger','PLAYER: THE GRAVEDIGGER UNDEAD','His own empty grave open in the foreground, corpse-green lantern. Death took him; his work ethic survived.')
 + fig('n-knight','PLAYER: THE NOBLE GOOD KNIGHT','Chapel vigil, greatsword planted, a vow in the dark.')
 + fig('n-wizard','PLAYER: THE COVEN HIDDEN WIZARD','Standing stones answering her cyan staff. No banner, no court, the old law.'))

scenes = (fig('s-bard-skel','THE BARD SKELETON','Crypt ossuary minstrel, spectral green candles. Nobody told him the party ended.')
 + fig('s-ghouls','THE RISING','Drowned-dead climbing from black water, grave-green rim, a hunter holding a tussock.')
 + fig('s-dragon','THE DRAGON\'S WINDUP','A tiny knight carrying the princess, one heartbeat ahead of the furnace breath.')
 + fig('s-toll','THE TOLL-KEEPER\'S BRIDGE','The Shadow Court\'s oldest institution: passage always has a price.'))

camps = (fig('camp-good','THE GOOD CAMP','White-and-gold order at dawn: banners flown, chapel shrine, warmth earned.')
 + fig('camp-neutral','THE NEUTRAL CAMP','Built for deniability: no banners, teal glass lanterns, a toll-ring den entrance.')
 + fig('camp-dark','THE DARK CAMP','The veil-black court at night: broken-sun banners, blood-red altar, undead watch. Wealth as threat.'))

pilots = (fig('n-gravedigger','PILOT I: THE GRAVEDIGGER UNDEAD','First character through S1-S7: turnaround, 8 directions, 5-frame idle, cleanup, atlas, live billboard.')
 + '<div class="grid2">'
 + '<figure class="panel"><div class="frame"><img src="' + b64f('gdir-atlas') + '"></div><figcaption><span class="cap-title">Gravedigger: 8-direction atlas</span><span class="cap-body">Turnaround-derived views; cloth subject, gentle boil in the idle.</span></figcaption></figure>'
 + '<figure class="panel"><div class="frame"><img src="' + b64f('gidle-atlas') + '"></div><figcaption><span class="cap-title">Gravedigger: 5-frame idle</span><span class="cap-body">Derived image-to-image from a single source view.</span></figcaption></figure>'
 + '</div>'
 + fig('n-knight','PILOT II: THE NOBLE KNIGHT','The armor consistency test: 3 QA rounds before PASS. Rigid armor animates cleaner than cloth.')
 + '<div class="grid2">'
 + '<figure class="panel"><div class="frame"><img src="' + b64f('kdir-atlas') + '"></div><figcaption><span class="cap-title">Knight: 8-direction atlas</span><span class="cap-body">Heraldic charge + held weapon: the consistency killers, caught by QA.</span></figcaption></figure>'
 + '<figure class="panel"><div class="frame"><img src="' + b64f('kidle-atlas') + '"></div><figcaption><span class="cap-title">Knight: 5-frame idle</span><span class="cap-body">Flicker improved vs cloth: symmetric subjects loop cleaner.</span></figcaption></figure>'
 + '</div>')

CSS = open(artdir + '/hub-template.css').read() if os.path.exists(artdir + '/hub-template.css') else ''
html = open(artdir + '/hub-template.html').read()
html = html.replace('__WORLD__', world).replace('__CAST__', cast).replace('__SCENES__', scenes)
html = html.replace('__CAMPS__', camps).replace('__PILOTS__', pilots)
html = html.replace('__L_CLOAK__', LF['piece-cloak']).replace('__L_BODY__', LF['body-front'])
html = html.replace('__L_LEGS__', LF['piece-legs']).replace('__L_FAULDS__', LF['piece-faulds'])
html = html.replace('__L_GORGET__', LF['piece-gorget']).replace('__L_GLOVES__', LF['piece-gloves'])
html = html.replace('__L_CHEST__', LF['piece-chest']).replace('__L_HELM__', LF['piece-helm'])
html = html.replace('__K_COMPOSITE__', b64f('knight-composite')).replace('__K_CONCEPT__', b64f('n-knight'))

out = artdir + '/index.html'
open(out, 'w').write(html)
leftover = [p for p in ['__WORLD__','__CAST__','__SCENES__','__CAMPS__','__PILOTS__','__L_BODY__','__K_COMPOSITE__'] if p in html]
print('written', out, os.path.getsize(out)//1024, 'KB; leftovers:', leftover)
