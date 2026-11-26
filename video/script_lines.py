# -*- coding: utf-8 -*-
"""Découpage du script en répliques : texte dit, scène visuelle, mots-clés colorés, pauses et bruitages."""

def L(text, scene=None, kw="", pause=0.0, sfx=None, tts=None, voice=None, pre=0.0):
    return dict(text=text, scene=scene, kw=kw.split("|") if kw else [], pause=pause,
                sfx=sfx, tts=tts, voice=voice, pre=pre)

CHAPTERS = ["L'affaire", "La méthode", "La résolution", "Ce qu'on retient"]

LINES = [
    # ---------------- 1. ACCROCHE ET CONTEXTE ----------------
    L("Mars 1971.", "title_mars", "Mars 1971", pause=0.3, sfx="impact", pre=0.4),
    L("Imaginez : vous dirigez le New York Times, l'un des plus grands journaux des États-Unis.",
      "nyt_desk", "New York Times"),
    L("Sur votre bureau, 7 000 pages ultra-secrètes.", "pages", "7 000 pages|ultra-secrètes",
      tts="Sur votre bureau, sept mille pages ultra-secrètes."),
    L("C'est un rapport venant du Pentagone, le ministère de la Défense américain, sur la guerre du Vietnam,",
      "pentagon", "Pentagone|guerre du Vietnam"),
    L("qu'un ancien analyste, Daniel Ellsberg, a fait fuiter.", "ellsberg", "Daniel Ellsberg|fuiter"),
    L("Et ce que ce document révèle est totalement explosif :", "explosif", "explosif", sfx="impact"),
    L("on comprend que pendant des années, le gouvernement a caché la vérité aux Américains sur cette guerre.",
      "verite", "caché la vérité"),
    L("Alors, vous faites quoi dans cette situation ?", "dilemma", "vous faites quoi", pause=0.3),
    L("Si vous publiez, le gouvernement peut vous attaquer en justice.", None, "publiez|en justice"),
    L("Si vous vous taisez, vous passez à côté du scoop du siècle pour votre journal.", None,
      "taisez|scoop du siècle"),
    L("Le 13 juin 1971, le Times publie.", "cal13", "13 juin 1971|publie", sfx="impact"),
    L("Et là, tout bascule.", "bascule", "tout bascule", sfx="swoosh"),
    L("Le lendemain, le ministre de la Justice du président Nixon exige que le journal s'arrête, sinon : procès.",
      "ultimatum", "ministre de la Justice|Nixon|procès"),
    L("Le Times refuse.", "refuse", "refuse", sfx="impact"),
    L("Un juge bloque alors la publication.", "bloque", "bloque", sfx="impact"),
    L("Mais voilà où ça devient fou :", "fou", "fou", sfx="glitch"),
    L("le Washington Post, un journal concurrent, obtient les mêmes documents.", "post",
      "Washington Post|mêmes documents"),
    L("Il a vu ce qui est arrivé au Times. Il connaît le risque.", "post_risk", "connaît le risque"),
    L("Et il publie quand même, le 18 juin.", "cal18", "publie quand même|18 juin", sfx="impact"),
    L("Pourquoi ?", "pourquoi", "Pourquoi", pause=0.8, sfx="impact", pre=0.9),

    # ---------------- 2. LES QUESTIONS ET LA MÉTHODE ----------------
    L("C'est là qu'on s'est posé deux questions.", "chap2", "deux questions", sfx="swoosh"),
    L("Pourquoi un journal prend-il le risque d'un procès ?", "q1", "journal|risque d'un procès"),
    L("Et pourquoi un gouvernement lance-t-il un procès qu'il peut perdre ?", "q2", "gouvernement|perdre"),
    L("Let's break it down.", "breakdown", "Let's break it down", voice="en-us", sfx="glitch", pause=0.2),
    L("Pour y répondre, on utilise la théorie des jeux.", "theorie", "théorie des jeux"),
    L("Son idée : étudier des choix où la meilleure décision dépend de ce que les autres vont décider.",
      "interdep", "meilleure décision|les autres"),
    L("Ici, c'est un jeu séquentiel, c'est-à-dire que les joueurs jouent chacun leur tour.", "tree",
      "jeu séquentiel|chacun leur tour"),
    L("D'abord le Times choisit de publier ou non.", None, "Times|publier"),
    L("Ensuite Nixon choisit de poursuivre ou non.", None, "Nixon|poursuivre"),
    L("Puis le Post décide à son tour.", None, "Post"),
    L("Et Nixon réagit encore.", None, "Nixon"),
    L("Pour résoudre ce jeu, on raisonne à rebours : on part de la fin et on remonte.", "tree_back",
      "à rebours|de la fin", sfx="swoosh"),
    L("Pourquoi ? Parce que chaque joueur anticipe ce que l'autre fera ensuite.", None, "anticipe"),
    L("Trois ingrédients comptent : le gain de publier, le coût d'un procès, et les chances de gagner au tribunal.",
      "ingredients", "gain|coût|chances"),

    # ---------------- 3. LA RÉSOLUTION ----------------
    L("Prenons un exemple simple.", "chap3", "exemple simple", sfx="swoosh", pre=0.3),
    L("Publier une information rapporte beaucoup à un journal : du prestige, des lecteurs, de la fierté.",
      "gain", "rapporte beaucoup|prestige|lecteurs|fierté"),
    L("S'il perd son procès, il ne gagne rien.", None, "ne gagne rien", sfx="impact"),
    L("Et un procès coûte de l'argent, du temps et de l'énergie.", None, "coûte"),
    L("Si le gouvernement n'est pas sûr de gagner, le journal peut encore espérer beaucoup pour un petit coût.",
      "graph1", "pas sûr de gagner|petit coût"),
    L("Il publie sans hésiter.", None, "publie sans hésiter"),
    L("Mais à partir de quand le journal se tait-il ?", None, "se tait-il"),
    L("Seulement quand le gouvernement est presque certain de gagner : à ce moment-là, ce que le journal peut "
      "espérer ne vaut plus le coût du procès.", None, "presque certain|ne vaut plus"),
    L("Autant dire que, pour le Times, le gouvernement ne devrait avoir quasiment aucune chance de perdre.",
      None, "quasiment aucune chance"),
    L("On applique maintenant le raisonnement à rebours.", "tree_back2", "à rebours", sfx="swoosh"),
    L("Au bout du chemin, il y a la Cour suprême, le plus haut tribunal du pays.", "court", "Cour suprême"),
    L("Là, un procès coûte encore plus cher.", None, "encore plus cher"),
    L("Mais même ainsi, le Post ne se tait que s'il est presque sûr de perdre.", "graph2",
      "presque sûr de perdre"),
    L("Donc que fait Nixon ?", "nixon_think", "Nixon", pause=0.2),
    L("Il anticipe que les deux journaux publieront, quoi qu'il arrive.", "tree_pub",
      "deux journaux publieront"),
    L("Pour lui, laisser publier est pire que risquer un procès.", "scale", "pire"),
    L("Il poursuit donc, même sans être sûr de gagner.", "gavel", "Il poursuit", sfx="impact"),
    L("Et la réalité ?", "reality", "la réalité", pause=0.6, pre=0.6),
    L("Le 30 juin 1971, la Cour suprême tranche, à la majorité : les journaux ont le droit de publier.",
      "verdict", "30 juin 1971|droit de publier"),

    # ---------------- 4. RÉSULTATS ET CONCLUSION ----------------
    L("Alors, qu'est-ce qu'on retient ? Trois résultats.", "chap4", "Trois résultats", sfx="swoosh", pre=0.3),
    L("Premier résultat : seules des chances extrêmes font taire la presse.", "res1", "chances extrêmes"),
    L("Il faut que le journal soit quasiment sûr de perdre, que ce soit le Times ou le Post.", "graph3",
      "quasiment sûr de perdre"),
    L("Une presse libre se laisse très difficilement intimider.", "shield", "presse libre|intimider"),
    L("Deuxième résultat : le gain compte.", "res2", "le gain compte", sfx="swoosh"),
    L("Imaginez une toute petite histoire, qui rapporte peu.", "small_story", "petite histoire"),
    L("Là, même un risque modéré de perdre suffit à faire taire les journaux.", "graph4", "risque modéré"),
    L("Ici, le scoop était gigantesque, et ça a tout changé.", "big_story", "gigantesque", sfx="impact"),
    L("Troisième résultat : les coûts jouent dans les deux sens.", "res3", "deux sens", sfx="swoosh"),
    L("Si les procès coûtent cher seulement aux journaux, ils se mettent à craindre le tribunal et se taisent.",
      "costs", "seulement aux journaux|se taisent"),
    L("Mais s'ils coûtent cher aussi au gouvernement, Nixon ne poursuit plus, et les journaux publient.",
      None, "aussi au gouvernement|publient"),
    L("Le message final ?", "final_msg", "message final", pause=0.3, sfx="swoosh"),
    L("La liberté de la presse ne dépend pas seulement du courage de quelques journalistes.", "courage",
      "liberté de la presse|courage"),
    L("Elle dépend aussi des incitations : qui paie quoi, et qui risque quoi.", "incitations",
      "incitations|qui paie quoi|qui risque quoi"),
    L("Alors, une dernière question.", "last_q", "dernière question", pause=0.4),
    L("Si les procès avaient coûté beaucoup moins cher au gouvernement, est-ce que vous auriez pris le risque "
      "de publier ?", "final_q", "beaucoup moins cher|publier", pause=4.5),
]

# Début de chaque chapitre (index de réplique)
CHAPTER_START = [0, 20, 34, 53]
