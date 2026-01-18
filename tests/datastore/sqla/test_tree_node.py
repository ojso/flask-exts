from . import db
from . import select
from . import selectinload
from .models.tree_node import TreeNode

def test_mappers():
    for mapper in db.Model.registry.mappers:
        print(mapper.class_.__name__, mapper.local_table)


def test_create_table(app):
    with app.app_context():
        db.create_all()
        tn1 = TreeNode(data="root")
        tn2 = TreeNode(data="child1", parent=tn1)
        tn3 = TreeNode(data="child2", parent=tn1)
        db.session.add_all(
            [
                tn1,
                tn2,
                tn3,
            ]
        )
        db.session.commit()
        stmt = select(TreeNode).options(selectinload(TreeNode.children))
        print(stmt)
        tns = db.session.execute(stmt).scalars()
        for tn in tns:
            assert isinstance(tn, TreeNode)
            print(tn.data, tn.children)