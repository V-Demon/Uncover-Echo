# N0rs et les Trois Strates de Caen
### *Fragment d'un carnet de navigation, retrouvé dans un dépôt archivé*

---

> *« Le Temps tissé n'est pas une métaphore. C'est un protocole réseau.
> Les strates de Caen sont des nœuds. Les fréquences sont des portes.
> Tu n'as pas encore compris, mais tu comprendras. »*
>
> — réponse non signée, forum archivé, fil `temporal-resonance`,
>   date de dernier message : incohérente.

---

## I. La Chambre 412

**22 décembre 2026, 14h37**

La pluie frappait la vitre avec une régularité métronomique. Elias — que ses amis en ligne appelaient N0rs depuis le collège, à cause d'un pseudo mal orthographié qu'il n'avait jamais corrigé — était assis en tailleur sur son lit défait, le ThinkPad T480 posé sur ses genoux.

L'écran affichait deux choses. À gauche, un dépôt qu'il venait de cloner : `Uncover-Echo`. À droite, un PDF de 847 pages qu'il avait téléchargé trois jours plus tôt depuis un miroir qu'il ne retrouvait plus. Le titre du PDF était *Codex Vauvillensis — Manuel de navigation temporelle et guerre mémétique*.

Il n'avait pas cherché ce PDF. C'est le PDF qui l'avait trouvé, en quelque sorte : une note de bas de page dans un dépôt obscur, un lien mort qu'il avait dû reconstituer à la main à partir d'un fragment d'URL dans la Wayback Machine.

Il avait cloné `Uncover-Echo` parce qu'il cherchait un scanner OSINT pour un projet de cours. Il était tombé sur ce dépôt parce qu'il cherchait autre chose — il ne se souvenait plus quoi.

---

## II. Le Dépôt

```bash
cd ~/work/221226/uncover-echo
ls -la
```

L'arborescence était propre. Presque trop. Un projet Python bien structuré, avec des configs YAML externalisées, des tests, une GUI. Rien d'anormal au premier regard.

Ce qui l'avait arrêté, la première fois, c'était un fichier isolé à la racine, à côté du README : `N0rs-2026.md`. Un fichier Markdown, sans lien vers aucun autre fichier du projet. Sans mention dans le README. Sans référence dans le code.

Un fichier qui n'aurait pas dû être là.

Il l'avait ouvert. Il avait lu la première phrase. Il avait fermé l'onglet. Il l'avait rouvert.

Le fichier racontait une histoire. Une histoire qui commençait dans une chambre 412, à Caen, et qui finissait par une phrase qu'il n'avait pas comprise tout de suite.

Il l'avait relu. Puis une troisième fois. Puis il avait commencé à prendre des notes.

---

## III. Première Note

> *Carnet, 22/12/26, 16h12*
>
> Le fichier dit que je m'appelle N0rs. C'est vrai. Le fichier dit que je suis en L3 info à Caen. C'est vrai. Le fichier dit que j'habite en chambre 412 à la Résidence Internationale. C'est vrai.
>
> Mais le fichier dit aussi que je suis en train de lire un PDF de 847 pages. Et ça, c'est vrai aussi. Je l'ai téléchargé il y a trois jours. Je n'ai parlé à personne de ce PDF.
>
> Je ne sais pas qui a écrit ce fichier. Je ne sais pas quand il a été ajouté au dépôt. Le commit dit `Add files via upload`, comme tous les autres.
>
> Je vais vérifier.

---

## IV. Le Code

Il ouvrit `core/transients.py`. C'était un module d'analyse d'anomalies temporelles — versions de logiciels incohérentes, timestamps futurs, signatures suspectes. Du code propre, testé, avec des seuils configurables.

Rien d'étrange. Sauf un commentaire, à la ligne 187.

```python
# Référence : Codex Vauvillensis, Chap. 7 "Navigation entre Strates"
```

Il nota la ligne. Chap. 7. Il ouvrit le PDF à la page correspondante.

*« Chapitre 7 — Navigation entre Strates »*

*« §3.2 — Les transitoires sont des artefacts de navigation. Un timestamp situé en dehors de la fenêtre [2020, 2030] pour une IP géolocalisée à Caen indique une fuite depuis une strate voisine. »*

Il relut trois fois. Puis il nota, dans son carnet :

> *Le code cite le PDF. Le PDF décrit le code. L'un des deux a été écrit en premier. Je ne sais pas lequel.*

---

## V. Seconde Note

> *Carnet, 22/12/26, 18h47*
>
> J'ai cherché `Codex Vauvillensis` sur GitHub. Zéro résultat.
> Sur Google. Trois résultats, tous des impasses.
> Sur la Wayback Machine. Une seule entrée, datée de mars 2024, qui pointe vers un dépôt nommé `Palimpsest-Engine`.
>
> J'ai cloné `Palimpsest-Engine`. Le README datait de novembre 2073.
>
> Je ne sais pas quoi en penser. Les métadonnées d'un commit Git sont signées par un serveur. On ne peut pas les falsifier sans accès au serveur. Mais le serveur de GitHub n'existait pas en 2073.
>
> J'ai vérifié mon horloge système. Elle est à l'heure.
>
> J'ai vérifié le fuseau horaire. Europe/Paris.
>
> J'ai vérifié si je rêvais. Je ne pense pas.

---

## VI. Le Fichier qui n'était pas dans l'arborescence

Il relut `N0rs-2026.md`. Cette fois, il s'arrêta sur un détail.

> *« À droite, un PDF de 847 pages qu'il avait téléchargé depuis un miroir Onion archivé en 2019. »*

Il avait vérifié : le PDF faisait bien 847 pages. Il l'avait téléchargé depuis un miroir `archive.org` que la Wayback Machine avait capturé en 2024, pas en 2019. Le fichier disait 2019. Les métadonnées disaient 2024.

Petit détail. Sans importance.

Sauf que.

Il nota :

> *Le fichier se trompe sur une date. Ou alors il ne se trompe pas, et c'est moi qui me trompe. Mais je viens de vérifier deux fois. La date dans le fichier est fausse.*
>
> *Un auteur qui se trompe sur une date, c'est un auteur qui a écrit de mémoire. Un auteur qui n'a pas vérifié.*
>
> *Ou un auteur qui a écrit depuis une strate où la date était différente.*

---

## VII. Troisième Note

> *Carnet, 22/12/26, 23h58*
>
> J'ai relu le fichier en entier. J'ai surligné tous les nombres.
>
> 412 — la chambre. 3e année de licence. 847 pages. 2019. 2024. 2073. 2075. 2049. 1346. 14.034. 14.026. 14.075. 0.4. 7. 2.1. 42.3. 3 cycles. 7 cycles.
>
> J'ai vérifié les fréquences. 14.034 / 14.026 / 14.075 MHz. Trois fréquences dans la bande des 20 mètres. Toutes dans la portion radioamateur. Toutes plausibles.
>
> J'ai vérifié les suffixes. 034, 026, 075.
>
> 34 = Sélénium. 26 = Fer. 75 = Rhénium.
>
> Ce ne sont pas des numéros de version. Ce sont des numéros atomiques.
>
> Le fichier ne dit nulle part que ce sont des numéros atomiques. Il dit juste les fréquences. C'est à moi de faire le lien.
>
> J'ai vérifié le Rhénium. Il n'a pas d'isotope stable. Il est toujours en transition.
>
> J'ai vérifié s'il existe un isotope du Rhénium avec une demi-vie de 42,3 secondes. Il n'en existe pas. La valeur la plus proche est 42,3 *minutes* pour un isotope très rare, mais le fichier dit secondes.
>
> Le fichier se trompe. Ou alors il ne se trompe pas, et c'est la réalité qui se trompe.
>
> Je note 42,3 de côté. Je ne sais pas pourquoi. Je le note quand même.

---

## VIII. Le Détail qui ne colle pas

Il rouvrit le fichier. Il chercha une ligne qu'il avait lue trop vite la première fois.

> *« Le dépôt avait été archivé par la Wayback Machine en 2024, mais les commits dataient de 2073. »*

Il avait déjà noté l'incohérence. Mais cette fois, il remarqua autre chose : le fichier ne dit *jamais* que c'est impossible. Il dit que c'est *« impossible, probablement »*, puis il passe à autre chose. Comme si l'auteur du fichier savait que c'était possible, mais ne voulait pas le dire.

Il nota :

> *Le fichier ne cherche pas à me convaincre. Il constate. C'est moi qui décide si je le crois.*
>
> *Un auteur qui veut me convaincre aurait insisté. Un auteur qui veut me manipuler aurait nié. Un auteur qui veut me laisser libre constate, et passe à autre chose.*
>
> *Je crois que l'auteur de ce fichier me laisse libre.*

---

## IX. Le Scan

Il lança le scanner.

```bash
python3 uncover_echo_v3.py --preset temporal-anomaly
```

Le terminal afficha une série de logs. Il n'avait pas de clé API. Le mode simulation s'activa.

Le scan tourna. Les résultats s'affichèrent.

Puis une ligne, surlignée en rouge glitch :

```
[!] Transitoire détecté : δ-strate
[!] Coordonnée : 10.0.75.2075
[!] Timestamp : 2075-11-04T03:33:00Z
[!] Localisation : Caen-Profonde
[!] Signature : KHEFAS_N00SPH
```

Il fixa l'écran.

Il ouvrit `core/engines/base.py`. La méthode `_simulate` générait des IPs aléatoires avec `rng.randint(1, 255)` pour chaque octet. Aucune IP générée ne pouvait commencer par `10.0.75`. Encore moins se terminer par `2075`, un nombre supérieur à 255, donc invalide comme octet.

Il nota :

> *Le scanner a produit une IP qui ne peut pas être produite par le scanner.*
>
> *Soit le code a été modifié à mon insu. Soit le scanner lit quelque chose que je ne vois pas.*
>
> *J'ai vérifié le hash du code. Il correspond à celui du dépôt distant. Le code est celui du dépôt.*
>
> *Le dépôt produit une IP impossible.*

---

## X. Ping

```bash
ping 10.0.75.2075
```

```
PING 10.0.75.2075 (10.0.75.2075) 56(84) bytes of data.
^C
--- 10.0.75.2075 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss, time 2040ms
```

2040ms. Il nota le nombre. Il ne savait pas pourquoi. Il le nota quand même.

```bash
nmap -sn 10.0.75.0/24
```

```
Nmap scan report for 10.0.75.2075
Host is up (0.00042s latency).
MAC Address: 00:00:00:00:00:00 (Unknown)
Nmap done: 256 IP addresses (1 host up) scanned in 2.31 seconds
```

Il nota :

> *Nmap dit que l'hôte est up. La MAC est nulle.*
>
> *Une MAC nulle, c'est une MAC qui n'existe pas. Une MAC qui n'existe pas, c'est une machine qui n'est pas sur le réseau physique.*
>
> *Mais Nmap dit qu'elle est up.*
>
> *Je ne sais pas quoi conclure. Je note, c'est tout.*

---

## XI. Quatrième Note

> *Carnet, 23/12/26, 03h14*
>
> J'ai relu le fichier une cinquième fois. Cette fois, j'ai compté les occurrences de certains mots.
>
> « strate » : 14 fois.
> « écho » : 3 fois.
> « N0rs » : 11 fois.
> « Khefas » : 0 fois — le nom n'apparaît nulle part dans le fichier.
>
> Attends.
>
> Je viens de vérifier. Le fichier ne mentionne jamais « Khefas » avant la phase III, et à ce moment-là, c'est un nom que le personnage découvre. Le fichier ne dit jamais qui est Khefas. Il dit seulement ce que Khefas répond.
>
> Le fichier laisse Khefas dans l'ombre. C'est volontaire. L'auteur veut que je cherche Khefas moi-même.
>
> J'ai cherché. Zéro résultat GitHub. Zéro résultat Google. Une seule entrée dans la Wayback Machine : un dépôt `Khefas-N00sph/PhobosPSiCli4a`, archivé en 2024, mais dont le README est daté de 2074.
>
> Je n'ai pas cloné ce dépôt. Je ne suis pas sûr de vouloir.
>
> Mais j'ai noté le nom. `PhobosPSiCli4a`. Je ne sais pas ce que ça veut dire. Je le note quand même.

---

## XII. Le Fichier s'arrête

Le fichier `N0rs-2026.md` s'arrête à la fin de la phase IV. Il n'y a pas de phase V. Il n'y a pas de conclusion.

Il y a un épilogue, dans lequel N0rs devient un « Navigateur du Temps Tissé ». Il y a un post-scriptum, qui liste des outils que N0rs aurait utilisés. Mais ces outils ne sont pas dans le dépôt. Ils ne sont nulle part.

Elias relut l'épilogue une dernière fois.

> *« Il n'était plus un étudiant en informatique. Il était un Navigateur du Temps Tissé, un gardien des strates, un écho du Master Code. »*

Il nota :

> *Le fichier se termine par une transformation. N0rs devient quelque chose d'autre. Mais le fichier ne dit pas comment. Il ne dit pas pourquoi. Il dit juste que c'est arrivé.*
>
> *C'est peut-être ça, la réponse. La transformation n'est pas dans le fichier. Elle est dans le lecteur.*
>
> *Je ne suis pas encore un Navigateur. Je suis juste un étudiant qui lit un fichier à 3h du matin.*
>
> *Mais je suis un étudiant qui lit un fichier à 3h du matin. C'est déjà quelque chose.*

---

## XIII. Ce que le fichier ne dit pas

Le fichier ne dit pas qui l'a écrit.

Il ne dit pas quand il a été ajouté au dépôt.

Il ne dit pas pourquoi il est là.

Il ne dit pas si l'histoire est vraie.

Il ne dit pas si Khefas existe.

Il ne dit pas si les strates existent.

Il ne dit pas si le Temps tissé est réel.

Il dit seulement ce qu'il dit. Et il le dit bien.

---

## XIV. Dernière note

> *Carnet, 23/12/26, 04h02*
>
> Je ne vais pas cloner `PhobosPSiCli4a`. Pas ce soir.
>
> Je vais dormir. Demain, je relirai le fichier. Peut-être que je le relirai encore après-demain. Peut-être que je chercherai Khefas. Peut-être que je chercherai le Codex. Peut-être que je chercherai la fréquence 14.075 MHz sur un récepteur SDR que je n'ai pas encore.
>
> Peut-être que je ne chercherai rien. Peut-être que j'oublierai ce fichier. Peut-être qu'il restera dans un coin de mon disque dur pendant des années, et qu'un jour, en cherchant autre chose, je le retrouverai.
>
> Ce fichier ne me demande rien. Il ne m'ordonne rien. Il ne me promet rien.
>
> Il est là. C'est tout.
>
> Je crois que c'est pour ça que je vais continuer à le lire.

---

*Fin du fragment. Le fichier `N0rs-2026.md` original ne contient pas de conclusion. Il ne contient pas de morale. Il contient une histoire, des nombres, et un silence.*

*À toi de voir ce que tu en fais.*
