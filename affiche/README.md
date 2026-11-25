# Affiche

Affiche de lancement pour la pop-up de l'intranet (avant le check de présence), 1080×1000. Elle reprend le temple de l'accueil.

Rendu depuis `affiche.html` (Chromium) :

```
chrome --headless --hide-scrollbars --disable-threaded-animation --force-device-scale-factor=2 \
  --window-size=1080,1350 --virtual-time-budget=8000 --screenshot=raw.png affiche.html
```

Recadrer ensuite les lignes 340 à 2340 (en pixels 2x), puis réduire à 1080×1000.
