import random
import datetime
from flask_exts.proxies import _userstore
from .models import db
from .models.author import Author
from .models.author import AVAILABLE_USER_TYPES
from .models.tag import Tag
from .models.post import Post
from .models.tree import Tree
from .models.keyword import Keyword
from .models.user import MyUser
from .models.location_image import ImageType


def build_user_admin():
    u, _ = _userstore.create_user(
        username="admin", password="admin", email="admin@example.com"
    )
    r, _ = _userstore.create_role(name="admin")
    _userstore.user_add_role(u, r)


def build_sample_image_type():

    # Add some image types for the form_ajax_refs inside the inline_model
    image_types = ("JPEG", "PNG", "GIF")
    for image_type in image_types:
        itype = ImageType(name=image_type)
        db.session.add(itype)
    db.session.commit()


def build_sample_userkeyword():
    user_log = MyUser()
    user_log.username = "log"
    user_log.email = "log"
    user_log.password = "log"
    for kw in (Keyword("blammo"), Keyword("itsig")):
        user_log.keywords.append(kw)
    db.session.add(user_log)
    db.session.commit()


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
            "title": "de Finibus Bonorum et Malorum - Part I",
            "content": "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor \
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud \
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure \
dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. \
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt \
mollit anim id est laborum.",
        },
        {
            "title": "de Finibus Bonorum et Malorum - Part II",
            "content": "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque \
laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto \
beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur \
aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi \
nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, \
adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam \
aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam \
corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum \
iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum \
qui dolorem eum fugiat quo voluptas nulla pariatur?",
        },
        {
            "title": "de Finibus Bonorum et Malorum - Part III",
            "content": "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium \
voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati \
cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id \
est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam \
libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod \
maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. \
Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet \
ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur \
a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis \
doloribus asperiores repellat.",
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
    return


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    db.drop_all()
    db.create_all()

    build_sample_userkeyword()
    build_sample_tree()
    build_sample_post()
    build_user_admin()
    build_sample_image_type()

    return
