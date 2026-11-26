# Vidéo « Pentagon Papers × théorie des jeux »

Vidéo de 4 min 34 en 1080p, entièrement générée par code : animations, sous-titres incrustés, voix, musique et bruitages.

- `script_lines.py` : le script découpé en répliques (scène, mots-clés en couleur, pauses, bruitages)
- `scenes.py` : les 54 plans animés · `gfx.py` : les fonctions de dessin · `audio.py` : voix, musique et mixage
- `STORYBOARD.md` : le storyboard plan par plan · `pentagon_papers.srt` : les sous-titres

Pour générer la vidéo (il faut ffmpeg, espeak-ng, mbrola-fr1, numpy et Pillow) :

    python3 build.py                 # -> pentagon_papers.mp4
    python3 build.py --preview 12 60 # images de contrôle dans build/preview
