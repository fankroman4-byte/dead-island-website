"""Render static build: add canonical metadata for the actual deployed hostname."""
import json
import os
import zipfile
import shutil
from pathlib import Path
from urllib.parse import urlsplit

project=Path(__file__).resolve().parent
root=project/'public'
root.mkdir(exist_ok=True)
with zipfile.ZipFile(project/'website-assets.zip') as archive:
    for member in archive.infolist():
        assert (root/member.filename).resolve().is_relative_to(root.resolve())
    archive.extractall(root)

url=(os.environ.get('SITE_URL') or os.environ.get('RENDER_EXTERNAL_URL') or 'https://dead-island-outpost-game.onrender.com').rstrip('/')
assert urlsplit(url).scheme=='https' and urlsplit(url).hostname
page=(root/'index.html').read_text(encoding='utf-8')
page=page.replace('<title>DEAD ISLAND — Outpost 07</title>','<title>DEAD ISLAND — Outpost 07 | Скачать игру для Windows</title>')
metadata='''
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{url}/">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:site_name" content="DEAD ISLAND — Outpost 07">
  <meta property="og:title" content="DEAD ISLAND — Outpost 07 | Скачать игру для Windows">
  <meta property="og:description" content="Бесплатная ранняя Windows-сборка: выживание на острове, Official 1 и PvP. Реальные скриншоты, Google-вход и готовая игра без исходного проекта.">
  <meta property="og:url" content="{url}/">
  <meta property="og:image" content="{url}/assets/combat.png">
  <meta property="og:image:width" content="1280">
  <meta property="og:image:height" content="720">
  <meta name="twitter:card" content="summary_large_image">
'''.format(url=url)
data={'@context':'https://schema.org','@type':'VideoGame','name':'DEAD ISLAND — Outpost 07','url':url+'/',
      'description':'Независимый multiplayer survival-проект: выживание на острове, крафт, лутбоксы и два публичных режима.',
      'operatingSystem':'Windows 10, Windows 11','gamePlatform':'PC','applicationCategory':'GameApplication',
      'inLanguage':'ru','image':url+'/assets/combat.png','offers':{'@type':'Offer','price':'0','priceCurrency':'USD'},
      'playMode':['SinglePlayer','MultiPlayer']}
metadata+='<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>\n'
verification=os.environ.get('GOOGLE_SITE_VERIFICATION','')
if verification:
    assert all(c.isalnum() or c in '_-' for c in verification)
    metadata+='<meta name="google-site-verification" content="'+verification+'">'
page=page.replace('</head>',metadata+'</head>')
(root/'index.html').write_text(page,encoding='utf-8')
(root/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /downloads/\nSitemap: '+url+'/sitemap.xml\n',encoding='utf-8')
(root/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+url+'/</loc></url></urlset>\n',encoding='utf-8')
print('STATIC_SITE_READY',url)




# The player archive is a separate Release asset.
release={'filename': 'DeadIsland-Windows.zip', 'bytes': 47980075, 'sha256': '6d4166f885d914dffc888e0f7ec79a975f316cea956ad9788c53e973e13c38ee', 'url': 'https://github.com/fankroman4-byte/dead-island-website/releases/download/v0.3.0-alpha/DeadIsland-Windows.zip'}
(root/'downloads').mkdir(exist_ok=True)
(root/'downloads/release.json').write_text(json.dumps(release,indent=2),encoding='utf-8')
