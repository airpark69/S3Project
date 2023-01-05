from .db_models import db

def get_all(model):
    data = model.query.all()
    return data

## FOR CORPUS category and time query
def get_by_category_time(model, category, g_time):
    data = model.query.filter_by(category=category).filter_by(g_time=g_time)
    return data

def get_by_time(model, g_time):
    data = model.query.filter_by(g_time=g_time)
    return data

def add_instance(model, **kwargs):
    instance = model(**kwargs)
    db.session.add(instance)
    commit_changes()

def delete_instance(model, id):
    model.query.filter_by(id=id).delete()
    commit_changes()

def edit_instance(model, id, **kwargs):
    instance = model.query.filter_by(id=id).all()[0]
    for attr, new_value in kwargs.items():
        setattr(instance, attr, new_value)
    commit_changes()

def commit_changes():
    db.session.commit()