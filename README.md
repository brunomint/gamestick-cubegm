# gamestick-cubegm

Guia e script para **adicionar jogos e capas** nos "Game Stick 4K" de TV (M15 Pro, M8 e parecidos) que rodam o sistema **CUBEGM**.

> **Resumo:** nesses sticks, só copiar o jogo para a pasta do cartão **não faz ele aparecer no menu**. O menu lê um índice (`roms/root.dat`) que precisa ser atualizado. O script `adicionar_jogos.py` faz isso.

Este repositório **não contém jogos, BIOS nem arquivos do sistema do stick**. Ele traz só a explicação e um script escrito do zero, que trabalha com os arquivos que já estão no **seu** cartão.

---

## Sumário

1. [Meu stick usa CUBEGM?](#1-meu-stick-usa-cubegm)
2. [Como o sistema funciona](#2-como-o-sistema-funciona)
3. [Cuidados antes de mexer no cartão](#3-cuidados-antes-de-mexer-no-cartão)
4. [Adicionar jogos](#4-adicionar-jogos)
5. [Capas dos jogos (libretro-thumbnails)](#5-capas-dos-jogos-libretro-thumbnails)
6. [Desfazer as mudanças](#6-desfazer-as-mudanças)
7. [Cartão "vazio" ou que o PC não reconhece](#7-cartão-vazio-ou-que-o-pc-não-reconhece)
8. [Detalhes técnicos do índice](#8-detalhes-técnicos-do-índice)
9. [Perguntas frequentes](#9-perguntas-frequentes)
10. [Aviso legal e licença](#10-aviso-legal-e-licença)

---

## 1. Meu stick usa CUBEGM?

Muitos anúncios dizem que o stick roda **EmuELEC**, mas vários lotes vêm com outro sistema, o **CUBEGM**. Para saber qual é o seu, coloque o cartão no PC e olhe a raiz:

| Se o cartão tem... | Sistema |
|---|---|
| pastas `cubegm/` e `roms/`, e dentro de `cubegm/` arquivos como `rkgame`, `vmlinux.uImage`, `setting.xml` | **CUBEGM** → este guia serve |
| várias partições, uma delas com `emuelec/`, `.config/`, `roms/` (exFAT ou ext4) | EmuELEC → este guia **não** serve |

Este guia foi feito com um **Game Stick M15 Pro 4K**: processador dual-core Cortex-A7 ("GB2"), 256 MB de RAM e o menu "ALL GAMES" com abas MAME, Final Burn Neo, Arcade Classics, Favorites e PlayStation.

> ⚠️ **Não grave imagens de EmuELEC/RK3032 do archive.org num stick CUBEGM.** São sistemas diferentes, e o stick não liga.

---

## 2. Como o sistema funciona

Tudo fica num cartão de memória **FAT32** comum:

```
cartão/
├── cubegm/                 ← sistema (NÃO MEXER, exceto o "fileinfo")
│   ├── vmlinux.uImage      ← kernel Linux (MIPS)
│   ├── rkgame              ← o programa do menu e dos emuladores
│   ├── cores/              ← emuladores e BIOS
│   ├── saves/  states/     ← jogos salvos
│   ├── setting.xml         ← configurações (idioma, volume...)
│   └── fileinfo            ← contador de jogos por console
└── roms/
    ├── root.dat            ← ÍNDICE DO MENU
    ├── psx/
    │   ├── gamelist.xml    ← lista de jogos desta pasta
    │   ├── images/         ← capas
    │   └── (os jogos)
    ├── snes/  sfc/  nes/  nesh/  megadrive/  genesis/  ...
    └── arcade/  fbneo/  mame/  cps1/  cps2/  cps3/
```

**Pontos importantes:**

- O menu **não procura arquivos novos** nas pastas. Ele mostra só o que está em `roms/root.dat`.
- O `gamelist.xml` de cada pasta **não é lido para montar o menu**. Ele parece ser só a "fonte" usada por quem montou o cartão. O script atualiza ele também, para manter tudo coerente.
- O número no menu (ex.: **20536 GAMES**) é o **maior código de jogo** do índice, não a quantidade de jogos.

### Pastas e formatos

| Console | Pasta | Formatos |
|---|---|---|
| PlayStation 1 | `psx` | **`.img`, `.iso`, `.pbp`** (**`.cue` não abre**, veja abaixo) |
| Super Nintendo | `snes` / `sfc` | `.zip`, `.sfc`, `.smc` |
| Nintendinho (NES) | `nes` / `nesh` | `.nes`, `.zip` |
| Mega Drive / Genesis | `megadrive` / `genesis` | `.zip`, `.md`, `.smd`, `.bin` |
| Game Boy / Color / Advance | `gb` / `gbc` / `gba` | `.zip`, `.gb`, `.gbc`, `.gba` |
| Game Gear | `gamegear` | `.zip`, `.gg` |
| Neo Geo Pocket Color | `ngpc` | `.zip`, `.ngc` |
| PC Engine | `pcengine` | `.zip`, `.pce` |
| Atari | `atari2600` / `atari5200` / `atari7800` / `atarilynx` | conforme os jogos que já existem na pasta |
| Arcade | `arcade` / `fbneo` / `mame` / `cps1-3` | `.zip`, `.fba` (romsets com nome exato) |

> **Testado:** PlayStation (`.img`/`.iso`) e Mega Drive (`.zip` e `.smd`) funcionam depois de colocados no índice pelo script. Nos outros consoles, a regra é **usar o mesmo formato dos jogos que já funcionam naquela pasta**.
>
> **Traduções e versões modificadas** (hacks, ex.: "Sunset Riders (BR)") podem **não rodar**. Os emuladores do stick são simples, e esses jogos costumam ficar com a tela preta. Prefira as versões originais (USA/Europe/Japan).

### PlayStation: por que `.cue` não abre

O emulador por dentro até entende `.cue`, mas **o menu não abre jogos `.cue`**. Os jogos de fábrica estão todos em `.img`, `.iso` ou `.pbp`. A solução, que o script aplica sozinho:

| Seu jogo | Vira |
|---|---|
| `Jogo.cue` + `Jogo.bin` (1 faixa) | `Jogo.img` (só renomeia, o conteúdo é o mesmo) |
| `Jogo.cue` + `Jogo (Track 1).bin`, `(Track 2).bin`, ... | `Jogo (Track 1).iso` e as outras faixas são apagadas |

No segundo caso, o jogo roda normalmente, mas **sem as músicas de CD**, que eram as faixas 2 em diante. Os efeitos sonoros continuam. É o mesmo que o fabricante fez com os jogos de fábrica, como `Ridge Racer (USA) (Track 01).iso`. **Guarde as faixas originais em outro lugar** se quiser mantê-las.

---

## 3. Cuidados antes de mexer no cartão

1. **Faça uma cópia do cartão inteiro** antes de qualquer coisa. Os cartões que vêm com o stick são de baixa qualidade e corrompem com facilidade.
   - **Linux:** `sudo dd if=/dev/sdX of=cartao_backup.img bs=4M status=progress`, trocando `sdX` pelo seu cartão (confira com `lsblk`).
   - **Windows:** Win32 Disk Imager → "Read".
2. **Melhor ainda: passe tudo para um cartão novo de marca** (SanDisk, Samsung, Kingston) e guarde o original. Basta formatar o novo em **FAT32** e copiar todas as pastas. O stick funciona normalmente, desde que o cartão novo tenha o mesmo conteúdo.
3. **Desligue o stick do jeito certo:** saia do jogo, volte ao menu, espere ~5 segundos e só então tire o cabo. Desligar no meio de um jogo ou logo depois de salvar pode corromper o cartão.
4. **Alimentação:** use carregador de tomada **5V / 2A**. A USB da TV ou do PC pode não dar conta, e o stick trava ao abrir jogos mais pesados.
5. **Ejete o cartão** no sistema operacional antes de tirar do PC.

---

## 4. Adicionar jogos

### Requisitos

- **Python 3** (no Linux já vem; no Windows, instale em https://www.python.org/).
- Opcional, para gerar capas provisórias: `pip install pillow`

### Passo 1: copiar os jogos

Copie cada jogo para a pasta do console certo, por exemplo `roms/psx/`.

- Jogos de PSX em `.cue` + `.bin` podem ser copiados assim mesmo. O script converte.
- Use nomes de arquivo simples. O nome do arquivo (sem extensão) vira o nome no menu.

### Passo 2: simular

O script **primeiro só mostra o que faria, sem mudar nada**:

```bash
python3 adicionar_jogos.py /media/SEU_USUARIO/disk
```

No Windows, troque o caminho pela letra do cartão:

```bat
python adicionar_jogos.py E:/
```

Exemplo de saída:

```
PSX: Crash Bandicoot.bin -> Crash Bandicoot.img

Tirar do menu (arquivo não existe): nenhum
Colocar no menu: 1
  20537  megadrive  Sonic (World)

Nada foi alterado. Rode de novo com --aplicar para fazer as mudanças.
```

> Na simulação, os jogos de PSX que ainda estão em `.cue` aparecem só na linha da conversão. Eles entram no menu quando você aplicar.

### Passo 3: aplicar

```bash
python3 adicionar_jogos.py /media/SEU_USUARIO/disk --aplicar
```

O script:

1. converte os `.cue`/`.bin` de PSX para `.img`/`.iso`;
2. **faz backup** do índice atual em `~/gamestick-backups/indice_<data-hora>/`;
3. coloca os jogos novos em `roms/root.dat`, `cubegm/fileinfo` e no `gamelist.xml` do console;
4. **tira do menu** as entradas cujo arquivo foi apagado, para não ficarem jogos que não abrem;
5. cria uma **capa provisória** (fundo azul com o nome do jogo) para quem não tem capa.

O script **não mexe** em `arcade`, `fbneo`, `mame` e `cps1-3`. Muitos zips de arcade são peças usadas por outros jogos (romsets "pai" ou BIOS), e não jogos completos. Colocar esses zips no menu criaria entradas que não abrem.

### Passo 4: testar

Ejete o cartão, coloque no stick e procure o jogo **no fim da lista** do console.

---

## 5. Capas dos jogos (libretro-thumbnails)

### Onde as capas ficam

```
roms/<console>/images/<nome do arquivo do jogo, sem extensão>.png
```

| Arquivo do jogo | Capa |
|---|---|
| `roms/psx/Crash Bandicoot.img` | `roms/psx/images/Crash Bandicoot.png` |
| `roms/psx/Vigilante 8 - 2nd Offense (Track 01).iso` | `roms/psx/images/Vigilante 8 - 2nd Offense (Track 01).png` |
| `roms/megadrive/Sonic (World).md` | `roms/megadrive/images/Sonic (World).png` |

- **Formato:** PNG, **640 × 480**, como as capas de fábrica.
- **Para trocar uma capa,** basta substituir o `.png` com o mesmo nome. **Não precisa** rodar o script de novo.

### Onde conseguir capas

O projeto **[libretro-thumbnails](https://github.com/libretro-thumbnails/libretro-thumbnails)** (o mesmo usado pelo RetroArch) tem capas grátis de quase todos os jogos:

- **Navegar pelo site:** https://thumbnails.libretro.com/
- **GitHub:** https://github.com/libretro-thumbnails/libretro-thumbnails

Cada console tem três tipos de imagem:

| Pasta | Conteúdo |
|---|---|
| `Named_Boxarts` | **capa da caixa** (a melhor para o menu) |
| `Named_Titles` | tela de título |
| `Named_Snaps` | foto de dentro do jogo |

Nome das pastas de cada console:

| Console | Pasta no site | Repositório no GitHub |
|---|---|---|
| PlayStation | `Sony - PlayStation` | `Sony_-_PlayStation` |
| Super Nintendo | `Nintendo - Super Nintendo Entertainment System` | `Nintendo_-_Super_Nintendo_Entertainment_System` |
| NES | `Nintendo - Nintendo Entertainment System` | `Nintendo_-_Nintendo_Entertainment_System` |
| Mega Drive / Genesis | `Sega - Mega Drive - Genesis` | `Sega_-_Mega_Drive_-_Genesis` |
| Game Boy | `Nintendo - Game Boy` | `Nintendo_-_Game_Boy` |
| Game Boy Color | `Nintendo - Game Boy Color` | `Nintendo_-_Game_Boy_Color` |
| Game Boy Advance | `Nintendo - Game Boy Advance` | `Nintendo_-_Game_Boy_Advance` |
| Game Gear | `Sega - Game Gear` | `Sega_-_Game_Gear` |
| Neo Geo Pocket Color | `SNK - Neo Geo Pocket Color` | `SNK_-_Neo_Geo_Pocket_Color` |
| PC Engine | `NEC - PC Engine - TurboGrafx 16` | `NEC_-_PC_Engine_-_TurboGrafx_16` |

**Dicas para achar o jogo:**

- Os nomes seguem o padrão **No-Intro / Redump**, com a região entre parênteses: `Crash Bandicoot (USA).png`, `Sonic The Hedgehog (USA, Europe).png`.
- Os caracteres `& * / : < > ? \ | "` viram `_` no nome do arquivo.
- No site, use **Ctrl+F** para procurar na página.

### Passo a passo (exemplo: Crash Bandicoot de PSX)

**1. Baixar** a capa pelo navegador (https://thumbnails.libretro.com/Sony%20-%20PlayStation/Named_Boxarts/) ou pelo terminal:

```bash
wget -O capa.png "https://raw.githubusercontent.com/libretro-thumbnails/Sony_-_PlayStation/master/Named_Boxarts/Crash%20Bandicoot%20(USA).png"
```

Na URL, espaço vira `%20`. O endereço é `https://raw.githubusercontent.com/libretro-thumbnails/<REPOSITÓRIO>/master/Named_Boxarts/<NOME>.png`.

**2. Converter para 640 × 480** e salvar no cartão com **o mesmo nome do arquivo do jogo**. Com o [ImageMagick](https://imagemagick.org/):

```bash
convert capa.png -resize 640x480 -background black -gravity center \
        -extent 640x480 -colors 256 "/media/SEU_USUARIO/disk/roms/psx/images/Crash Bandicoot.png"
```

| Opção | Para quê |
|---|---|
| `-resize 640x480` | reduz a imagem mantendo a proporção |
| `-extent 640x480` + `-background black` | completa com bordas pretas para não esticar |
| `-colors 256` | deixa o arquivo leve, como as capas de fábrica |

No Windows, o comando do ImageMagick 7 é `magick` em vez de `convert`. Programas como GIMP ou Paint.NET também servem: redimensione para 640 × 480 e exporte em PNG.

**3. Ejetar o cartão e conferir** no stick.

---

## 6. Desfazer as mudanças

Toda vez que roda com `--aplicar`, o script guarda o índice anterior em:

```
~/gamestick-backups/indice_AAAAMMDD-HHMMSS/
├── root.dat
├── fileinfo
└── gamelist_<console>.xml      (um para cada console alterado)
```

Para voltar, copie esses arquivos de volta para o cartão:

| Backup | Volta para |
|---|---|
| `root.dat` | `roms/root.dat` |
| `fileinfo` | `cubegm/fileinfo` |
| `gamelist_psx.xml` | `roms/psx/gamelist.xml` (idem para os outros consoles) |

As conversões de `.cue` para `.img`/`.iso` **não** são desfeitas. Com o índice antigo, esses jogos só somem do menu, mas os arquivos continuam no cartão. Para trazê-los de volta, rode o script de novo.

---

## 7. Cartão "vazio" ou que o PC não reconhece

Um problema comum: o cartão para de funcionar no stick e, no PC, **aparece sem partições ou "vazio"**. Muitas vezes **só o setor inicial (a tabela de partições) foi danificado**, e todos os arquivos continuam lá.

**Não formate o cartão.** Antes, tente recuperar:

1. Faça uma cópia do cartão inteiro (item 3).
2. Use o **[TestDisk](https://www.cgsecurity.org/wiki/TestDisk)** (grátis, Linux/Windows/Mac). Ele procura a partição FAT32 perdida e recria a tabela de partições, ou permite copiar os arquivos para outro lugar.
3. Copie as pastas `cubegm/` e `roms/` para um **cartão novo** formatado em FAT32.

No cartão em que este guia foi testado, a partição FAT32 começava no setor 63 e estava intacta. Só a tabela de partições tinha sido apagada. Todos os 30 mil arquivos foram recuperados.

---

## 8. Detalhes técnicos do índice

Para quem quer entender ou editar à mão.

### `roms/root.dat`

É um arquivo **ZIP** comum com três arquivos de texto, um para cada grupo de idiomas do menu:

| Arquivo | Idioma da 4ª coluna |
|---|---|
| `fileinfo.001` | chinês simplificado / padrão |
| `fileinfo.002` | chinês tradicional |
| `fileinfo.003` | coreano |

Cada linha é um jogo, com **6 campos separados por TAB** e quebra de linha Unix (LF), em UTF-8:

```
<console>/<arquivo>	<ID>  <NOME EM MAIÚSCULAS>	<ID>  <NOME EM MAIÚSCULAS>	<ID>  <nome no idioma>	<texto de busca>	images/<capa>.png
```

Exemplo real:

```
psx/Crash Bandicoot.img	20525  CRASH BANDICOOT	20525  CRASH BANDICOOT	20525  Crash Bandicoot	Crash Bandicoot	images/Crash Bandicoot.png
```

- **ID:** número único, em sequência. Os jogos novos usam o maior ID existente + 1.
- Entre o ID e o nome há **dois espaços**.
- As linhas ficam agrupadas por console. O script insere os jogos novos logo depois do último jogo do mesmo console.

### `cubegm/fileinfo`

Uma linha de números separados por vírgula:

```
<maior ID>,<?>,arcade,fbneo,mame,atari2600,atari5200,atari7800,atarilynx,cps1,cps2,cps3,pcengine,nes,nesh,gb,sfc,snes,gbc,gba,genesis,gamegear,megadrive,ngpc,psx
```

O primeiro número é o maior ID, que é o número mostrado no menu. Depois vem um campo sempre `0` e a **quantidade de jogos de cada console**, nessa ordem. A ordem foi tirada do próprio programa `rkgame`.

### `roms/<console>/gamelist.xml`

XML em UTF-8 **com BOM** e quebras de linha **Windows (CRLF)**. Cada jogo é um bloco:

```xml
<game>
    <gameid>20525</gameid>
    <path>./Crash Bandicoot.img</path>
    <image>./images/Crash Bandicoot.png</image>
    <video_id>9</video_id>
    <class_type>9</class_type>
    <game_type>0</game_type>
    <timer>psx</timer>
    <zh_CN>20525  Crash Bandicoot</zh_CN>
    <en_US>20525  Crash Bandicoot</en_US>
    <zh_TW>20525  Crash Bandicoot</zh_TW>
    <ko_KR>20525  Crash Bandicoot</ko_KR>
    <name>Crash Bandicoot</name>
</game>
```

O script copia `video_id`, `class_type`, `game_type` e `timer` de um jogo que já existe no mesmo arquivo.

---

## 9. Perguntas frequentes

**Copiei o jogo, mas ele não aparece no menu.**
Falta colocar no índice. Rode o script (item 4).

**O jogo aparece, mas não abre.**
- **PSX:** confira se está em `.img`, `.iso` ou `.pbp`. `.cue` não abre.
- **Outros consoles:** use o mesmo formato dos jogos que já funcionam naquela pasta.
- **Tela preta:** comum em traduções feitas por fãs e versões modificadas. Teste a versão original do jogo.
- **Arquivos que já estavam no cartão mas fora do menu:** o fabricante pode ter deixado esses de fora justamente porque não funcionam. Ao colocá-los no menu, teste cada um e apague os que não abrirem (depois rode o script de novo, para ele tirar as entradas).
- **Se o stick trava ou reinicia:** veja a alimentação (5V / 2A).

**Tem limite de espaço?**
Não há "contêiner" de tamanho fixo: o limite é o tamanho do cartão. O FAT32 só não aceita arquivos acima de 4 GB, o que nenhum jogo de PS1 atinge. O arquivo `cubegm/pagefile.sys` (128 MB) é só a memória de troca (swap) do sistema.

**Os nomes de alguns jogos estão estranhos ("Combat Effectiveness", "Soul Douluo Adventure C").**
São traduções automáticas do chinês feitas pelo fabricante. Dá para corrigir editando o nome nas três listas do `root.dat` (item 8).

**Posso usar um cartão maior?**
Pode. Formate em FAT32 e copie tudo. Cartões acima de 32 GB precisam de uma ferramenta para formatar em FAT32: no Windows, por exemplo, o "guiformat"; no Linux, `mkfs.vfat -F 32`.

**Funciona no Windows?**
O script, sim. O caminho do cartão é a letra da unidade (ex.: `E:/`).

---

## 10. Aviso legal e licença

- Este projeto **não distribui jogos (ROMs), BIOS nem o sistema do stick**. Use apenas jogos que você tem o direito de usar.
- **Não publique** o conteúdo do seu cartão: a pasta `cubegm/` contém BIOS de console e programas sem licença de redistribuição, e `roms/` contém jogos comerciais.
- Não há relação com os fabricantes ou vendedores do stick. Use por sua conta e risco, e **sempre faça backup antes**.
- As capas do libretro-thumbnails seguem os termos daquele projeto.

O script `adicionar_jogos.py` e este guia estão sob a [licença MIT](LICENSE).
