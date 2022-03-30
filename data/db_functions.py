from werkzeug.exceptions import abort


def pin_something(to_pin, db_sess):
    if to_pin:
        if to_pin.pinned is True:
            to_pin.pinned = False
        else:
            to_pin.pinned = True
        db_sess.commit()
    else:
        return abort(404)


def delete_something(to_delete, db_sess):
    if to_delete:
        db_sess.delete(to_delete)
        db_sess.commit()
    else:
        return abort(404)
