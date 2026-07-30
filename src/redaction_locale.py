"""Rédaction sans API : assemblage de fond éditorial paramétré par le sujet.

Utilité : tester le système, dépanner un jour où l'API est indisponible, et
garantir qu'aucune journée ne passe sans publication. Pour de la publication
quotidienne durable, préférez le mode "api" (textes uniques).
"""

from __future__ import annotations

import hashlib
import random
from typing import Any

from .sujets import slugifier


def _alea(graine: str) -> random.Random:
    return random.Random(int(hashlib.md5(graine.encode()).hexdigest()[:8], 16))


def _mots(*textes: str) -> int:
    return sum(len(t.split()) for t in textes)


def _groupe_nominal(mot_cle: str) -> str:
    """Rend le mot-clé utilisable dans une phrase française correcte.

    « coiffeuse LED » -> « une coiffeuse LED », « meilleure coiffeuse » ->
    « la meilleure coiffeuse ». Tout le reste retombe sur une formule neutre.
    """
    mc = (mot_cle or "").strip().lower()
    if mc.startswith(("meilleur", "meilleure")):
        return f"la {mc}"
    if mc.startswith("coiffeuse"):
        return f"une {mc}"
    if mc.startswith(("petite", "grande", "table")):
        return f"une {mc}"
    return "une coiffeuse"


# --------------------------------------------------------------- blocs texte


def _bloc_criteres(mc: str) -> dict[str, Any]:
    return {
        "titre": f"Les critères qui comptent vraiment pour {mc}",
        "paragraphes": [
            f"Avant de comparer des modèles, il faut savoir ce que l'on regarde. Sur {mc}, quatre paramètres décident de la satisfaction à long terme : la hauteur du plateau, sa profondeur, la qualité du miroir et la capacité de rangement réellement exploitable. Tout le reste, y compris le style, se corrige plus tard avec de la peinture ou des poignées. Ces quatre-là, non : ils sont figés le jour de la livraison.",
            "La hauteur du plateau se situe presque toujours entre 73 et 78 cm, ce qui correspond à la hauteur d'un bureau classique. C'est confortable pour la majorité des adultes assis sur une assise de 45 cm environ. Si vous mesurez moins d'un mètre soixante, visez plutôt le bas de la fourchette, ou prévoyez un tabouret réglable. Un plateau trop haut oblige à lever les épaules pendant toute la séance, et cette fatigue-là ne se remarque qu'au bout de plusieurs semaines.",
            "La profondeur est le critère le plus sous-estimé. En dessous de 35 cm, vous ne pouvez pas poser une trousse ouverte et travailler devant sans que quelque chose tombe. Entre 40 et 45 cm, tout devient fluide. Au-delà de 50 cm, le meuble commence à manger le passage dans une chambre standard, et vous vous cognerez dedans en faisant le lit.",
            "Le rangement, enfin, se juge en volume utile et non en nombre de tiroirs. Trois tiroirs de 6 cm de haut valent moins qu'un seul tiroir de 15 cm capable d'avaler des flacons debout. Regardez la hauteur intérieure annoncée, pas la façade. Et vérifiez la présence de glissières : un tiroir qui frotte sur du bois brut finit toujours par rester ouvert en biais.",
        ],
        "liste": [
            "Hauteur de plateau : 73 à 78 cm pour un adulte, moins pour un enfant ou un ado.",
            "Profondeur : 40 cm est le point d'équilibre entre confort et encombrement.",
            "Largeur : 80 cm minimum pour travailler à l'aise, 100 cm si vous avez une vraie collection.",
            "Tiroirs : privilégiez un grand tiroir profond plutôt que trois tiroirs plats.",
            "Miroir : au moins 40 cm de haut pour voir son visage entier sans reculer.",
        ],
        "encadre": {
            "titre": "Le test des trois mesures",
            "texte": "Avant de commander, tracez au sol l'emprise du meuble avec du ruban de masquage, asseyez-vous sur la chaise que vous comptez utiliser et vérifiez que vos genoux passent sous le plateau. Trois minutes qui évitent un retour de colis.",
        },
    }


def _bloc_eclairage(mc: str) -> dict[str, Any]:
    return {
        "titre": "L'éclairage : le critère que tout le monde découvre trop tard",
        "paragraphes": [
            "Un maquillage réussi dépend davantage de la lumière que du meuble. La règle est simple : la lumière doit venir de face, jamais du plafond. Un plafonnier placé derrière vous projette l'ombre de votre propre tête sur le visage et creuse les cernes, ce qui pousse à sur-corriger. Résultat classique : un fond de teint parfait dans la chambre, un masque visible dès qu'on sort.",
            "La température de couleur se mesure en kelvins. Autour de 4000 à 5000 K, on obtient un blanc neutre proche de la lumière du jour, celui qui permet de juger correctement une teinte de fond de teint. En dessous de 3000 K, la lumière est chaude et jaunit tout : agréable pour se détendre, trompeuse pour se maquiller. Les modèles à trois modes réglables restent le meilleur compromis, à condition de prendre l'habitude de toujours utiliser le même pour les gestes précis.",
            "L'indice de rendu des couleurs, noté IRC ou CRI, mérite un regard. Au-dessus de 90, les nuances sont restituées fidèlement ; en dessous de 80, les rouges et les roses se ressemblent tous. Cette information n'est pas toujours communiquée, mais quand elle l'est, elle départage deux modèles à l'identique par ailleurs.",
            "Enfin, pensez à l'alimentation. Un miroir lumineux à piles s'affaiblit progressivement sans qu'on s'en aperçoive, et l'on finit par se maquiller sous une lumière plus faible chaque semaine. Un branchement secteur, même avec un câble à dissimuler, reste plus fiable. Vérifiez qu'une prise se trouve à moins de deux mètres de l'emplacement prévu, sinon prévoyez une multiprise plate à fixer derrière le meuble.",
        ],
        "liste": [
            "Lumière frontale obligatoire : de part et d'autre du miroir, à hauteur de visage.",
            "4000 à 5000 K pour juger une teinte, jamais moins de 3500 K.",
            "IRC supérieur à 90 quand l'information est disponible.",
            "Alimentation secteur plutôt que piles pour une intensité constante.",
        ],
    }


def _bloc_espace(mc: str) -> dict[str, Any]:
    return {
        "titre": "Où installer le meuble et combien de place prévoir",
        "paragraphes": [
            "Le bon emplacement se choisit avant le modèle, pas l'inverse. Le meilleur endroit est un mur perpendiculaire à la fenêtre : vous profitez de la lumière naturelle sans avoir le soleil dans les yeux ni de contre-jour dans le miroir. Placer la coiffeuse dos à la fenêtre est l'erreur la plus fréquente, et elle condamne l'usage du meuble en journée.",
            "Comptez 70 cm de dégagement devant le plateau pour pouvoir reculer la chaise et vous asseoir sans manœuvre. Si le meuble fait 40 cm de profondeur, l'emprise réelle est donc de 110 cm depuis le mur. Dans une chambre où le lit laisse 90 cm de passage, un modèle d'angle ou une version murale rabattable devient nettement plus pertinent qu'une coiffeuse classique.",
            "Le voisinage compte aussi. Évitez de coller le meuble contre un radiateur : la chaleur sèche fait travailler les panneaux et gondole les chants au bout de deux hivers. Évitez également la proximité immédiate d'une douche ou d'une baignoire, l'humidité étant le pire ennemi des panneaux de particules mélaminés.",
            "Dernier point souvent oublié : la porte. Vérifiez que le battant de la porte de la chambre, une fois ouvert, ne vient pas heurter l'angle du plateau ni le tabouret laissé sorti. C'est le genre de détail qui transforme un bon achat en agacement quotidien.",
        ],
        "encadre": {
            "titre": "Emprise à retenir",
            "texte": "Profondeur du meuble + 70 cm de dégagement = la surface réelle à réserver. Un modèle de 40 cm demande donc 110 cm depuis le mur.",
        },
    }


def _bloc_materiaux(mc: str) -> dict[str, Any]:
    return {
        "titre": "Matériaux et finitions : ce qui tient dans le temps",
        "paragraphes": [
            "La très grande majorité des modèles accessibles est construite en panneaux de particules mélaminés ou en MDF. Ce n'est pas un défaut en soi : bien conçu, un panneau de 16 mm d'épaisseur tient parfaitement une décennie. Le vrai signal de qualité est l'épaisseur annoncée et la présence de chants collés proprement sur les quatre côtés. Un panneau de 12 mm avec un chant nu sur la tranche arrière trahit une économie qui se paiera au premier déménagement.",
            "Le bois massif, plus rare et plus cher, apporte deux avantages concrets : il se ponce et se répare, et il supporte d'être vissé plusieurs fois au même endroit. Sur un panneau de particules, une vis retirée puis remise ne tient plus. Si vous prévoyez de démonter et remonter le meuble à chaque déménagement, cette différence devient décisive.",
            "Côté finition, le laqué brillant est spectaculaire en photo et exigeant au quotidien : il montre chaque trace de doigt, chaque projection de poudre et chaque micro-rayure. Le mat, le bois clair et les surfaces texturées pardonnent beaucoup plus. Le verre, lui, se nettoie très bien mais réclame un passage quotidien pour rester net.",
            "Regardez enfin les pieds et le piètement. Un piètement métallique soudé est plus rigide qu'un assemblage de panneaux vissés, et il encaisse mieux les déplacements. Des patins en feutre sous les pieds évitent de rayer un parquet et facilitent le repositionnement du meuble au centimètre près.",
        ],
        "liste": [
            "Panneaux de 16 mm minimum, chants collés sur les quatre côtés.",
            "Bois massif si le meuble sera démonté et remonté plusieurs fois.",
            "Finition mate ou texturée si vous détestez repasser un chiffon tous les jours.",
            "Piètement métal pour la rigidité, patins feutre pour le sol.",
        ],
    }


def _bloc_rangement(mc: str) -> dict[str, Any]:
    return {
        "titre": "Organiser le rangement pour que le plateau reste dégagé",
        "paragraphes": [
            "Un poste de maquillage se dégrade toujours de la même façon : le plateau se couvre, puis on cesse de l'utiliser parce qu'il faut dix minutes pour dégager de quoi travailler. La parade consiste à décider dès le premier jour de ce qui a le droit de rester dehors. La règle qui fonctionne : uniquement les produits utilisés quotidiennement, soit rarement plus de huit références.",
            "Le reste se range par famille et par fréquence, pas par couleur. Un tiroir pour le teint, un pour les yeux, un pour les pinceaux et les outils. Les compartiments amovibles en acrylique transparent transforment un tiroir profond en rangement lisible : on voit le contenu sans fouiller, ce qui évite de racheter un produit qu'on possède déjà en trois exemplaires.",
            "Les pinceaux méritent un traitement à part. Rangés à plat dans un tiroir, ils s'écrasent et perdent leur forme. Debout dans un pot, poils vers le haut, ils sèchent correctement après nettoyage et restent accessibles d'une main. Un pot lesté au fond avec des perles de verre les maintient droits même à moitié vide.",
            "Enfin, pensez à la lumière et à la chaleur. Les produits cosmétiques se conservent mal derrière une vitre exposée au sud : les textures crémeuses tournent et les pigments virent. Un tiroir fermé prolonge la durée de vie d'un fond de teint bien plus efficacement qu'un présentoir ouvert, aussi joli soit-il.",
        ],
        "liste": [
            "Maximum huit produits laissés sur le plateau, ceux du quotidien.",
            "Un tiroir par famille : teint, yeux, outils.",
            "Pinceaux debout, poils vers le haut, jamais écrasés à plat.",
            "Produits sensibles à l'abri de la lumière directe, tiroir fermé de préférence.",
        ],
    }


def _bloc_montage(mc: str) -> dict[str, Any]:
    return {
        "titre": "Montage, stabilité et sécurité",
        "paragraphes": [
            "Comptez entre quarante minutes et deux heures selon la complexité, et prévoyez une surface plane et protégée, un tapis ou un carton, pour ne pas rayer les panneaux pendant l'assemblage. Sortez et triez toute la visserie avant de commencer : la moitié des erreurs de montage vient d'une vis de 30 mm utilisée à la place d'une vis de 20 mm, qui traverse alors le panneau visible.",
            "Serrez tout à la main d'abord, sans bloquer, puis reprenez le serrage final une fois la structure entièrement assemblée. Un meuble serré section par section se retrouve systématiquement de travers, et l'on découvre le problème au moment de poser le tiroir qui frotte. Une visseuse électrique est utile pour l'approche, jamais pour le serrage final : le couple arrache facilement le filetage dans un panneau de particules.",
            "La fixation antibasculement n'est pas une option décorative. Tout meuble plus haut que large, et tout meuble susceptible d'être escaladé par un enfant, doit être arrimé au mur avec l'équerre fournie et une cheville adaptée au support. Sur une cloison en plaque de plâtre, les chevilles à expansion métalliques sont indispensables ; les chevilles plastiques livrées d'origine sont prévues pour le béton et ne tiendront pas.",
            "Dernier réflexe : reprenez le serrage de l'ensemble après deux à trois semaines d'utilisation. Les panneaux travaillent légèrement, et un quart de tour sur chaque vis à ce moment-là double tranquillement la durée de vie du meuble.",
            "Pensez aussi à ce que devient l'ancien meuble. Sur les modèles lourds, le carton arrive rarement seul : il faut avoir prévu où va la commode ou le bureau qu'il remplace, sous peine de se retrouver avec deux meubles dans la même pièce pendant des semaines. Une éco-participation étant incluse dans le prix des meubles neufs, de nombreux vendeurs proposent une reprise de l'ancien mobilier au moment de la livraison : la case est à cocher pendant la commande, rarement après. Vérifiez-le avant de valider, c'est le genre d'option qu'on ne peut plus activer une fois le colis expédié.",
        ],
        "encadre": {
            "titre": "À ne pas négliger",
            "texte": "Fixation murale obligatoire pour tout meuble haut ou installé dans une chambre d'enfant. La cheville doit correspondre au mur, pas au meuble.",
        },
    }


def _bloc_entretien(mc: str) -> dict[str, Any]:
    return {
        "titre": "Entretien : les gestes qui prolongent la durée de vie",
        "paragraphes": [
            "Un poste de maquillage subit des agressions que les autres meubles ignorent : projections de poudre, gouttes de sérum, traces de fond de teint gras, vapeur de laque. Le réflexe le plus rentable est de passer un chiffon microfibre légèrement humide sur le plateau chaque soir, avant que les résidus ne durcissent. Trente secondes qui évitent des heures de récupération plus tard.",
            "Sur une tache de fond de teint déjà sèche, évitez l'éponge abrasive et l'alcool pur qui attaquent le vernis. Un peu de savon doux sur un chiffon, en tamponnant plutôt qu'en frottant, suffit dans la grande majorité des cas. Pour un plateau laqué, une goutte d'huile végétale sur un coton peut décoller un résidu gras sans agresser la finition, à condition d'essuyer soigneusement ensuite.",
            "Le miroir se nettoie de haut en bas avec un produit sans ammoniaque, pulvérisé sur le chiffon et non directement sur la surface : le liquide qui coule dans la jointure attaque le tain par l'arrière, et les taches noires qui apparaissent alors sont définitives. C'est la cause numéro un des miroirs piqués au bout de quelques années.",
            "Une protection de plateau change tout. Un sous-main en cuir végétal, une plaque de verre sur mesure ou même un simple set de table lavable placé sous la zone de travail encaisse les projections à la place du meuble. C'est l'accessoire le plus rentable de tout le poste.",
        ],
        "liste": [
            "Chiffon microfibre chaque soir sur le plateau, avant durcissement.",
            "Jamais d'alcool pur ni d'éponge abrasive sur une finition laquée.",
            "Produit à vitres pulvérisé sur le chiffon, jamais sur le miroir.",
            "Une protection de plateau lavable sous la zone de travail.",
        ],
    }


def _bloc_erreurs(mc: str) -> dict[str, Any]:
    return {
        "titre": "Les erreurs les plus fréquentes à l'achat",
        "paragraphes": [
            "La première erreur est de choisir sur photo sans lire les dimensions. Les visuels de catalogue sont cadrés pour flatter le meuble, souvent dans une pièce plus grande que la vôtre, avec des accessoires à l'échelle réduite. Un modèle qui paraît compact en image peut faire 120 cm de large. Le remède tient en un mètre ruban et cinq minutes.",
            "La deuxième est d'oublier l'assise. On commande un plateau à 76 cm de haut, puis on récupère une chaise de cuisine à 46 cm : la position est correcte. Mais un tabouret bas à 38 cm oblige à lever les bras et transforme chaque séance en effort. La règle utile : environ 30 cm d'écart entre l'assise et le dessous du plateau.",
            "La troisième est de sous-estimer l'éclairage en pensant l'ajouter plus tard. Dans les faits, on l'ajoute rarement, et l'on se maquille pendant des mois sous un plafonnier mal placé. Si le modèle choisi n'a pas de lumière intégrée, commandez le miroir lumineux en même temps, pas dans six mois.",
            "La quatrième, enfin, est d'acheter trop grand par anticipation. Un meuble surdimensionné dans une chambre étroite gêne la circulation tous les jours pour un rangement dont on n'utilise jamais la moitié. Mieux vaut un modèle juste dimensionné et un rangement d'appoint dans le placard.",
        ],
        "liste": [
            "Ne jamais commander sans avoir mesuré l'emplacement au sol.",
            "Prévoir l'assise en même temps que le meuble, avec 30 cm d'écart.",
            "Commander l'éclairage le même jour, pas « plus tard ».",
            "Choisir la taille en fonction de la pièce, pas d'une collection future.",
        ],
    }


def _bloc_budget(mc: str) -> dict[str, Any]:
    return {
        "titre": "Où placer son budget intelligemment",
        "paragraphes": [
            "Sans parler de montants, la logique d'arbitrage est toujours la même. L'argent bien placé va d'abord dans la structure et les glissières de tiroirs, ensuite dans l'éclairage, enfin dans l'esthétique. Un meuble magnifique dont les tiroirs coincent au bout d'un an génère plus de frustration qu'un modèle sobre parfaitement fonctionnel.",
            "L'entrée de gamme se justifie pleinement dans trois cas : un premier achat pour tester l'usage réel, une chambre d'adolescente dont les goûts changeront, ou une location temporaire. Dans ces situations, la question n'est pas la durabilité sur quinze ans mais le risque financier limité.",
            "Le milieu de gamme est le meilleur rapport satisfaction sur durée pour un usage quotidien d'adulte. On y trouve des panneaux plus épais, des glissières correctes et parfois un éclairage intégré. C'est le segment où la différence de prix se traduit vraiment par une différence d'usage.",
            "Le haut de gamme se justifie si vous vous maquillez tous les jours, si vous filmez, ou si le meuble structure visuellement la pièce. Vous payez alors la surface de plateau, la qualité de lumière et la finition. En dessous de cet usage, la dépense supplémentaire se ressent peu au quotidien.",
        ],
    }


def _bloc_style(mc: str) -> dict[str, Any]:
    return {
        "titre": "Accorder le meuble à la décoration existante",
        "paragraphes": [
            "Un meuble de maquillage réussi ne se remarque pas comme une pièce rapportée : il prolonge ce qui existe déjà. La méthode la plus simple consiste à reprendre le matériau dominant de la chambre. Si votre tête de lit est en bois clair, une coiffeuse en bois clair s'intègre sans effort. Si la pièce est très blanche, jouer le contraste avec un modèle noir ou en verre crée un point focal volontaire plutôt qu'une fausse note.",
            "Les poignées sont le levier de personnalisation le plus rentable. Remplacer des poignées standard par des boutons en laiton, en céramique ou en cuir change radicalement la perception du meuble pour un coût dérisoire et un tournevis. C'est aussi la façon la plus rapide de faire passer un modèle très diffusé pour une pièce choisie.",
            "Le miroir participe autant que le meuble à l'ambiance. Un miroir rond adoucit une pièce anguleuse et très graphique ; un miroir rectangulaire renforce au contraire une composition ordonnée. Un modèle sur pied posé sur le plateau se change en cinq minutes, ce qui permet de faire évoluer le coin maquillage sans racheter le meuble.",
            "Enfin, traitez le mur derrière le meuble comme faisant partie du poste. Un papier peint sur cette seule portion, deux appliques murales ou une simple étagère alignée transforment un meuble posé contre une cloison en véritable coin dédié. C'est ce qui distingue une chambre aménagée d'une chambre meublée.",
        ],
    }


def _bloc_alternatives(mc: str) -> dict[str, Any]:
    return {
        "titre": "Les alternatives à considérer avant de trancher",
        "paragraphes": [
            "Toutes les situations ne réclament pas une coiffeuse dédiée. Une console étroite de 30 cm de profondeur, associée à un miroir mural et à deux paniers, remplit la même fonction dans un couloir ou un pied de lit. C'est souvent la meilleure réponse quand la chambre ne peut pas céder un mètre carré supplémentaire.",
            "Le bureau détourné est la deuxième alternative sérieuse, en particulier dans un studio. Un plan de travail unique servant au travail et au maquillage évite de dupliquer un meuble rarement utilisé plus d'une demi-heure par jour. Le compromis porte sur l'esthétique et sur la nécessité de dégager la surface entre deux usages.",
            "Le modèle à miroir relevable constitue une troisième voie intéressante : il offre le confort d'une vraie coiffeuse quand le miroir est levé, et redevient une console neutre le reste du temps. Cette réversibilité est particulièrement adaptée aux chambres d'amis et aux pièces de vie partagées.",
            "Enfin, la solution murale rabattable reste imbattable là où le sol ne peut rien accueillir de permanent. Elle demande un mur porteur ou des chevilles adaptées, mais elle libère intégralement la circulation en journée. Le seul vrai renoncement porte sur la charge admissible et donc sur ce que l'on peut poser dessus.",
        ],
    }


def _bloc_qualite(mc: str) -> dict[str, Any]:
    return {
        "titre": "Comment reconnaître un bon modèle avant de commander",
        "paragraphes": [
            "Les fiches produit se ressemblent toutes, mais quelques indices distinguent un meuble sérieux d'un meuble simplement bien photographié. Le premier est la présence de dimensions intérieures de tiroirs, et pas seulement des cotes extérieures. Un vendeur qui les publie sait que son rangement tient la comparaison.",
            "Le deuxième indice est le poids annoncé. À dimensions équivalentes, un meuble plus lourd est presque toujours construit avec des panneaux plus épais. Un modèle d'un mètre de large annoncé à quinze kilos est nécessairement fin ; le même à vingt-cinq kilos inspire davantage confiance sur la tenue dans le temps.",
            "Le troisième est le détail du contenu du carton. Une notice illustrée, une visserie triée par sachets numérotés et une équerre antibasculement fournie signalent un fabricant qui a pensé au montage. À l'inverse, une visserie en vrac dans un sachet unique annonce une heure supplémentaire de tri.",
            "Le quatrième, enfin, concerne les avis : lisez ceux qui portent sur l'usage à six mois, pas sur la livraison. Les commentaires utiles parlent de tiroirs qui frottent, de chants qui se décollent ou de miroir qui bouge. Ce sont eux qui prédisent votre satisfaction réelle, pas la note globale.",
        ],
        "liste": [
            "Dimensions intérieures des tiroirs publiées : bon signe.",
            "Poids cohérent avec la taille annoncée.",
            "Visserie triée et équerre antibasculement fournie.",
            "Avis portant sur six mois d'usage plutôt que sur la livraison.",
        ],
    }


BLOCS = [
    _bloc_criteres,
    _bloc_eclairage,
    _bloc_espace,
    _bloc_materiaux,
    _bloc_rangement,
    _bloc_montage,
    _bloc_entretien,
    _bloc_erreurs,
    _bloc_budget,
    _bloc_style,
    _bloc_alternatives,
    _bloc_qualite,
]


# ------------------------------------------------------------------- FAQ


FAQ_BASE = [
    ("Quelle est la hauteur idéale pour ce type de meuble ?",
     "Le plateau se situe le plus souvent entre 73 et 78 cm du sol, comme un bureau. Cette hauteur convient à la majorité des adultes assis sur une assise d'environ 45 cm. Si vous mesurez moins d'un mètre soixante, visez le bas de la fourchette ou choisissez un tabouret réglable. L'objectif est d'avoir les avant-bras à l'horizontale sans lever les épaules."),
    ("Quelle largeur minimum faut-il prévoir ?",
     "Quatre-vingts centimètres constituent le seuil en dessous duquel on se sent à l'étroit dès qu'on pose une trousse ouverte. Entre 90 et 100 cm, le confort est net et l'on peut travailler à deux mains sans déplacer d'objets. Au-delà de 120 cm, le gain devient surtout esthétique. Mesurez toujours l'espace disponible avant de vous fier à une photo."),
    ("Faut-il obligatoirement fixer le meuble au mur ?",
     "C'est indispensable dès que le meuble est plus haut que large, et dans toute chambre d'enfant sans exception. L'équerre antibasculement est généralement fournie, mais les chevilles livrées conviennent au béton, pas au placo. Sur une cloison creuse, utilisez des chevilles à expansion métalliques. Cette précaution prend dix minutes et supprime le seul vrai risque du meuble."),
    ("Peut-on s'en servir comme bureau ?",
     "Oui, à condition que la profondeur atteigne au moins 45 cm pour accueillir un ordinateur portable et laisser de la place devant. Les modèles à miroir relevable sont conçus exactement pour ce double usage. Le seul vrai compromis concerne le rangement : un poste partagé exige de trier régulièrement. Prévoyez un caisson mobile si les deux usages sont quotidiens."),
    ("Quel éclairage choisir pour ne pas se tromper de teinte ?",
     "Une lumière frontale, placée de part et d'autre du miroir à hauteur de visage, avec une température autour de 4000 à 5000 K. En dessous de 3000 K, la lumière jaunit et fausse le jugement sur un fond de teint. Un indice de rendu des couleurs supérieur à 90 est un vrai plus quand l'information est disponible. Évitez de vous fier au seul plafonnier, qui crée des ombres sous les yeux."),
    ("Comment enlever une tache de fond de teint sur le plateau ?",
     "Tamponnez avec un chiffon microfibre et un peu de savon doux, sans frotter. Sur une finition laquée, une goutte d'huile végétale sur un coton décolle les résidus gras sans attaquer le vernis, à condition d'essuyer ensuite soigneusement. Évitez l'alcool pur et les éponges abrasives, qui ternissent définitivement la surface. Le mieux reste de passer un chiffon chaque soir avant que la tache ne sèche."),
    ("Combien de temps faut-il pour le montage ?",
     "Comptez de quarante minutes à deux heures selon la complexité et le nombre de tiroirs. Triez toute la visserie avant de commencer et serrez d'abord à la main sans bloquer, puis reprenez le serrage final une fois la structure assemblée. Une visseuse électrique aide pour l'approche mais arrache facilement le filetage au serrage. Reprenez le serrage général après deux à trois semaines d'usage."),
    ("Quelle taille de miroir est réellement utile ?",
     "Quarante centimètres de hauteur constituent le minimum pour voir son visage entier sans reculer. Entre 50 et 60 cm, vous contrôlez aussi le haut du buste et la coiffure. Un miroir triptyque ajoute la vision de profil, très utile pour les cheveux et pour les sourcils. Au-delà, le gain est surtout décoratif."),
    ("Que faire s'il n'y a pas de prise à proximité ?",
     "Une multiprise plate fixée derrière le meuble, avec un câble plat passé le long de la plinthe, règle la question proprement. Évitez les rallonges qui traversent le passage. Les modèles à piles restent une solution de dépannage, mais leur intensité baisse progressivement sans qu'on s'en aperçoive. Si vous rénovez, prévoyez une prise à 30 cm du sol à l'emplacement du meuble."),
    ("Comment éviter que le plateau soit envahi en deux semaines ?",
     "Décidez dès le premier jour du nombre de produits autorisés à rester dehors, huit étant une limite réaliste. Rangez le reste par famille d'usage plutôt que par couleur, avec des séparateurs transparents dans les tiroirs. Les pinceaux se conservent debout, poils vers le haut, jamais écrasés à plat. Un rangement lisible se maintient tout seul ; un rangement joli mais opaque se dégrade en quelques jours."),
]


# ------------------------------------------------------------- assemblage


def sections_supplementaires(
    sujet: dict[str, Any], produits: list[dict[str, Any]], mots_manquants: int
) -> list[dict[str, Any]]:
    """Sections de fond ajoutées quand un article n'atteint pas le plancher."""
    gn = _groupe_nominal(sujet.get("mot_cle", "coiffeuse"))
    alea = _alea(sujet["id"] + "-complement")
    blocs = list(BLOCS)
    alea.shuffle(blocs)

    ajouts: list[dict[str, Any]] = []
    total = 0
    for constructeur in blocs:
        if total >= mots_manquants:
            break
        section = constructeur(gn)
        ajouts.append(section)
        total += _mots(*section["paragraphes"]) + _mots(*section.get("liste", []))
    return ajouts


def rediger(
    sujet: dict[str, Any],
    produits: list[dict[str, Any]],
    articles_lies: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    mc = sujet.get("mot_cle", "coiffeuse")
    gn = _groupe_nominal(mc)
    titre = sujet["titre"]
    alea = _alea(sujet["id"])
    objectif = config["publication"]["objectif_mots"]

    # Les parties fixes (chapeau, avis produits, FAQ, conclusion) pèsent déjà
    # lourd : on ne rajoute des sections de fond que jusqu'à l'objectif réel.
    poids_fixe = 250  # chapeau + conclusion
    poids_fixe += sum(
        _mots(
            p.get("pour_qui", ""),
            *p.get("points_forts", []),
            *p.get("points_faibles", []),
        )
        + 45
        for p in produits
    )
    poids_fixe += sum(_mots(q, r) for q, r in FAQ_BASE[:8])

    blocs = list(BLOCS)
    alea.shuffle(blocs)
    sections: list[dict[str, Any]] = []
    total = poids_fixe
    for constructeur in blocs:
        if total >= objectif:
            break
        section = constructeur(gn)
        sections.append(section)
        total += _mots(*section["paragraphes"]) + _mots(*section.get("liste", []))

    # Section d'ouverture propre au sujet
    sections.insert(
        0,
        {
            "titre": f"Ce qu'il faut comprendre avant de choisir {gn}",
            "paragraphes": [
                f"Chercher {gn} revient presque toujours à arbitrer entre trois contraintes : la place réellement disponible, le confort d'usage au quotidien et le budget que l'on accepte d'y consacrer. Aucun modèle ne maximise les trois en même temps, et c'est précisément pour cela que la question « quel est le meilleur » n'a pas de réponse universelle. La bonne question est plutôt : quelle contrainte êtes-vous prête à assouplir.",
                "Dans les faits, la contrainte de place est la seule qui ne se négocie pas. Un meuble trop encombrant reste encombrant pour toute sa durée de vie, tandis qu'un rangement un peu juste se complète avec un caisson d'appoint, et qu'un éclairage absent s'ajoute avec un miroir lumineux. C'est pourquoi la première étape reste toujours la même : mesurer, puis choisir.",
                f"Cet article passe en revue les modèles les plus pertinents si vous cherchez {gn}, puis détaille les critères qui font vraiment la différence à l'usage : dimensions, matériaux, éclairage, rangement, montage et entretien. L'objectif est que vous puissiez commander en connaissance de cause, sans avoir à comparer dix fiches produit dont les descriptions se ressemblent toutes.",
            ],
        },
    )

    # Maillage interne : les titres cités sont transformés en liens au rendu.
    if articles_lies:
        citations = " ".join(f"Le guide « {a['titre_h1']} » complète utilement ce point." for a in articles_lies[:2])
        sections.append(
            {
                "titre": "Pour aller plus loin",
                "paragraphes": [
                    "Le choix d'un meuble de maquillage se joue rarement sur un seul critère. "
                    "Si vous hésitez encore entre deux configurations, quelques lectures ciblées "
                    "font généralement basculer la décision plus vite qu'une comparaison "
                    f"supplémentaire de fiches produit. {citations}",
                ],
            }
        )

    avis = []
    for produit in produits:
        avis.append(
            {
                "produit_id": produit["id"],
                "accroche": "Pour " + produit.get("pour_qui", "un usage courant"),
                "verdict": (
                    f"{produit['nom']} s'adresse à {produit.get('pour_qui', 'un usage courant')}. "
                    f"{produit.get('points_forts', [''])[0]}. "
                    f"En contrepartie, {produit.get('points_faibles', ['il faut accepter quelques compromis'])[0].lower()}. "
                    "Un modèle cohérent dès lors que ces limites correspondent à votre usage réel."
                ),
                "points_forts": produit.get("points_forts", []),
                "points_faibles": produit.get("points_faibles", []),
                "ideal_pour": produit.get("pour_qui", ""),
            }
        )

    faq = [{"q": q, "r": r} for q, r in FAQ_BASE[:8]]

    return {
        "titre_seo": titre[:60],
        "titre_h1": titre,
        "meta": (
            f"Comment choisir {gn} : dimensions à vérifier, éclairage, rangement "
            "et sélection commentée de modèles."
        )[:155],
        "chapeau": (
            f"Choisir {gn} paraît simple jusqu'au moment où l'on compare deux fiches produit "
            "quasiment identiques, avec les mêmes photos flatteuses et des dimensions écrites en tout petit. "
            "La différence se joue pourtant sur des détails très concrets : la profondeur du plateau, "
            "la hauteur intérieure des tiroirs, la position de la lumière et la solidité du piètement. "
            "Ce guide reprend ces critères un par un, les applique à une sélection de modèles, "
            "et vous donne les mesures à vérifier avant de commander."
        ),
        "sections": sections,
        "avis_produits": avis,
        "faq": faq,
        "conclusion": (
            f"Au terme de cette revue, la recommandation tient en une phrase : mesurez d'abord, "
            "choisissez ensuite. La très grande majorité des déceptions vient d'un meuble mal "
            "dimensionné pour la pièce, pas d'un défaut de fabrication. Une fois l'emprise validée "
            "au sol avec du ruban de masquage, le choix se réduit à deux ou trois modèles et "
            "devient facile. Prévoyez l'assise et l'éclairage dans la même commande plutôt que "
            "« plus tard », fixez le meuble au mur si sa hauteur le justifie, et reprenez le serrage "
            "des vis après trois semaines. Ces trois réflexes suffisent à transformer un achat "
            "correct en installation dont on est encore satisfaite plusieurs années après."
        ),
        "_source": "local",
    }
