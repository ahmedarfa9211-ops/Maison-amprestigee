"""Rédaction sans API : assemblage de fond éditorial paramétré par le sujet.

Utilité : tester le système, dépanner un jour où l'API est indisponible, et
garantir qu'aucune journée ne passe sans publication. Pour de la publication
quotidienne durable, préférez le mode "api" (textes uniques).

Version « Panoplie Halloween » : le fond éditorial porte sur les costumes et
déguisements d'Halloween (taille, confort, sécurité, accessoires, maquillage,
budget, dernière minute, groupe, entretien).
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

    « déguisement sorcière » -> « un déguisement sorcière », « meilleur
    déguisement Halloween » -> « le meilleur déguisement Halloween ». Tout le
    reste retombe sur une formule neutre.
    """
    mc = (mot_cle or "").strip().lower()
    if mc.startswith(("meilleur", "meilleure")):
        return f"le {mc}"
    if mc.startswith("accessoire"):
        return f"des {mc}"
    if mc.startswith(("déguisement", "costume", "maquillage")):
        return f"un {mc}"
    return "un déguisement"


# --------------------------------------------------------------- blocs texte


def _bloc_taille(mc: str) -> dict[str, Any]:
    return {
        "titre": "La taille : le premier critère qui gâche ou sauve un costume",
        "paragraphes": [
            f"Avant même de choisir le personnage, il faut regarder ce qui fait rater le plus de commandes : la taille. Un déguisement ne se choisit jamais à sa taille de prêt-à-porter habituelle, car chaque fabricant applique son propre patron, souvent taillé petit et importé d'une autre grille que la grille française. La règle qui évite la déception consiste à toujours ouvrir le guide des tailles de la fiche et à comparer ses propres mensurations, en centimètres, aux valeurs annoncées.",
            "Prenez trois mesures avant de commander : le tour de poitrine, le tour de taille et la hauteur totale si le costume est une combinaison intégrale. Reportez-les sur le tableau du vendeur et, en cas d'hésitation entre deux tailles, montez d'un cran : un costume légèrement ample se porte toute une soirée, un costume trop juste devient inconfortable au bout d'une heure et craque à la première danse. Pour un enfant, fiez-vous à la taille en centimètres plutôt qu'à l'âge indiqué, qui reste très approximatif.",
            "Méfiez-vous des combinaisons moulantes de type squelette ou super-héros, dont l'imprimé se déforme dès que la taille n'est pas exacte : un squelette étiré n'a plus rien d'effrayant, il fait simplement négligé. À l'inverse, les capes, les robes longues et les costumes gonflables pardonnent presque tout et conviennent quand on hésite ou qu'on commande pour quelqu'un d'autre. C'est un critère à intégrer dès le choix du type de déguisement.",
            "Enfin, anticipez le délai. Un costume commandé la veille ne se renvoie pas s'il taille mal, et l'échange est impossible à quelques heures de la fête. Commander une semaine à l'avance laisse le temps d'essayer, de renvoyer si besoin et d'ajuster avec un accessoire. C'est le seul moyen d'arriver le 31 octobre avec un costume qui tombe bien.",
        ],
        "liste": [
            "Prenez trois mesures : tour de poitrine, tour de taille, hauteur totale.",
            "Comparez toujours vos centimètres au guide des tailles, jamais votre taille habituelle.",
            "En cas de doute entre deux tailles, montez d'un cran.",
            "Pour un enfant, choisissez la taille en centimètres, pas selon l'âge indiqué.",
            "Commandez une semaine avant pour pouvoir essayer et échanger.",
        ],
        "encadre": {
            "titre": "Le réflexe qui évite le retour de colis",
            "texte": "Mesurez-vous au mètre ruban, notez trois chiffres, puis lisez le tableau de tailles du vendeur avant de cliquer. Deux minutes qui évitent un costume inportable le soir même.",
        },
    }


def _bloc_confort_meteo(mc: str) -> dict[str, Any]:
    return {
        "titre": "Confort et météo : Halloween tombe fin octobre, pas en été",
        "paragraphes": [
            "Le piège du costume d'Halloween est de le choisir pour la photo et d'oublier qu'on va le porter plusieurs heures, souvent dehors, un soir de fin octobre. Les températures tournent fréquemment autour de dix degrés, et une robe fine ou une combinaison légère devient vite un supplice pour la tournée des bonbons comme pour rejoindre une soirée à pied. Le confort thermique se pense donc avant l'achat, pas une fois qu'on grelotte.",
            "La parade la plus simple consiste à choisir un costume qui accepte une couche chaude en dessous : un legging et un sous-pull thermique sous une robe, un tee-shirt technique sous une combinaison. Les capes et les costumes amples se prêtent parfaitement à ce jeu de superposition, ce qui les rend précieux pour les enfants qui sortent longtemps. À l'inverse, un costume moulant ne laisse aucune place à une épaisseur supplémentaire.",
            "Pensez aussi aux chaussures et aux extrémités. On soigne le haut du costume et on oublie qu'on va marcher une heure : des chaussures confortables et déjà rodées valent mieux que des escarpins assortis qui blessent au bout de dix minutes. Une paire de collants chauds, des chaussettes épaisses et une écharpe discrète glissée sous une cape font une vraie différence sans casser l'effet.",
            "Enfin, la respirabilité compte pour les costumes intégraux et les masques. Un masque en latex tient chaud et embue la vision : prévoyez de le retirer pour manger, boire et vous déplacer dans le noir. Un costume gonflable, très amusant, devient étouffant en intérieur chauffé : réservez-le aux moments forts de la soirée plutôt qu'à toute la nuit.",
        ],
        "liste": [
            "Choisissez un costume qui accepte une couche thermique en dessous.",
            "Privilégiez des chaussures déjà rodées : vous allez marcher.",
            "Collants chauds et chaussettes épaisses ne se voient pas et changent tout.",
            "Retirez masque intégral et costume gonflable pour manger et vous déplacer.",
        ],
    }


def _bloc_securite(mc: str) -> dict[str, Any]:
    return {
        "titre": "Sécurité : le point non négociable, surtout pour les enfants",
        "paragraphes": [
            "Un déguisement reste un vêtement de fête, mais quelques règles de sécurité ne se discutent pas, en particulier pour les enfants. La première concerne l'inflammabilité : les tissus et les perruques synthétiques bon marché prennent feu très vite, et les bougies de citrouille sont partout le 31 octobre. Tenez tout costume à distance des flammes et privilégiez, quand l'information existe, les articles indiquant une conformité aux normes textiles européennes.",
            "La visibilité nocturne est le deuxième point souvent négligé. Un enfant vêtu de noir ou de blanc sombre est presque invisible pour une voiture lors de la tournée des bonbons. Ajoutez des bandes réfléchissantes sur le costume et le sac, glissez une petite lampe ou un bâton lumineux dans sa main, et restez du côté trottoir. Ces précautions ne coûtent presque rien et changent le niveau de risque.",
            "Le champ de vision et la liberté de mouvement viennent ensuite. Une capuche qui tombe sur les yeux, un masque mal ajusté ou une cape trop longue qui traîne au sol provoquent des chutes. Vérifiez que l'enfant voit correctement, marche sans se prendre les pieds et peut lever les bras. Pour les tout-petits, préférez un maquillage léger à un masque, et évitez tout petit accessoire détachable qui pourrait finir dans la bouche.",
            "Enfin, les produits appliqués sur la peau et les yeux méritent une vraie vigilance. Faites un test de maquillage la veille sur l'avant-bras pour repérer une réaction, et n'utilisez que des fards prévus pour le visage. Les lentilles de contact fantaisie ne sont pas des accessoires anodins : elles doivent porter le marquage CE, ne jamais se partager, et respecter la durée de port indiquée, sous peine de blessure oculaire.",
        ],
        "liste": [
            "Tenez costumes et perruques synthétiques loin des bougies : le synthétique s'enflamme vite.",
            "Ajoutez bandes réfléchissantes et une lampe pour la tournée des bonbons.",
            "Vérifiez que l'enfant voit, marche et lève les bras sans gêne.",
            "Testez le maquillage la veille ; n'utilisez que des lentilles marquées CE.",
        ],
        "encadre": {
            "titre": "La règle des tout-petits",
            "texte": "Pour un jeune enfant, un maquillage léger vaut mieux qu'un masque, et aucun petit élément détachable ne doit se trouver à hauteur de bouche.",
        },
    }


def _bloc_accessoires(mc: str) -> dict[str, Any]:
    return {
        "titre": "Les accessoires : ce qui sépare un costume réussi d'un costume banal",
        "paragraphes": [
            "C'est le levier le plus rentable d'Halloween, et pourtant le plus sous-estimé. Un costume acheté seul ressemble à celui de dix autres invités ; le même costume complété de deux ou trois accessoires bien choisis devient une tenue qu'on remarque et qu'on photographie. La logique est simple : la base habille, l'accessoire raconte le personnage. Une robe noire n'est rien ; avec un chapeau de sorcière, une perruque et un maquillage, elle devient un vrai déguisement.",
            "Certains accessoires sont de véritables couteaux suisses. Une cape noire à capuche transforme n'importe quelle tenue sombre en sorcier, faucheuse ou vampire selon ce qu'on y ajoute. Une perruque change radicalement une silhouette et distingue immédiatement un costume soigné d'une version bâclée. Un chapeau signe un personnage à lui seul. Ce sont des achats à petit prix qui resservent chaque année et pour d'autres soirées costumées.",
            "Le maquillage occupe une place à part : c'est l'accessoire qui offre le meilleur rapport effet sur prix. Quelques euros de fards et de faux sang suffisent à faire passer un costume ordinaire au niveau supérieur, voire à improviser un déguisement complet avec des vêtements sombres déjà dans l'armoire. Une seule palette sert à toute la famille et resservira plusieurs Halloween de suite.",
            "Attention, cependant, à ne pas surcharger. Un bon costume repose sur un ou deux accessoires forts et cohérents, pas sur une accumulation qui brouille le message. Choisissez ce qui précise le personnage et écartez le reste : mieux vaut une sorcière avec un beau chapeau et un maquillage soigné qu'une silhouette couverte de gadgets qui ne racontent rien.",
        ],
        "liste": [
            "Une cape à capuche : l'accessoire le plus polyvalent, base de plusieurs personnages.",
            "Une perruque : elle distingue instantanément un costume soigné d'une version bâclée.",
            "Une palette de maquillage : le meilleur rapport effet/prix de tout Halloween.",
            "Un accessoire signature (chapeau, masque) plutôt qu'une accumulation de gadgets.",
        ],
    }


def _bloc_maquillage(mc: str) -> dict[str, Any]:
    return {
        "titre": "Maquillage et finitions : l'effet qui tient toute la soirée",
        "paragraphes": [
            "Le maquillage est ce qui distingue un costume porté d'un personnage incarné, et c'est souvent lui qu'on rate faute de méthode. La première règle est de préparer la peau : un visage propre et une fine couche de crème ou de base aident les fards à tenir et facilitent le démaquillage. Sur une peau nue et grasse, le maquillage file, migre et disparaît au bout de deux heures de fête.",
            "Travaillez par couches fines et fixez au fur et à mesure. Un fond blanc de zombie ou de squelette tient mieux poudré légèrement, et les contours noirs se posent avec un pinceau fin plutôt qu'au doigt, qui bave. Le faux sang s'applique en dernier, par petites touches : trop, il déteint sur les cols et les mains ; juste ce qu'il faut, il rend l'ensemble crédible. Gardez un mouchoir pour éponger l'excédent.",
            "Adaptez l'intensité au contexte et à la personne. Pour un jeune enfant, un motif simple sur la joue ou un contour d'yeux suffit et évite le masque qui gêne. Pour une soirée entre adultes, on peut appuyer les creux et les ombres, qui ressortent sous une lumière tamisée. Un maquillage pensé pour la pénombre d'une fête n'est pas le même que celui qu'on juge en pleine lumière de salle de bain.",
            "Prévoyez enfin le retour à la normale. Le maquillage FX et le faux sang ne partent pas à l'eau seule : un démaquillant gras, une huile ou un lait démaquillant sont indispensables, suivis d'un nettoyant doux. Anticiper cette étape évite de se coucher à moitié démaquillé et de retrouver l'oreiller taché le lendemain.",
        ],
        "liste": [
            "Préparez la peau avec une base : le maquillage tient et part plus facilement.",
            "Travaillez par couches fines, fixez à la poudre, posez le faux sang en dernier.",
            "Adaptez l'intensité : léger pour un enfant, appuyé pour une soirée en pénombre.",
            "Gardez un démaquillant gras : ni le FX ni le faux sang ne partent à l'eau.",
        ],
    }


def _bloc_derniere_minute(mc: str) -> dict[str, Any]:
    return {
        "titre": "Dernière minute : s'en sortir quand il ne reste qu'une soirée",
        "paragraphes": [
            "Il arrive qu'on décide de se déguiser la veille, voire le jour même. Tout n'est pas perdu, à condition de viser les personnages qui reposent sur un accessoire fort plutôt que sur un costume complet. Une cape à capuche, un chapeau de sorcière ou un masque en latex, combinés à des vêtements sombres déjà possédés, composent un déguisement crédible en quelques minutes et sans couture.",
            "Le maquillage est le meilleur allié de la dernière minute. Avec une palette basique et un peu de faux sang, on transforme une tenue noire ordinaire en zombie, en mort-vivant ou en sorcière sans rien acheter d'autre. C'est aussi la solution la plus économique : quelques euros de fards remplacent un costume entier et resservent les années suivantes.",
            "Côté logistique, privilégiez ce qui est disponible tout de suite : magasin de proximité pour un accessoire, ou livraison rapide quand elle est proposée sur la fiche produit. Vérifiez le délai annoncé avant de commander, car un costume qui arrive le 1er novembre ne sert à rien. En cas de doute, l'accessoire acheté en boutique physique reste la valeur sûre.",
            "Enfin, jouez collectif. Si vous êtes plusieurs à être pris de court, un thème commun improvisé — tous en noir avec un accessoire chacun, tous fantômes sous une cape claire — a plus d'allure que des déguisements individuels bâclés. L'uniformité d'un groupe compense largement la simplicité de chaque tenue prise isolément.",
        ],
        "liste": [
            "Misez sur un accessoire fort (cape, chapeau, masque) plus des vêtements sombres.",
            "Le maquillage transforme une tenue noire en costume complet à moindre frais.",
            "Vérifiez le délai de livraison avant de commander : sinon, boutique physique.",
            "À plusieurs, un thème commun simple bat des costumes individuels bâclés.",
        ],
        "encadre": {
            "titre": "Le kit de secours",
            "texte": "Une cape noire, un peu de faux sang et une palette de maquillage suffisent à improviser un déguisement crédible en dix minutes, sans rien coudre.",
        },
    }


def _bloc_diy(mc: str) -> dict[str, Any]:
    return {
        "titre": "Fait maison : réussir un déguisement avec ce qu'on a déjà",
        "paragraphes": [
            "Le costume fait maison a deux atouts : il ne coûte presque rien et il est unique. La méthode qui fonctionne consiste à partir de son armoire plutôt que d'une idée trop ambitieuse. Une tenue entièrement noire est la base la plus polyvalente : elle devient chat, sorcière, voleur ou ombre selon les oreilles, le chapeau ou le maquillage qu'on y ajoute. On construit le personnage à partir de l'existant, sans machine à coudre.",
            "Quelques fournitures simples ouvrent beaucoup de possibilités : du carton, du feutre, des épingles à nourrice, un vieux drap et un peu de maquillage. Un drap blanc reste le fantôme le plus rapide de l'histoire ; du carton peint fait un bouclier, une hache ou une pierre tombale ; des vêtements déchirés volontairement et tachés de faux sang composent un zombie convaincant. L'imperfection fait partie du charme et se remarque à peine le soir.",
            "Le fait maison brille particulièrement pour les enfants, qui adorent participer à la fabrication. Impliquer l'enfant dans la création du costume prolonge le plaisir bien au-delà de la soirée et permet d'ajuster à sa morphologie exacte. On garde en tête les mêmes règles de sécurité que pour un costume acheté : rien qui gêne la vue, rien d'inflammable près des bougies, et une bonne visibilité la nuit.",
            "Reste que le fait maison a ses limites. Pour un effet très net — un squelette phosphorescent, un masque en latex réaliste — l'achat reste plus efficace et plus rapide. La meilleure stratégie est souvent hybride : une base faite maison, complétée d'un ou deux accessoires achetés qui font monter l'ensemble d'un cran sans exploser le budget.",
        ],
        "liste": [
            "Partez d'une tenue noire : la base la plus polyvalente pour improviser.",
            "Carton, feutre, vieux drap et maquillage ouvrent des dizaines de personnages.",
            "Faites participer les enfants : ajustement parfait et plaisir prolongé.",
            "Combinez base maison et un accessoire acheté pour l'effet net.",
        ],
    }


def _bloc_budget(mc: str) -> dict[str, Any]:
    return {
        "titre": "Où placer son budget déguisement intelligemment",
        "paragraphes": [
            "Sans parler de montants, la logique d'arbitrage reste la même chaque année. L'argent le mieux placé va d'abord dans ce qui se remarque et se réutilise : un accessoire de qualité, une perruque correcte, un maquillage qui tient. Un costume complet bas de gamme porté une seule fois rend souvent moins service qu'une base sobre relevée d'accessoires soignés qui resserviront.",
            "L'entrée de gamme se justifie pleinement dans trois cas : un déguisement porté une seule soirée, un enfant qui changera de goût l'an prochain, ou un costume de groupe où c'est le nombre qui fait l'effet et non la finition d'une pièce isolée. Dans ces situations, la durabilité importe peu et le petit prix est le bon choix.",
            "Le milieu de gamme est le meilleur compromis pour un adulte qui se déguise chaque année. On y gagne des tissus plus épais, des coutures qui tiennent la soirée et un rendu plus crédible sur les photos. C'est le segment où la différence de prix se traduit vraiment par une différence visible et par un costume qu'on ressort sans honte.",
            "Le haut de gamme ne se justifie que si le costume sert à plusieurs occasions : soirées à thème, murder party, festivals, jeux de rôle grandeur nature. Un déguisement médiéval bien coupé ou un costume élaboré s'amortit sur plusieurs événements. Pour un unique 31 octobre, la dépense supplémentaire se ressent peu et l'entrée ou le milieu de gamme suffisent.",
        ],
        "liste": [
            "Investissez d'abord dans ce qui se réutilise : accessoires, perruque, maquillage.",
            "Entrée de gamme : soirée unique, enfant qui grandit, costume de groupe nombreux.",
            "Milieu de gamme : le bon compromis pour qui se déguise chaque année.",
            "Haut de gamme : seulement si le costume ressert à plusieurs occasions.",
        ],
    }


def _bloc_groupe(mc: str) -> dict[str, Any]:
    return {
        "titre": "Couple, groupe, famille : coordonner sans uniformiser",
        "paragraphes": [
            "Se déguiser à plusieurs change la donne : un thème commun a toujours plus d'impact qu'une addition de costumes isolés. Pour un couple, le plus simple est un duo assorti — deux squelettes, un vampire et sa victime, un couple médiéval — qui se lit immédiatement sur les photos. L'astuce est d'acheter les deux pièces ensemble pour garantir la cohérence de style et de tailles plutôt que de tenter d'assortir deux costumes trouvés séparément.",
            "Pour un groupe d'amis, deux stratégies fonctionnent. La première, économique, consiste à habiller tout le monde de la même base bon marché — des capes de fantôme, par exemple — pour un effet de masse imbattable au mètre. La seconde décline un univers commun en personnages différents : une bande de monstres classiques, une équipe de super-héros. Dans les deux cas, l'uniformité visuelle prime sur la richesse de chaque costume.",
            "En famille, l'enjeu est de coordonner des âges et des envies très différents. Un thème souple laisse à chacun son personnage tout en gardant un fil rouge : une palette de couleurs commune, un même univers, un accessoire partagé. On évite ainsi le costume enfantin imposé à un ado récalcitrant comme le costume trop effrayant qui fait peur au plus petit.",
            "Anticipez enfin la logistique de groupe : centraliser les commandes évite les tailles incohérentes et les livraisons en retard. Fixez une date limite de commande commune, vérifiez que chaque pièce arrive à temps, et prévoyez un ou deux accessoires de rechange. Un groupe coordonné se prépare une à deux semaines avant, pas la veille.",
        ],
        "liste": [
            "En couple, achetez le duo ensemble pour la cohérence de style et de tailles.",
            "En groupe, misez sur une base commune ou un univers décliné en personnages.",
            "En famille, un fil rouge souple respecte l'âge et les envies de chacun.",
            "Centralisez les commandes et fixez une date limite commune.",
        ],
    }


def _bloc_entretien(mc: str) -> dict[str, Any]:
    return {
        "titre": "Après la fête : nettoyer, ranger et réutiliser son costume",
        "paragraphes": [
            "Un déguisement bien rangé est un déguisement qu'on ressort l'année suivante, ou qu'on revend, plutôt qu'un achat perdu au fond d'un placard. Le premier geste, dès le lendemain, est de traiter les taches de maquillage et de faux sang avant qu'elles ne s'incrustent. Un tamponnage à l'eau froide et au savon doux, à l'envers, vient à bout de la plupart des marques ; l'eau chaude, elle, fixe définitivement le sang textile.",
            "Respectez les consignes de lavage, souvent plus strictes que pour un vêtement ordinaire. Les imprimés squelette et les tissus à paillettes se lavent à froid, à l'envers, et sèchent à plat pour ne pas se craqueler ni se déformer. Beaucoup de costumes bon marché ne supportent pas le sèche-linge, dont la chaleur ruine les imprimés et les colles. En cas de doute, le lavage à la main reste la solution la plus sûre.",
            "Les accessoires se conservent mieux séparément. Une perruque se brosse doucement, se laisse sécher sur un support et se range dans son filet pour ne pas s'emmêler. Un masque en latex se garde à plat, à l'abri de la chaleur et de la lumière, avec un peu de talc pour éviter qu'il ne colle. Les chapeaux en feutre se rangent garnis de papier pour tenir leur forme.",
            "Pensez enfin à la seconde vie du costume. Ce qui ne resservira pas se revend facilement d'occasion après Halloween, ou se donne. Les pièces polyvalentes — cape, perruque, maquillage, chapeau — méritent au contraire d'être conservées : elles constituent, d'année en année, une petite réserve qui permet d'improviser un déguisement sans tout racheter.",
        ],
        "liste": [
            "Traitez les taches dès le lendemain, à l'eau froide : la chaleur fixe le faux sang.",
            "Lavez les imprimés à froid, à l'envers, séchage à plat, jamais au sèche-linge.",
            "Rangez perruque, masque et chapeau séparément pour préserver leur forme.",
            "Conservez les accessoires polyvalents : ils servent à improviser chaque année.",
        ],
    }


def _bloc_erreurs(mc: str) -> dict[str, Any]:
    return {
        "titre": "Les erreurs les plus fréquentes à l'achat d'un déguisement",
        "paragraphes": [
            "La première erreur est de commander à sa taille habituelle sans lire le guide des tailles. Les costumes taillent souvent petit et suivent une grille propre à chaque fabricant : un costume trop juste est inconfortable et craque, un costume trop grand pend et gâche l'effet. Trois mesures et une lecture du tableau règlent la question en deux minutes.",
            "La deuxième est de choisir un costume superbe en photo mais impraticable le soir : trop léger pour la météo, trop encombrant pour danser, trop chaud en intérieur, ou masquant trop la vision. Un déguisement se porte des heures ; l'oublier, c'est passer la soirée à souffrir dans une tenue qu'on retire à mi-parcours. Le confort d'usage doit peser autant que l'apparence.",
            "La troisième est d'attendre le dernier moment. Un costume commandé la veille n'a plus de solution de repli s'il taille mal ou arrive en retard. Les délais de livraison s'allongent à l'approche du 31 octobre, et les tailles courantes partent en premier. Commander une semaine avant, c'est se garder le droit d'essayer, de renvoyer et d'ajuster.",
            "La quatrième, enfin, est d'oublier les accessoires et le maquillage en pensant les ajouter plus tard. Dans les faits, on ne les ajoute pas, et le costume reste au niveau de tout le monde. L'accessoire et le maquillage, commandés en même temps que la base, sont précisément ce qui distingue une tenue mémorable d'un déguisement anonyme.",
        ],
        "liste": [
            "Ne commandez jamais sans lire le guide des tailles et vos mensurations.",
            "Pesez le confort d'usage autant que l'apparence : on porte le costume des heures.",
            "Anticipez : une semaine d'avance pour pouvoir essayer et échanger.",
            "Commandez accessoires et maquillage en même temps que le costume, pas « plus tard ».",
        ],
    }


def _bloc_original(mc: str) -> dict[str, Any]:
    return {
        "titre": "Se démarquer quand tout le monde se déguise pareil",
        "paragraphes": [
            "Chaque année, les mêmes sorcières, vampires et squelettes se croisent aux mêmes soirées. Se démarquer ne demande pas forcément un costume plus cher, mais un angle un peu différent. La première voie est le détournement : jouer un classique avec une exécution soignée — une sorcière au maquillage travaillé, un vampire à la cape impeccable — suffit à se distinguer de la version bâclée que tout le monde porte.",
            "La deuxième voie est l'humour. Les costumes humoristiques et gonflables ne font peur à personne, mais ils déclenchent les rires et restent l'entrée la plus remarquée de la soirée. C'est un pari qui fonctionne surtout entre adultes et en groupe, moins pour qui vise l'ambiance horreur. Le second degré est souvent ce dont on se souvient le lendemain.",
            "La troisième voie est le costume à concept, qui repose sur une idée plus que sur un achat : un jeu de mots costumé, une référence à un film ou à un mème, un duo qui n'a de sens qu'à deux. Ces déguisements coûtent souvent peu et marquent beaucoup, parce qu'ils surprennent. Ils demandent en revanche un public qui saisit la référence.",
            "La dernière voie, la plus sûre, tient au soin apporté aux finitions. À personnage égal, c'est toujours le costume le mieux fini — accessoires cohérents, maquillage net, coiffure assortie — qui se remarque. Se démarquer, le plus souvent, ce n'est pas choisir un personnage rare, c'est mieux exécuter un personnage connu.",
        ],
        "liste": [
            "Détournez un classique avec une exécution très soignée.",
            "L'humour et le gonflable marquent les esprits entre adultes.",
            "Le costume à concept coûte peu et surprend, s'il est compris.",
            "À personnage égal, ce sont les finitions qui font la différence.",
        ],
    }


BLOCS = [
    _bloc_taille,
    _bloc_confort_meteo,
    _bloc_securite,
    _bloc_accessoires,
    _bloc_maquillage,
    _bloc_derniere_minute,
    _bloc_diy,
    _bloc_budget,
    _bloc_groupe,
    _bloc_entretien,
    _bloc_erreurs,
    _bloc_original,
]


# ------------------------------------------------------------------- FAQ


FAQ_BASE = [
    ("Comment choisir la bonne taille pour un costume d'Halloween ?",
     "Ne vous fiez jamais à votre taille de prêt-à-porter habituelle : chaque fabricant a sa propre grille, souvent taillée petit. Prenez trois mesures au mètre ruban — tour de poitrine, tour de taille et hauteur si c'est une combinaison — et comparez-les au guide des tailles de la fiche. En cas d'hésitation entre deux tailles, montez d'un cran. Pour un enfant, choisissez selon la taille en centimètres, pas selon l'âge indiqué."),
    ("Quel déguisement choisir quand on s'y prend à la dernière minute ?",
     "Visez les personnages qui reposent sur un accessoire fort plutôt que sur un costume complet : une cape à capuche, un chapeau de sorcière ou un masque, portés sur des vêtements sombres déjà possédés. Le maquillage est votre meilleur allié : une palette basique et un peu de faux sang transforment une tenue noire en zombie ou en sorcière. Vérifiez toujours le délai de livraison avant de commander en ligne, sinon passez en boutique physique."),
    ("Quel costume tient chaud pour la tournée des bonbons ?",
     "Halloween tombe fin octobre : privilégiez un costume ample qui accepte une couche thermique en dessous, comme une cape ou une combinaison rembourrée. Un legging et un sous-pull sous une robe, ou un tee-shirt technique sous une combinaison, règlent le problème sans se voir. Ajoutez des chaussures déjà rodées et des chaussettes épaisses. Les costumes rembourrés de type citrouille tiennent chaud par eux-mêmes, ce qui les rend parfaits pour les enfants."),
    ("Comment faire un maquillage d'Halloween qui tient toute la soirée ?",
     "Préparez la peau avec une fine base ou une crème : les fards tiennent mieux et partent plus facilement ensuite. Travaillez par couches fines, fixez à la poudre et posez le faux sang en dernier, par petites touches, pour qu'il ne déteigne pas. Adaptez l'intensité au contexte : léger et sur la joue pour un enfant, plus appuyé pour une soirée en pénombre. Gardez un démaquillant gras, car ni le maquillage FX ni le faux sang ne partent à l'eau seule."),
    ("Comment se déguiser pour Halloween sans rien acheter ?",
     "Partez de votre armoire : une tenue entièrement noire est la base la plus polyvalente et devient chat, sorcière ou ombre selon l'accessoire ajouté. Un vieux drap blanc fait le fantôme le plus rapide qui soit ; des vêtements déchirés et un peu de faux sang composent un zombie convaincant. Du carton, du feutre et des épingles ouvrent de nombreuses possibilités. Faites participer les enfants à la fabrication : le costume s'ajuste parfaitement et le plaisir dure plus longtemps."),
    ("Les lentilles de contact fantaisie sont-elles sans danger ?",
     "Elles peuvent l'être à condition de respecter des règles strictes : n'achetez que des lentilles portant le marquage CE, ne les partagez jamais, et respectez la durée de port indiquée sur l'emballage. Lavez-vous les mains avant de les poser et entraînez-vous quelques jours avant la fête si vous n'avez pas l'habitude. Elles sont déconseillées aux enfants. Au moindre inconfort, rougeur ou vision trouble, retirez-les immédiatement."),
    ("Quel déguisement d'Halloween choisir en couple ?",
     "Le plus efficace est un duo assorti qui se lit immédiatement : deux squelettes, un couple médiéval, un vampire et sa victime. Achetez les deux pièces ensemble pour garantir la cohérence de style et pouvoir choisir chaque taille séparément. Un thème commun a toujours plus d'impact sur les photos que deux costumes trouvés chacun de son côté. Pensez aussi à ce que chaque pièce reste portable seule les années suivantes."),
    ("Comment rendre un enfant visible la nuit avec son costume ?",
     "Un enfant vêtu de noir ou de blanc sombre est presque invisible pour une voiture. Ajoutez des bandes réfléchissantes sur le costume et le sac à bonbons, glissez une petite lampe ou un bâton lumineux dans sa main, et restez côté trottoir. Les costumes phosphorescents, comme certains squelettes, améliorent nettement la visibilité tout en plaisant aux enfants. Vérifiez enfin que la capuche ne tombe pas sur les yeux et gêne la marche."),
]


# ------------------------------------------------------------- assemblage


def sections_supplementaires(
    sujet: dict[str, Any], produits: list[dict[str, Any]], mots_manquants: int
) -> list[dict[str, Any]]:
    """Sections de fond ajoutées quand un article n'atteint pas le plancher."""
    gn = _groupe_nominal(sujet.get("mot_cle", "déguisement"))
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
    mc = sujet.get("mot_cle", "déguisement")
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
            "titre": f"Ce qu'il faut savoir avant de choisir {gn}",
            "paragraphes": [
                f"Chercher {gn} revient presque toujours à arbitrer entre trois contraintes : l'effet recherché, le confort réel une fois le costume porté plusieurs heures, et le budget qu'on accepte d'y consacrer. Aucun modèle ne maximise les trois en même temps, et c'est précisément pour cela que la question « quel est le meilleur » n'a pas de réponse unique. La bonne question est plutôt : pour qui, pour quelle soirée, et pour combien de fois.",
                "Dans les faits, deux paramètres décident de la réussite bien plus que le personnage lui-même : la taille et les accessoires. Un costume mal taillé gâche le plus beau des déguisements, tandis qu'une base sobre relevée d'un accessoire et d'un maquillage soignés dépasse largement un costume complet porté tel quel. C'est pourquoi la première étape reste toujours la même : mesurer, puis choisir, puis accessoiriser.",
                f"Ce guide passe en revue les options les plus pertinentes si vous cherchez {gn}, puis détaille les critères qui font vraiment la différence le soir de la fête : la taille et la coupe, le confort face à la météo de fin octobre, la sécurité, les accessoires, le maquillage et le budget. L'objectif est que vous puissiez commander en connaissance de cause, sans comparer dix fiches produit qui se ressemblent toutes.",
            ],
        },
    )

    # Maillage interne : les titres cités sont transformés en liens au rendu.
    if articles_lies:
        citations = " ".join(
            f"Le guide « {a['titre_h1']} » complète utilement ce point." for a in articles_lies[:2]
        )
        sections.append(
            {
                "titre": "Pour aller plus loin",
                "paragraphes": [
                    "Le choix d'un déguisement se joue rarement sur un seul critère. "
                    "Si vous hésitez encore entre deux personnages ou deux formats, quelques "
                    "lectures ciblées font généralement basculer la décision plus vite qu'une "
                    f"comparaison supplémentaire de fiches produit. {citations}",
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
                    "Un choix cohérent dès lors que ces limites correspondent à votre usage réel."
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
            f"Comment choisir {gn} : la bonne taille, le confort, les accessoires, "
            "le maquillage et une sélection commentée."
        )[:155],
        "chapeau": (
            f"Choisir {gn} paraît simple jusqu'au moment où l'on compare deux fiches produit "
            "quasi identiques, avec les mêmes photos flatteuses et des tailles écrites en tout petit. "
            "La différence se joue pourtant sur des détails très concrets : la coupe et la taille réelle, "
            "le confort face au froid de fin octobre, la sécurité, et les accessoires qui font passer "
            "un costume ordinaire au niveau supérieur. Ce guide reprend ces critères un par un, "
            "les applique à une sélection de modèles, et vous donne les points à vérifier avant de commander."
        ),
        "sections": sections,
        "avis_produits": avis,
        "faq": faq,
        "conclusion": (
            f"Au terme de cette revue, la recommandation tient en une phrase : mesurez d'abord, "
            "accessoirisez ensuite. La très grande majorité des déceptions vient d'un costume mal "
            "taillé ou porté tel quel, pas d'un mauvais choix de personnage. Une fois la bonne taille "
            "validée sur le guide du vendeur, le reste se joue sur deux ou trois accessoires cohérents "
            "et un maquillage soigné. Pensez au confort pour une soirée de fin octobre, à la sécurité "
            "pour les enfants, et commandez une semaine à l'avance plutôt que la veille. Ces réflexes "
            "suffisent à transformer un achat correct en costume dont on garde une belle photo."
        ),
        "_source": "local",
    }
