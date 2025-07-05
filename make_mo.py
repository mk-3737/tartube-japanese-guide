import polib

po = polib.pofile('tartube.po')
po.save_as_mofile('tartube.mo')
