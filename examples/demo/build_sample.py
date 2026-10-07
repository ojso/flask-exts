import datetime
import random

from flask_exts.proxies import current_userstore

from .models import db
from .models.author import AVAILABLE_USER_TYPES, Author
from .models.post import Post
from .models.tag import Tag
from .models.tree import Tree


def build_user_admin():
    user_admin = current_userstore.create_user(
        username="admin", password="admin", email="admin@example.com"
    )
    role_admin = current_userstore.create_role(name="admin")
    current_userstore.user_add_role(user_admin, role_admin)


def build_sample_tree():
    # Create a sample Tree structure
    trunk = Tree(name="Trunk")
    db.session.add(trunk)
    for i in range(5):
        branch = Tree()
        branch.name = "Branch " + str(i + 1)
        branch.parent = trunk
        db.session.add(branch)
        for j in range(5):
            leaf = Tree()
            leaf.name = "Leaf " + str(j + 1)
            leaf.parent = branch
            db.session.add(leaf)
    db.session.commit()


def build_sample_post():
    first_names = [
        "Harry",
        "Amelia",
        "Oliver",
        "Jack",
        "Isabella",
        "Charlie",
        "Sophie",
        "Mia",
        "Jacob",
        "Thomas",
        "Emily",
        "Lily",
        "Ava",
        "Isla",
        "Alfie",
        "Olivia",
        "Jessica",
        "Riley",
        "William",
        "James",
        "Geoffrey",
        "Lisa",
        "Benjamin",
        "Stacey",
        "Lucy",
    ]
    last_names = [
        "Brown",
        "Brown",
        "Patel",
        "Jones",
        "Williams",
        "Johnson",
        "Taylor",
        "Thomas",
        "Roberts",
        "Khan",
        "Clarke",
        "Clarke",
        "Clarke",
        "James",
        "Phillips",
        "Wilson",
        "Ali",
        "Mason",
        "Mitchell",
        "Rose",
        "Davis",
        "Davies",
        "Rodriguez",
        "Cox",
        "Alexander",
    ]

    countries = [
        ("ZA", "South Africa", 27, "ZAR", "Africa/Johannesburg"),
        ("BF", "Burkina Faso", 226, "XOF", "Africa/Ouagadougou"),
        ("US", "United States of America", 1, "USD", "America/New_York"),
        ("BR", "Brazil", 55, "BRL", "America/Sao_Paulo"),
        ("TZ", "Tanzania", 255, "TZS", "Africa/Dar_es_Salaam"),
        ("DE", "Germany", 49, "EUR", "Europe/Berlin"),
        ("CN", "China", 86, "CNY", "Asia/Shanghai"),
    ]

    author_list = []
    for i in range(len(first_names)):
        author = Author()
        country = random.choice(countries)
        author.type = random.choice(AVAILABLE_USER_TYPES)[0]
        author.first_name = first_names[i]
        author.last_name = last_names[i]
        author.email = first_names[i].lower() + "@example.com"

        author.website = "https://www.example.com"
        author.ip_address = "127.0.0.1"

        author.coutry = country[1]
        author.currency = country[3]
        author.timezone = country[4]

        author.dialling_code = country[2]
        author.local_phone_number = "0" + "".join(random.choices("123456789", k=9))

        author_list.append(author)
        db.session.add(author)

    # Create sample Tags
    tag_list = []
    for tmp in [
        "YELLOW",
        "WHITE",
        "BLUE",
        "GREEN",
        "RED",
        "BLACK",
        "BROWN",
        "PURPLE",
        "ORANGE",
    ]:
        tag = Tag()
        tag.name = tmp
        tag_list.append(tag)
        db.session.add(tag)

    # Create sample Posts
    sample_text = [
        {
            "title": "Cities Turn Empty Offices Into Housing",
            "content": (
                "Across many cities, vacant office buildings are being converted into apartments "
                "and mixed-use spaces. The projects aim to revive downtowns, ease housing shortages, "
                "and adapt to remote work. Supporters say the trend could reshape urban life, "
                "but high renovation costs and zoning rules remain major obstacles."
            ),
        },
        {
            "title": "Universities Warn of Budget Cuts as Overseas Students Decline",
            "content": (
                "Universities are preparing for tighter budgets after a fall in international applications. "
                "Leaders warn that cuts could hit research, staffing, and courses that depend on overseas fees. "
                "The government says it is reviewing visa rules and funding to protect the sector's global reputation."
            ),
        },
        {
            "title": "Les villes accelerent la transition vers le velo",
            "content": (
                "Face a la pollution et aux embouteillages, de nombreuses villes developpent pistes cyclables, "
                "aides a l'achat et parkings securises. Les elus esperent changer les habitudes quotidiennes, "
                "mais certains habitants craignent que les travaux et les nouvelles regles compliquent la circulation."
            ),
        },
        {
            "title": "Staedte testen autofreie Innenstaedte",
            "content": (
                "Mehrere Staedte erproben Verkehrskonzepte, die private Autos aus zentralen Bereichen "
                "verdraengen sollen. Sie hoffen auf weniger Laerm, sauberere Luft und mehr Raum fuer "
                "Fussgaenger und Radfahrer. Kritiker bezweifeln jedoch, dass der oeffentliche Nahverkehr "
                "schon bereit ist."
            ),
        },
        {
            "title": "Ciudades amplian zonas verdes contra el calor",
            "content": (
                "Varios ayuntamientos crean nuevos parques y plantan arboles en barrios densamente poblados. "
                "El objetivo es reducir las temperaturas, mejorar la salud publica y adaptarse al cambio climatico. "
                "Los expertos advierten que estas medidas deben ir acompanadas de planes de agua y vivienda."
            ),
        },
    ]

    for author in author_list:
        entry = random.choice(sample_text)  # select text at random
        post = Post()
        post.author = author
        post.title = "{}'s opinion on {}".format(author.first_name, entry["title"])
        post.text = entry["content"]
        post.color = random.choice(["#cccccc", "red", "lightblue", "#0f0"])
        tmp = int(1000 * random.random())  # random number between 0 and 1000:
        post.date = datetime.datetime.now() - datetime.timedelta(days=tmp)
        # select a couple of tags at random
        post.tags = random.sample(tag_list, 2)
        # for tag in random.sample(tag_list, 2):
        #     a=AssociationPostTag()
        #     a.tag = tag
        #     post.tags.append(a)
        db.session.add(post)

    db.session.commit()


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    db.drop_all()
    db.create_all()

    build_sample_tree()
    build_sample_post()
    build_user_admin()

