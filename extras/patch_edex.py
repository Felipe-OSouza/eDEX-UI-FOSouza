#!/usr/bin/env python3
"""
Aplica patches no eDEX-UI AppImage extraído.

Patches:
  1. _boot.js: lastWindowState inclui width/height/x/y
  2. _boot.js: restaurar e salvar geometria da janela
  3. _renderer.js: desabilitar keepGeometry (força 16:9)
  4. _renderer.js: desabilitar leave-full-screen (força 960x540)

Uso:
  python3 patch_edex.py
"""

import os, shutil

BASE = os.path.expanduser("~/AppImage/squashfs-root/resources/app")
BOOT_PATH     = os.path.join(BASE, "_boot.js")
RENDERER_PATH = os.path.join(BASE, "_renderer.js")

# ── Backups ───────────────────────────────────────────────────────────────────
for p in [BOOT_PATH, RENDERER_PATH]:
    bak = p + ".bak"
    if not os.path.exists(bak):
        shutil.copy(p, bak)
        print(f"Backup criado: {bak}")
    else:
        print(f"Backup já existe: {bak}")

# ══════════════════════════════════════════════════════════════════════════════
# _boot.js
# ══════════════════════════════════════════════════════════════════════════════
with open(BOOT_PATH, "r", encoding="utf-8") as f:
    boot = f.read()

boot_original_len = len(boot)

# Patch 1 – default lastWindowState inclui campos de geometria
OLD1 = 'JSON.stringify({useFullscreen:!0},"",4)'
NEW1 = 'JSON.stringify({useFullscreen:!0,width:null,height:null,x:null,y:null},"",4)'

if OLD1 in boot:
    boot = boot.replace(OLD1, NEW1, 1)
    print("✔ Patch 1: default lastWindowState atualizado")
else:
    print("✘ Patch 1: âncora não encontrada (pode já estar aplicado)")

# Patch 2 – restaurar e salvar geometria da janela
OLD2 = (
    'signale.complete("Frontend window created!"),'
    'win.show(),'
    'e.allowWindowed?require(lastWindowStateFile).useFullscreen||win.setFullScreen(!1):win.setResizable(!1),'
    'signale.watch("Waiting for frontend connection...")'
    '}'
)
NEW2 = (
    'signale.complete("Frontend window created!"),'
    '(()=>{'
        'let _st={};'
        'try{_st=JSON.parse(fs.readFileSync(lastWindowStateFile,"utf-8"))}catch(_e){}'
        'let _full=_st.useFullscreen!==!1;'
        'if(e.allowWindowed&&!_full){'
            'if(_st.width&&_st.height)win.setSize(_st.width,_st.height);'
            'if(_st.x!=null&&_st.y!=null)win.setPosition(_st.x,_st.y);'
            'win.setFullScreen(!1);'
        '}else if(!e.allowWindowed){'
            'win.setResizable(!1);'
        '}'
        'const _save=()=>{'
            'if(win.isFullScreen()||win.isMaximized())return;'
            'try{'
                'let _s=JSON.parse(fs.readFileSync(lastWindowStateFile,"utf-8"));'
                'let[_w,_h]=win.getSize();'
                'let[_wx,_wy]=win.getPosition();'
                '_s.width=_w;_s.height=_h;_s.x=_wx;_s.y=_wy;'
                'fs.writeFileSync(lastWindowStateFile,JSON.stringify(_s,"",4));'
            '}catch(_e){}'
        '};'
        'win.on("resize",_save);'
        'win.on("move",_save);'
    '})(),'
    'win.show(),'
    'signale.watch("Waiting for frontend connection...")'
    '}'
)

if OLD2 in boot:
    boot = boot.replace(OLD2, NEW2, 1)
    print("✔ Patch 2: geometria de janela implementada")
else:
    print("✘ Patch 2: âncora não encontrada (pode já estar aplicado)")

with open(BOOT_PATH, "w", encoding="utf-8") as f:
    f.write(boot)

print(f"   _boot.js: {boot_original_len} → {len(boot)} bytes")

# ══════════════════════════════════════════════════════════════════════════════
# _renderer.js
# ══════════════════════════════════════════════════════════════════════════════
with open(RENDERER_PATH, "r", encoding="utf-8") as f:
    rnd = f.read()

rnd_original_len = len(rnd)

# Patch 3 – desabilitar keepGeometry (força 16:9 ao redimensionar)
OLD3 = (
    'electronWin.on("resize",(()=>{'
    '!1!==settings.keepGeometry&&'
    '(clearTimeout(window.resizeTimeout),'
    'window.resizeTimeout=setTimeout((()=>{'
    'let e=electron.remote.getCurrentWindow();'
    'if(e.isFullScreen())return!1;'
    'if(e.isMaximized())return e.unmaximize(),e.setFullScreen(!0),!1;'
    'let t=e.getSize();'
    't[0]>=t[1]?e.setSize(t[0],parseInt(9*t[0]/16)):e.setSize(t[1],parseInt(9*t[1]/16))'
    '}),100))'
    '}))'
)
NEW3 = 'electronWin.on("resize",(()=>{/* keepGeometry desabilitado */}))'

# Patch 4 – desabilitar leave-full-screen (força 960x540)
OLD4 = 'electronWin.on("leave-full-screen",(()=>{electron.remote.getCurrentWindow().setSize(960,540)}));'
NEW4 = 'electronWin.on("leave-full-screen",(()=>{/* tamanho fixo desabilitado */}));'

if OLD3 in rnd:
    rnd = rnd.replace(OLD3, NEW3, 1)
    print("✔ Patch 3: keepGeometry/resize desabilitado")
else:
    print("✘ Patch 3: âncora resize não encontrada")

if OLD4 in rnd:
    rnd = rnd.replace(OLD4, NEW4, 1)
    print("✔ Patch 4: leave-full-screen 960x540 desabilitado")
else:
    print("✘ Patch 4: âncora leave-full-screen não encontrada")

with open(RENDERER_PATH, "w", encoding="utf-8") as f:
    f.write(rnd)

print(f"   _renderer.js: {rnd_original_len} → {len(rnd)} bytes")
print("\nTodos os patches aplicados. Próximo passo: reempacotar o .asar e testar.")
