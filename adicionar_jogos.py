#!/usr/bin/env python3
"""Coloca no menu do Game Stick (CUBEGM) os jogos copiados para roms/<sistema>/.

Uso:
  python3 adicionar_jogos.py <pasta_do_cartao>            -> só mostra o que faria
  python3 adicionar_jogos.py <pasta_do_cartao> --aplicar  -> faz as mudanças

  <pasta_do_cartao> é onde o cartão aparece no PC (a pasta que contém cubegm/ e roms/).
  No Linux costuma ser /media/<usuario>/disk; no Windows, algo como E:/
  Requer Python 3. Para gerar capas provisórias: pip install pillow

- Converte .cue/.bin de PSX para .img (1 faixa) ou "(Track 1).iso" (várias faixas).
- Acrescenta os jogos novos em roms/root.dat (3 idiomas), cubegm/fileinfo e gamelist.xml.
- Tira do menu entradas cujo arquivo não existe mais.
- Cria uma capa simples para quem não tem imagem em roms/<sistema>/images/.
- Antes de mudar, guarda cópia do índice em ~/gamestick-backups/indice_<data>/.
Arcade/CPS/FBNeo/MAME são ignorados (zips de arcade podem ser peças de outros jogos).
"""
import glob, os, re, shutil, sys, time, zipfile

args = [a for a in sys.argv[1:] if not a.startswith('--')]
CARD = args[0] if args else f"/media/{os.environ.get('USER', '')}/disk"  # ponto de montagem comum no Linux
APLICAR = '--aplicar' in sys.argv
R = f'{CARD}/roms'; FI = f'{CARD}/cubegm/fileinfo'
ORDER = ['?', 'arcade', 'fbneo', 'mame', 'atari2600', 'atari5200', 'atari7800', 'atarilynx', 'cps1', 'cps2', 'cps3',
         'pcengine', 'nes', 'nesh', 'gb', 'sfc', 'snes', 'gbc', 'gba', 'genesis', 'gamegear', 'megadrive', 'ngpc', 'psx']
ARCADE = {'arcade', 'fbneo', 'mame', 'cps1', 'cps2', 'cps3'}
IGNORAR = {'.xml', '.png', '.jpg', '.srm', '.sav', '.state', '.state1', '.txt', '.dat', '.cue', '.html', '.old'}
PSX_OK = {'.img', '.iso', '.pbp'}

if not os.path.exists(R + '/root.dat'):
    sys.exit(f'Não achei {R}/root.dat. O cartão está montado em {CARD}?')

# 1) PSX: .cue/.bin -> .img / (Track 1).iso
for cue in sorted(glob.glob(R + '/psx/*.cue')):
    b = os.path.basename(cue)[:-4]
    tr = sorted(glob.glob(glob.escape(f'{R}/psx/{b}') + ' (Track *).bin'))
    src = tr[0] if tr else f'{R}/psx/{b}.bin'
    dst = src[:-4] + ('.iso' if tr else '.img')
    if not os.path.exists(src):
        print('AVISO: .cue sem .bin correspondente:', cue); continue
    print(f'PSX: {os.path.basename(src)} -> {os.path.basename(dst)}' + (f' (+{len(tr)-1} faixas de música removidas)' if len(tr) > 1 else ''))
    if APLICAR:
        os.rename(src, dst)
        for t in tr[1:]: os.remove(t)
        os.remove(cue)

fi = list(map(int, open(FI).read().split(',')))
z = zipfile.ZipFile(R + '/root.dat'); files = {n: z.read(n).decode('utf-8') for n in z.namelist()}; z.close()
idx = {l.split('\t')[0] for l in files['fileinfo.001'].split('\n') if l}
low = {p.lower() for p in idx}
remove = {p for p in idx if not os.path.exists(f'{R}/{p}')}

nid = fi[0]; new = []
for s in ORDER[1:]:
    if s in ARCADE or not os.path.isdir(f'{R}/{s}'): continue
    for fn in sorted(os.listdir(f'{R}/{s}')):
        p = f'{s}/{fn}'; ext = os.path.splitext(fn)[1].lower()
        if os.path.isdir(f'{R}/{p}') or p in idx or p.lower() in low or fn.lower().startswith('disksys'): continue
        if s == 'psx' and (ext not in PSX_OK or (not APLICAR and ext == '.bin')): continue
        if ext in IGNORAR or (ext == '.bin' and s != 'megadrive'): continue
        nome = os.path.splitext(fn)[0]
        nome = re.sub(r'\s*\((USA|Europe|Japan|World|USA, Europe|Track 0?1)\)', '', nome).strip() if s == 'psx' else nome.strip()
        nid += 1; new.append((s, nid, fn, nome, os.path.splitext(fn)[0]))

print('\nTirar do menu (arquivo não existe):', sorted(remove) or 'nenhum')
print('Colocar no menu:', len(new))
for s, i, fn, nome, b in new: print(f'  {i}  {s:10} {nome}')
if not APLICAR:
    print('\nNada foi alterado. Rode de novo com --aplicar para fazer as mudanças.'); sys.exit()
if not new and not remove:
    print('Nada a fazer.'); sys.exit()

bk = os.path.expanduser('~/gamestick-backups/indice_' + time.strftime('%Y%m%d-%H%M%S'))
os.makedirs(bk); shutil.copy(R + '/root.dat', bk); shutil.copy(FI, bk)
for s in {x[0] for x in new} | {p.split('/')[0] for p in remove}:
    if os.path.exists(f'{R}/{s}/gamelist.xml'): shutil.copy(f'{R}/{s}/gamelist.xml', f'{bk}/gamelist_{s}.xml')
print('Backup do índice em', bk)

# capas provisórias
try:
    from PIL import Image, ImageDraw, ImageFont
    TTF = f'{CARD}/cubegm/Arial_en.ttf'; big = ImageFont.truetype(TTF, 44); small = ImageFont.truetype(TTF, 28)
    for s, i, fn, nome, b in new:
        os.makedirs(f'{R}/{s}/images', exist_ok=True); img = f'{R}/{s}/images/{b}.png'
        if os.path.exists(img): continue
        im = Image.new('RGB', (640, 480), (20, 30, 70)); d = ImageDraw.Draw(im)
        d.rectangle([12, 12, 627, 467], outline=(0, 200, 255), width=6)
        d.text((320, 80), s.upper(), font=small, fill=(180, 180, 180), anchor='mm')
        linhas, cur = [], ''
        for w in nome.split():
            t = (cur + ' ' + w).strip()
            if d.textlength(t, font=big) > 570 and cur: linhas.append(cur); cur = w
            else: cur = t
        linhas.append(cur); y = 250 - (len(linhas) - 1) * 28
        for l in linhas[:5]: d.text((320, y), l, font=big, fill=(255, 255, 255), anchor='mm'); y += 56
        im.convert('P', palette=Image.ADAPTIVE).save(img)
except ImportError:
    print('Pillow não instalado: jogos novos ficam sem capa.')

# root.dat
for n, txt in files.items():
    trail = txt.endswith('\n'); lines = [l for l in txt.split('\n') if l and l.split('\t')[0] not in remove]
    for s in ORDER[1:]:
        add = [f'{s}/{fn}\t{i}  {nome.upper()}\t{i}  {nome.upper()}\t{i}  {nome}\t{nome}\timages/{b}.png'
               for ss, i, fn, nome, b in new if ss == s]
        if not add: continue
        pos = [k for k, l in enumerate(lines) if l.startswith(s + '/')]
        at = max(pos) + 1 if pos else len(lines); lines[at:at] = add
    files[n] = '\n'.join(lines) + ('\n' if trail else '')
with zipfile.ZipFile(R + '/root.dat.new', 'w', zipfile.ZIP_DEFLATED) as zo:
    for n in sorted(files): zo.writestr(n, files[n].encode('utf-8'))
os.replace(R + '/root.dat.new', R + '/root.dat')

# fileinfo
for p in remove: fi[ORDER.index(p.split('/')[0]) + 1] -= 1
for s, *_ in new: fi[ORDER.index(s) + 1] += 1
fi[0] = nid; open(FI, 'w').write(','.join(map(str, fi)))

# gamelist.xml
for s in {x[0] for x in new} | {p.split('/')[0] for p in remove}:
    gp = f'{R}/{s}/gamelist.xml'
    if not os.path.exists(gp): continue
    g = open(gp, encoding='utf-8-sig', newline='').read(); nl = '\r\n' if '\r\n' in g else '\n'
    for p in remove:
        if p.startswith(s + '/'):
            g = re.sub(r'\t<game>(?:(?!</game>).)*?<path>\./' + re.escape(p.split('/', 1)[1]) + r'</path>.*?</game>\r?\n', '', g, flags=re.S)
    m = re.search(r'<video_id>(.*?)</video_id>\s*<class_type>(.*?)</class_type>\s*<game_type>(.*?)</game_type>\s*<timer>(.*?)</timer>', g)
    v, c, gt, tm = m.groups() if m else ('x', '0', '0', s)
    blk = ''.join(f'\t<game>\n\t\t<gameid>{i}</gameid>\n\t\t<path>./{fn}</path>\n\t\t<image>./images/{b}.png</image>\n'
                  f'\t\t<video_id>{v}</video_id>\n\t\t<class_type>{c}</class_type>\n\t\t<game_type>{gt}</game_type>\n'
                  f'\t\t<timer>{tm}</timer>\n\t\t<zh_CN>{i}  {nome}</zh_CN>\n\t\t<en_US>{i}  {nome}</en_US>\n'
                  f'\t\t<zh_TW>{i}  {nome}</zh_TW>\n\t\t<ko_KR>{i}  {nome}</ko_KR>\n\t\t<name>{nome}</name>\n\t</game>\n'
                  for ss, i, fn, nome, b in new if ss == s and f'./{fn}</path>' not in g)
    g = g.replace('</gameList>', blk.replace('\n', nl) + '</gameList>')
    open(gp, 'w', encoding='utf-8-sig', newline='').write(g)
getattr(os, "sync", lambda: None)()  # os.sync não existe no Windows
print('Pronto. Novo total (maior ID):', nid, '— ejete o cartão antes de tirar.')
