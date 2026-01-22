from . import db
from . import select
from . import selectinload
from .models.relation import OneToManyParent
from .models.relation import ManyToOneChild
from .models.relation import ManyToOneChild2
from .models.relation import ManyToOneChild3
from .models.relation import OneToOneParent
from .models.relation import OneToOneChild
from .models.relation import ManyToManyLeft
from .models.relation import ManyToManyRight

def test_mappers():
    print("======MAPPERS:======")
    for mapper in db.Model.registry.mappers:
        print(mapper.class_.__name__, mapper.local_table)
        # for key in mapper.all_orm_descriptors.keys():
        kk = mapper.all_orm_descriptors.keys()
        for key,value in mapper.class_.__dict__.items():
            if key in kk:
                print(" ",key, value, type(value))
        for p in mapper.relationships:
            print(" ",p, p.key, p.direction.name, p.uselist)


# def test_create_table(app):7
#     with app.app_context():
#         db.create_all()
#         tn1 = TreeNode(data="root")
#         tn2 = TreeNode(data="child1", parent=tn1)
#         tn3 = TreeNode(data="child2", parent=tn1)
#         db.session.add_all(
#             [
#                 tn1,
#                 tn2,
#                 tn3,
#             ]
#         )
#         db.session.commit()
#         stmt = select(TreeNode).options(selectinload(TreeNode.children))
#         print(stmt)
#         tns = db.session.execute(stmt).scalars()
#         for tn in tns:
#             assert isinstance(tn, TreeNode)
#             print(tn.data, tn.children)